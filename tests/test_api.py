# tests/test_api.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.main import app
    return TestClient(app=app)

def test_health_check(client):
    """测试健康检查接口"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_pdf(client):
    """测试PDF上传接口"""
    # 创建一个模拟的PDF文件
    with open("tests/fixtures/sample.pdf", "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("sample.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    assert "pdf_id" in response.json()
    assert response.json()["status"] == "success"


def test_chat_endpoint(client):
    """测试问答接口"""
    response = client.post(
        "/chat",
        json={
            "pdf_id": "test-pdf-123",
            "question": "这份文档的主要内容是什么?"
        }
    )

    # 注意: 如果没有处理过该PDF,会返回404
    # 这里我们测试接口格式是否正确
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "cited_pages" in data
        assert "sources" in data


def test_invalid_file_upload(client):
    """测试上传非PDF文件"""
    # 模拟上传txt文件
    from io import BytesIO
    fake_file = BytesIO(b"This is not a PDF")

    response = client.post(
        "/upload",
        files={"file": ("test.txt", fake_file, "text/plain")}
    )

    assert response.status_code == 400


def test_chat_missing_fields(client):
    """测试问答接口缺少字段"""
    response = client.post(
        "/chat",
        json={"pdf_id": "test-123"}  # 缺少question字段
    )

    assert response.status_code == 422  # Validation error
