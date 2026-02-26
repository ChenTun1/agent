"""Tests for task management API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from backend.main import app


client = TestClient(app)


@patch('backend.routers.tasks.process_pdf_task')
def test_submit_pdf_task(mock_process_pdf_task):
    """Test POST /tasks/pdf/process returns task_id and status."""
    # Mock the Celery task delay() method
    mock_result = Mock()
    mock_result.id = 'test-task-id-123'
    mock_process_pdf_task.delay.return_value = mock_result

    # Submit task
    response = client.post(
        '/tasks/pdf/process',
        json={
            'pdf_path': '/path/to/test.pdf',
            'pdf_id': 'test-pdf-id'
        }
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-id-123'
    assert data['status'] == 'PENDING'
    assert 'message' in data

    # Verify task was submitted
    mock_process_pdf_task.delay.assert_called_once_with(
        '/path/to/test.pdf',
        'test-pdf-id'
    )


@patch('backend.routers.tasks.celery_app')
def test_get_task_status(mock_celery_app):
    """Test GET /tasks/{task_id} returns state and progress/result."""
    # Test case 1: PENDING state
    mock_result = MagicMock()
    mock_result.state = 'PENDING'
    mock_result.info = None
    mock_celery_app.AsyncResult.return_value = mock_result

    response = client.get('/tasks/test-task-pending')
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-pending'
    assert data['status'] == 'PENDING'
    assert data['result'] is None

    # Test case 2: PROGRESS state with metadata
    mock_result.state = 'PROGRESS'
    mock_result.info = {
        'current': 2,
        'total': 4,
        'percent': 50,
        'message': 'Building BM25 index'
    }
    mock_celery_app.AsyncResult.return_value = mock_result

    response = client.get('/tasks/test-task-progress')
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-progress'
    assert data['status'] == 'PROGRESS'
    assert data['result']['current'] == 2
    assert data['result']['total'] == 4
    assert data['result']['percent'] == 50
    assert data['result']['message'] == 'Building BM25 index'

    # Test case 3: SUCCESS state with result
    mock_result.state = 'SUCCESS'
    mock_result.info = {
        'status': 'completed',
        'pdf_id': 'test-pdf-id',
        'chunks_count': 42,
        'message': 'Successfully processed PDF with 42 chunks'
    }
    mock_celery_app.AsyncResult.return_value = mock_result

    response = client.get('/tasks/test-task-success')
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-success'
    assert data['status'] == 'SUCCESS'
    assert data['result']['status'] == 'completed'
    assert data['result']['chunks_count'] == 42

    # Test case 4: FAILURE state with error
    mock_result.state = 'FAILURE'
    mock_result.info = {
        'error': 'File not found',
        'pdf_id': 'test-pdf-id',
        'pdf_path': '/invalid/path.pdf'
    }
    mock_celery_app.AsyncResult.return_value = mock_result

    response = client.get('/tasks/test-task-failure')
    assert response.status_code == 200
    data = response.json()
    assert data['task_id'] == 'test-task-failure'
    assert data['status'] == 'FAILURE'
    assert data['result']['error'] == 'File not found'
