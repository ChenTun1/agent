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
