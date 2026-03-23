from supabase import Client
from app.services.embedding_service import embed_texts
import uuid
import logging

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def process_document(self, document_id: str, user_id: str) -> dict:
        """Main ingestion pipeline."""
        try:
            # Get document
            doc = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            if not doc.data:
                raise ValueError(f"Document {document_id} not found")

            document = doc.data[0]

            # Update status to processing
            self.supabase.table("documents").update({"status": "processing"}).eq("id", document_id).execute()

            # Read file content
            file_path = document["file_path"]
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Chunk text
            chunks = self.chunk_text(content, chunk_size=500, overlap=50)

            # Filter out empty chunks
            original_count = len(chunks)
            chunks = [c for c in chunks if c and c.strip()]
            logger.info(f"[Ingestion] Chunked into {original_count} chunks, {len(chunks)} non-empty")

            if not chunks:
                raise ValueError("No content to embed after chunking")

            # Generate embeddings
            embeddings = embed_texts(chunks)

            # Store chunks
            self.store_chunks(document_id, user_id, chunks, embeddings)

            # Update document status to completed (include user_id for RLS)
            result = self.supabase.table("documents").update({
                "status": "completed",
                "chunk_count": len(chunks)
            }).eq("id", document_id).eq("user_id", user_id).execute()

            return {"status": "completed", "chunk_count": len(chunks)}

        except Exception as e:
            import traceback
            logger.error(f"Ingestion error: {e}")
            logger.error(traceback.format_exc())
            try:
                self.supabase.table("documents").update({
                    "status": "failed",
                    "metadata": {"error": str(e)}
                }).eq("id", document_id).eq("user_id", user_id).execute()
            except:
                pass
            raise

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    def store_chunks(self, document_id: str, user_id: str, chunks: list[str], embeddings: list[list[float]]):
        """Store chunks with embeddings in database."""
        rows = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            rows.append({
                "id": str(uuid.uuid4()),
                "document_id": document_id,
                "user_id": user_id,
                "chunk_index": i,
                "content": chunk,
                "embedding": embedding
            })

        if rows:
            self.supabase.table("document_chunks").insert(rows).execute()
