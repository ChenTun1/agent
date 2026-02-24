# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-railway-app.railway.app`

## Endpoints

### Health Check

#### `GET /health`
Check if the API is running.

**Response**
```json
{
  "status": "healthy"
}
```

---

### Upload PDF

#### `POST /upload`
Upload and process a PDF file.

**Request**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file (max 10MB)

**Response**
```json
{
  "status": "success",
  "pdf_id": "uuid-string",
  "filename": "document.pdf",
  "page_count": 25
}
```

**Error Responses**
- `400 Bad Request`: Invalid file type (only PDF allowed)
- `500 Internal Server Error`: Processing failed

**Example**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

---

### Ask Question

#### `POST /chat`
Ask a question about an uploaded PDF.

**Request**
```json
{
  "pdf_id": "uuid-string",
  "question": "What is the main finding?"
}
```

**Response**
```json
{
  "answer": "According to page 5, the main finding is...",
  "cited_pages": [5, 12],
  "sources": [
    {
      "page": 5,
      "text": "Excerpt from page 5..."
    },
    {
      "page": 12,
      "text": "Excerpt from page 12..."
    }
  ]
}
```

**Error Responses**
- `404 Not Found`: No relevant content found for the question
- `500 Internal Server Error`: Failed to generate answer

**Example**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_id": "abc-123",
    "question": "What is the conclusion?"
  }'
```

---

### Get Suggested Questions

#### `POST /suggestions`
Get suggested questions for a PDF based on its content.

**Request**
```json
{
  "pdf_id": "uuid-string"
}
```

**Response**
```json
{
  "questions": [
    "What is the main contribution?",
    "What methodology was used?",
    "What are the key findings?"
  ]
}
```

---

### Submit Feedback

#### `POST /feedback`
Submit user feedback on answer quality.

**Request**
```json
{
  "pdf_id": "uuid-string",
  "question": "What is X?",
  "answer": "According to page 3...",
  "feedback": "helpful"
}
```

**Feedback Types**
- `helpful`: Answer was accurate and helpful
- `inaccurate`: Answer contained errors or was not helpful

**Response**
```json
{
  "status": "received"
}
```

---

## Data Models

### UploadResponse
```python
{
  "status": str,        # "success" or "error"
  "pdf_id": str,        # UUID of uploaded PDF
  "filename": str,      # Original filename
  "page_count": int     # Number of pages in PDF
}
```

### QuestionRequest
```python
{
  "pdf_id": str,        # UUID of PDF to query
  "question": str       # User's question
}
```

### AnswerResponse
```python
{
  "answer": str,              # AI-generated answer with citations
  "cited_pages": List[int],   # Page numbers cited in answer
  "sources": List[dict]       # Source excerpts from PDF
}
```

### FeedbackRequest
```python
{
  "pdf_id": str,        # UUID of PDF
  "question": str,      # Original question
  "answer": str,        # Generated answer
  "feedback": str       # "helpful" or "inaccurate"
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:
- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

---

## Rate Limiting

Free tier limits:
- Max 3 PDF uploads
- Max 10 questions per PDF
- Max file size: 10MB

---

## Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI with interactive API testing.

Visit http://localhost:8000/redoc for ReDoc documentation.
