from abc import ABC, abstractmethod
from typing import Generator, Optional

class LLMResponse:
    def __init__(self, content: str = "", response_id: str = None):
        self.content = content
        self.response_id = response_id

class LLMStreamChunk:
    def __init__(
        self,
        delta: str = "",
        response_id: str = None,
        done: bool = False,
        tool_calls: Optional[list[dict]] = None
    ):
        self.delta = delta
        self.response_id = response_id
        self.done = done
        self.tool_calls = tool_calls

class BaseLLMProvider(ABC):
    @abstractmethod
    def chat_complete(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: Optional[list[dict]] = None
    ):
        pass