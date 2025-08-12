"""Ollama client for local model inference."""

import json
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    """Client for interacting with Ollama local models."""

    def __init__(self) -> None:
        """Initialize Ollama client."""
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            data = response.json()
            models = []

            for model in data.get("models", []):
                models.append({
                    "name": model["name"],
                    "size": model.get("size", 0),
                    "modified_at": model.get("modified_at"),
                    "digest": model.get("digest"),
                })

            logger.info(f"Retrieved {len(models)} Ollama models")
            return models

        except Exception as e:
            logger.error("Failed to list Ollama models", error=str(e))
            raise

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get chat completion from Ollama model."""
        try:
            model_name = model or self.default_model

            # Prepare request
            request_data = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs,
                },
            }

            logger.info(
                "Requesting Ollama chat completion",
                model=model_name,
                message_count=len(messages),
            )

            # Make request
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=request_data,
            )
            response.raise_for_status()

            data = response.json()

            # Format response to match OpenAI format
            formatted_response = {
                "id": f"ollama-{model_name}-{hash(str(messages))}",
                "object": "chat.completion",
                "created": data.get("created_at", 0),
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": data["message"]["content"],
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
            }

            logger.info("Ollama chat completion successful", model=model_name)
            return formatted_response

        except Exception as e:
            logger.error(
                "Ollama chat completion failed",
                error=str(e),
                model=model or self.default_model,
            )
            raise

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get streaming chat completion from Ollama model."""
        try:
            model_name = model or self.default_model

            # Prepare request
            request_data = {
                "model": model_name,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs,
                },
            }

            logger.info(
                "Requesting Ollama streaming chat completion",
                model=model_name,
                message_count=len(messages),
            )

            # Make streaming request
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=request_data,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)

                            if "message" in data:
                                # Format chunk to match OpenAI format
                                chunk = {
                                    "id": f"ollama-{model_name}-{hash(str(messages))}",
                                    "object": "chat.completion.chunk",
                                    "created": data.get("created_at", 0),
                                    "model": model_name,
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {
                                                "role": "assistant",
                                                "content": data["message"]["content"],
                                            },
                                            "finish_reason": data.get("done", False) and "stop" or None,
                                        }
                                    ],
                                }
                                yield chunk

                        except json.JSONDecodeError:
                            continue

            logger.info("Ollama streaming chat completion completed", model=model_name)

        except Exception as e:
            logger.error(
                "Ollama streaming chat completion failed",
                error=str(e),
                model=model or self.default_model,
            )
            raise

    async def generate_embeddings(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> List[float]:
        """Generate embeddings for text."""
        try:
            model_name = model or self.default_model

            request_data = {
                "model": model_name,
                "prompt": text,
            }

            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=request_data,
            )
            response.raise_for_status()

            data = response.json()
            embeddings = data.get("embedding", [])

            logger.info("Ollama embeddings generated", model=model_name)
            return embeddings

        except Exception as e:
            logger.error("Failed to generate Ollama embeddings", error=str(e))
            raise

    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama registry."""
        try:
            request_data = {
                "name": model_name,
            }

            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json=request_data,
            )
            response.raise_for_status()

            data = response.json()

            logger.info("Ollama model pulled", model=model_name)
            return data

        except Exception as e:
            logger.error("Failed to pull Ollama model", error=str(e))
            raise

    async def delete_model(self, model_name: str) -> Dict[str, Any]:
        """Delete a model from Ollama."""
        try:
            request_data = {
                "name": model_name,
            }

            response = await self.client.delete(
                f"{self.base_url}/api/delete",
                json=request_data,
            )
            response.raise_for_status()

            data = response.json()

            logger.info("Ollama model deleted", model=model_name)
            return data

        except Exception as e:
            logger.error("Failed to delete Ollama model", error=str(e))
            raise

    async def test_connection(self) -> bool:
        """Test connection to Ollama server."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("Ollama connection test failed", error=str(e))
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
