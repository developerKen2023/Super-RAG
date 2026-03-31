import pytest
from unittest.mock import patch, MagicMock
from app.services.metadata_service import extract_metadata
from app.schemas.metadata import DocumentMetadata, MetadataExtractionResult


class TestMetadataExtraction:
    def test_extract_metadata_success(self):
        with patch('app.services.metadata_service.get_llm_provider') as mock:
            mock.return_value.chat_complete.return_value = '{"title":"Test","tags":["ai"]}'
            result = extract_metadata("test content")
            assert result.success is True
            assert result.metadata.title == "Test"
            assert "ai" in result.metadata.tags

    def test_extract_metadata_failure_graceful(self):
        with patch('app.services.metadata_service.get_llm_provider') as mock:
            mock.return_value.chat_complete.side_effect = Exception("API Error")
            result = extract_metadata("content")
            assert result.success is False
            assert result.metadata.title is None

    def test_truncates_long_content(self):
        """Verify content > 4000 chars is truncated."""
        with patch('app.services.metadata_service.get_llm_provider') as mock:
            mock.return_value.chat_complete.return_value = '{"title":"Test","tags":[]}'

            # Create content longer than 4000 chars
            long_content = "x" * 5000
            extract_metadata(long_content)

            # Verify the provider was called with truncated content
            call_args = mock.return_value.chat_complete.call_args
            messages = call_args[0][0]
            user_content = messages[1]["content"]
            # The content should be truncated to 4000 chars
            assert len(user_content) < 5000


class TestMetadataSchema:
    def test_valid_metadata(self):
        meta = DocumentMetadata(title="Test", tags=["a", "b"])
        assert meta.title == "Test"
        assert len(meta.tags) == 2

    def test_optional_fields_default(self):
        meta = DocumentMetadata()
        assert meta.title is None
        assert meta.tags == []

    def test_all_fields_populated(self):
        meta = DocumentMetadata(
            title="My Document",
            author="John Doe",
            date="2024-01-15",
            category="technical",
            tags=["python", "testing"],
            summary="A test document",
            language="en"
        )
        assert meta.title == "My Document"
        assert meta.author == "John Doe"
        assert meta.category == "technical"
        assert len(meta.tags) == 2
        assert meta.language == "en"
