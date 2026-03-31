from app.services.llm_providers import get_llm_provider
from app.schemas.metadata import DocumentMetadata, MetadataExtractionResult
import json
import re
import logging

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a document analysis assistant. Extract structured metadata from the document content.
Return ONLY valid JSON matching the schema. If information is not available, use null for optional fields.
Required fields: title, author, date, category, tags (array), summary, language"""


def extract_metadata(content: str, provider: str = "minimax") -> MetadataExtractionResult:
    """Extract metadata from document content using LLM."""
    truncated = content[:4000]  # Limit to avoid excessive tokens

    user_prompt = f"""Extract metadata from this document:
{truncated}

Return a valid JSON object with these exact fields (keep tags to 3-5 most relevant ones):
{{
    "title": "document title or null",
    "author": "author name or null",
    "date": "date string or null",
    "category": "category or null",
    "tags": ["tag1", "tag2", "tag3"] (maximum 5 tags, only the most relevant),
    "summary": "brief summary or null",
    "language": "language code or null"
}}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    llm_provider = get_llm_provider(provider)

    try:
        result = llm_provider.chat_complete(messages, stream=False)

        # Handle different return types
        if isinstance(result, str):
            content_str = result
        elif hasattr(result, 'choices') and hasattr(result.choices[0].message, 'content'):
            content_str = result.choices[0].message.content
        else:
            content_str = str(result)

        logger.info(f"[Metadata] Raw LLM response: {content_str[:500]}")

        # Try to extract JSON from the response
        # Handle cases where LLM might wrap JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content_str)
        if json_match:
            content_str = json_match.group(1)
        else:
            # Try to find JSON object in the response
            json_start = content_str.find('{')
            json_end = content_str.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                content_str = content_str[json_start:json_end]

        metadata_dict = json.loads(content_str)
        metadata = DocumentMetadata(**metadata_dict)
        logger.info(f"[Metadata] Extracted successfully: {metadata}")
        return MetadataExtractionResult(success=True, metadata=metadata)
    except json.JSONDecodeError as e:
        logger.error(f"[Metadata] JSON parse error: {e}")
        return MetadataExtractionResult(
            success=False,
            metadata=DocumentMetadata(),
            error=f"JSON parse error: {e}"
        )
    except Exception as e:
        logger.error(f"[Metadata] Extraction error: {e}")
        return MetadataExtractionResult(
            success=False,
            metadata=DocumentMetadata(),
            error=str(e)
        )
