# AI PDF Chat

智能PDF对话工具 - 上传PDF,用自然语言提问,AI精准回答并标注出处

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- Vector DB: Qdrant
- LLM: Claude API
- Database: PostgreSQL (Supabase)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in API keys
3. Run backend: `uvicorn backend.main:app --reload`
4. Run frontend: `streamlit run frontend/app.py`

## Features
- PDF upload and text extraction
- Intelligent Q&A with source citations
- Conversation history
- Accurate retrieval with mixed search
