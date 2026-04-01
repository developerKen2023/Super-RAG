import httpx
from app.config import get_settings
from app.services.llm_providers.base import BaseLLMProvider, LLMStreamChunk
from langsmith import traceable
from typing import Generator, Optional
import json

settings = get_settings()

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    @traceable(project_name=settings.langsmith_project, run_name="chat_completion")
    def chat_complete(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: Optional[list[dict]] = None
    ):
        if stream:
            return self._stream(messages, tools)
        else:
            return self._non_stream(messages, tools)

    def _stream(self, messages: list[dict], tools: Optional[list[dict]]) -> Generator[LLMStreamChunk, None, None]:
        payload = {"model": self.model, "messages": messages, "stream": True}
        if tools:
            payload["tools"] = tools

        with httpx.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=60.0
        ) as response:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        content = data["message"].get("content", "")
                        yield LLMStreamChunk(
                            delta=content,
                            done=data.get("done", False)
                        )
                    # Check for tool calls
                    if data.get("done", False):
                        return
            # Fallback: yield done chunk if not sent
            yield LLMStreamChunk(delta="", done=True)

    def _non_stream(self, messages: list[dict], tools: Optional[list[dict]]):
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            data = response.json()
            return data.get("message", {}).get("content", "")