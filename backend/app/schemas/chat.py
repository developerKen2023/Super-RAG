from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: str | None = None


class ConversationResponse(BaseModel):
    """Response model for a conversation."""
    id: str
    user_id: str
    title: str
    openai_thread_id: str | None
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    """Request model for creating a message."""
    conversation_id: str
    content: str


class MessageResponse(BaseModel):
    """Response model for a message."""
    id: str
    conversation_id: str
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    openai_response_id: str | None
    created_at: datetime


class ChatStreamRequest(BaseModel):
    """Request model for streaming chat."""
    conversation_id: str | None
    message: str
    provider: str = "minimax"
