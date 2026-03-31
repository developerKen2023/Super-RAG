import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
from app.services.ingestion_service import IngestionService


class TestIngestionServiceUnit:
    """Unit tests for IngestionService."""

    def test_service_init(self):
        """Service initializes with supabase client."""
        mock_client = MagicMock()
        service = IngestionService(mock_client)
        assert service.supabase == mock_client

    def test_chunk_text_basic(self):
        """Text is chunked correctly with overlap."""
        service = IngestionService(MagicMock())

        text = "This is a long document that needs to be broken into smaller chunks for embedding."
        chunks = service.chunk_text(text, chunk_size=20, overlap=5)

        assert len(chunks) > 1
        assert chunks[0] == text[:20]

    def test_chunk_text_empty(self):
        """Empty text returns empty list."""
        service = IngestionService(MagicMock())
        chunks = service.chunk_text("", chunk_size=20, overlap=5)
        assert chunks == []

    def test_chunk_text_short(self):
        """Text shorter than chunk_size returns single chunk."""
        service = IngestionService(MagicMock())
        text = "Short text"
        chunks = service.chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_store_chunks_calls_insert(self):
        """Store chunks calls table insert."""
        mock_client = MagicMock()
        service = IngestionService(mock_client)

        chunks = ["chunk 1", "chunk 2"]
        embeddings = [[0.1] * 1536, [0.2] * 1536]

        service.store_chunks("doc-id", "user-id", chunks, embeddings)

        mock_client.table.assert_called_with("document_chunks")

    def test_store_chunks_empty(self):
        """Empty chunks does not call insert."""
        mock_client = MagicMock()
        service = IngestionService(mock_client)

        service.store_chunks("doc-id", "user-id", [], [])

        # Should not call insert for empty chunks
        mock_client.table.return_value.insert.return_value.execute.assert_not_called()


class TestIngestionProcessDocument:
    """Tests for process_document method."""

    def test_document_not_found(self):
        """Raises error when document not found."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        service = IngestionService(mock_client)

        with pytest.raises(ValueError, match="not found"):
            service.process_document("nonexistent-id", "user-id")


class TestContentHashing:
    """Tests for content hashing (Module 3)."""

    def test_compute_content_hash_consistency(self):
        """Same content produces same hash."""
        service = IngestionService(MagicMock())

        # Create temp file with known content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            hash1 = service.compute_content_hash(temp_path)
            hash2 = service.compute_content_hash(temp_path)
            assert hash1 == hash2
            assert len(hash1) == 64  # SHA-256 produces 64 hex chars
        finally:
            os.unlink(temp_path)

    def test_compute_content_hash_different_content(self):
        """Different content produces different hash."""
        service = IngestionService(MagicMock())

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Content A")
            path_a = f.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Content B")
            path_b = f.name

        try:
            hash_a = service.compute_content_hash(path_a)
            hash_b = service.compute_content_hash(path_b)
            assert hash_a != hash_b
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_find_duplicate_document_found(self):
        """Returns existing document when hash matches."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "doc-123", "filename": "test.txt"}]
        )

        service = IngestionService(mock_client)
        result = service.find_duplicate_document("user-1", "abc123")

        assert result["id"] == "doc-123"

    def test_find_duplicate_document_not_found(self):
        """Returns None when no duplicate exists."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )

        service = IngestionService(mock_client)
        result = service.find_duplicate_document("user-1", "abc123")

        assert result is None
