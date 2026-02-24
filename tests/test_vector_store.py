from backend.vector_store import VectorStore

def test_vector_store_connection():
    vs = VectorStore()
    assert vs.client is not None
    assert vs.collection_name == "pdf_chunks"
