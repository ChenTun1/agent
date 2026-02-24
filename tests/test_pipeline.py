import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.pipeline import PDFPipeline

@patch('backend.pipeline.VectorStore')
@patch('backend.pipeline.EmbeddingService')
@patch('backend.pipeline.PDFProcessor')
def test_process_pdf_full_pipeline(mock_pdf_processor, mock_embedding_service, mock_vector_store):
    # Mock PDF processor
    mock_pdf_instance = Mock()
    mock_pdf_instance.extract_pages.return_value = [
        {'page_num': 1, 'text': 'Page 1 content'},
        {'page_num': 2, 'text': 'Page 2 content'}
    ]
    mock_pdf_instance.smart_chunking.return_value = [
        {'text': 'Chunk 1', 'page': 1, 'type': 'paragraph'},
        {'text': 'Chunk 2', 'page': 2, 'type': 'paragraph'}
    ]
    mock_pdf_processor.return_value = mock_pdf_instance

    # Mock embedding service
    mock_emb_instance = Mock()
    mock_emb_instance.get_embeddings_batch.return_value = [
        [0.1] * 1536,
        [0.2] * 1536
    ]
    mock_embedding_service.return_value = mock_emb_instance

    # Mock vector store
    mock_vs_instance = Mock()
    mock_vs_instance.add_chunks.return_value = None
    mock_vector_store.return_value = mock_vs_instance

    # Test pipeline
    pipeline = PDFPipeline()
    pdf_id = "test-pdf-123"

    result = pipeline.process_pdf(
        pdf_path="tests/fixtures/sample.pdf",
        pdf_id=pdf_id
    )

    assert result['success'] == True
    assert result['chunks_created'] == 2
    assert result['pdf_id'] == pdf_id
    assert result['pages_processed'] == 2

    # Verify all components were called
    mock_pdf_instance.extract_pages.assert_called_once()
    mock_pdf_instance.smart_chunking.assert_called_once()
    mock_emb_instance.get_embeddings_batch.assert_called_once()
    mock_vs_instance.add_chunks.assert_called_once()

@patch('backend.pipeline.VectorStore')
@patch('backend.pipeline.EmbeddingService')
@patch('backend.pipeline.PDFProcessor')
def test_process_pdf_error_handling(mock_pdf_processor, mock_embedding_service, mock_vector_store):
    # Mock PDF processor to raise error
    mock_pdf_instance = Mock()
    mock_pdf_instance.extract_pages.side_effect = Exception("PDF read error")
    mock_pdf_processor.return_value = mock_pdf_instance

    # Mock other services
    mock_embedding_service.return_value = Mock()
    mock_vector_store.return_value = Mock()

    # Test pipeline error handling
    pipeline = PDFPipeline()
    result = pipeline.process_pdf("bad.pdf", "test-id")

    assert result['success'] == False
    assert 'error' in result
    assert 'PDF read error' in result['error']

@patch('backend.pipeline.VectorStore')
@patch('backend.pipeline.EmbeddingService')
@patch('backend.pipeline.PDFProcessor')
def test_pipeline_integration(mock_pdf_processor, mock_embedding_service, mock_vector_store):
    # Mock services
    mock_pdf_instance = Mock()
    mock_pdf_instance.extract_pages.return_value = [{'page_num': 1, 'text': 'Test'}]
    mock_pdf_instance.smart_chunking.return_value = [{'text': 'Test chunk', 'page': 1}]
    mock_pdf_processor.return_value = mock_pdf_instance

    mock_emb_instance = Mock()
    mock_emb_instance.get_embeddings_batch.return_value = [[0.1] * 1536]
    mock_embedding_service.return_value = mock_emb_instance

    mock_vs_instance = Mock()
    mock_vector_store.return_value = mock_vs_instance

    # Test
    pipeline = PDFPipeline()
    result = pipeline.process_pdf("test.pdf", "id-123")

    # Verify chunks have embeddings
    call_args = mock_vs_instance.add_chunks.call_args
    chunks = call_args[0][1]
    assert 'embedding' in chunks[0]
    assert len(chunks[0]['embedding']) == 1536
