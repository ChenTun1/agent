import pytest
from backend.embeddings import EmbeddingService

def test_get_embedding():
    service = EmbeddingService()
    text = "This is a test sentence."

    embedding = service.get_embedding(text)

    assert len(embedding) == 1536  # OpenAI embedding size
    assert all(isinstance(x, float) for x in embedding)

def test_batch_embeddings():
    service = EmbeddingService()
    texts = ["First text", "Second text", "Third text"]

    embeddings = service.get_embeddings_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)
