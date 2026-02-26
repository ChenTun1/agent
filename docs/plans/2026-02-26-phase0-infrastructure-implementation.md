# Phase 0: 基础设施准备 - 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标**: 搭建企业级基础设施,为后续开发奠定基础

**架构**: Docker Compose 编排 Redis + Qdrant,创建 SQLite 数据库,配置 Celery 任务队列

**技术栈**: Docker, Redis 7.0, Celery 5.3, SQLite 3.40, pytest

**预计时间**: 2-3 天

---

## 前置检查

**验证现有环境**:
```bash
python --version  # 应为 3.11+
docker --version  # 应为 24.0+
docker-compose --version
```

---

## Task 1: Docker Compose 配置

**文件**:
- Create: `docker-compose.yml`
- Create: `.env.example`

**Step 1: 创建 Docker Compose 配置**

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: ai-pdf-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: ai-pdf-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis_data:
    driver: local
  qdrant_data:
    driver: local
```

**Step 2: 创建环境变量模板**

```bash
# .env.example
# 复制此文件为 .env 并填写实际值

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Database
DATABASE_URL=sqlite:///data/app.db

# API Keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

**Step 3: 启动服务**

```bash
# 创建 .env 文件
cp .env.example .env

# 启动 Docker 服务
docker-compose up -d

# 等待服务就绪
sleep 10
```

**Step 4: 验证服务运行**

```bash
# 检查容器状态
docker-compose ps

# 预期输出:
#     Name                   State    Ports
# ai-pdf-redis      Up      0.0.0.0:6379->6379/tcp
# ai-pdf-qdrant     Up      0.0.0.0:6333->6333/tcp

# 测试 Redis 连接
docker exec ai-pdf-redis redis-cli ping
# 预期: PONG

# 测试 Qdrant 健康检查
curl http://localhost:6333/health
# 预期: {"status":"ok"}
```

**Step 5: 提交**

```bash
git add docker-compose.yml .env.example
git commit -m "chore: add Docker Compose for Redis and Qdrant

- Redis 7 with persistence and LRU eviction
- Qdrant 1.7.4 for vector storage
- Health checks for both services
- Volume configuration for data persistence

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Python 依赖更新

**文件**:
- Modify: `requirements.txt`
- Create: `requirements-dev.txt`

**Step 1: 更新 requirements.txt**

添加新依赖到现有文件:

```txt
# requirements.txt (在现有内容基础上添加)

# 现有依赖 (保持不变)
fastapi==0.110.0
uvicorn[standard]==0.40.0
python-multipart==0.0.6
pydantic==2.11.7
pydantic-settings==2.1.0
pypdf==3.17.4
anthropic==0.75.0
openai==2.18.0
qdrant-client==1.17.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
streamlit==1.31.0
python-dotenv==1.0.0
httpx==0.26.0

# 新增依赖
rank-bm25==0.2.2           # BM25 稀疏检索
celery==5.3.6              # 任务队列
redis==5.0.1               # Redis 客户端
jieba==0.42.1              # 中文分词
slowapi==0.1.9             # API 限流
structlog==24.1.0          # 结构化日志
```

**Step 2: 创建开发依赖**

```txt
# requirements-dev.txt
-r requirements.txt

# 测试
pytest==9.0.2
pytest-asyncio==1.3.0
pytest-cov==6.0.0
pytest-mock==3.12.0

# 代码质量
black==24.2.0
isort==5.13.2
flake8==7.0.0
mypy==1.8.0

# 性能分析
py-spy==0.3.14
memory-profiler==0.61.0
```

**Step 3: 安装依赖**

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

**Step 4: 验证安装**

```bash
# 验证关键包
python -c "import redis; print(f'Redis: {redis.__version__}')"
python -c "import celery; print(f'Celery: {celery.__version__}')"
python -c "import rank_bm25; print('BM25: OK')"
python -c "import jieba; print('Jieba: OK')"

# 预期: 所有包成功导入
```

**Step 5: 提交**

```bash
git add requirements.txt requirements-dev.txt
git commit -m "chore: add enterprise-level dependencies

New dependencies:
- rank-bm25: Sparse retrieval (BM25)
- celery: Async task queue
- redis: Cache layer
- jieba: Chinese word segmentation
- slowapi: Rate limiting
- structlog: Structured logging

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: SQLite 数据库设置

**文件**:
- Create: `backend/database.py`
- Create: `backend/models_db.py`
- Create: `data/.gitkeep`

**Step 1: 创建数据目录**

```bash
mkdir -p data
touch data/.gitkeep
```

**Step 2: 编写数据库模型**

```python
# backend/models_db.py
"""
SQLAlchemy 数据库模型

用于存储文档元数据、对话历史等
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """文档表 - 存储 PDF 元数据"""
    __tablename__ = 'documents'

    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    page_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(Text)  # JSON 格式存储额外信息

    # 关系
    conversations = relationship(
        'Conversation',
        back_populates='document',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"


class Conversation(Base):
    """对话表 - 存储对话会话"""
    __tablename__ = 'conversations'

    id = Column(String(36), primary_key=True)
    document_id = Column(
        String(36),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False
    )
    title = Column(String(255))  # 对话标题 (通常是第一个问题)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关系
    document = relationship('Document', back_populates='conversations')
    messages = relationship(
        'Message',
        back_populates='conversation',
        cascade='all, delete-orphan',
        order_by='Message.created_at'
    )

    # 索引
    __table_args__ = (
        Index('idx_conversation_document', 'document_id'),
        Index('idx_conversation_updated', 'updated_at'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """消息表 - 存储对话消息"""
    __tablename__ = 'messages'

    id = Column(String(36), primary_key=True)
    conversation_id = Column(
        String(36),
        ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON 格式存储来源
    cited_pages = Column(Text)  # JSON 格式存储引用页码
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    conversation = relationship('Conversation', back_populates='messages')

    # 索引
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
```

**Step 3: 编写数据库管理器**

```python
# backend/database.py
"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os

from backend.models_db import Base

# 数据库 URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')


class DatabaseManager:
    """数据库管理器 - 单例模式"""

    _instance = None
    _engine = None
    _SessionLocal = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._init_engine()

    def _init_engine(self):
        """初始化数据库引擎"""
        # SQLite 特殊配置
        if DATABASE_URL.startswith('sqlite'):
            self._engine = create_engine(
                DATABASE_URL,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self._engine = create_engine(DATABASE_URL, echo=False)

        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self._engine)
        print("[DB] Tables created successfully")

    def drop_tables(self):
        """删除所有表 (慎用!)"""
        Base.metadata.drop_all(bind=self._engine)
        print("[DB] Tables dropped")

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self._SessionLocal()

    @contextmanager
    def session_scope(self):
        """上下文管理器 - 自动提交和回滚"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 全局实例
db_manager = DatabaseManager()


# FastAPI 依赖注入
def get_db():
    """获取数据库会话 (用于 FastAPI Depends)"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: 初始化数据库**

```python
# scripts/init_db.py
"""初始化数据库脚本"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import db_manager


def main():
    print("Initializing database...")

    # 创建表
    db_manager.create_tables()

    print("✓ Database initialized successfully!")
    print(f"  Location: data/app.db")
    print(f"  Tables: documents, conversations, messages")


if __name__ == '__main__':
    main()
```

**Step 5: 运行初始化**

```bash
# 创建数据目录
mkdir -p data

# 运行初始化脚本
python scripts/init_db.py

# 预期输出:
# Initializing database...
# [DB] Tables created successfully
# ✓ Database initialized successfully!
```

**Step 6: 验证数据库**

```bash
# 使用 sqlite3 检查表结构
sqlite3 data/app.db ".schema documents"

# 预期输出:
# CREATE TABLE documents (
#   id VARCHAR(36) NOT NULL,
#   filename VARCHAR(255) NOT NULL,
#   ...
# );
```

**Step 7: 提交**

```bash
git add backend/database.py backend/models_db.py scripts/init_db.py data/.gitkeep
git commit -m "feat: add SQLite database with SQLAlchemy models

Tables:
- documents: PDF metadata
- conversations: Chat sessions
- messages: Chat messages

Features:
- Foreign key constraints with CASCADE delete
- Indexes for performance
- Session management with context manager
- Initialization script

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Celery 配置

**文件**:
- Create: `backend/celeryconfig.py`
- Create: `backend/celery_app.py`
- Create: `scripts/start_celery.sh`

**Step 1: Celery 配置文件**

```python
# backend/celeryconfig.py
"""Celery 配置"""
import os

# Broker 配置
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# 任务配置
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = True

# 任务结果过期时间 (1小时)
result_expires = 3600

# Worker 配置
worker_prefetch_multiplier = 4
worker_max_tasks_per_child = 1000

# 任务路由
task_routes = {
    'backend.tasks.pdf.*': {'queue': 'pdf_processing'},
    'backend.tasks.embedding.*': {'queue': 'embedding'},
}

# 队列配置
task_queues = {
    'pdf_processing': {
        'exchange': 'pdf',
        'routing_key': 'pdf.processing',
    },
    'embedding': {
        'exchange': 'embedding',
        'routing_key': 'embedding.compute',
    },
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    }
}
```

**Step 2: Celery 应用**

```python
# backend/celery_app.py
"""Celery 应用实例"""
from celery import Celery

# 创建 Celery 应用
celery_app = Celery('ai_pdf_chat')

# 加载配置
celery_app.config_from_object('backend.celeryconfig')

# 自动发现任务
celery_app.autodiscover_tasks(['backend.tasks'])


@celery_app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'
```

**Step 3: 启动脚本**

```bash
# scripts/start_celery.sh
#!/bin/bash

# Celery Worker 启动脚本

echo "Starting Celery worker..."

# 启动 Worker
celery -A backend.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=pdf_processing,embedding,default \
    --logfile=logs/celery.log

# 注: 生产环境建议使用 supervisord 或 systemd 管理
```

**Step 4: 使启动脚本可执行**

```bash
chmod +x scripts/start_celery.sh
```

**Step 5: 测试 Celery**

创建临时测试文件:

```python
# test_celery.py (临时)
from backend.celery_app import celery_app, debug_task

# 提交任务
result = debug_task.delay()

print(f"Task ID: {result.id}")
print(f"Task State: {result.state}")

# 等待结果 (最多 10 秒)
try:
    output = result.get(timeout=10)
    print(f"Result: {output}")
except Exception as e:
    print(f"Error: {e}")
```

运行测试:

```bash
# 终端 1: 启动 Worker
./scripts/start_celery.sh

# 终端 2: 运行测试
python test_celery.py

# 预期输出:
# Task ID: xxxxx-xxxx-xxxx
# Task State: SUCCESS
# Result: Debug task completed

# 清理测试文件
rm test_celery.py
```

**Step 6: 提交**

```bash
git add backend/celeryconfig.py backend/celery_app.py scripts/start_celery.sh
git commit -m "feat: add Celery task queue configuration

Features:
- Redis as broker and result backend
- Multiple queues (pdf_processing, embedding)
- Worker concurrency configuration
- Task routing
- Startup script

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: 健康检查脚本

**文件**:
- Create: `scripts/check_infrastructure.sh`
- Create: `backend/health.py`

**Step 1: 健康检查脚本**

```bash
# scripts/check_infrastructure.sh
#!/bin/bash

# 基础设施健康检查脚本

echo "=== Infrastructure Health Check ==="
echo ""

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_passed=0
check_failed=0

# 检查函数
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((check_passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((check_failed++))
    fi
}

# 1. 检查 Docker
echo "1. Docker Services"
docker ps | grep -q ai-pdf-redis
check "Redis container running"

docker ps | grep -q ai-pdf-qdrant
check "Qdrant container running"

# 2. 检查 Redis 连接
echo ""
echo "2. Redis Connection"
docker exec ai-pdf-redis redis-cli ping > /dev/null 2>&1
check "Redis ping successful"

# 3. 检查 Qdrant 健康
echo ""
echo "3. Qdrant Connection"
curl -s http://localhost:6333/health | grep -q "ok"
check "Qdrant health check passed"

# 4. 检查 SQLite 数据库
echo ""
echo "4. SQLite Database"
[ -f data/app.db ]
check "Database file exists"

sqlite3 data/app.db "SELECT name FROM sqlite_master WHERE type='table';" | grep -q documents
check "Documents table exists"

# 5. 检查 Python 依赖
echo ""
echo "5. Python Dependencies"
python -c "import redis" 2>/dev/null
check "Redis Python client installed"

python -c "import celery" 2>/dev/null
check "Celery installed"

python -c "import rank_bm25" 2>/dev/null
check "BM25 installed"

python -c "import jieba" 2>/dev/null
check "Jieba installed"

# 6. 检查 Celery Worker
echo ""
echo "6. Celery Worker"
celery -A backend.celery_app inspect ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    check "Celery worker responding"
else
    echo -e "${RED}✗${NC} Celery worker not running (optional for now)"
fi

# 总结
echo ""
echo "==================================="
echo "Passed: $check_passed"
echo "Failed: $check_failed"

if [ $check_failed -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed.${NC}"
    exit 1
fi
```

**Step 2: Python 健康检查模块**

```python
# backend/health.py
"""健康检查工具"""
import redis
from qdrant_client import QdrantClient
from sqlalchemy import text
import os

from backend.database import db_manager


class HealthChecker:
    """基础设施健康检查器"""

    def check_redis(self) -> dict:
        """检查 Redis 连接"""
        try:
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0))
            )
            r.ping()
            info = r.info()

            return {
                'status': 'healthy',
                'version': info.get('redis_version'),
                'memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients')
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_qdrant(self) -> dict:
        """检查 Qdrant 连接"""
        try:
            client = QdrantClient(
                host=os.getenv('QDRANT_HOST', 'localhost'),
                port=int(os.getenv('QDRANT_PORT', 6333))
            )
            collections = client.get_collections()

            return {
                'status': 'healthy',
                'collections': len(collections.collections)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_database(self) -> dict:
        """检查 SQLite 数据库"""
        try:
            with db_manager.session_scope() as session:
                # 测试查询
                result = session.execute(text("SELECT 1"))
                result.scalar()

                # 检查表
                tables = session.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )).fetchall()

                return {
                    'status': 'healthy',
                    'tables': [t[0] for t in tables]
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_all(self) -> dict:
        """执行所有健康检查"""
        return {
            'redis': self.check_redis(),
            'qdrant': self.check_qdrant(),
            'database': self.check_database()
        }


# 快捷函数
def health_check() -> dict:
    """执行健康检查"""
    checker = HealthChecker()
    return checker.check_all()
```

**Step 3: 使脚本可执行**

```bash
chmod +x scripts/check_infrastructure.sh
```

**Step 4: 运行健康检查**

```bash
./scripts/check_infrastructure.sh

# 预期输出:
# === Infrastructure Health Check ===
# 1. Docker Services
# ✓ Redis container running
# ✓ Qdrant container running
# ...
# Passed: 8
# Failed: 0
# All checks passed!
```

**Step 5: 提交**

```bash
git add scripts/check_infrastructure.sh backend/health.py
git commit -m "feat: add infrastructure health check tools

Features:
- Bash script for automated checks
- Python module for programmatic health checks
- Checks Redis, Qdrant, SQLite, and dependencies
- Color-coded output

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: 文档和验收

**文件**:
- Create: `docs/phase0-completion.md`
- Modify: `README.md`

**Step 1: 创建阶段完成文档**

```markdown
# Phase 0: 基础设施准备 - 完成报告

**完成日期**: 2026-02-26
**状态**: ✅ 已完成

## 已完成项目

### 1. Docker 服务
- ✅ Redis 7-alpine (缓存层)
- ✅ Qdrant 1.7.4 (向量数据库)
- ✅ Docker Compose 编排
- ✅ 健康检查配置

### 2. Python 依赖
- ✅ rank-bm25 (BM25 检索)
- ✅ celery (任务队列)
- ✅ redis (Redis 客户端)
- ✅ jieba (中文分词)
- ✅ 其他企业级依赖

### 3. SQLite 数据库
- ✅ 数据库模型 (Document, Conversation, Message)
- ✅ SQLAlchemy ORM 配置
- ✅ 会话管理
- ✅ 初始化脚本

### 4. Celery 任务队列
- ✅ Celery 应用配置
- ✅ 多队列支持
- ✅ Worker 启动脚本

### 5. 健康检查
- ✅ Bash 自动化检查脚本
- ✅ Python 健康检查模块

## 验收结果

```bash
./scripts/check_infrastructure.sh
```

**结果**: 所有检查通过 ✅

## 下一步

Phase 1: 核心算法实现 (混合检索、智能分块)

参见: `docs/plans/2026-02-26-phase1-hybrid-retrieval-implementation.md`
```

**Step 2: 更新 README**

在 README.md 中添加基础设施部分:

```markdown
## 🛠️ 基础设施

### 启动服务

```bash
# 1. 启动 Docker 服务
docker-compose up -d

# 2. 初始化数据库
python scripts/init_db.py

# 3. 验证环境
./scripts/check_infrastructure.sh
```

### 服务端口

- **Redis**: http://localhost:6379
- **Qdrant**: http://localhost:6333
- **Qdrant UI**: http://localhost:6334/dashboard

### 停止服务

```bash
docker-compose down
```
```

**Step 3: 提交**

```bash
git add docs/phase0-completion.md README.md
git commit -m "docs: complete Phase 0 infrastructure setup

All infrastructure components verified and operational:
- Docker services (Redis + Qdrant)
- Python dependencies
- SQLite database
- Celery task queue
- Health check tools

Ready for Phase 1: Core Algorithm Implementation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 验收标准

运行以下命令验证 Phase 0 完成:

```bash
# 1. 健康检查
./scripts/check_infrastructure.sh

# 预期: All checks passed!

# 2. 服务状态
docker-compose ps

# 预期: 所有服务 State=Up

# 3. Python 导入测试
python -c "
import redis
import celery
import rank_bm25
import jieba
from backend.database import db_manager
from backend.health import health_check
print('All imports successful!')
"

# 预期: All imports successful!

# 4. 数据库表检查
sqlite3 data/app.db ".tables"

# 预期: conversations  documents  messages
```

---

## 下一步

Phase 0 完成后,继续 **Phase 1: 核心算法实现**

参见: `docs/plans/2026-02-26-phase1-hybrid-retrieval-implementation.md`
