import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from app.services.docling_parser import DoclingParser


class TestDoclingParser:
    """Tests for DoclingParser."""

    def test_can_parse_pdf(self):
        """Returns True for .pdf files."""
        parser = DoclingParser()
        assert parser.can_parse("document.pdf") is True
        assert parser.can_parse("DOCUMENT.PDF") is True

    def test_can_parse_docx(self):
        """Returns True for .docx files."""
        parser = DoclingParser()
        assert parser.can_parse("document.docx") is True
        assert parser.can_parse("DOCUMENT.DOCX") is True

    def test_can_parse_html(self):
        """Returns True for .html and .htm files."""
        parser = DoclingParser()
        assert parser.can_parse("document.html") is True
        assert parser.can_parse("document.htm") is True

    def test_can_parse_markdown(self):
        """Returns True for .md files."""
        parser = DoclingParser()
        assert parser.can_parse("document.md") is True

    def test_can_parse_unsupported(self):
        """Returns False for unsupported file types."""
        parser = DoclingParser()
        assert parser.can_parse("document.txt") is False
        assert parser.can_parse("document.py") is False
        assert parser.can_parse("document.json") is False
        assert parser.can_parse("document.xlsx") is False

    @patch('app.services.docling_parser.DocumentConverter')
    def test_parse_returns_text(self, mock_converter):
        """Parse returns text content from document."""
        mock_result = MagicMock()
        mock_result.document.export_to_text.return_value = "Extracted text content"
        mock_converter.return_value.convert.return_value = mock_result

        parser = DoclingParser()
        result = parser.parse("/fake/path/doc.pdf", "doc.pdf")

        assert result == "Extracted text content"
        mock_converter.return_value.convert.assert_called_once_with("/fake/path/doc.pdf")

    @patch('app.services.docling_parser.DocumentConverter')
    def test_parse_failure_returns_empty_string(self, mock_converter):
        """Parse failure returns empty string gracefully."""
        mock_converter.return_value.convert.side_effect = Exception("Parse error")

        parser = DoclingParser()
        result = parser.parse("/fake/path/doc.pdf", "doc.pdf")

        assert result == ""

    def test_supported_types_contains_expected_formats(self):
        """SUPPORTED_TYPES contains all expected formats."""
        parser = DoclingParser()
        expected = {".pdf", ".docx", ".html", ".htm", ".md"}
        assert parser.SUPPORTED_TYPES == expected
