from openai import OpenAI
from app.config import get_settings
from langsmith import traceable
from typing import Generator

settings = get_settings()


class ChatService:
    """Service for interacting with OpenAI-compatible Chat Completions API."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model

    @traceable(project_name=settings.langsmith_project, run_name="chat_completion")
    def create_chat(
        self,
        messages: list[dict],
        stream: bool = True
    ):
        """
        Create a chat completion using OpenAI-compatible Chat Completions API.

        Args:
            messages: List of message dicts with 'role' and 'content'
                     e.g., [{"role": "user", "content": "Hello"}]
            stream: Whether to stream the response

        Returns:
            Chat completion response or stream generator
        """
        if stream:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
        else:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )


def get_chat_service() -> ChatService:
    return ChatService()
