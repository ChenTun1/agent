# Listener AI - 详细实施计划

**项目**: Listener AI情感陪伴系统
**开发周期**: 10周 (每周10-15小时)
**开始日期**: 2026-02-24
**预计完成**: 2026-05-05

---

## 开发阶段概览

```
Phase 1: 学习准备 (Week 1-2)    → 学习LangChain基础
Phase 2: RAG系统 (Week 3-4)     → 学习向量数据库和RAG
Phase 3: LangGraph (Week 5-6)   → 学习Agent编排
Phase 4: 全栈开发 (Week 7-9)    → 前后端集成
Phase 5: 部署发布 (Week 10)     → 上线和优化
```

---

## Week 1-2: LangChain基础学习

### 学习目标
- [ ] 理解LangChain核心概念
- [ ] 掌握Chains和Runnables
- [ ] 学会Memory管理
- [ ] 掌握Prompt Templates

### 具体任务

#### Day 1-2: 环境准备和基础概念
**时间**: 3-4小时

**任务**:
1. 安装开发环境
```bash
# Python环境
python -m venv venv
source venv/bin/activate
pip install langchain langchain-anthropic langchain-openai
```

2. 注册API账号
- Anthropic (Claude): https://console.anthropic.com
- OpenAI: https://platform.openai.com
- 获取API keys

3. 学习资源
- 阅读LangChain官方文档: https://python.langchain.com/docs/get_started/introduction
- 观看: "LangChain Crash Course" (YouTube, 1小时)

**学习笔记模板**:
```markdown
# LangChain学习笔记 - Day 1

## 核心概念
- Chain: 链式调用多个组件
- Runnable: 可执行的基础单元
- LLM vs ChatModel: 区别是什么?

## 疑问
- [ ] Memory是如何持久化的?
- [ ] Streaming如何实现?

## 实践
- [x] 完成第一个Hello World
```

#### Day 3-4: 基础对话链
**时间**: 4-5小时

**任务**:
1. 实现第一个聊天机器人
```python
# chat_basic.py
from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.7
)

memory = ConversationBufferMemory()

chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True  # 看到内部过程
)

# 测试对话
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break

    response = chain.invoke({"input": user_input})
    print(f"AI: {response['response']}")
```

2. 实验不同的Memory类型
- ConversationBufferMemory
- ConversationSummaryMemory
- ConversationBufferWindowMemory

3. 记录对比结果

**练习项目**: 做一个命令行聊天工具,能记住对话历史

#### Day 5-7: Prompt工程
**时间**: 5-6小时

**任务**:
1. 学习Prompt Templates
```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# 创建倾听者Prompt
listener_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a compassionate listener.

    Your role:
    - Listen actively and acknowledge feelings
    - Ask gentle follow-up questions
    - Never give advice unless asked
    - Keep responses short (1-3 sentences)

    Remember: You're here to listen, not fix.
    """),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
```

2. Few-shot Learning实践
```python
from langchain.prompts import FewShotPromptTemplate

examples = [
    {
        "user": "I feel so lonely",
        "ai": "That sounds really hard. Want to tell me more?"
    },
    # 添加更多例子
]

# 构建few-shot template
```

3. A/B测试不同Prompt
- 对比有/无few-shot的效果
- 测试不同的system prompt

**练习项目**: 做一个Prompt测试工具,对比不同prompt的输出

#### Day 8-10: Streaming和高级特性
**时间**: 4-5小时

**任务**:
1. 实现Streaming响应
```python
# streaming_chat.py
async def chat_stream(message: str):
    async for chunk in chain.astream({"input": message}):
        print(chunk.content, end="", flush=True)
    print()  # 换行
```

2. 学习LCEL (LangChain Expression Language)
```python
from langchain_core.runnables import RunnablePassthrough

# 构建可组合的链
chain = (
    {"input": RunnablePassthrough()}
    | prompt
    | llm
    | output_parser
)
```

3. 错误处理和重试
```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    response = chain.invoke({"input": message})
    print(f"Tokens used: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost}")
```

**交付物**:
- [ ] `src/learning/langchain_basics/` 目录下的练习代码
- [ ] `docs/learning/langchain-notes.md` 学习笔记
- [ ] 一个可运行的命令行聊天工具

### Week 1-2 验收标准

**必须完成**:
- [ ] 能用LangChain构建基础对话系统
- [ ] 理解不同Memory类型的区别
- [ ] 会写和调试Prompt Templates
- [ ] 实现了Streaming响应

**加分项**:
- [ ] 尝试了LCEL
- [ ] 做了成本监控
- [ ] 写了详细的学习笔记

---

## Week 3-4: RAG系统和向量数据库

### 学习目标
- [ ] 理解Embeddings和向量化
- [ ] 掌握Qdrant向量数据库
- [ ] 实现基础RAG系统
- [ ] 学会语义搜索

### 具体任务

#### Day 11-13: Embeddings基础
**时间**: 5-6小时

**任务**:
1. 理解Embeddings原理
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 测试embedding
text = "I feel lonely today"
vector = embeddings.embed_query(text)
print(f"Vector dimension: {len(vector)}")
print(f"First 5 values: {vector[:5]}")
```

2. 相似度计算
```python
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

# 测试语义相似度
text1 = "I feel sad"
text2 = "I am unhappy"
text3 = "The weather is nice"

vec1 = embeddings.embed_query(text1)
vec2 = embeddings.embed_query(text2)
vec3 = embeddings.embed_query(text3)

print(f"Similarity(sad, unhappy): {cosine_similarity(vec1, vec2)}")
print(f"Similarity(sad, weather): {cosine_similarity(vec1, vec3)}")
```

3. 学习资源
- 视频: "What are Embeddings" (3Blue1Brown风格的解释)
- 阅读: OpenAI Embeddings文档

#### Day 14-16: Qdrant向量数据库
**时间**: 5-6小时

**任务**:
1. 安装和启动Qdrant
```bash
# 使用Docker
docker pull qdrant/qdrant
docker run -p 6333:6333 qdrant/qdrant

# 或注册Qdrant Cloud免费层
# https://cloud.qdrant.io
```

2. 基础操作
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 连接Qdrant
client = QdrantClient(url="http://localhost:6333")

# 创建collection
client.create_collection(
    collection_name="test_conversations",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small的维度
        distance=Distance.COSINE
    )
)

# 插入数据
from qdrant_client.models import PointStruct

points = [
    PointStruct(
        id=1,
        vector=vector,
        payload={"text": "original text", "user_id": "123"}
    )
]
client.upsert(collection_name="test_conversations", points=points)

# 搜索
results = client.search(
    collection_name="test_conversations",
    query_vector=query_vector,
    limit=5
)
```

3. 与LangChain集成
```python
from langchain_community.vectorstores import Qdrant

vectorstore = Qdrant(
    client=client,
    collection_name="conversations",
    embeddings=embeddings
)

# 添加文档
vectorstore.add_texts(
    texts=["I feel sad", "I am happy"],
    metadatas=[{"user_id": "123"}, {"user_id": "123"}]
)

# 搜索
results = vectorstore.similarity_search("feeling down", k=3)
```

#### Day 17-20: 完整RAG系统
**时间**: 6-8小时

**任务**:
1. 构建对话记忆RAG系统
```python
# rag_conversation.py
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain

# 初始化组件
embeddings = OpenAIEmbeddings()
vectorstore = Qdrant(...)
llm = ChatAnthropic(model="claude-3-sonnet-20240229")

# 构建RAG链
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# 使用
def chat_with_memory(user_message, user_id):
    # 1. 检索相关历史
    relevant_history = vectorstore.similarity_search(
        user_message,
        k=5,
        filter={"user_id": user_id}
    )

    # 2. 生成回复
    response = qa_chain({
        "question": user_message,
        "chat_history": relevant_history
    })

    # 3. 存储新对话
    vectorstore.add_texts(
        texts=[user_message, response['answer']],
        metadatas=[
            {"user_id": user_id, "role": "user"},
            {"user_id": user_id, "role": "assistant"}
        ]
    )

    return response['answer']
```

2. 优化检索策略
- 测试不同的k值
- 添加metadata过滤
- 时间衰减(最近的对话权重更高)

3. 性能测试
- 插入1000条对话
- 测试检索速度
- 测试相关性

**练习项目**: 做一个"对话历史问答"工具
- 导入大量对话
- 可以问"我们之前聊过XX吗?"
- AI能找到相关的历史对话

### Week 3-4 验收标准

**必须完成**:
- [ ] 理解Embeddings和向量相似度
- [ ] 会使用Qdrant CRUD操作
- [ ] 实现了基础RAG系统
- [ ] 能够语义搜索历史对话

**加分项**:
- [ ] 优化了检索策略
- [ ] 做了性能测试
- [ ] 理解了不同distance metric的区别

**交付物**:
- [ ] `src/learning/rag/` 目录下的代码
- [ ] `docs/learning/rag-notes.md` 学习笔记
- [ ] 一个可运行的RAG Demo

---

## Week 5-6: LangGraph和Agent编排

### 学习目标
- [ ] 理解LangGraph的Graph概念
- [ ] 掌握State管理
- [ ] 实现多步骤工作流
- [ ] 构建情绪检测Agent

### 具体任务

#### Day 21-23: LangGraph基础
**时间**: 5-6小时

**任务**:
1. LangGraph核心概念
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# 定义State
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    emotion: str
    next_action: str

# 定义节点函数
def detect_emotion(state):
    # 分析最后一条消息的情绪
    last_message = state["messages"][-1]
    # 简单情绪检测(后面会用LLM)
    emotion = analyze_emotion(last_message)
    return {"emotion": emotion}

def decide_next(state):
    if state["emotion"] in ["sad", "anxious"]:
        return {"next_action": "empathize"}
    else:
        return {"next_action": "continue"}

# 构建Graph
workflow = StateGraph(AgentState)
workflow.add_node("emotion_detector", detect_emotion)
workflow.add_node("decision", decide_next)

# 添加边
workflow.set_entry_point("emotion_detector")
workflow.add_edge("emotion_detector", "decision")
workflow.add_conditional_edges(
    "decision",
    lambda x: x["next_action"],
    {
        "empathize": "empathy_response",
        "continue": "normal_response"
    }
)

# 编译
app = workflow.compile()
```

2. 学习资源
- LangGraph官方教程
- "LangGraph Academy" 免费课程
- YouTube: "LangGraph Introduction"

#### Day 24-26: 情绪检测工作流
**时间**: 6-7小时

**任务**:
1. 实现完整的情绪检测系统
```python
# emotion_workflow.py
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END

class ConversationState(TypedDict):
    user_message: str
    emotion: str
    emotion_confidence: float
    crisis_detected: bool
    ai_response: str

def detect_emotion_node(state):
    """使用LLM检测情绪"""
    llm = ChatAnthropic(model="claude-3-haiku-20240307")

    prompt = f"""Analyze the emotion in this message: "{state['user_message']}"

    Respond in JSON format:
    {{
        "emotion": "happy/sad/anxious/angry/neutral",
        "confidence": 0.0-1.0
    }}
    """

    response = llm.invoke(prompt)
    result = parse_json(response.content)

    return {
        "emotion": result["emotion"],
        "emotion_confidence": result["confidence"]
    }

def crisis_detection_node(state):
    """检测危机关键词"""
    crisis_keywords = [
        "suicide", "kill myself", "end my life",
        "self harm", "hurt myself"
    ]

    message_lower = state["user_message"].lower()
    crisis = any(keyword in message_lower for keyword in crisis_keywords)

    # 如果关键词匹配,用LLM二次确认
    if crisis:
        llm = ChatAnthropic(model="claude-3-sonnet-20240229")
        confirmation = llm.invoke(f"""
        Is this message indicating a mental health crisis?
        Message: "{state['user_message']}"

        Answer: yes/no with explanation
        """)
        # 解析确认结果
        crisis = "yes" in confirmation.content.lower()

    return {"crisis_detected": crisis}

def generate_response_node(state):
    """根据情绪和危机状态生成回复"""
    llm = ChatAnthropic(model="claude-3-sonnet-20240229")

    if state["crisis_detected"]:
        # 危机回复
        response = generate_crisis_response(state)
    elif state["emotion"] in ["sad", "anxious"]:
        # 共情回复
        response = generate_empathy_response(state, llm)
    else:
        # 正常倾听回复
        response = generate_listening_response(state, llm)

    return {"ai_response": response}

# 构建工作流
workflow = StateGraph(ConversationState)
workflow.add_node("emotion", detect_emotion_node)
workflow.add_node("crisis", crisis_detection_node)
workflow.add_node("response", generate_response_node)

workflow.set_entry_point("emotion")
workflow.add_edge("emotion", "crisis")
workflow.add_edge("crisis", "response")
workflow.add_edge("response", END)

app = workflow.compile()

# 使用
result = app.invoke({
    "user_message": "I feel so alone today"
})

print(f"Emotion: {result['emotion']}")
print(f"Crisis: {result['crisis_detected']}")
print(f"Response: {result['ai_response']}")
```

2. 测试不同场景
- 正常对话
- 负面情绪
- 危机情况

3. 优化准确率

#### Day 27-28: 可视化和调试
**时间**: 3-4小时

**任务**:
1. 使用LangSmith调试(可选)
```python
# 配置LangSmith
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"

# 运行工作流
# 在LangSmith UI中可以看到完整执行流程
```

2. 绘制工作流图
```python
from IPython.display import Image

# 生成流程图
Image(app.get_graph().draw_mermaid_png())
```

3. 性能分析
- 每个节点耗时
- Token使用统计
- 成本计算

**练习项目**: 做一个情绪分析Dashboard
- 输入对话,显示情绪检测结果
- 可视化工作流执行过程

### Week 5-6 验收标准

**必须完成**:
- [ ] 理解LangGraph的State和Graph概念
- [ ] 实现了情绪检测工作流
- [ ] 能够处理危机检测
- [ ] 根据不同情绪生成不同回复

**加分项**:
- [ ] 使用了LangSmith调试
- [ ] 做了可视化
- [ ] 优化了检测准确率

**交付物**:
- [ ] `src/learning/langgraph/` 目录下的代码
- [ ] `docs/learning/langgraph-notes.md` 学习笔记
- [ ] 情绪检测工作流Demo

---

## Week 7: 后端开发

### 学习目标
- [ ] 搭建FastAPI后端项目
- [ ] 集成LangChain/LangGraph
- [ ] 实现核心API
- [ ] 数据库设计和集成

### 具体任务

#### Day 29-31: 项目搭建
**时间**: 6-8小时

**任务**:
1. 创建项目结构
```bash
listener-backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置管理
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py          # 对话API
│   │   ├── auth.py          # 认证API
│   │   └── history.py       # 历史API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── langchain_setup.py   # LangChain配置
│   │   ├── rag.py               # RAG系统
│   │   └── emotion_agent.py     # 情绪Agent
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── message.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # 数据库连接
│   │   └── vector_store.py  # Qdrant封装
│   └── schemas/
│       ├── __init__.py
│       ├── chat.py
│       └── user.py
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

2. 安装依赖
```bash
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain==0.1.0
langchain-anthropic==0.1.0
langchain-openai==0.0.5
qdrant-client==1.7.0
python-dotenv==1.0.0
pydantic==2.5.0
sqlalchemy==2.0.25
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

3. 配置管理
```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    # Database
    DATABASE_URL: str = "postgresql://..."
    QDRANT_URL: str = "http://localhost:6333"

    # Security
    SECRET_KEY: str

    # LLM Config
    MAIN_MODEL: str = "claude-3-sonnet-20240229"
    EMOTION_MODEL: str = "claude-3-haiku-20240307"

    class Config:
        env_file = ".env"

settings = Settings()
```

4. FastAPI基础设置
```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Listener API")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js前端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Listener API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### Day 32-35: 核心API实现
**时间**: 8-10小时

**任务**:
1. 对话API(Streaming)
```python
# src/api/chat.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.core.langchain_setup import get_conversation_chain
from src.core.emotion_agent import emotion_workflow
from src.db.database import get_db
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """流式对话API"""

    async def generate():
        # 1. 运行情绪检测工作流
        emotion_result = await emotion_workflow.ainvoke({
            "user_message": request.message,
            "user_id": request.session_id
        })

        # 2. 获取对话链
        chain = get_conversation_chain(
            user_id=request.session_id,
            emotion=emotion_result["emotion"],
            crisis_detected=emotion_result["crisis_detected"]
        )

        # 3. 流式生成回复
        full_response = ""
        async for chunk in chain.astream({"input": request.message}):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            full_response += content

            # 发送SSE事件
            yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

        # 4. 存储对话到数据库
        save_message(db, request.session_id, "user", request.message)
        save_message(db, request.session_id, "assistant", full_response,
                    emotion=emotion_result["emotion"])

        # 5. 存储到向量数据库
        store_to_vectordb(request.session_id, request.message, full_response)

        # 6. 发送完成事件
        yield f"data: {json.dumps({'type': 'done', 'emotion': emotion_result['emotion']})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

2. 历史记录API
```python
# src/api/history.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.models.message import Message

router = APIRouter(prefix="/api", tags=["history"])

@router.get("/history")
async def get_history(
    session_id: str = Query(...),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    messages = db.query(Message)\
        .filter(Message.user_id == session_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

    total = db.query(Message)\
        .filter(Message.user_id == session_id)\
        .count()

    return {
        "messages": [m.to_dict() for m in messages],
        "total": total
    }
```

3. 认证API
```python
# src/api/auth.py
from fastapi import APIRouter
from src.schemas.user import UserCreate
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/anonymous")
async def create_anonymous_session():
    """创建匿名session"""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}

@router.post("/register")
async def register(user: UserCreate):
    """注册用户(可选功能)"""
    # TODO: 后续实现
    pass
```

#### 数据库集成
```python
# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# src/models/message.py
from sqlalchemy import Column, String, Text, Boolean, DateTime, Float
from datetime import datetime
from src.db.database import Base
import uuid

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    emotion = Column(String)
    crisis_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "emotion": self.emotion,
            "created_at": self.created_at.isoformat()
        }
```

### Week 7 验收标准

**必须完成**:
- [ ] FastAPI项目结构搭建完成
- [ ] 实现了Streaming对话API
- [ ] 集成了LangChain和LangGraph
- [ ] 数据库读写正常
- [ ] 向量数据库集成

**测试检查**:
```bash
# 启动服务
uvicorn src.main:app --reload

# 测试健康检查
curl http://localhost:8000/health

# 测试匿名session
curl -X POST http://localhost:8000/api/auth/anonymous

# 测试对话(使用httpie或Postman测试SSE)
```

---

## Week 8: 前端开发

### 学习目标
- [ ] 搭建Next.js 14项目
- [ ] 实现聊天界面
- [ ] 集成shadcn/ui
- [ ] 实现Streaming显示

### 具体任务

#### Day 36-38: 项目搭建
**时间**: 6-8小时

**任务**:
1. 创建Next.js项目
```bash
npx create-next-app@latest listener-frontend --typescript --tailwind --app
cd listener-frontend
```

2. 安装依赖
```bash
# UI组件库
npx shadcn-ui@latest init

# 状态管理
npm install zustand

# 数据获取
npm install @tanstack/react-query

# 工具库
npm install date-fns uuid
npm install -D @types/uuid
```

3. 项目结构
```
listener-frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── chat/
│       └── page.tsx
├── components/
│   ├── ui/              # shadcn组件
│   ├── ChatMessage.tsx
│   ├── ChatInput.tsx
│   └── ChatContainer.tsx
├── lib/
│   ├── api.ts          # API调用
│   └── store.ts        # Zustand store
└── types/
    └── chat.ts
```

4. 配置shadcn/ui
```bash
# 安装需要的组件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add avatar
```

#### Day 39-42: 聊天界面实现
**时间**: 8-10小时

**任务**:
1. 聊天消息组件
```tsx
// components/ChatMessage.tsx
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  emotion?: string
  timestamp: Date
}

export function ChatMessage({ role, content, emotion, timestamp }: ChatMessageProps) {
  const isUser = role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <Avatar>
        <AvatarFallback>
          {isUser ? 'You' : 'AI'}
        </AvatarFallback>
      </Avatar>

      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-2 rounded-2xl max-w-[80%] ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {content}
        </div>

        <span className="text-xs text-gray-500 mt-1">
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}
```

2. 输入组件
```tsx
// components/ChatInput.tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (message.trim()) {
      onSend(message)
      setMessage('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex gap-2 p-4 border-t">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        className="resize-none"
        rows={2}
        disabled={disabled}
      />
      <Button onClick={handleSend} disabled={disabled || !message.trim()}>
        Send
      </Button>
    </div>
  )
}
```

3. Streaming实现
```tsx
// lib/api.ts
export async function sendMessage(
  sessionId: string,
  message: string,
  onChunk: (chunk: string) => void,
  onComplete: (emotion: string) => void
) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  })

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader!.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))

        if (data.type === 'token') {
          onChunk(data.content)
        } else if (data.type === 'done') {
          onComplete(data.emotion)
        }
      }
    }
  }
}
```

4. 聊天页面
```tsx
// app/chat/page.tsx
'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatMessage } from '@/components/ChatMessage'
import { ChatInput } from '@/components/ChatInput'
import { sendMessage } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  emotion?: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 创建匿名session
    fetch('http://localhost:8000/api/auth/anonymous', { method: 'POST' })
      .then(res => res.json())
      .then(data => setSessionId(data.session_id))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  const handleSend = async (message: string) => {
    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])

    // 开始streaming
    setIsLoading(true)
    setStreamingContent('')

    await sendMessage(
      sessionId,
      message,
      // onChunk
      (chunk) => {
        setStreamingContent(prev => prev + chunk)
      },
      // onComplete
      (emotion) => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: streamingContent,
          emotion,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiMessage])
        setStreamingContent('')
        setIsLoading(false)
      }
    )
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <header className="p-4 border-b">
        <h1 className="text-2xl font-bold">Listener</h1>
        <p className="text-sm text-gray-500">Someone's listening, 24/7</p>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <ChatMessage key={msg.id} {...msg} />
        ))}

        {streamingContent && (
          <ChatMessage
            role="assistant"
            content={streamingContent}
            timestamp={new Date()}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  )
}
```

### Week 8 验收标准

**必须完成**:
- [ ] Next.js项目运行正常
- [ ] 聊天界面美观且响应式
- [ ] Streaming显示流畅
- [ ] 可以正常对话
- [ ] 移动端适配良好

**视觉检查**:
- 界面简洁温馨
- 夜间模式(可选)
- 打字动画流畅
- 滚动自然

---

## Week 9: 集成测试与优化

### 学习目标
- [ ] 前后端联调
- [ ] 性能优化
- [ ] Bug修复
- [ ] 用户体验优化

### 具体任务

#### Day 43-45: 功能完善
**时间**: 6-8小时

**任务**:
1. 对话历史加载
2. 删除历史功能
3. 错误处理
4. Loading状态优化
5. 情绪标识显示(可选)

#### Day 46-49: 测试和优化
**时间**: 8-10小时

**任务**:
1. 端到端测试
- 测试完整对话流程
- 测试情绪检测准确性
- 测试危机检测

2. 性能优化
- API响应时间
- Streaming延迟
- 数据库查询优化

3. 成本优化
- Token使用统计
- 优化Prompt长度
- 缓存策略

4. Bug修复
- 收集并修复所有bug
- 边界情况处理

### Week 9 验收标准

**必须完成**:
- [ ] 所有核心功能正常工作
- [ ] 无严重bug
- [ ] 性能可接受
- [ ] 成本在预算内

---

## Week 10: 部署和发布

### 学习目标
- [ ] 部署到生产环境
- [ ] 配置域名和HTTPS
- [ ] 监控和日志
- [ ] 发布和推广

### 具体任务

#### Day 50-52: 部署准备
**时间**: 6-8小时

**任务**:
1. 环境配置
```bash
# .env.production
ANTHROPIC_API_KEY=xxx
DATABASE_URL=xxx
QDRANT_URL=xxx
```

2. 数据库迁移
- Supabase创建生产数据库
- 运行迁移脚本

3. Qdrant部署
- 注册Qdrant Cloud
- 创建collection

#### Day 53-56: 正式部署
**时间**: 6-8小时

**任务**:
1. 后端部署到Railway
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 创建项目
railway init

# 部署
railway up
```

2. 前端部署到Vercel
```bash
# 安装Vercel CLI
npm install -g vercel

# 部署
vercel --prod
```

3. 配置环境变量
4. 测试生产环境

#### Day 57-60: 发布
**时间**: 4-6小时

**任务**:
1. 准备发布材料
- 截图
- 演示视频(可选)
- 产品描述

2. 隐私政策页面
```markdown
# Privacy Policy

Listener is committed to protecting your privacy.

What we collect:
- Anonymous conversation data
- Basic usage analytics

What we DON'T collect:
- Personal information (unless you register)
- IP addresses (beyond basic security)

Your rights:
- Delete your data anytime
- Export your conversations
...
```

3. Reddit发布
- r/lonely
- r/socialanxiety

4. Product Hunt发布

### Week 10 验收标准

**必须完成**:
- [ ] 网站可访问
- [ ] HTTPS配置
- [ ] 功能正常
- [ ] 至少发布到1个渠道

**最终检查**:
```bash
# 生产环境测试清单
- [ ] 注册/登录流程
- [ ] 对话功能
- [ ] Streaming正常
- [ ] 历史记录
- [ ] 移动端适配
- [ ] 错误处理
- [ ] 性能可接受
```

---

## 你需要准备什么

### 开发环境
- [ ] 电脑: Mac/Windows/Linux均可
- [ ] 编辑器: VS Code推荐
- [ ] Git: 版本控制
- [ ] Node.js: v18+
- [ ] Python: v3.10+

### 账号注册
- [ ] Anthropic账号(Claude API)
- [ ] OpenAI账号(Embeddings)
- [ ] Supabase账号(数据库)
- [ ] Qdrant Cloud账号(向量数据库)
- [ ] Vercel账号(前端部署)
- [ ] Railway账号(后端部署)
- [ ] GitHub账号(代码托管)

### 资金准备
- [ ] $50-100: API测试和学习
- [ ] $50-100/月: 运营成本(如果有用户)

### 时间承诺
- [ ] 每周10-15小时
- [ ] 持续10周
- [ ] 最好固定时间段(如每晚8-10点,周末全天)

### 学习心态
- [ ] 接受出错和失败
- [ ] 遇到问题主动搜索
- [ ] 做笔记记录学习过程
- [ ] 不追求完美,先完成再优化

---

## 成功标准

### 最低标准(必须达到)
- [ ] 10周内完成MVP
- [ ] 网站可以访问和使用
- [ ] 核心功能(对话+记忆)正常
- [ ] 代码可以放在GitHub

### 理想标准
- [ ] 有10-50个真实用户试用
- [ ] D7留存率>20%
- [ ] 完整的学习笔记和代码注释
- [ ] 在1个社区发布

### 加分标准
- [ ] Product Hunt上发布
- [ ] 有用户反馈并迭代
- [ ] 写了技术博客分享经验
- [ ] 有人说"这个帮到我了"

---

## 风险应对

### 如果时间不够
- 优先完成核心功能(对话+基础记忆)
- 砍掉LangGraph(改用简单的if-else)
- 砍掉RAG(只用最近20条对话)
- 目标:做出能用的Demo

### 如果学习困难
- 每个技术点都先看官方教程
- 加入相关Discord/Slack社区提问
- 降低难度,用更简单的实现方式
- 允许延期1-2周

### 如果成本超支
- 严格限流
- 使用免费层
- 暂停新用户注册

---

## 下一步行动

**今天(Day 0)**:
1. [ ] 阅读完整的设计文档和实施计划
2. [ ] 注册所有需要的账号
3. [ ] 设置开发环境
4. [ ] 创建项目文件夹结构

**明天(Day 1)**:
1. [ ] 开始Week 1的学习
2. [ ] 安装LangChain
3. [ ] 运行第一个Hello World

**记住**: 这是一个学习项目,重点是过程而非结果。享受学习的过程!

---

**祝你成功!有任何问题随时问我。**