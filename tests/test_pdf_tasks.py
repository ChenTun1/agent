"""Tests for Celery PDF processing tasks."""
import pytest
import os
from pathlib import Path


class TestProcessPdfTaskSignature:
    """Test that the task has the correct Celery signature."""

    def test_process_pdf_task_has_delay_method(self):
        """Verify task has .delay method for async execution."""
        from backend.tasks.pdf_tasks import process_pdf_task

        assert hasattr(process_pdf_task, 'delay'), \
            "Task should have .delay method for async execution"

    def test_process_pdf_task_has_apply_async_method(self):
        """Verify task has .apply_async method for advanced async execution."""
        from backend.tasks.pdf_tasks import process_pdf_task

        assert hasattr(process_pdf_task, 'apply_async'), \
            "Task should have .apply_async method for advanced async execution"


class TestTaskRegistration:
    """Test that the task is properly registered with Celery."""

    def test_task_registered_in_celery_app(self):
        """Verify task is registered in celery_app.tasks."""
        from backend.celery_app import celery_app
        from backend.tasks.pdf_tasks import process_pdf_task

        # Get the task name
        task_name = process_pdf_task.name

        # Check if task is registered
        assert task_name in celery_app.tasks, \
            f"Task {task_name} should be registered in celery_app.tasks"


class TestProcessPdfTaskExecution:
    """Integration test for PDF processing task execution."""

    @pytest.mark.skipif(
        not os.path.exists('tests/fixtures/sample.pdf'),
        reason="Test PDF not available"
    )
    def test_process_pdf_task_execution(self):
        """Integration test: process a real PDF and verify all steps complete."""
        from backend.tasks.pdf_tasks import process_pdf_task
        from backend.services.cache_service import get_cache_service
        from backend.services.sparse_retrieval import get_sparse_retriever

        # Setup
        pdf_path = str(Path('tests/fixtures/sample.pdf').absolute())
        pdf_id = 'test_pdf_integration'

        # Clean up any existing data
        cache = get_cache_service()
        retriever = get_sparse_retriever()
        cache.delete(f'pdf:chunks:{pdf_id}')
        if pdf_id in retriever.bm25_index:
            del retriever.bm25_index[pdf_id]
        if pdf_id in retriever.documents:
            del retriever.documents[pdf_id]

        # Execute task synchronously (eager mode)
        result = process_pdf_task.apply(args=[pdf_path, pdf_id])

        # Verify task succeeded
        assert result.successful(), f"Task should succeed, but got state: {result.state}"

        # Verify return value
        task_result = result.get()
        assert task_result['status'] == 'completed', \
            "Task should return completed status"
        assert 'chunks_count' in task_result, \
            "Task should return chunks_count"
        assert task_result['chunks_count'] > 0, \
            "Task should process at least one chunk"
        assert 'pdf_id' in task_result, \
            "Task should return pdf_id"
        assert task_result['pdf_id'] == pdf_id, \
            f"Task should return correct pdf_id"

        # Verify chunks were cached
        cached_chunks = cache.get(f'pdf:chunks:{pdf_id}')
        assert cached_chunks is not None, \
            "Chunks should be cached"
        assert len(cached_chunks) == task_result['chunks_count'], \
            "Cached chunks count should match task result"

        # Verify BM25 index was created
        assert pdf_id in retriever.bm25_index, \
            "BM25 index should be created for pdf_id"
        assert pdf_id in retriever.documents, \
            "Documents should be stored for pdf_id"

        # Clean up
        cache.delete(f'pdf:chunks:{pdf_id}')
        del retriever.bm25_index[pdf_id]
        del retriever.documents[pdf_id]


class TestCallbackTask:
    """Test the CallbackTask base class."""

    def test_callback_task_has_update_progress_method(self):
        """Verify CallbackTask has update_progress method."""
        from backend.tasks.pdf_tasks import CallbackTask

        assert hasattr(CallbackTask, 'update_progress'), \
            "CallbackTask should have update_progress method"
