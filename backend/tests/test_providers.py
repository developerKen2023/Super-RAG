import pytest
from unittest.mock import MagicMock, patch


class TestLLMProviderFactory:
    """Tests for LLM provider factory."""

    def test_factory_minimax_provider(self):
        """Factory creates MiniMax provider for 'minimax'."""
        from app.services.llm_providers.factory import LLMProviderType

        # Just verify the enum values exist
        assert LLMProviderType.MINIMAX.value == "minimax"
        assert LLMProviderType.OLLAMA.value == "ollama"

    def test_factory_ollama_provider(self):
        """Factory enum has correct values."""
        from app.services.llm_providers.factory import LLMProviderType

        assert LLMProviderType.OLLAMA.value == "ollama"


class TestBaseLLMProvider:
    """Tests for base provider interface."""

    def test_llm_response_init(self):
        """LLMResponse initializes correctly."""
        from app.services.llm_providers.base import LLMResponse

        response = LLMResponse(content="Hello", response_id="resp-1")
        assert response.content == "Hello"
        assert response.response_id == "resp-1"

    def test_llm_response_defaults(self):
        """LLMResponse has correct defaults."""
        from app.services.llm_providers.base import LLMResponse

        response = LLMResponse()
        assert response.content == ""
        assert response.response_id is None

    def test_llm_stream_chunk_init(self):
        """LLMStreamChunk initializes correctly."""
        from app.services.llm_providers.base import LLMStreamChunk

        chunk = LLMStreamChunk(delta="Hello", response_id="resp-1", done=False)
        assert chunk.delta == "Hello"
        assert chunk.response_id == "resp-1"
        assert chunk.done is False

    def test_llm_stream_chunk_defaults(self):
        """LLMStreamChunk has correct defaults."""
        from app.services.llm_providers.base import LLMStreamChunk

        chunk = LLMStreamChunk()
        assert chunk.delta == ""
        assert chunk.response_id is None
        assert chunk.done is False


class TestMiniMaxProviderUnit:
    """Unit tests for MiniMax provider."""

    def test_provider_initialization(self):
        """MiniMax provider initializes with config."""
        from app.services.llm_providers.minimax import MiniMaxProvider

        with patch('app.services.llm_providers.minimax.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            provider = MiniMaxProvider()

            mock_openai.assert_called_once()

    def test_chat_complete_returns_content_string(self):
        """chat_complete returns content string for non-stream."""
        from app.services.llm_providers.minimax import MiniMaxProvider

        with patch('app.services.llm_providers.minimax.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            mock_message = MagicMock()
            mock_message.content = "Hello!"
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response

            provider = MiniMaxProvider()
            content = provider.chat_complete(
                messages=[{"role": "user", "content": "Hi"}],
                stream=False
            )

            assert content == "Hello!"


class TestOllamaProviderUnit:
    """Unit tests for Ollama provider."""

    def test_provider_initialization(self):
        """Ollama provider initializes with config."""
        from app.services.llm_providers.ollama import OllamaProvider

        with patch('app.services.llm_providers.ollama.httpx.Client'):
            provider = OllamaProvider()
            assert provider.base_url is not None
