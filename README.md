# AI App Bootstrap

A modern, production-ready monorepo for building AI applications with FastAPI backend and Next.js frontend.

## 🚀 Features

- **FastAPI Backend**: Async Python API with optional AI modules
- **Next.js Frontend**: TypeScript + TailwindCSS with App Router
- **Monorepo**: pnpm + Turborepo for efficient development
- **Optional AI Modules**: Workers, RAG, Local Models (Ollama)
- **Free-First**: Optimized for free hosting tiers
- **Type Safety**: Strict TypeScript and Python typing throughout

## 📁 Architecture

```
ai-app-bootstrap/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── packages/
│   └── shared/       # Shared TypeScript types & client SDK
├── infra/
│   ├── docker/       # Dockerfiles
│   └── compose/      # Docker Compose variants
├── config/           # Linting & typecheck configs
└── .github/workflows # CI/CD pipelines
```

## 🛠️ Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- pnpm 8+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone and install dependencies
git clone <your-repo>
cd ai-app-bootstrap
pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development servers
pnpm dev
```

### Development Commands

```bash
# Start all services
pnpm dev

# Build all packages
pnpm build

# Run tests
pnpm test

# Lint code
pnpm lint

# Type checking
pnpm typecheck

# Format code
pnpm format

# Docker commands
pnpm docker:up      # Start with Docker Compose
pnpm docker:down    # Stop containers
pnpm docker:build   # Build images
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
# Backend (apps/api)
DATABASE_URL=sqlite:///./app.db
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# AI Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional Modules
USE_WORKERS=false
USE_RAG=false
USE_OLLAMA=false

# Frontend (apps/web)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Optional Modules

Enable optional AI modules by setting environment variables:

- **Workers**: `USE_WORKERS=true` - Celery + Redis for background jobs
- **RAG**: `USE_RAG=true` - Vector search with Chroma/Pinecone
- **Ollama**: `USE_OLLAMA=true` - Local model inference

## 🏗️ Backend (FastAPI)

### Structure

```
apps/api/
├── core/           # Settings, logging, security
├── routes/         # API endpoints
├── services/       # Business logic & AI providers
├── models/         # SQLAlchemy models
├── db/            # Database configuration
└── modules/       # Optional AI modules
    ├── workers/   # Celery tasks
    ├── rag/       # Vector search
    └── ollama/    # Local models
```

### Key Endpoints

- `GET /health` - Health check
- `POST /auth/verify` - JWT verification
- `POST /ai/chat` - Chat completion
- `POST /ai/chat/stream` - Streaming chat (SSE)

### Development

```bash
cd apps/api
uv sync          # Install dependencies
uv run dev       # Start development server
uv run test      # Run tests
```

## 🎨 Frontend (Next.js)

### Structure

```
apps/web/
├── app/          # App Router pages
├── components/   # React components
├── lib/          # Utilities & clients
├── types/        # TypeScript types
└── styles/       # Global styles
```

### Development

```bash
cd apps/web
pnpm dev         # Start development server
pnpm build       # Build for production
pnpm test        # Run tests
```

## 🐳 Docker

### Local Development

```bash
# Start all services
pnpm docker:up

# Start with specific profiles
docker-compose --profile workers up -d
docker-compose --profile rag up -d
docker-compose --profile ollama up -d
```

### Production

```bash
# Build and start production stack
docker-compose -f infra/compose/docker-compose.prod.yml up -d
```

## 🚀 Deployment

### Frontend (Vercel)

1. Connect your GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Backend (Railway/Fly.io)

1. Set up Railway or Fly.io project
2. Configure environment variables
3. Deploy with Docker or direct deployment

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Backend tests only
cd apps/api && uv run test

# Frontend tests only
cd apps/web && pnpm test

# E2E tests
cd apps/web && pnpm test:e2e
```

## 📊 Monitoring

- **Logging**: Structured JSON logs with structlog
- **Health Checks**: `/health` endpoints for monitoring
- **OpenTelemetry**: Optional tracing integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the [docs](./docs/) directory for detailed guides
- Open an issue for bugs or feature requests
- Join our community discussions
