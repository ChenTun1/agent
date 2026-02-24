import pytest
from unittest.mock import Mock, patch
from backend.retrieval import RetrievalService

@patch('backend.retrieval.VectorStore')
@patch('backend.retrieval.EmbeddingService')
def test_retrieve_chunks(mock_embedding_service, mock_vector_store):
    # Mock embedding service
    mock_emb_instance = Mock()
    mock_emb_instance.get_embedding.return_value = [0.1] * 1536
    mock_embedding_service.return_value = mock_emb_instance

    # Mock vector store search results
    mock_vs_instance = Mock()
    mock_result1 = Mock()
    mock_result1.payload = {
        'text': 'This is the main finding.',
        'page_num': 5,
        'chunk_id': 'chunk-1'
    }
    mock_result1.score = 0.95

    mock_result2 = Mock()
    mock_result2.payload = {
        'text': 'Additional context.',
        'page_num': 6,
        'chunk_id': 'chunk-2'
    }
    mock_result2.score = 0.85

    mock_vs_instance.search.return_value = [mock_result1, mock_result2]
    mock_vector_store.return_value = mock_vs_instance

    # Test retrieval
    service = RetrievalService()
    question = "What is the main finding?"
    pdf_id = "test-pdf-123"

    results = service.retrieve(question, pdf_id, k=5)

    assert len(results) <= 5
    assert all('text' in r for r in results)
    assert all('page' in r for r in results)
    assert all('score' in r for r in results)
    assert results[0]['text'] == 'This is the main finding.'
    assert results[0]['page'] == 5

@patch('backend.retrieval.VectorStore')
@patch('backend.retrieval.EmbeddingService')
def test_page_number_extraction(mock_embedding_service, mock_vector_store):
    # Mock services
    mock_emb_instance = Mock()
    mock_emb_instance.get_embedding.return_value = [0.1] * 1536
    mock_embedding_service.return_value = mock_emb_instance

    mock_vs_instance = Mock()
    mock_vs_instance.search.return_value = []
    mock_vector_store.return_value = mock_vs_instance

    service = RetrievalService()

    # Test page number extraction
    assert service._extract_page_number("第5页的内容是什么?") == 5
    assert service._extract_page_number("第12页") == 12
    assert service._extract_page_number("没有页码") is None

@patch('backend.retrieval.VectorStore')
@patch('backend.retrieval.EmbeddingService')
def test_page_boosting(mock_embedding_service, mock_vector_store):
    # Mock services
    mock_emb_instance = Mock()
    mock_emb_instance.get_embedding.return_value = [0.1] * 1536
    mock_embedding_service.return_value = mock_emb_instance

    # Mock results from different pages
    mock_vs_instance = Mock()
    mock_result1 = Mock()
    mock_result1.payload = {'text': 'Content from page 3', 'page_num': 3, 'chunk_id': 'c1'}
    mock_result1.score = 0.90

    mock_result2 = Mock()
    mock_result2.payload = {'text': 'Content from page 5', 'page_num': 5, 'chunk_id': 'c2'}
    mock_result2.score = 0.85

    mock_result3 = Mock()
    mock_result3.payload = {'text': 'More from page 5', 'page_num': 5, 'chunk_id': 'c3'}
    mock_result3.score = 0.80

    mock_vs_instance.search.return_value = [mock_result1, mock_result2, mock_result3]
    mock_vector_store.return_value = mock_vs_instance

    service = RetrievalService()
    results = service.retrieve("第5页的内容", "test-pdf", k=3)

    # Results from page 5 should be boosted to top
    assert results[0]['page'] == 5
    assert results[1]['page'] == 5
    assert results[2]['page'] == 3
