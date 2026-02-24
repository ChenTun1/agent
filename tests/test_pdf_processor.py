# tests/test_pdf_processor.py
import pytest
from backend.pdf_processor import PDFProcessor

def test_extract_text_from_pdf():
    processor = PDFProcessor()
    # Use a sample PDF for testing
    pages = processor.extract_pages("tests/fixtures/sample.pdf")

    assert len(pages) > 0
    assert pages[0]['page_num'] == 1
    assert 'text' in pages[0]
    assert len(pages[0]['text']) > 0

def test_get_pdf_metadata():
    processor = PDFProcessor()
    metadata = processor.get_pdf_metadata("tests/fixtures/sample.pdf")

    assert 'page_count' in metadata
    assert metadata['page_count'] > 0
    assert 'title' in metadata
    assert 'author' in metadata

def test_clean_text():
    processor = PDFProcessor()
    dirty_text = "This   has   extra    spaces\n\n\nand newlines   42  "
    clean = processor._clean_text(dirty_text)

    assert "  " not in clean  # No double spaces
    assert clean.strip() == clean  # No leading/trailing whitespace
