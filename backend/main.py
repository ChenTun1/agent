# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import (
    UploadResponse,
    QuestionRequest,
    AnswerResponse,
    FeedbackRequest,
    HealthResponse
)
from backend.routers import tasks
import uuid
import os
import shutil

# 延迟导入,避免在测试时需要所有依赖
def get_pipeline():
    from backend.pipeline import PDFPipeline
    return PDFPipeline()

def get_retrieval_service():
    from backend.retrieval import RetrievalService
    return RetrievalService()

def get_qa_service():
    from backend.qa_service import QAService
    return QAService()

def get_suggester():
    from backend.suggestions import QuestionSuggester
    return QuestionSuggester()


app = FastAPI(
    title="AI PDF Chat API",
    description="智能PDF问答系统 - 上传PDF并通过自然语言提问",
    version="0.1.0"
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(tasks.router)

# 文件存储目录
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    Returns:
        健康状态
    """
    return {"status": "healthy"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    上传并处理PDF文件

    Args:
        file: 上传的PDF文件

    Returns:
        处理结果,包含pdf_id和页数

    Raises:
        HTTPException: 文件类型错误或处理失败
    """
    # 验证文件类型
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="只支持PDF文件。请上传.pdf格式的文件。"
        )

    # 生成唯一ID
    pdf_id = str(uuid.uuid4())

    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件保存失败: {str(e)}"
        )

    # 处理PDF
    try:
        pipeline = get_pipeline()
        result = pipeline.process_pdf(file_path, pdf_id)

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"PDF处理失败: {result.get('error', '未知错误')}"
            )

        return UploadResponse(
            status="success",
            pdf_id=pdf_id,
            filename=file.filename,
            page_count=result['pages_processed']
        )
    except Exception as e:
        # 清理失败的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"处理PDF时发生错误: {str(e)}"
        )


@app.post("/chat", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    对PDF提问并获取答案

    Args:
        request: 包含pdf_id和问题的请求

    Returns:
        答案、引用页码和来源片段

    Raises:
        HTTPException: PDF不存在或未找到相关内容
    """
    try:
        # 检索相关内容块
        retrieval_service = get_retrieval_service()
        chunks = retrieval_service.retrieve(
            question=request.question,
            pdf_id=request.pdf_id,
            k=5
        )

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail="未找到相关内容。请确认PDF已上传并尝试换个问题。"
            )

        # 生成答案
        qa_service = get_qa_service()
        answer = qa_service.answer(request.question, chunks)

        return AnswerResponse(
            answer=answer['answer'],
            cited_pages=answer['cited_pages'],
            sources=[
                {
                    'page': c['page'],
                    'text': c['text'][:200] + ('...' if len(c['text']) > 200 else '')
                }
                for c in chunks
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成答案时发生错误: {str(e)}"
        )


@app.get("/")
async def root():
    """
    API根路径,显示欢迎信息
    """
    return {
        "message": "欢迎使用 AI PDF Chat API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    提交用户反馈

    Args:
        request: 反馈信息

    Returns:
        接收状态
    """
    # TODO: 将反馈存储到数据库以供后续分析
    # 目前只是记录日志
    print(f"[FEEDBACK] {request.feedback} - Q: {request.question[:50]}...")

    return {"status": "received", "message": "感谢您的反馈!"}


@app.post("/suggestions")
async def get_suggestions(request: dict):
    """
    获取PDF的智能推荐问题

    Args:
        request: 包含pdf_id的请求

    Returns:
        推荐问题列表
    """
    try:
        pdf_id = request.get('pdf_id')

        # TODO: 从数据库获取第一页文本作为样本
        # 目前使用通用问题
        sample_text = ""

        suggester = get_suggester()
        questions = suggester.suggest(sample_text, doc_type='general')

        return {"questions": questions}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成推荐问题时发生错误: {str(e)}"
        )


# 开发环境运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
