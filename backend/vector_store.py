from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
import uuid
from backend.config import get_settings

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = "pdf_chunks"
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if not exists"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI text-embedding-3-small
                    distance=Distance.COSINE
                )
            )

    def add_chunks(self, pdf_id: str, chunks: List[Dict]):
        """Add PDF chunks to vector store"""
        points = []
        for chunk in chunks:
            point_id = str(uuid.uuid4())
            points.append(PointStruct(
                id=point_id,
                vector=chunk['embedding'],
                payload={
                    'pdf_id': pdf_id,
                    'page_num': chunk['page'],
                    'text': chunk['text'],
                    'chunk_type': chunk.get('type', 'paragraph'),
                    'chunk_id': point_id
                }
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: List[float], pdf_id: str, limit: int = 10):
        """Search for relevant chunks"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter={
                "must": [
                    {"key": "pdf_id", "match": {"value": pdf_id}}
                ]
            },
            limit=limit
        )
        return results
