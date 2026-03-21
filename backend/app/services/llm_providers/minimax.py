from openai import OpenAI
from app.config import get_settings
from app.services.llm_providers.base import BaseLLMProvider, LLMStreamChunk
from langsmith import traceable
from typing import Generator

settings = get_settings()

class MiniMaxProvider(BaseLLMProvider):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.minimax_api_key,
            base_url=settings.minimax_base_url
        )
        self.model = settings.minimax_model

    @traceable(project_name=settings.langsmith_project, run_name="chat_completion")
    def chat_complete(self, messages: list[dict], stream: bool = False):
        if stream:
            return self._stream(messages)
        else:
            return self._non_stream(messages)

    def _stream(self, messages: list[dict]) -> Generator[LLMStreamChunk, None, None]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        last_response_id = None
        for chunk in response:
            if chunk.id:
                last_response_id = chunk.id
            if chunk.choices and chunk.choices[0].delta.content:
                yield LLMStreamChunk(
                    delta=chunk.choices[0].delta.content,
                    response_id=chunk.id,
                    done=False
                )
            if chunk.choices and getattr(chunk.choices[0], 'finish_reason', None):
                yield LLMStreamChunk(delta="", response_id=chunk.id, done=True)
        # Always yield a final done chunk
        yield LLMStreamChunk(delta="", response_id=last_response_id, done=True)

    def _non_stream(self, messages: list[dict]):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content