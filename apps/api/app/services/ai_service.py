"""AI service for handling different AI providers."""

import time
from typing import AsyncGenerator, Dict, Any, List, Optional

import litellm
from litellm import completion, acompletion

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIService:
    """Service for handling AI provider interactions."""

    def __init__(self) -> None:
        """Initialize AI service with provider configuration."""
        self._configure_litellm()

    def _configure_litellm(self) -> None:
        """Configure LiteLLM with provider settings."""
        # Configure OpenAI
        if settings.OPENAI_API_KEY:
            litellm.set_verbose = settings.DEBUG
            litellm.api_key = settings.OPENAI_API_KEY
            if settings.OPENAI_BASE_URL != "https://api.openai.com/v1":
                litellm.api_base = settings.OPENAI_BASE_URL

        # Configure Anthropic
        if settings.ANTHROPIC_API_KEY:
            litellm.anthropic_key = settings.ANTHROPIC_API_KEY

        # Configure OpenRouter
        if settings.OPENROUTER_API_KEY:
            litellm.openrouter_key = settings.OPENROUTER_API_KEY
            if settings.OPENROUTER_BASE_URL != "https://openrouter.ai/api/v1":
                litellm.openrouter_base = settings.OPENROUTER_BASE_URL

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        provider: str = "openai",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get chat completion from AI provider."""
        try:
            # Map provider to model
            model_name = self._get_model_name(model, provider)

            # Prepare completion parameters
            completion_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs,
            }

            logger.info(
                "Requesting chat completion",
                model=model_name,
                provider=provider,
                message_count=len(messages),
            )

            # Get completion
            response = await acompletion(**completion_params)

            # Format response
            formatted_response = {
                "id": response.id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response.choices[0].message.content,
                        },
                        "finish_reason": response.choices[0].finish_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

            logger.info(
                "Chat completion successful",
                model=model_name,
                tokens_used=response.usage.total_tokens,
            )

            return formatted_response

        except Exception as e:
            logger.error(
                "Chat completion failed",
                error=str(e),
                model=model,
                provider=provider,
            )
            raise

    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        provider: str = "openai",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get streaming chat completion from AI provider."""
        try:
            # Map provider to model
            model_name = self._get_model_name(model, provider)

            # Prepare completion parameters
            completion_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs,
            }

            logger.info(
                "Requesting streaming chat completion",
                model=model_name,
                provider=provider,
                message_count=len(messages),
            )

            # Get streaming completion
            response = await acompletion(**completion_params)

            # Stream chunks
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    formatted_chunk = {
                        "id": chunk.id,
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "role": "assistant",
                                    "content": chunk.choices[0].delta.content,
                                },
                                "finish_reason": chunk.choices[0].finish_reason,
                            }
                        ],
                    }
                    yield formatted_chunk

            logger.info("Streaming chat completion completed", model=model_name)

        except Exception as e:
            logger.error(
                "Streaming chat completion failed",
                error=str(e),
                model=model,
                provider=provider,
            )
            raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from configured providers."""
        models = []

        # Add OpenAI models
        if settings.OPENAI_API_KEY:
            models.extend([
                {"id": "gpt-4", "provider": "openai", "name": "GPT-4"},
                {"id": "gpt-4-turbo", "provider": "openai", "name": "GPT-4 Turbo"},
                {"id": "gpt-3.5-turbo", "provider": "openai", "name": "GPT-3.5 Turbo"},
            ])

        # Add Anthropic models
        if settings.ANTHROPIC_API_KEY:
            models.extend([
                {"id": "claude-3-opus", "provider": "anthropic", "name": "Claude 3 Opus"},
                {"id": "claude-3-sonnet", "provider": "anthropic", "name": "Claude 3 Sonnet"},
                {"id": "claude-3-haiku", "provider": "anthropic", "name": "Claude 3 Haiku"},
            ])

        # Add OpenRouter models
        if settings.OPENROUTER_API_KEY:
            models.extend([
                {"id": "openai/gpt-4", "provider": "openrouter", "name": "GPT-4 (via OpenRouter)"},
                {"id": "anthropic/claude-3-opus", "provider": "openrouter", "name": "Claude 3 Opus (via OpenRouter)"},
                {"id": "meta-llama/llama-2-70b-chat", "provider": "openrouter", "name": "Llama 2 70B (via OpenRouter)"},
            ])

        return models

    def _get_model_name(self, model: str, provider: str) -> str:
        """Get the correct model name for the provider."""
        if provider == "openai":
            return model
        elif provider == "anthropic":
            return model
        elif provider == "openrouter":
            return f"openrouter/{model}"
        else:
            return model

    async def test_connection(self, provider: str = "openai") -> bool:
        """Test connection to AI provider."""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(
                messages=test_messages,
                model="gpt-3.5-turbo" if provider == "openai" else "claude-3-haiku",
                provider=provider,
                max_tokens=10,
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed for {provider}", error=str(e))
            return False
