import pytest
from unittest.mock import Mock, patch
from backend.qa_service import QAService

@patch('backend.qa_service.Anthropic')
def test_answer_question(mock_anthropic):
    # Mock Anthropic response
    mock_client = Mock()
    mock_response = Mock()
    mock_content = Mock()
    mock_content.text = "根据第5页的内容,主要贡献是X方法。[来源: 第5页]"
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    service = QAService()
    question = "What is the main contribution?"
    chunks = [
        {'text': 'The main contribution is X', 'page': 5},
        {'text': 'We propose method Y', 'page': 6}
    ]

    answer = service.answer(question, chunks)

    assert len(answer['answer']) > 0
    assert 'cited_pages' in answer
    assert len(answer['cited_pages']) > 0
    assert 5 in answer['cited_pages']
    assert answer['model'] == "claude-sonnet-4-20250514"

@patch('backend.qa_service.Anthropic')
def test_extract_cited_pages(mock_anthropic):
    # Mock Anthropic
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    service = QAService()

    # Test page extraction
    answer1 = "根据第5页的内容,实验结果在第12页。[来源: 第5页, 第12页]"
    pages1 = service._extract_cited_pages(answer1)
    assert 5 in pages1
    assert 12 in pages1

    answer2 = "文档中未找到相关内容"
    pages2 = service._extract_cited_pages(answer2)
    assert len(pages2) == 0

@patch('backend.qa_service.Anthropic')
def test_build_context(mock_anthropic):
    # Mock Anthropic
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    service = QAService()
    chunks = [
        {'text': 'First chunk', 'page': 1},
        {'text': 'Second chunk', 'page': 2}
    ]

    context = service._build_context(chunks)

    assert "第1页" in context
    assert "第2页" in context
    assert "First chunk" in context
    assert "Second chunk" in context

@patch('backend.qa_service.Anthropic')
def test_system_prompt(mock_anthropic):
    # Mock Anthropic
    mock_client = Mock()
    mock_anthropic.return_value = mock_client

    service = QAService()
    prompt = service._get_system_prompt()

    assert "来源" in prompt
    assert "页码" in prompt
    assert "严格" in prompt
