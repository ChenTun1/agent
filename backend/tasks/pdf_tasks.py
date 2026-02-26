"""PDF processing Celery tasks with progress tracking and error handling."""
from celery import Task
from typing import Dict, Any
from backend.celery_app import celery_app
from backend.pdf_processor import PDFProcessor
from backend.services.smart_chunking import get_smart_chunker
from backend.services.sparse_retrieval import get_sparse_retriever
from backend.services.cache_service import get_cache_service


class CallbackTask(Task):
    """Base task class with progress tracking support."""

    def update_progress(self, current_step: int, total_steps: int, message: str = ""):
        """
        Update task progress.

        Args:
            current_step: Current step number (0-based)
            total_steps: Total number of steps
            message: Optional progress message
        """
        progress_percent = int((current_step / total_steps) * 100)
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current_step,
                'total': total_steps,
                'percent': progress_percent,
                'message': message
            }
        )


@celery_app.task(bind=True, base=CallbackTask)
def process_pdf_task(self, pdf_path: str, pdf_id: str) -> Dict[str, Any]:
    """
    Asynchronously process a PDF: extract text, chunk, index, and cache.

    This task performs the following steps:
    1. Extract text from PDF pages
    2. Apply smart chunking with semantic boundaries
    3. Build BM25 sparse retrieval index
    4. Cache chunks in Redis
    5. Return completion status

    Args:
        pdf_path: Absolute path to the PDF file
        pdf_id: Unique identifier for this PDF

    Returns:
        Dict containing:
            - status: 'completed'
            - pdf_id: The PDF identifier
            - chunks_count: Number of chunks created
            - message: Success message

    Raises:
        Exception: Any processing error will be caught and stored in task state
    """
    total_steps = 4

    try:
        # Step 1: Extract text from PDF
        self.update_progress(0, total_steps, "Extracting text from PDF")
        pdf_processor = PDFProcessor()
        pages = pdf_processor.extract_pages(pdf_path)

        # Combine all page text
        full_text = '\n\n'.join([page['text'] for page in pages])

        # Step 2: Smart chunking with semantic boundaries
        self.update_progress(1, total_steps, "Applying smart chunking")
        chunker = get_smart_chunker()
        raw_chunks = chunker.chunk(full_text, max_tokens=512, overlap=50)

        # Format chunks with IDs and page numbers
        chunks = []
        for idx, chunk in enumerate(raw_chunks):
            chunks.append({
                'id': f"{pdf_id}_chunk_{idx}",
                'text': chunk['text'],
                'page': 1,  # Default page, can be enhanced to track actual page
                'tokens': chunk['tokens']
            })

        # Step 3: Build BM25 index
        self.update_progress(2, total_steps, "Building BM25 index")
        retriever = get_sparse_retriever()
        retriever.index_document(pdf_id, chunks)

        # Step 4: Cache chunks in Redis
        self.update_progress(3, total_steps, "Caching chunks")
        cache = get_cache_service()
        cache.set(f'pdf:chunks:{pdf_id}', chunks, ttl=3600)

        # Complete
        self.update_progress(4, total_steps, "Processing complete")

        return {
            'status': 'completed',
            'pdf_id': pdf_id,
            'chunks_count': len(chunks),
            'message': f'Successfully processed PDF with {len(chunks)} chunks'
        }

    except Exception as e:
        # Update state to FAILURE with error details
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'pdf_id': pdf_id,
                'pdf_path': pdf_path
            }
        )
        # Re-raise the exception so Celery marks the task as failed
        raise
