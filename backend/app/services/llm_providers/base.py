from abc import ABC, abstractmethod
from typing import Generator

class LLMResponse:
    def __init__(self, content: str = "", response_id: str = None):
        self.content = content
        self.response_id = response_id

class LLMStreamChunk:
    def __init__(self, delta: str = "", response_id: str = None, done: bool = False):
        self.delta = delta
        self.response_id = response_id
        self.done = done

class BaseLLMProvider(ABC):
    @abstractmethod
    def chat_complete(self, messages: list[dict], stream: bool = False):
        pass