from backend.pdf_processor import PDFProcessor
from backend.embeddings import EmbeddingService
from backend.vector_store import VectorStore
from typing import Dict


class PDFPipeline:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def process_pdf(self, pdf_path: str, pdf_id: str) -> Dict:
        """Full pipeline: extract -> chunk -> embed -> store"""
        try:
            # 1. Extract text from PDF
            pages = self.pdf_processor.extract_pages(pdf_path)

            # 2. Smart chunking
            chunks = self.pdf_processor.smart_chunking(pages)

            # 3. Generate embeddings
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_service.get_embeddings_batch(texts)

            # 4. Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk['embedding'] = embedding

            # 5. Store in vector database
            self.vector_store.add_chunks(pdf_id, chunks)

            return {
                'success': True,
                'pdf_id': pdf_id,
                'chunks_created': len(chunks),
                'pages_processed': len(pages)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
