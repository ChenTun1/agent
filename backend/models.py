# backend/models.py
from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    """PDF上传响应模型"""
    status: str
    pdf_id: str
    filename: str
    page_count: int


class QuestionRequest(BaseModel):
    """问答请求模型"""
    pdf_id: str
    question: str


class AnswerResponse(BaseModel):
    """问答响应模型"""
    answer: str
    cited_pages: List[int]
    sources: List[dict]


class FeedbackRequest(BaseModel):
    """用户反馈模型"""
    pdf_id: str
    question: str
    answer: str
    feedback: str  # helpful, inaccurate


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
