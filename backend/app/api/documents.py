from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from supabase import Client
from app.deps import get_authenticated_supabase
from app.services.ingestion_service import IngestionService
from typing import Optional
import uuid
import os
import hashlib

router = APIRouter(prefix="/documents", tags=["documents"])

DOCUMENTS_DIR = "uploads/documents"

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """Upload a document with deduplication."""
    current_user, supabase = user_supabase

    # Read file content for hash computation
    content = await file.read()
    file_size = len(content)

    # Compute SHA-256 hash of content
    content_hash = hashlib.sha256(content).hexdigest()

    # Check for existing document with same hash before saving
    existing = supabase.table("documents").select(
        "id, filename, file_size, created_at"
    ).eq("user_id", current_user.id).eq("content_hash", content_hash).execute()

    if existing.data:
        # Return existing document info as duplicate
        existing_doc = existing.data[0]
        return {
            "id": existing_doc["id"],
            "filename": existing_doc["filename"],
            "status": "duplicate",
            "duplicate_of": existing_doc["id"],
            "message": "Document with same content already exists"
        }

    # Ensure upload directory exists
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(DOCUMENTS_DIR, filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record with content_hash
    response = supabase.table("documents").insert({
        "id": file_id,
        "user_id": current_user.id,
        "filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": file.content_type,
        "status": "pending",
        "content_hash": content_hash
    }).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create document record")

    # Start ingestion (synchronous for now)
    try:
        ingestion = IngestionService(supabase)
        result = ingestion.process_document(file_id, current_user.id)

        # If duplicate found during processing (race condition), return that info
        if result.get("status") == "duplicate":
            return result

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

@router.get("/check-duplicate")
async def check_duplicate(
    content_hash: str = Query(..., description="SHA-256 hash of file content"),
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """Check if a document with this content hash already exists."""
    current_user, supabase = user_supabase

    response = supabase.table("documents").select(
        "id, filename, file_size, created_at"
    ).eq("user_id", current_user.id).eq("content_hash", content_hash).execute()

    if response.data:
        return {
            "is_duplicate": True,
            "existing_document": response.data[0]
        }
    return {"is_duplicate": False}

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

@router.get("/filter")
async def filter_documents(
    tag: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """Filter documents by metadata fields."""
    current_user, supabase = user_supabase

    query = supabase.table("documents").select("*").eq("user_id", current_user.id).eq("status", "completed")

    if tag:
        query = query.contains("metadata", {"tags": [tag]})
    if category:
        query = query.eq("metadata->>category", category)

    response = query.order("created_at", desc=True).limit(limit).execute()
    return response.data
