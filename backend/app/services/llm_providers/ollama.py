import httpx
from app.config import get_settings
from app.services.llm_providers.base import BaseLLMProvider, LLMStreamChunk
from langsmith import traceable
from typing import Generator

settings = get_settings()

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    @traceable(project_name=settings.langsmith_project, run_name="chat_completion")
    def chat_complete(self, messages: list[dict], stream: bool = False):
        if stream:
            return self._stream(messages)
        else:
            return self._non_stream(messages)

    def _stream(self, messages: list[dict]) -> Generator[LLMStreamChunk, None, None]:
        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": True},
            timeout=60.0
        ) as response:
            for line in response.iter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "message" in data:
                        yield LLMStreamChunk(
                            delta=data["message"].get("content", ""),
                            done=data.get("done", False)
                        )
                    if data.get("done", False):
                        return
            # Fallback: yield done chunk if not sent
            yield LLMStreamChunk(delta="", done=True)

    def _non_stream(self, messages: list[dict]):
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False}
            )
            data = response.json()
            return data.get("message", {}).get("content", "")