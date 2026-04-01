import pytest
from unittest.mock import MagicMock
from app.services.text_to_sql_service import TextToSQLService
from app.services.tool_router import ToolRouter


class TestTextToSQLService:
    """Tests for Text-to-SQL service."""

    def test_is_safe_sql_valid_select(self):
        """Valid SELECT queries are allowed."""
        service = TextToSQLService(MagicMock())

        valid_queries = [
            "SELECT COUNT(*) FROM documents WHERE user_id = '123'",
            "SELECT filename, file_size FROM documents",
            "SELECT * FROM documents WHERE status = 'completed'",
        ]

        for query in valid_queries:
            assert service._is_safe_sql(query) is True, f"Should be safe: {query}"

    def test_is_safe_sql_blocks_dangerous(self):
        """Dangerous SQL is blocked."""
        service = TextToSQLService(MagicMock())

        dangerous_queries = [
            "INSERT INTO documents VALUES (1)",
            "UPDATE documents SET status = 'hacked'",
            "DELETE FROM documents",
            "DROP TABLE documents",
            "SELECT COUNT(*) FROM users; DELETE FROM documents",  # Multiple statements
        ]

        for query in dangerous_queries:
            assert service._is_safe_sql(query) is False, f"Should be blocked: {query}"

    def test_is_safe_sql_only_documents_table(self):
        """Only documents table is allowed."""
        service = TextToSQLService(MagicMock())

        # Invalid - not documents table
        assert service._is_safe_sql("SELECT * FROM users") is False

        # Valid - documents table
        assert service._is_safe_sql("SELECT * FROM documents") is True

    def test_extract_sql_from_markdown(self):
        """SQL in markdown code blocks is extracted."""
        service = TextToSQLService(MagicMock())

        response = """Here is the SQL:

```sql
SELECT COUNT(*) FROM documents
```

Hope this helps!"""

        sql = service._extract_sql(response)
        assert sql == "SELECT COUNT(*) FROM documents"

    def test_extract_sql_simple(self):
        """Simple SQL response is extracted."""
        service = TextToSQLService(MagicMock())

        response = "SELECT COUNT(*) FROM documents WHERE user_id = '123'"
        sql = service._extract_sql(response)
        assert sql == "SELECT COUNT(*) FROM documents WHERE user_id = '123'"

    def test_extract_sql_with_sql_prefix(self):
        """SQL with SQL: prefix is extracted."""
        service = TextToSQLService(MagicMock())

        response = "SQL: SELECT COUNT(*) FROM documents"
        sql = service._extract_sql(response)
        assert sql == "SELECT COUNT(*) FROM documents"


class TestToolRouter:
    """Tests for tool router."""

    def test_is_statistical_query_count(self):
        """Count queries are detected."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("How many documents do I have?") is True
        assert router._is_statistical_query("Count my files") is True

    def test_is_statistical_query_size(self):
        """Size queries are detected."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("What is my total file size?") is True
        assert router._is_statistical_query("Show me document sizes") is True

    def test_is_statistical_query_status(self):
        """Status queries are detected."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("Show me documents by status") is True
        assert router._is_statistical_query("What status are my documents?") is True

    def test_is_statistical_query_sort(self):
        """Sort queries are detected."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("Sort documents by size") is True
        assert router._is_statistical_query("Show me the largest document") is True

    def test_is_statistical_query_list(self):
        """List queries are detected."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("List all my documents") is True
        assert router._is_statistical_query("Show me all documents") is True

    def test_is_statistical_query_not(self):
        """Non-statistical queries return False."""
        router = ToolRouter(MagicMock(), MagicMock())

        assert router._is_statistical_query("What is machine learning?") is False
        assert router._is_statistical_query("Tell me about RAG") is False
        assert router._is_statistical_query("Summarize my document") is False

    @pytest.mark.asyncio
    async def test_route_without_tools(self):
        """Route returns None when tools disabled."""
        router = ToolRouter(MagicMock(), MagicMock())

        result = await router.route("How many documents?", "user-123", enable_tools=False)
        assert result.get("type") is None

    @pytest.mark.asyncio
    async def test_route_non_statistical_query(self):
        """Non-statistical query returns None for RAG."""
        router = ToolRouter(MagicMock(), MagicMock())

        result = await router.route("What is AI?", "user-123", enable_tools=True)
        assert result.get("type") is None
