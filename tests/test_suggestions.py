import pytest
from backend.suggestions import QuestionSuggester


def test_suggest_questions():
    """测试问题推荐功能"""
    suggester = QuestionSuggester()
    sample_text = "This paper proposes a new method for image classification..."

    questions = suggester.suggest(sample_text, doc_type='academic_paper')

    assert len(questions) >= 3
    assert all(isinstance(q, str) for q in questions)


def test_detect_academic_paper():
    """测试学术论文检测"""
    suggester = QuestionSuggester()
    text = "Abstract: This paper presents a novel approach. Introduction: We propose..."

    questions = suggester.suggest(text, doc_type='general')

    assert len(questions) >= 3
    assert "论文" in questions[0]


def test_detect_contract():
    """测试合同检测"""
    suggester = QuestionSuggester()
    text = "甲方和乙方签订本合同，违约责任如下..."

    questions = suggester.suggest(text, doc_type='general')

    assert len(questions) >= 3
    assert "合同" in questions[0]


def test_detect_technical_doc():
    """测试技术文档检测"""
    suggester = QuestionSuggester()
    text = "API Usage: To install this tool, run the configuration..."

    questions = suggester.suggest(text, doc_type='general')

    assert len(questions) >= 3


def test_general_document():
    """测试通用文档"""
    suggester = QuestionSuggester()
    text = "这是一份普通文档，没有特定类型标识。"

    questions = suggester.suggest(text, doc_type='general')

    assert len(questions) >= 3
    assert "文档" in questions[0]
