from pydantic import BaseModel, Field
from typing import Optional


class DocumentMetadata(BaseModel):
    """Structured metadata extracted from document content."""
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    language: Optional[str] = None


class MetadataExtractionResult(BaseModel):
    success: bool
    metadata: DocumentMetadata
    error: Optional[str] = None
