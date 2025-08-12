# Test Plan: AI Chat Application Scaffold

This test plan provides step-by-step instructions for cloning and testing the full-stack AI chat application scaffold.

## Prerequisites

Before starting, ensure you have the following installed:
- **Git** (for cloning)
- **Python 3.11+** (for API backend)
- **Node.js 18+** (for web frontend)
- **Docker & Docker Compose** (for containerized testing)
- **PostgreSQL** (optional, for local database testing)

## Phase 1: Repository Setup

### Step 1: Clone the Repository
```bash
# Clone the template repository
git clone https://github.com/alignmktg/scaffold2.git
cd scaffold2

# Verify the structure
ls -la
# Should show: apps/, packages/, docker-compose.yml, etc.
```

### Step 2: Set Up Environment
```bash
# Copy environment template
cp env.example .env.local

# Review and update environment variables as needed
cat .env.local
```

## Phase 2: Backend API Testing

### Step 3: Set Up Python Environment
```bash
# Navigate to API directory
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
python -c "import app.main; print('✅ FastAPI app imports successfully')"
```

### Step 4: Test API Dependencies
```bash
# Test core imports
python -c "
from fastapi import FastAPI
from sqlalchemy import create_engine
from pydantic import BaseModel
print('✅ All core dependencies work')
"

# Test AI service imports
python -c "
from app.services.ai_service import AIService
print('✅ AI service imports work')
"
```

### Step 5: Test API Startup (Optional)
```bash
# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

## Phase 3: Frontend Web App Testing

### Step 6: Set Up Node.js Dependencies
```bash
# Navigate to web directory
cd ../../apps/web

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### Step 7: Test Web App Build
```bash
# Test TypeScript compilation
npm run typecheck

# Test build process
npm run build

# Expected: Build should complete successfully with no errors
```

### Step 8: Test Web App Development Server
```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
# Should see the chat interface
```

## Phase 4: Shared Package Testing

### Step 9: Test Shared Package
```bash
# Navigate to shared package
cd ../../packages/shared

# Install dependencies
npm install

# Test TypeScript compilation
npm run build

# Expected: Build should complete successfully
```

### Step 10: Test Shared Package Exports
```bash
# Test package exports
node -e "
const { ApiClient } = require('./dist/client');
const client = new ApiClient('http://localhost:8000');
console.log('✅ Shared package exports work');
"
```

## Phase 5: Docker Integration Testing

### Step 11: Test Docker Configuration
```bash
# Return to project root
cd ../..

# Validate Docker Compose configuration
docker-compose config

# Expected: Should show valid configuration without errors
```

### Step 12: Test Docker Builds
```bash
# Build API container
docker build -f infra/docker/Dockerfile.api -t ai-app-api .

# Build Web container
docker build -f infra/docker/Dockerfile.web -t ai-app-web .

# Expected: Both builds should complete successfully
```

### Step 13: Test Full Stack with Docker
```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test web app
curl http://localhost:3000

# Stop services
docker-compose down
```

## Phase 6: Integration Testing

### Step 14: Test API Endpoints
```bash
# Start API server
cd apps/api
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, test endpoints:
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl http://localhost:8000/ai/models
```

### Step 15: Test Web-API Communication
```bash
# Start web app
cd ../../apps/web
npm run dev

# Open browser to http://localhost:3000
# Open browser dev tools
# Check Network tab for API calls
# Verify no CORS errors
```

### Step 16: Test Chat Functionality
```bash
# With both servers running:
# 1. Open http://localhost:3000 in browser
# 2. Try sending a test message
# 3. Check browser console for errors
# 4. Check API server logs for requests
```

## Phase 7: Database Testing

### Step 17: Test Database Connection
```bash
# Start PostgreSQL (if using Docker)
docker run --name test-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=ai_app -p 5432:5432 -d postgres:15-alpine

# Test database connection
cd apps/api
source venv/bin/activate
python -c "
from app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('✅ Database connection works')
"
```

## Phase 8: AI Integration Testing

### Step 18: Test Ollama Integration (Optional)
```bash
# Start Ollama (if installed)
ollama serve

# Test Ollama connection
curl http://localhost:11434/api/tags

# Test with API
curl -X POST http://localhost:8000/ollama/models
```

### Step 19: Test RAG Integration (Optional)
```bash
# Test vector store
cd apps/api
source venv/bin/activate
python -c "
from app.modules.rag.vector_store import VectorStore
print('✅ RAG module imports work')
"
```

## Phase 9: Performance Testing

### Step 20: Test Build Performance
```bash
# Test API build time
cd apps/api
time pip install -e .

# Test web build time
cd ../../apps/web
time npm run build

# Test shared package build time
cd ../../packages/shared
time npm run build
```

### Step 21: Test Runtime Performance
```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Test web app load time
# Use browser dev tools Performance tab
```

## Phase 10: Error Handling Testing

### Step 22: Test Error Scenarios
```bash
# Test invalid API endpoints
curl http://localhost:8000/invalid-endpoint
# Expected: 404 error

# Test malformed requests
curl -X POST http://localhost:8000/ai/chat -H "Content-Type: application/json" -d '{"invalid": "data"}'
# Expected: 422 validation error
```

## Success Criteria

✅ **All tests pass** - No build errors, runtime errors, or integration issues

✅ **API responds correctly** - Health endpoint returns 200, all routes accessible

✅ **Web app loads** - No console errors, UI renders correctly

✅ **Docker builds work** - All containers build and run successfully

✅ **Database connects** - No connection errors, migrations work

✅ **AI integrations ready** - Ollama and RAG modules import correctly

## Troubleshooting

### Common Issues:

1. **Python import errors**: Ensure virtual environment is activated
2. **Node.js build errors**: Clear node_modules and reinstall
3. **Docker build failures**: Check Dockerfile syntax and context
4. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
5. **CORS errors**: Check API URL configuration in web app

### Debug Commands:
```bash
# Check Python environment
which python
pip list

# Check Node.js environment
node --version
npm --version

# Check Docker environment
docker --version
docker-compose --version

# Check system resources
df -h
free -h
```

## Next Steps

After completing this test plan:

1. **Customize the application** for your specific use case
2. **Add your own AI models** and integrations
3. **Deploy to production** using the provided Docker configuration
4. **Add monitoring and logging** for production use
5. **Implement authentication** and user management
6. **Add tests** for your custom functionality

---

**Test Plan Version**: 1.0  
**Last Updated**: $(date)  
**Tested Against**: scaffold2 template repository
