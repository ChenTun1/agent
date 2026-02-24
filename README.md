# AI PDF Chat

智能PDF对话工具 - 上传PDF,用自然语言提问,AI精准回答并标注出处

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- Vector DB: Qdrant
- LLM: Claude API
- Database: PostgreSQL (Supabase)

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Docker (for Qdrant)
- Git

### Development Setup

1. **Clone repository**
   ```bash
   git clone <your-repo-url>
   cd agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Qdrant vector database**
   ```bash
   docker-compose up -d
   ```
   Qdrant will be available at http://localhost:6333

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your API keys (see Environment Variables section below)

5. **Run backend server**
   ```bash
   uvicorn backend.main:app --reload
   ```
   API will be available at http://localhost:8000
   Interactive API docs: http://localhost:8000/docs

6. **Run frontend (in a new terminal)**
   ```bash
   streamlit run frontend/app.py
   ```
   Frontend will be available at http://localhost:8501

### Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_api.py -v
```

Run with coverage:
```bash
pytest --cov=backend tests/
```

## Features
- PDF upload and text extraction
- Intelligent Q&A with source citations
- Conversation history
- Accurate retrieval with mixed search

## Deployment

### Railway (Backend)
1. Create new project on Railway
2. Connect GitHub repo
3. Set environment variables:
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: PostgreSQL connection string
   - `SUPABASE_URL`: Supabase project URL
   - `SUPABASE_KEY`: Supabase API key
   - `QDRANT_URL`: Qdrant instance URL
   - `QDRANT_API_KEY`: Qdrant API key (if required)
4. Deploy from main branch using `deploy/railway.json` config

### Streamlit Cloud (Frontend)
1. Deploy frontend on Streamlit Cloud
2. Set environment variable:
   - `BACKEND_URL`: Your Railway backend URL
3. Deploy from main branch

### Docker Local Development
Build and run backend:
```bash
docker build -f Dockerfile.backend -t pdf-chat-backend .
docker run -p 8000:8000 --env-file .env pdf-chat-backend
```

Build and run frontend:
```bash
docker build -f Dockerfile.frontend -t pdf-chat-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://localhost:8000 pdf-chat-frontend
```

## Environment Variables
All environment variables are defined in `.env.example`. Copy this file to `.env` and fill in your API keys:

- `ANTHROPIC_API_KEY`: Claude API key from Anthropic Console
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon/service key
- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)
- `QDRANT_API_KEY`: Qdrant API key (optional for local)
- `MAX_FILE_SIZE_MB`: Maximum PDF file size (default: 10)
- `FREE_TIER_PDF_LIMIT`: Free tier PDF upload limit (default: 3)
- `FREE_TIER_QUESTION_LIMIT`: Free tier questions per PDF (default: 10)
