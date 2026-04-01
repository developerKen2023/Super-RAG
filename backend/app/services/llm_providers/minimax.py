from openai import OpenAI
from app.config import get_settings
from app.services.llm_providers.base import BaseLLMProvider, LLMStreamChunk
from langsmith import traceable
from typing import Generator, Optional

settings = get_settings()

class MiniMaxProvider(BaseLLMProvider):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.minimax_api_key,
            base_url=settings.minimax_base_url
        )
        self.model = settings.minimax_model

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
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
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
            # Check for tool calls in delta
            if chunk.choices and getattr(chunk.choices[0].delta, 'tool_calls', None):
                tool_calls = [
                    {
                        "id": tc.index,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in chunk.choices[0].delta.tool_calls
                ]
                yield LLMStreamChunk(
                    delta="",
                    response_id=chunk.id,
                    done=False,
                    tool_calls=tool_calls
                )
            if chunk.choices and getattr(chunk.choices[0], 'finish_reason', None):
                yield LLMStreamChunk(delta="", response_id=chunk.id, done=True)
        # Always yield a final done chunk
        yield LLMStreamChunk(delta="", response_id=last_response_id, done=True)

    def _non_stream(self, messages: list[dict], tools: Optional[list[dict]]):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content