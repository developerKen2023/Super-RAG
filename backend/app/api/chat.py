from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.supabase import get_supabase
from app.deps import get_authenticated_supabase, get_current_user
from app.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ChatStreamRequest
)
from app.services.llm_providers import get_llm_provider
from app.services.retrieval_service import RetrievalService
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


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    Update a conversation's title.
    """
    user = await get_current_user(credentials)
    supabase.auth.set_session(credentials.credentials, credentials.credentials)

    # Verify conversation exists and belongs to user
    conv = supabase.table("conversations").select("*").eq(
        "id", conversation_id
    ).eq("user_id", user.id).execute()

    if not conv.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    response = supabase.table("conversations").update(
        {"title": request.title, "updated_at": "now()"}
    ).eq("id", conversation_id).execute()

    return response.data[0]


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


def build_messages(conversation_id: str, new_message: str, supabase: Client, rag_context: str = "") -> list[dict]:
    """
    Build messages array for Chat Completions API from database history.
    If rag_context is provided, prepend a system message with the retrieved context.
    """
    messages = []

    # Add system message with RAG context if available
    if rag_context:
        messages.append({
            "role": "system",
            "content": f"""You are a helpful assistant. Use the following context from the user's documents to answer questions. If the context doesn't contain relevant information, say so.

Context:
{rag_context}
"""
        })

    # Get existing messages
    response = supabase.table("messages").select("*").eq(
        "conversation_id", conversation_id
    ).order("created_at", desc=False).execute()

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

    # Retrieve relevant document chunks for RAG
    retrieval_service = RetrievalService(supabase)
    rag_context = retrieval_service.get_context_for_query(user_message, current_user.id, top_k=5)
    print(f"RAG retrieved context: {len(rag_context)} chars")

    # Build messages array with conversation history + RAG context
    messages = build_messages(conversation_id, user_message, supabase, rag_context)

    # Stream response from LLM
    provider = get_llm_provider(request.provider)

    def event_generator():
        try:
            response_stream = provider.chat_complete(
                messages=messages,
                stream=True
            )

            full_content = ""
            completion_id = None
            stream_done = False

            # Chat Completions streaming format
            for chunk in response_stream:
                print(f"Received chunk: delta={len(chunk.delta) if chunk.delta else 0}, done={chunk.done}")
                if chunk.delta:
                    delta = chunk.delta
                    full_content += delta
                    try:
                        yield f"data: {json.dumps({'type': 'delta', 'content': delta})}\n\n"
                    except Exception as e:
                        print(f"Yield delta failed: {e}")
                        break

                if chunk.response_id:
                    completion_id = chunk.response_id

                if chunk.done:
                    print("Chunk marked as done!")
                    stream_done = True
                    try:
                        yield f"data: {json.dumps({'type': 'done', 'response_id': completion_id, 'conversation_id': conversation_id})}\n\n"
                    except Exception as e:
                        print(f"Yield done failed: {e}")
                    break  # Exit loop after sending done

            print(f"Stream loop ended. full_content length: {len(full_content)}, stream_done={stream_done}")

            # Save assistant message to database (insert, not update)
            if full_content and stream_done:
                print(f"Saving assistant message to database: {conversation_id}")
                supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "user_id": current_user.id,
                    "role": "assistant",
                    "content": full_content,
                    "openai_response_id": completion_id
                }).execute()
                print("Assistant message saved successfully")

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
