import os
import logging
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)


class DoclingParser:
    """Parses PDF, DOCX, HTML, Markdown using Docling."""

    SUPPORTED_TYPES = {".pdf", ".docx", ".html", ".htm", ".md"}

    def can_parse(self, filename: str) -> bool:
        """Check if file type is supported."""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.SUPPORTED_TYPES

    def parse(self, file_path: str, filename: str) -> str:
        """Parse document and return text content."""
        try:
            converter = DocumentConverter()
            result = converter.convert(file_path)
            return result.document.export_to_text()
        except Exception as e:
            logger.warning(f"[DoclingParser] Failed to parse {filename}: {e}")
            return ""
