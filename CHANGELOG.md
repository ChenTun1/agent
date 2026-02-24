# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-mvp] - 2026-02-25

### Added
- **PDF Processing**
  - PDF upload and text extraction using PyPDF2
  - Smart chunking algorithm with semantic awareness
  - Sliding window chunking with overlap for long documents
  - Page-by-page text extraction with metadata

- **AI-Powered Q&A**
  - Claude Sonnet 4 integration for question answering
  - Forced citation system ensuring all answers include source pages
  - System prompts preventing hallucination
  - Answer validation with confidence scoring
  - Citation accuracy verification

- **Vector Search**
  - Qdrant vector database integration
  - OpenAI text-embedding-3-small for embeddings
  - Semantic search for relevant chunks
  - Page number extraction from questions
  - Page-based result boosting

- **Backend API**
  - FastAPI REST API with CORS support
  - `/upload` endpoint for PDF processing
  - `/chat` endpoint for Q&A
  - `/suggestions` endpoint for question suggestions
  - `/feedback` endpoint for user feedback
  - `/health` endpoint for health checks
  - Comprehensive API documentation with Swagger UI

- **Frontend Interface**
  - Streamlit web application
  - File upload with drag-and-drop
  - Real-time chat interface
  - Source citation display with expandable views
  - Conversation history
  - Suggested questions based on document type
  - User feedback (thumbs up/down)

- **Quality & Testing**
  - Golden Q&A test suite for accuracy validation
  - Answer validation system
  - Citation verification
  - Content consistency checks
  - Confidence scoring for answers
  - Unit tests for all core components
  - Integration tests for API endpoints

- **Deployment**
  - Dockerfile for backend deployment
  - Dockerfile for frontend deployment
  - Railway deployment configuration
  - Environment variable management
  - Docker Compose for local Qdrant
  - Comprehensive deployment documentation

- **Documentation**
  - Complete README with setup instructions
  - API documentation with examples
  - Environment variable guide
  - Testing guide
  - Deployment guide for Railway and Streamlit Cloud

### Technical Details
- **Backend**: FastAPI, Python 3.11+
- **Frontend**: Streamlit
- **Vector DB**: Qdrant
- **LLM**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Database**: PostgreSQL (Supabase)
- **PDF Processing**: PyPDF2

### Performance
- Answer generation: ~3 seconds average
- PDF processing: ~5 seconds for 50-page document
- Embedding generation: Batch processing support
- Vector search: Sub-second response time

### Quality Metrics
- Target accuracy: >80% on golden Q&A set
- Citation accuracy: >90%
- Zero hallucination goal on test set
- Confidence scoring for answer validation

### Known Limitations
- Maximum PDF file size: 10MB
- Free tier: 3 PDFs, 10 questions per PDF
- Supports text-based PDFs only (no OCR for scanned documents)
- Single-language support (optimized for Chinese)
- No multi-user session management

### Future Enhancements
- Multi-language support
- OCR for scanned PDFs
- User authentication and session management
- Usage analytics and monitoring
- Payment integration (Stripe)
- PDF comparison features
- Export answers to markdown/PDF
- Mobile-responsive design improvements

---

## [Unreleased]

### Planned
- User authentication system
- Payment integration
- Usage analytics dashboard
- Multi-language support
- OCR for scanned PDFs
- Batch PDF processing
- Advanced search filters
- Answer export functionality
