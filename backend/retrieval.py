from backend.embeddings import EmbeddingService
from backend.vector_store import VectorStore
from typing import List, Dict
import re


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def retrieve(self, question: str, pdf_id: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant chunks for question"""
        # 1. Get question embedding
        question_embedding = self.embedding_service.get_embedding(question)

        # 2. Vector search
        search_results = self.vector_store.search(
            query_vector=question_embedding,
            pdf_id=pdf_id,
            limit=k * 2  # Get more for potential reranking
        )

        # 3. Check for page number mention
        page_num = self._extract_page_number(question)

        # 4. Format results
        results = []
        for result in search_results[:k]:
            results.append({
                'text': result.payload['text'],
                'page': result.payload['page_num'],
                'score': result.score,
                'chunk_id': result.payload['chunk_id']
            })

        # 5. Boost results from mentioned page
        if page_num:
            results = self._boost_page_results(results, page_num)

        return results[:k]

    def _extract_page_number(self, question: str) -> int:
        """Extract page number from question like '第5页'"""
        match = re.search(r'第\s*(\d+)\s*页', question)
        if match:
            return int(match.group(1))
        return None

    def _boost_page_results(self, results: List[Dict], page_num: int) -> List[Dict]:
        """Move results from specific page to top"""
        page_results = [r for r in results if r['page'] == page_num]
        other_results = [r for r in results if r['page'] != page_num]
        return page_results + other_results
