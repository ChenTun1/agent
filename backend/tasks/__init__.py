"""Celery tasks package."""
from backend.tasks.pdf_tasks import process_pdf_task

__all__ = ['process_pdf_task']
