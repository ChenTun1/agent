# backend/pdf_processor.py
from PyPDF2 import PdfReader
from typing import List, Dict
import re

class PDFProcessor:
    def extract_pages(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF page by page"""
        reader = PdfReader(pdf_path)
        pages = []

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            # Clean up text
            text = self._clean_text(text)

            pages.append({
                'page_num': page_num,
                'text': text,
                'char_count': len(text)
            })

        return pages

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers at end
        text = re.sub(r'\s+\d+\s*$', '', text)
        return text.strip()

    def get_pdf_metadata(self, pdf_path: str) -> Dict:
        """Extract PDF metadata"""
        reader = PdfReader(pdf_path)
        return {
            'page_count': len(reader.pages),
            'title': reader.metadata.get('/Title', 'Untitled') if reader.metadata else 'Untitled',
            'author': reader.metadata.get('/Author', 'Unknown') if reader.metadata else 'Unknown'
        }

    def smart_chunking(self, pages: List[Dict], max_chunk_size: int = 1000) -> List[Dict]:
        """Smart chunking with semantic awareness"""
        chunks = []

        for page in pages:
            page_num = page['page_num']
            text = page['text']

            # Split into paragraphs
            paragraphs = self._split_paragraphs(text)

            for para in paragraphs:
                if len(para) > max_chunk_size:
                    # Split long paragraphs into sentences with overlap
                    sentences = self._split_sentences(para)

                    # Sliding window: 5 sentences, overlap 2
                    for i in range(0, len(sentences), 3):
                        chunk_text = ' '.join(sentences[i:i+5])
                        if chunk_text.strip():
                            chunks.append({
                                'text': chunk_text,
                                'page': page_num,
                                'type': 'paragraph',
                                'char_count': len(chunk_text)
                            })
                else:
                    # Short paragraph as single chunk
                    if para.strip():
                        chunks.append({
                            'text': para,
                            'page': page_num,
                            'type': 'paragraph',
                            'char_count': len(para)
                        })

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or paragraph markers
        paragraphs = re.split(r'\n\n+', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
