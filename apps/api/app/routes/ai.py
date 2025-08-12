"""AI chat endpoints."""

import json
from typing import AsyncGenerator, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import extract_user_from_token
from app.services.ai_service import AIService
from app.services.chat_service import ChatService

logger = get_logger(__name__)
router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: str = Field(default="gpt-3.5-turbo", description="AI model to use")
    provider: str = Field(default="openai", description="AI provider")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Chat completion response model."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class StreamChatResponse(BaseModel):
    """Streaming chat response model."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


async def get_current_user(token: str) -> Dict[str, Any]:
    """Extract user from token."""
    user = extract_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> ChatResponse:
    """Chat completion endpoint."""
    try:
        # Get current user
        user = await get_current_user(token)

        # Initialize services
        ai_service = AIService()
        chat_service = ChatService()

        # Check if AI provider is configured
        if not settings.has_ai_provider_config:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No AI provider configured",
            )

        # Convert messages to dict format
        messages = [msg.dict() for msg in request.messages]

        # Get AI response
        response = await ai_service.chat_completion(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Save chat to database
        await chat_service.save_chat(
            user_id=user["user_id"],
            messages=messages,
            response=response,
            model=request.model,
            provider=request.provider,
        )

        logger.info(
            "Chat completion successful",
            user_id=user["user_id"],
            model=request.model,
            provider=request.provider,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat completion error", error=str(e), user_id=user.get("user_id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat completion failed",
        )


@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> StreamingResponse:
    """Streaming chat completion endpoint."""
    try:
        # Get current user
        user = await get_current_user(token)

        # Initialize services
        ai_service = AIService()
        chat_service = ChatService()

        # Check if AI provider is configured
        if not settings.has_ai_provider_config:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No AI provider configured",
            )

        # Convert messages to dict format
        messages = [msg.dict() for msg in request.messages]

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate streaming response."""
            full_response = ""

            async for chunk in ai_service.chat_completion_stream(
                messages=messages,
                model=request.model,
                provider=request.provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                full_response += chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                yield f"data: {json.dumps(chunk)}\n\n"

            # Send end marker
            yield "data: [DONE]\n\n"

            # Save chat to database (non-blocking)
            try:
                await chat_service.save_chat(
                    user_id=user["user_id"],
                    messages=messages,
                    response={"content": full_response},
                    model=request.model,
                    provider=request.provider,
                )
            except Exception as e:
                logger.error("Failed to save streaming chat", error=str(e))

        logger.info(
            "Streaming chat started",
            user_id=user["user_id"],
            model=request.model,
            provider=request.provider,
        )

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Streaming chat error", error=str(e), user_id=user.get("user_id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Streaming chat failed",
        )


@router.get("/models")
async def list_models() -> Dict[str, Any]:
    """List available AI models."""
    try:
        ai_service = AIService()
        models = await ai_service.list_models()
        return {"models": models}
    except Exception as e:
        logger.error("Failed to list models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models",
        )
