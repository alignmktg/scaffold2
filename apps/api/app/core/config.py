"""Application configuration settings."""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "AI App Bootstrap"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")
    API_WORKERS: int = Field(default=1, env="API_WORKERS")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        env="DATABASE_URL",
        description="Database connection URL",
    )

    # Supabase Auth
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY",
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    # AI Providers
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        env="OPENAI_BASE_URL",
    )
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL",
    )
    DEFAULT_AI_PROVIDER: str = Field(default="openai", env="DEFAULT_AI_PROVIDER")

    # Optional Modules
    USE_WORKERS: bool = Field(default=False, env="USE_WORKERS")
    USE_RAG: bool = Field(default=False, env="USE_RAG")
    USE_OLLAMA: bool = Field(default=False, env="USE_OLLAMA")

    # Workers (Celery + Redis)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_RESULT_BACKEND",
    )

    # RAG (Vector Search)
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: Optional[str] = Field(default=None, env="PINECONE_INDEX_NAME")
    QDRANT_URL: Optional[str] = Field(default=None, env="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")

    # Ollama (Local Models)
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        env="OLLAMA_BASE_URL",
    )
    OLLAMA_MODEL: str = Field(default="llama2", env="OLLAMA_MODEL")

    # Security
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS",
    )
    ALLOWED_HOSTS: Optional[List[str]] = Field(default=None, env="ALLOWED_HOSTS")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        """Pydantic configuration."""

        env_file = ".env.local"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.DEBUG or os.getenv("PYTHON_ENV") == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development

    @property
    def has_supabase_config(self) -> bool:
        """Check if Supabase is configured."""
        return all([
            self.SUPABASE_URL,
            self.SUPABASE_ANON_KEY,
            self.SUPABASE_SERVICE_KEY,
        ])

    @property
    def has_ai_provider_config(self) -> bool:
        """Check if any AI provider is configured."""
        return any([
            self.OPENAI_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.OPENROUTER_API_KEY,
        ])


# Global settings instance
settings = Settings()
