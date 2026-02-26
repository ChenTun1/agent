"""Task management API endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.tasks.pdf_tasks import process_pdf_task
from backend.celery_app import celery_app


router = APIRouter(prefix="/tasks", tags=["tasks"])


class PDFProcessRequest(BaseModel):
    """Request model for PDF processing task."""
    pdf_path: str
    pdf_id: str


class TaskResponse(BaseModel):
    """Response model for task submission."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response model for task status query."""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


@router.post("/pdf/process", response_model=TaskResponse)
async def submit_pdf_task(request: PDFProcessRequest):
    """
    Submit a PDF processing task.

    Args:
        request: PDF processing request with pdf_path and pdf_id

    Returns:
        Task ID, status, and submission message
    """
    # Submit task to Celery
    result = process_pdf_task.delay(request.pdf_path, request.pdf_id)

    return TaskResponse(
        task_id=result.id,
        status='PENDING',
        message=f'PDF processing task submitted for {request.pdf_id}'
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Query task status and result.

    Args:
        task_id: Unique task identifier

    Returns:
        Task status and result/progress information
    """
    # Get task result from Celery
    result = celery_app.AsyncResult(task_id)

    response = TaskStatusResponse(
        task_id=task_id,
        status=result.state,
        result=None
    )

    # Handle different task states
    if result.state == 'PENDING':
        # Task is waiting to be executed
        response.result = None
    elif result.state == 'PROGRESS':
        # Task is in progress, return progress metadata
        response.result = result.info
    elif result.state == 'SUCCESS':
        # Task completed successfully, return result
        response.result = result.info
    elif result.state == 'FAILURE':
        # Task failed, return error information
        response.result = result.info
    else:
        # Handle other states (STARTED, RETRY, etc.)
        response.result = result.info if result.info else None

    return response
