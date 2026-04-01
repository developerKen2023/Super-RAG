from supabase import Client
from app.services.llm_providers.base import BaseLLMProvider
from app.services.text_to_sql_service import TextToSQLService
import re
import logging

logger = logging.getLogger(__name__)


class ToolRouter:
    """
    Routes user queries to appropriate tools based on query analysis.
    """

    # Keywords that indicate statistical/document queries
    STATISTICAL_PATTERNS = [
        r"\bhow many\b",
        r"\bcount\b",
        r"\btotal\b",
        r"\bsum\b",
        r"\baverage\b",
        r"\bavg\b",
        r"\bmax\b",
        r"\bmin\b",
        r"\bsizes?\b",  # matches "size" or "sizes"
        r"\blist\b.*\bdocument",
        r"\bdocument.*\blist\b",
        r"\ball\b.*\bdocument",
        r"\bdocument.*\ball\b",
        r"\bsort\b.*\bdocument",
        r"\bdocument.*\bsort\b",
        r"\bstatus\b",
        r"\bmetadata\b",
        r"\btag\b.*\bdocument",
        r"\bdocument.*\btag\b",
        r"\bcategory\b.*\bdocument",
        r"\bdocument.*\bcategory\b",
        r"\bwhen\b.*\bupload",
        r"\bupload.*\bwhen\b",
        r"\blargest\b",
        r"\bsmallest\b",
        r"\bmost\b",
        r"\bleast\b",
        r"\bnewest\b",
        r"\boldest\b",
        r"\brecent\b",
    ]

    def __init__(self, supabase: Client, llm_provider: BaseLLMProvider):
        self.supabase = supabase
        self.llm_provider = llm_provider
        self.text_to_sql = TextToSQLService(supabase)

    async def route(self, query: str, user_id: str, enable_tools: bool = True) -> dict:
        """
        Decide which tool to use based on query analysis.

        Returns:
            dict with 'type' key:
            - 'text_to_sql': SQL results
            - 'rag': Continue with RAG (returns None for 'type')
            - 'error': Error occurred
        """
        if not enable_tools:
            return {"type": None}

        # Check if this is a statistical query
        if self._is_statistical_query(query):
            logger.info(f"Detected statistical query: {query}")
            return await self._handle_text_to_sql(query, user_id)

        # Not a statistical query, use RAG
        return {"type": None}

    def _is_statistical_query(self, query: str) -> bool:
        """Detect if query is asking for document statistics."""
        query_lower = query.lower()

        for pattern in self.STATISTICAL_PATTERNS:
            if re.search(pattern, query_lower):
                return True

        return False

    async def _handle_text_to_sql(self, query: str, user_id: str) -> dict:
        """Handle Text-to-SQL query."""
        try:
            result = await self.text_to_sql.generate_and_execute(query, user_id)
            if result.get("error"):
                return {"type": "error", "error": result["error"]}

            # Format results for display
            result["formatted"] = self.text_to_sql.format_results(result)
            return result

        except Exception as e:
            logger.error(f"Text-to-SQL failed: {e}")
            return {"type": "error", "error": str(e)}
