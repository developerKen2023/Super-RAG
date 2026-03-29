import pytest
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
    """Tests for content hashing (placeholders for Module 3)."""

    def test_placeholder_hash_generation(self):
        """Same content should produce same hash - placeholder."""
        # Module 3 will implement actual hashing
        pass

    def test_placeholder_duplicate_detection(self):
        """Duplicate content detected via hash - placeholder."""
        pass

    def test_placeholder_incremental_update(self):
        """Modified content reprocessed - placeholder."""
        pass
