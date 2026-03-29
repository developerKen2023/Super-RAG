import pytest
from unittest.mock import MagicMock, patch
from app.services.retrieval_service import RetrievalService


class TestRetrievalServiceUnit:
    """Unit tests for RetrievalService - no FastAPI dependencies."""

    def test_retrieval_service_init(self):
        """Service initializes with supabase client."""
        mock_client = MagicMock()
        service = RetrievalService(mock_client)
        assert service.supabase == mock_client

    def test_retrieve_relevant_chunks_no_results(self):
        """Returns empty list when no matching chunks."""
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = MagicMock(data=[])

        with patch('app.services.retrieval_service.embed_query') as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            service = RetrievalService(mock_client)
            chunks = service.retrieve_relevant_chunks("test query", "user-123", top_k=5)

            assert chunks == []
            mock_client.rpc.assert_called_once()

    def test_get_context_for_query_no_chunks(self):
        """Returns empty string when no chunks found."""
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = MagicMock(data=[])

        with patch('app.services.retrieval_service.embed_query') as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            service = RetrievalService(mock_client)
            context = service.get_context_for_query("test query", "user-123", top_k=5)

            assert context == ""

    def test_get_context_for_query_with_chunks(self):
        """Formats context correctly from chunks."""
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = MagicMock(data=[
            {"content": "First chunk content", "filename": "doc1.txt"},
            {"content": "Second chunk content", "filename": "doc2.txt"}
        ])

        with patch('app.services.retrieval_service.embed_query') as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            service = RetrievalService(mock_client)
            context = service.get_context_for_query("test query", "user-123", top_k=5)

            assert "First chunk content" in context
            assert "Second chunk content" in context
            assert "doc1.txt" in context

    def test_rpc_called_with_correct_params(self):
        """RPC is called with correct parameters."""
        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = MagicMock(data=[])

        with patch('app.services.retrieval_service.embed_query') as mock_embed:
            mock_embed.return_value = [0.1] * 1536

            service = RetrievalService(mock_client)
            service.retrieve_relevant_chunks("my query", "user-abc", top_k=10)

            # rpc is called with (function_name, params_dict)
            call_args = mock_client.rpc.call_args[0]
            assert call_args[0] == "match_document_chunks"
            params = call_args[1]
            assert params["query_embedding"] == [0.1] * 1536
            assert params["match_count"] == 10
            assert params["p_user_id"] == "user-abc"
