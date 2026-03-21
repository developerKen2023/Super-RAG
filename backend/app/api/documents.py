from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from supabase import Client
from app.deps import get_authenticated_supabase
from app.services.ingestion_service import IngestionService
import uuid
import os
import shutil

router = APIRouter(prefix="/documents", tags=["documents"])

DOCUMENTS_DIR = "uploads/documents"

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """Upload a document and create a pending record."""
    current_user, supabase = user_supabase

    # Ensure upload directory exists
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(DOCUMENTS_DIR, filename)

    # Save file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Create document record
    response = supabase.table("documents").insert({
        "id": file_id,
        "user_id": current_user.id,
        "filename": file.filename,
        "file_path": file_path,
        "file_size": file.size,
        "mime_type": file.content_type,
        "status": "pending"
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create document record")

    # Start ingestion (synchronous for now)
    try:
        ingestion = IngestionService(supabase)
        ingestion.process_document(file_id, current_user.id)
    except Exception as e:
        # Update status to failed
        supabase.table("documents").update({
            "status": "failed",
            "metadata": {"error": str(e)}
        }).eq("id", file_id).execute()
        raise e

    # Return the updated document (include user_id for RLS)
    updated = supabase.table("documents").select("*").eq("id", file_id).eq("user_id", current_user.id).execute()
    return updated.data[0]

@router.get("")
async def list_documents(
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """List all documents for current user."""
    current_user, supabase = user_supabase

    response = supabase.table("documents").select("*").eq(
        "user_id", current_user.id
    ).order("created_at", desc=True).execute()

    return response.data

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """Delete a document and its chunks."""
    current_user, supabase = user_supabase

    # Verify ownership
    doc = supabase.table("documents").select("*").eq(
        "id", document_id
    ).eq("user_id", current_user.id).execute()

    if not doc.data:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    file_path = doc.data[0]["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete chunks (RLS will handle user check)
    supabase.table("document_chunks").delete().eq("document_id", document_id).execute()

    # Delete document
    supabase.table("documents").delete().eq("id", document_id).execute()

    return {"message": "Document deleted"}
