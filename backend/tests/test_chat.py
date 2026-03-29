import pytest
from unittest.mock import MagicMock
from app.api.chat import build_messages


class TestBuildMessages:
    """Tests for message building utility."""

    def test_build_messages_empty(self):
        """Empty conversation builds basic messages."""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[]
        )

        messages = build_messages("conv-1", "Hello", mock_supabase, "")

        # Should have system (if rag_context) + user message
        assert len(messages) >= 1
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "Hello"

    def test_build_messages_with_history(self):
        """Conversation history is included."""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        )

        messages = build_messages("conv-1", "How are you?", mock_supabase, "")

        assert len(messages) >= 3  # history + new user message

    def test_build_messages_with_rag_context(self):
        """RAG context is prepended as system message."""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MagicMock(
            data=[]
        )

        rag_context = "From document: important info"
        messages = build_messages("conv-1", "What is X?", mock_supabase, rag_context)

        # First message should be system with rag context
        assert messages[0]["role"] == "system"
        assert "important info" in messages[0]["content"]
