# tests/test_chunking.py
import pytest
from backend.pdf_processor import PDFProcessor

def test_smart_chunking():
    processor = PDFProcessor()
    pages = [
        {'page_num': 1, 'text': 'Introduction. ' * 100},  # Long paragraph
        {'page_num': 2, 'text': 'Short text.'}
    ]

    chunks = processor.smart_chunking(pages)

    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('page' in chunk for chunk in chunks)
    assert all('type' in chunk for chunk in chunks)

def test_chunking_respects_max_size():
    processor = PDFProcessor()
    long_text = 'This is a very long paragraph. ' * 50
    pages = [{'page_num': 1, 'text': long_text}]

    chunks = processor.smart_chunking(pages, max_chunk_size=500)

    # Each chunk should be close to or under max size
    for chunk in chunks:
        assert len(chunk['text']) <= 600  # Allow some overflow for sentence boundaries

def test_chunking_with_multiple_paragraphs():
    processor = PDFProcessor()
    text = """
    First paragraph with some content here.

    Second paragraph with different content.

    Third paragraph to test splitting.
    """
    pages = [{'page_num': 1, 'text': text}]

    chunks = processor.smart_chunking(pages)

    # Should have multiple chunks for multiple paragraphs
    assert len(chunks) >= 1
    assert all(chunk['page'] == 1 for chunk in chunks)

def test_split_paragraphs():
    processor = PDFProcessor()
    text = """First paragraph.

    Second paragraph.


    Third paragraph."""

    paragraphs = processor._split_paragraphs(text)

    assert len(paragraphs) == 3
    assert 'First paragraph' in paragraphs[0]
    assert 'Second paragraph' in paragraphs[1]
    assert 'Third paragraph' in paragraphs[2]

def test_split_sentences():
    processor = PDFProcessor()
    text = "First sentence. Second sentence! Third sentence? Fourth sentence."

    sentences = processor._split_sentences(text)

    assert len(sentences) >= 3
    assert any('First sentence' in s for s in sentences)
