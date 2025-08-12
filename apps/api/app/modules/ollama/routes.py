"""Ollama module routes for local model interactions."""

import json
from typing import Dict, Any, List, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.core.security import extract_user_from_token
from app.modules.ollama.client import OllamaClient

logger = get_logger(__name__)
router = APIRouter()


class OllamaChatRequest(BaseModel):
    """Ollama chat request model."""
    messages: List[Dict[str, str]] = Field(..., description="List of chat messages")
    model: str = Field(default="llama2", description="Ollama model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Whether to stream the response")


class OllamaModelInfo(BaseModel):
    """Ollama model information model."""
    name: str
    size: int
    modified_at: str | None = None
    digest: str | None = None


@router.post("/chat")
async def ollama_chat(
    request: OllamaChatRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Chat completion with Ollama local model."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        # Get chat completion
        response = await client.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        logger.info(
            "Ollama chat completion successful",
            model=request.model,
            user_id=user.get("user_id"),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ollama chat completion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ollama chat completion failed",
        )


@router.post("/chat/stream")
async def ollama_chat_stream(
    request: OllamaChatRequest,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> StreamingResponse:
    """Streaming chat completion with Ollama local model."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate streaming response."""
            async for chunk in client.chat_completion_stream(
                messages=request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"

            # Send end marker
            yield "data: [DONE]\n\n"

        logger.info(
            "Ollama streaming chat started",
            model=request.model,
            user_id=user.get("user_id"),
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
        logger.error("Ollama streaming chat failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ollama streaming chat failed",
        )


@router.get("/models", response_model=List[OllamaModelInfo])
async def list_ollama_models(
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> List[OllamaModelInfo]:
    """List available Ollama models."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        # Get models
        models = await client.list_models()

        logger.info(f"Retrieved {len(models)} Ollama models", user_id=user.get("user_id"))

        return [
            OllamaModelInfo(
                name=model["name"],
                size=model["size"],
                modified_at=model.get("modified_at"),
                digest=model.get("digest"),
            )
            for model in models
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list Ollama models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list Ollama models",
        )


@router.post("/models/pull")
async def pull_ollama_model(
    model_name: str,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Pull a model from Ollama registry."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        # Pull model
        result = await client.pull_model(model_name)

        logger.info(f"Ollama model pulled: {model_name}", user_id=user.get("user_id"))

        return {
            "status": "success",
            "message": f"Model {model_name} pulled successfully",
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to pull Ollama model", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pull Ollama model",
        )


@router.delete("/models/{model_name}")
async def delete_ollama_model(
    model_name: str,
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Delete an Ollama model."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        # Delete model
        result = await client.delete_model(model_name)

        logger.info(f"Ollama model deleted: {model_name}", user_id=user.get("user_id"))

        return {
            "status": "success",
            "message": f"Model {model_name} deleted successfully",
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete Ollama model", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Ollama model",
        )


@router.post("/embeddings")
async def generate_embeddings(
    text: str,
    model: str = "llama2",
    token: str = Depends(lambda x: x.headers.get("authorization", "").replace("Bearer ", "")),
) -> Dict[str, Any]:
    """Generate embeddings using Ollama model."""
    try:
        # Verify user
        user = extract_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Initialize Ollama client
        client = OllamaClient()

        # Generate embeddings
        embeddings = await client.generate_embeddings(text, model)

        logger.info(
            "Ollama embeddings generated",
            model=model,
            user_id=user.get("user_id"),
        )

        return {
            "model": model,
            "embeddings": embeddings,
            "dimensions": len(embeddings),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate Ollama embeddings", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Ollama embeddings",
        )


@router.get("/health")
async def ollama_health() -> Dict[str, Any]:
    """Check Ollama module health status."""
    try:
        client = OllamaClient()

        # Test connection
        is_connected = await client.test_connection()

        if is_connected:
            # Get available models
            models = await client.list_models()

            return {
                "status": "healthy",
                "models_count": len(models),
                "ollama_url": settings.OLLAMA_BASE_URL,
                "default_model": settings.OLLAMA_MODEL,
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Cannot connect to Ollama server",
                "ollama_url": settings.OLLAMA_BASE_URL,
            }

    except Exception as e:
        logger.error("Ollama health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "ollama_url": settings.OLLAMA_BASE_URL,
        }
