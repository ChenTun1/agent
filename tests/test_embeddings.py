import pytest
from unittest.mock import Mock, patch
from backend.embeddings import EmbeddingService

@patch('backend.embeddings.OpenAI')
def test_get_embedding(mock_openai):
    # Mock OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = EmbeddingService()
    text = "This is a test sentence."

    embedding = service.get_embedding(text)

    assert len(embedding) == 1536  # OpenAI embedding size
    assert all(isinstance(x, float) for x in embedding)
    mock_client.embeddings.create.assert_called_once_with(
        input=text,
        model="text-embedding-3-small"
    )

@patch('backend.embeddings.OpenAI')
def test_batch_embeddings(mock_openai):
    # Mock OpenAI response
    mock_client = Mock()
    mock_response = Mock()
    mock_response.data = [
        Mock(embedding=[0.1] * 1536),
        Mock(embedding=[0.2] * 1536),
        Mock(embedding=[0.3] * 1536)
    ]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = EmbeddingService()
    texts = ["First text", "Second text", "Third text"]

    embeddings = service.get_embeddings_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)
    mock_client.embeddings.create.assert_called_once_with(
        input=texts,
        model="text-embedding-3-small"
    )
