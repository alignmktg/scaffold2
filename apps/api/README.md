# AI App API (FastAPI Backend)

FastAPI backend for the AI App Bootstrap with optional AI modules.

## 🚀 Features

- **FastAPI**: Modern async Python web framework
- **SQLAlchemy 2.x**: Type-safe database ORM
- **Alembic**: Database migrations
- **Supabase Auth**: JWT-based authentication
- **AI Providers**: OpenAI, Anthropic, OpenRouter via LiteLLM
- **Optional Modules**: Workers, RAG, Local Models
- **Structured Logging**: JSON logs with structlog
- **Type Safety**: Strict mypy configuration

## 📁 Structure

```
apps/api/
├── core/           # Settings, logging, security
├── routes/         # API endpoints
├── services/       # Business logic & AI providers
├── models/         # SQLAlchemy models
├── db/            # Database configuration
├── modules/       # Optional AI modules
│   ├── workers/   # Celery tasks
│   ├── rag/       # Vector search
│   └── ollama/    # Local models
├── tests/         # Test suite
└── main.py        # Application entry point
```

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- uv package manager
- SQLite (dev) or PostgreSQL (prod)

### Installation

```bash
cd apps/api

# Install dependencies
uv sync

# Set up environment
cp ../../env.example .env.local
# Edit .env.local with your configuration

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run dev
```

### Optional Modules

Enable optional modules by setting environment variables:

```bash
# Workers (Celery + Redis)
USE_WORKERS=true
uv sync --extra workers

# RAG (Vector Search)
USE_RAG=true
uv sync --extra rag

# Ollama (Local Models)
USE_OLLAMA=true
uv sync --extra ollama
```

## 🔧 Configuration

### Environment Variables

Key configuration options:

```bash
# Database
DATABASE_URL=sqlite:///./app.db

# Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEFAULT_AI_PROVIDER=openai

# Optional Modules
USE_WORKERS=false
USE_RAG=false
USE_OLLAMA=false
```

## 📡 API Endpoints

### Health Check
- `GET /health` - Application health status

### Authentication
- `POST /auth/verify` - Verify JWT token

### AI Chat
- `POST /ai/chat` - Chat completion
- `POST /ai/chat/stream` - Streaming chat (SSE)

### Optional Endpoints

#### Workers Module
- `POST /workers/tasks` - Submit background task
- `GET /workers/tasks/{task_id}` - Get task status

#### RAG Module
- `POST /rag/ingest` - Ingest documents
- `POST /rag/search` - Search documents
- `GET /rag/collections` - List collections

#### Ollama Module
- `POST /ollama/chat` - Local model chat
- `GET /ollama/models` - List available models

## 🧪 Testing

```bash
# Run all tests
uv run test

# Run with coverage
uv run test --cov=app --cov-report=html

# Run specific test file
uv run test tests/test_ai.py

# Run linting
uv run lint

# Type checking
uv run typecheck

# Format code
uv run format
```

## 🐳 Docker

```bash
# Build image
docker build -t ai-app-api .

# Run container
docker run -p 8000:8000 --env-file .env.local ai-app-api

# With Docker Compose
docker-compose up api
```

## 📊 Monitoring

### Logging

Structured JSON logs with different levels:

```python
import structlog

logger = structlog.get_logger()
logger.info("User logged in", user_id=123, action="login")
```

### Health Checks

Monitor application health:

```bash
curl http://localhost:8000/health
```

### Metrics

Optional OpenTelemetry integration for tracing and metrics.

## 🔒 Security

- JWT token verification via Supabase
- CORS configuration
- Rate limiting
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy

## 🚀 Deployment

### Railway

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Docker

```bash
# Build production image
docker build -f Dockerfile.prod -t ai-app-api:prod .

# Run with environment
docker run -p 8000:8000 --env-file .env.prod ai-app-api:prod
```

## 🤝 Contributing

1. Follow the code style (Black + Ruff)
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
