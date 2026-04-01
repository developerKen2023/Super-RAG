from supabase import Client
from app.services.embedding_service import embed_texts
from app.services.metadata_service import extract_metadata
from app.services.docling_parser import DoclingParser
import uuid
import hashlib
import logging

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.parser = DoclingParser()

    def compute_content_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def find_duplicate_document(self, user_id: str, content_hash: str) -> dict | None:
        """Find existing document with same content hash for user."""
        response = self.supabase.table("documents").select(
            "id, filename, file_size, content_hash, created_at"
        ).eq("user_id", user_id).eq("content_hash", content_hash).execute()
        return response.data[0] if response.data else None

    def process_document(self, document_id: str, user_id: str) -> dict:
        """Main ingestion pipeline with deduplication."""
        try:
            # Get document
            doc = self.supabase.table("documents").select("*").eq("id", document_id).execute()
            if not doc.data:
                raise ValueError(f"Document {document_id} not found")

            document = doc.data[0]

            # Compute content hash
            file_path = document["file_path"]
            content_hash = self.compute_content_hash(file_path)

            # Check for duplicate if not already hashed
            if not document.get("content_hash"):
                existing = self.find_duplicate_document(user_id, content_hash)
                if existing:
                    # Mark this document as duplicate and skip processing
                    self.supabase.table("documents").update({
                        "status": "duplicate",
                        "metadata": {"duplicate_of": existing["id"]}
                    }).eq("id", document_id).eq("user_id", user_id).execute()
                    return {
                        "status": "duplicate",
                        "duplicate_of": existing["id"],
                        "filename": existing["filename"]
                    }

            # Update status to processing and store hash
            self.supabase.table("documents").update({
                "status": "processing",
                "content_hash": content_hash
            }).eq("id", document_id).execute()

            # Read file content for chunking (use Docling for supported formats)
            filename = document["filename"]
            if self.parser.can_parse(filename):
                content = self.parser.parse(file_path, filename)
                if not content:
                    raise ValueError(f"Failed to parse document {filename}")
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            # Extract metadata using LLM
            metadata_result = extract_metadata(content)
            if metadata_result.success:
                self.supabase.table("documents").update({
                    "metadata": metadata_result.metadata.model_dump()
                }).eq("id", document_id).eq("user_id", user_id).execute()
                logger.info(f"[Ingestion] Extracted metadata: {metadata_result.metadata.model_dump()}")
            else:
                logger.warning(f"[Ingestion] Metadata extraction failed: {metadata_result.error}")

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
