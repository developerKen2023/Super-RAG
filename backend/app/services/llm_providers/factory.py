from enum import Enum
from app.services.llm_providers.minimax import MiniMaxProvider
from app.services.llm_providers.ollama import OllamaProvider
from app.services.llm_providers.base import BaseLLMProvider

class LLMProviderType(Enum):
    MINIMAX = "minimax"
    OLLAMA = "ollama"

def get_llm_provider(provider_type: str = None) -> BaseLLMProvider:
    if provider_type == LLMProviderType.OLLAMA.value:
        return OllamaProvider()
    return MiniMaxProvider()  # default