from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.supabase import get_supabase
from app.deps import get_authenticated_supabase, get_current_user
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ChatStreamRequest
)
from app.services.openai_service import get_chat_service
import json

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    List all conversations for the current user.
    """
    user = await get_current_user(credentials)
    supabase.auth.set_session(credentials.credentials, credentials.credentials)
    response = supabase.table("conversations").select("*").eq(
        "user_id", user.id
    ).order("updated_at", desc=True).execute()

    return response.data


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    Create a new conversation.
    """
    # Validate token and get user
    user = await get_current_user(credentials)

    # Set session so RLS works
    supabase.auth.set_session(credentials.credentials, credentials.credentials)

    data = {
        "user_id": user.id,
        "title": request.title or "New Conversation"
    }

    response = supabase.table("conversations").insert(data).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )

    return response.data[0]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    Delete a conversation and all its messages.
    """
    user = await get_current_user(credentials)
    supabase.auth.set_session(credentials.credentials, credentials.credentials)
    conv = supabase.table("conversations").select("*").eq(
        "id", conversation_id
    ).eq("user_id", user.id).execute()

    if not conv.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    supabase.table("conversations").delete().eq("id", conversation_id).execute()

    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages", response_model=list)
async def list_messages(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    List all messages in a conversation.
    """
    user = await get_current_user(credentials)
    supabase.auth.set_session(credentials.credentials, credentials.credentials)
    conv = supabase.table("conversations").select("*").eq(
        "id", conversation_id
    ).eq("user_id", user.id).execute()

    if not conv.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    response = supabase.table("messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=False).execute()

    return response.data


def build_messages(conversation_id: str, new_message: str, supabase: Client) -> list[dict]:
    """
    Build messages array for Chat Completions API from database history.
    """
    # Get existing messages
    response = supabase.table("messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=False).execute()

    messages = []
    for msg in response.data:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add new user message
    messages.append({
        "role": "user",
        "content": new_message
    })

    return messages


@router.post("/stream")
async def stream_chat(
    request: ChatStreamRequest,
    user_supabase: tuple[dict, Client] = Depends(get_authenticated_supabase)
):
    """
    Stream chat response using SSE.
    Creates a new conversation if conversation_id is not provided.
    """
    current_user, supabase = user_supabase
    conversation_id = request.conversation_id
    user_message = request.message

    # Get or create conversation
    if conversation_id:
        conv = supabase.table("conversations").select("*").eq(
            "id", conversation_id
        ).eq("user_id", current_user.id).execute()

        if not conv.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        conversation = conv.data[0]
    else:
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        conv_response = supabase.table("conversations").insert({
            "user_id": current_user.id,
            "title": title
        }).execute()

        if not conv_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )

        conversation = conv_response.data[0]
        conversation_id = conversation["id"]

    # Save user message
    supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "user_id": current_user.id,
        "role": "user",
        "content": user_message
    }).execute()

    # Build messages array with conversation history
    messages = build_messages(conversation_id, user_message, supabase)

    # Stream response from LLM
    chat_service = get_chat_service()

    def event_generator():
        try:
            response_stream = chat_service.create_chat(
                messages=messages,
                stream=True
            )

            full_content = ""
            completion_id = None

            # Chat Completions streaming format
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"

                if chunk.id:
                    completion_id = chunk.id

            yield f"data: {json.dumps({'type': 'done', 'response_id': completion_id})}\n\n"

            # Save assistant message to database (insert, not update)
            if full_content:
                supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "user_id": current_user.id,
                    "role": "assistant",
                    "content": full_content,
                    "openai_response_id": completion_id
                }).execute()

            # Update conversation timestamp
            supabase.table("conversations").update({
                "updated_at": "now()"
            }).eq("id", conversation_id).execute()

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
