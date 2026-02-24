"""
Utility functions for Streamlit frontend
"""
import streamlit as st
from typing import List, Dict


def format_source_citation(page: int, text: str, max_length: int = 200) -> str:
    """
    Format source citation for display

    Args:
        page: Page number
        text: Source text
        max_length: Maximum text length

    Returns:
        Formatted citation string
    """
    truncated_text = text[:max_length] + "..." if len(text) > max_length else text
    return f"**Page {page}**: {truncated_text}"


def display_sources(sources: List[Dict]):
    """
    Display source citations in an expander

    Args:
        sources: List of source dictionaries with 'page' and 'text' keys
    """
    if not sources:
        return

    with st.expander("📍 View sources"):
        for idx, source in enumerate(sources, 1):
            st.caption(format_source_citation(source['page'], source['text']))
            if idx < len(sources):
                st.divider()


def validate_pdf_file(file) -> tuple[bool, str]:
    """
    Validate uploaded PDF file

    Args:
        file: Uploaded file object

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file is None:
        return False, "No file uploaded"

    # Check file extension
    if not file.name.endswith('.pdf'):
        return False, "Only PDF files are allowed"

    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        return False, f"File size ({file.size / 1024 / 1024:.1f}MB) exceeds 10MB limit"

    return True, ""


def init_session_state():
    """Initialize session state variables if they don't exist"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pdf_id' not in st.session_state:
        st.session_state.pdf_id = None
    if 'filename' not in st.session_state:
        st.session_state.filename = None
    if 'page_count' not in st.session_state:
        st.session_state.page_count = None


def clear_session_state():
    """Clear all session state variables"""
    st.session_state.clear()


def get_suggested_questions(doc_type: str = 'general') -> List[str]:
    """
    Get suggested questions based on document type

    Args:
        doc_type: Type of document (general, academic_paper, contract, technical_doc)

    Returns:
        List of suggested questions
    """
    suggestions = {
        'academic_paper': [
            "这篇论文的主要贡献是什么?",
            "使用了什么研究方法?",
            "实验结果如何?",
            "有哪些局限性?"
        ],
        'contract': [
            "合同的主要条款是什么?",
            "违约责任如何规定?",
            "支付条件是什么?",
            "合同期限多久?"
        ],
        'technical_doc': [
            "这个工具如何使用?",
            "有哪些主要功能?",
            "如何安装配置?",
            "常见问题有哪些?"
        ],
        'general': [
            "这份文档的主要内容是什么?",
            "有哪些关键信息?",
            "总结全文要点"
        ]
    }

    return suggestions.get(doc_type, suggestions['general'])


def format_page_info(filename: str, page_count: int) -> str:
    """
    Format PDF information for display

    Args:
        filename: PDF filename
        page_count: Number of pages

    Returns:
        Formatted info string
    """
    return f"📄 {filename} ({page_count} pages)"


def extract_page_numbers(text: str) -> List[int]:
    """
    Extract page numbers mentioned in text

    Args:
        text: Text to search for page numbers

    Returns:
        List of page numbers found
    """
    import re
    pages = []
    # Match patterns like "第5页", "第12页"
    matches = re.findall(r'第\s*(\d+)\s*页', text)
    for match in matches:
        pages.append(int(match))
    return sorted(list(set(pages)))
