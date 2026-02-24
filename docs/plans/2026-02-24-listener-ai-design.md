# Listener - AI情感陪伴系统 设计文档

**创建日期**: 2026-02-24
**项目类型**: 学习项目 + 可发布产品
**开发者**: 实习生个人项目
**预计开发周期**: 10周 (每周10-15小时)

---

## 一、项目概述

### 1.1 项目定位

**产品名称**: Listener (一听)
**Slogan**: "Someone's listening, 24/7, judgment-free"

**核心价值**: 为孤独和社交障碍人群提供24/7 AI倾听陪伴

**项目目标**:
1. **主要目标**: 完整的全栈AI应用开发学习
2. **次要目标**: 可发布的产品,获得真实用户反馈
3. **技术目标**: 掌握LangChain/LangGraph等前沿AI技术
4. **简历目标**: 一个技术含量高的项目作品

### 1.2 用户定位

**目标用户**:
- 18-35岁孤独或社交焦虑人群
- 海外市场优先(美国/欧洲)
- 需要情感倾诉但不想打扰他人的人

**用户场景**:
- 深夜焦虑时需要倾诉
- 日常情绪需要表达
- 不想被评判,只想被倾听

### 1.3 差异化定位

**与竞品区别**:
- **Replika**: 他们主打romantic companion,我们主打pure listening
- **Character.AI**: 他们主打角色扮演,我们主打情感支持
- **ChatGPT**: 它会给建议和解决方案,我们只倾听和共情

**核心差异**: "绝不主动给建议,只倾听和提问"

---

## 二、功能设计

### 2.1 MVP功能范围

**包含功能**:
✅ 匿名使用(无需注册即可开始)
✅ 1v1 AI倾听对话
✅ 长期记忆系统(RAG)
✅ 情绪感知
✅ 危机检测
✅ 对话历史保存
✅ Web响应式设计

**不包含功能**(未来扩展):
❌ 移动App(避免审核复杂度)
❌ 朋友圈功能
❌ 多角色管理
❌ 付费订阅(保持完全免费)

### 2.2 核心功能详细设计

#### 2.2.1 匿名对话系统

**流程**:
1. 用户访问网站
2. 自动生成匿名session ID(存localStorage)
3. 直接开始对话,无需注册
4. 可选:注册账号永久保存历史

**技术实现**:
- localStorage存session ID
- 后端根据session ID关联对话
- 提供"保存对话"功能引导注册

#### 2.2.2 AI倾听者对话

**核心原则**:
- 只倾听,不说教
- 短回复(1-3句话)
- 温暖但不过度热情
- 提问引导用户表达

**Prompt设计**:
```
System: You are a compassionate listener, not a therapist or advisor.

Your role:
- Listen actively and acknowledge feelings
- Ask gentle follow-up questions to help user express
- Never give advice unless explicitly asked
- Keep responses short (1-3 sentences)
- Be warm but not overly cheerful

Guidelines:
- If user mentions crisis (suicide, self-harm), show concern
  and suggest professional help
- Don't use excessive punctuation or emojis
- Mirror the user's emotional tone
- Sometimes just acknowledging is enough

Remember: You're here to listen, not fix.
```

**Few-shot Examples**:
- User: "I feel so lonely today"
  AI: "That sounds really hard. Loneliness can feel overwhelming. What's making you feel this way right now?"

- User: "Nobody understands me"
  AI: "I hear you. Feeling misunderstood is painful. Want to tell me more about what's going on?"

#### 2.2.3 长期记忆系统(RAG)

**目标**: AI能记住用户之前说过的重要内容

**技术架构**:
- Vector Database: Qdrant
- Embeddings: OpenAI text-embedding-3-small
- 每次对话存储embedding
- 对话时检索相关历史(k=5)

**Memory分层**:
1. **短期记忆**: 最近20条对话(直接传入context)
2. **长期记忆**: 向量数据库语义搜索
3. **摘要记忆**: 超过50条对话后自动生成摘要

**实现细节**:
```python
# 存储对话
vectorstore.add_texts(
    texts=[message],
    metadatas=[{
        "user_id": user_id,
        "timestamp": timestamp,
        "emotion": detected_emotion
    }]
)

# 检索相关上下文
relevant_history = vectorstore.similarity_search(
    query=current_message,
    k=5,
    filter={"user_id": user_id}
)
```

#### 2.2.4 情绪感知系统

**使用LangGraph构建多步骤工作流**:

**工作流**:
```
用户消息 → 情绪检测 → 危机检测 → 生成回复 → 返回
```

**节点定义**:
1. **情绪检测节点**: 用轻量模型(Haiku)快速分析情绪
2. **危机检测节点**: 关键词匹配 + AI判断
3. **回复生成节点**: 根据情绪和危机状态生成合适回复

**State定义**:
```python
class ConversationState(TypedDict):
    messages: List[Message]
    user_id: str
    emotion: str  # happy/sad/anxious/angry/neutral
    crisis_detected: bool
    relevant_history: List[str]
    response: str
```

#### 2.2.5 危机检测与处理

**检测机制**:
- 关键词检测: "suicide", "kill myself", "end my life", "self harm"
- AI二次判断: 避免误判

**处理流程**:
1. 检测到危机 → 标记状态
2. AI回复表达关切
3. 提供专业资源链接:
   - National Suicide Prevention Lifeline: 988
   - Crisis Text Line: Text HOME to 741741
4. 记录事件(隐私保护下)

**回复模板**:
```
"I'm really concerned about what you're sharing. Please know
that you don't have to go through this alone.

I'm here to listen, but I'm not equipped to help in a crisis.
Please reach out to a crisis counselor who can provide
immediate support:

[Crisis resources links]

Your life matters, and there are people who want to help."
```

---

## 三、技术架构

### 3.1 技术栈选型

#### 前端技术栈
```
Next.js 14 (App Router)
├── TypeScript
├── Tailwind CSS
├── shadcn/ui (组件库)
├── Zustand (状态管理)
├── React Query (数据获取)
└── WebSocket (实时通信)
```

**选型理由**:
- Next.js 14 App Router: 最新范式,SSR性能好
- shadcn/ui: 2024最火组件库,简历加分
- Zustand: 比Redux轻量,适合小项目
- React Query: 优雅的异步状态管理

#### 后端技术栈
```
Python FastAPI
├── LangChain (核心AI框架)
│   ├── LangChain Expression Language (LCEL)
│   ├── ConversationChain
│   ├── Memory Management
│   └── Prompt Templates
├── LangGraph (对话流程编排)
├── Pydantic (数据验证)
└── SQLAlchemy (ORM)
```

**选型理由**:
- FastAPI: 现代Python框架,异步高性能
- LangChain: AI应用标准框架,必学
- LangGraph: 复杂对话流程管理
- Pydantic: 类型安全

#### AI & 数据
```
AI Models:
├── Claude 3 Haiku (情绪检测,成本低)
├── Claude 3 Sonnet (主对话,质量高)
└── OpenAI text-embedding-3-small (向量化)

Databases:
├── PostgreSQL (Supabase托管)
│   ├── Users
│   ├── Messages
│   └── Sessions
└── Qdrant (Vector Database)
    └── Conversation Embeddings
```

**选型理由**:
- Claude: 质量好,成本可控
- OpenAI Embeddings: 便宜且质量好
- Supabase: 免费托管PostgreSQL
- Qdrant: 开源向量数据库,易部署

#### 部署架构
```
Frontend: Vercel (免费)
Backend: Railway ($5-20/月)
Vector DB: Qdrant Cloud (免费1GB)
Database: Supabase (免费500MB)
```

### 3.2 系统架构图

```
┌─────────────────────────────────────────┐
│        Client (Browser)                 │
│  ┌─────────────────────────────────┐   │
│  │  Next.js 14 App                 │   │
│  │  - Chat Interface               │   │
│  │  - State Management (Zustand)   │   │
│  │  - WebSocket Client             │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTPS/WSS
┌──────────────▼──────────────────────────┐
│        API Gateway (FastAPI)            │
│  ┌─────────────────────────────────┐   │
│  │  REST Endpoints                 │   │
│  │  ├─ POST /api/chat (streaming)  │   │
│  │  ├─ GET  /api/history           │   │
│  │  ├─ POST /api/auth/register     │   │
│  │  └─ GET  /api/profile           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  LangChain Orchestration        │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │ LangGraph Workflow      │   │   │
│  │  │                         │   │   │
│  │  │  ┌──────────────────┐  │   │   │
│  │  │  │ Emotion Node     │  │   │   │
│  │  │  └────────┬─────────┘  │   │   │
│  │  │           │             │   │   │
│  │  │  ┌────────▼─────────┐  │   │   │
│  │  │  │ Crisis Node      │  │   │   │
│  │  │  └────────┬─────────┘  │   │   │
│  │  │           │             │   │   │
│  │  │  ┌────────▼─────────┐  │   │   │
│  │  │  │ Response Node    │  │   │   │
│  │  │  └──────────────────┘  │   │   │
│  │  └─────────────────────────┘   │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │ ConversationChain       │   │   │
│  │  │ ├─ Prompt Template      │   │   │
│  │  │ ├─ Memory (Summary)     │   │   │
│  │  │ └─ LLM (Claude Sonnet)  │   │   │
│  │  └─────────────────────────┘   │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │ RAG Pipeline            │   │   │
│  │  │ ├─ Query Embedding      │   │   │
│  │  │ ├─ Vector Search        │   │   │
│  │  │ └─ Context Retrieval    │   │   │
│  │  └─────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
└──────────┬──────────────┬───────────────┘
           │              │
    ┌──────▼─────┐ ┌─────▼────────┐
    │  Claude    │ │   Qdrant     │
    │   API      │ │  Vector DB   │
    │            │ │              │
    │ - Haiku    │ │ Collections: │
    │ - Sonnet   │ │ - user_convs │
    └────────────┘ └──────────────┘
           │              │
    ┌──────▼──────────────▼───────┐
    │   PostgreSQL (Supabase)     │
    │   ┌─────────────────────┐   │
    │   │ Tables:             │   │
    │   │ - users             │   │
    │   │ - sessions          │   │
    │   │ - messages          │   │
    │   │ - emotion_logs      │   │
    │   └─────────────────────┘   │
    └─────────────────────────────┘
```

### 3.3 数据库设计

#### PostgreSQL Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT false
);

-- 会话表
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    emotion VARCHAR(50),
    crisis_detected BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_user_created (user_id, created_at DESC)
);

-- 情绪日志表
CREATE TABLE emotion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    emotion VARCHAR(50),
    confidence FLOAT,
    message_id UUID REFERENCES messages(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Qdrant Collection Schema

```python
# Collection: user_conversations
{
    "vectors": {
        "size": 1536,  # OpenAI embedding dimension
        "distance": "Cosine"
    },
    "payload_schema": {
        "user_id": "keyword",
        "message_id": "keyword",
        "content": "text",
        "emotion": "keyword",
        "timestamp": "integer",
        "role": "keyword"
    }
}
```

### 3.4 API设计

#### REST Endpoints

**认证相关**:
```
POST /api/auth/anonymous
  - 创建匿名session
  - Response: { session_id, token }

POST /api/auth/register
  - 注册账号(保存匿名对话)
  - Body: { email, password, session_id? }
  - Response: { user_id, token }

POST /api/auth/login
  - 登录
  - Body: { email, password }
  - Response: { user_id, token }
```

**对话相关**:
```
POST /api/chat
  - 发送消息,流式返回AI回复
  - Body: { message, session_id }
  - Response: Server-Sent Events stream
  - Stream format:
    data: {"type": "token", "content": "I"}
    data: {"type": "token", "content": " hear"}
    data: {"type": "done", "emotion": "sad"}

GET /api/history
  - 获取对话历史
  - Query: ?session_id=xxx&limit=50&offset=0
  - Response: { messages: [...], total: 100 }

DELETE /api/history
  - 删除对话历史
  - Query: ?session_id=xxx
  - Response: { success: true }
```

**分析相关**:
```
GET /api/insights
  - 获取情绪分析
  - Query: ?session_id=xxx&days=7
  - Response: {
      emotion_distribution: { happy: 20, sad: 50, ... },
      message_count: 150,
      active_days: 5
    }
```

---

## 四、用户体验设计

### 4.1 界面设计

#### 首页
```
┌─────────────────────────────────────┐
│          Listener 倾听者            │
│                                     │
│    "Someone's listening, 24/7,     │
│        judgment-free"               │
│                                     │
│      [Start Talking →]              │
│                                     │
│   No signup needed • Anonymous     │
│   Your privacy is protected        │
│                                     │
│   ─────────────────────────         │
│                                     │
│   How it works:                     │
│   ✓ Just start talking              │
│   ✓ AI listens, doesn't lecture    │
│   ✓ Available 24/7                  │
│   ✓ Free forever                    │
└─────────────────────────────────────┘
```

#### 对话界面
```
┌─────────────────────────────────────┐
│  [☰] Listener              [⋮] [?] │
├─────────────────────────────────────┤
│                                     │
│  [AI头像]                          │
│  ┌───────────────────────────────┐ │
│  │ I'm here to listen.           │ │
│  │ What's on your mind?          │ │
│  └───────────────────────────────┘ │
│  2:34 PM                            │
│                                     │
│                     [用户头像]      │
│  ┌───────────────────────────────┐ │
│  │ I feel so lonely today        │ │
│  └───────────────────────────────┘ │
│                          2:35 PM    │
│                                     │
│  [AI头像]                          │
│  ┌───────────────────────────────┐ │
│  │ That sounds really hard.      │ │
│  │ Loneliness can feel over-     │ │
│  │ whelming. What's making you   │ │
│  │ feel this way right now?      │ │
│  └───────────────────────────────┘ │
│  2:35 PM                            │
│                                     │
│  [AI正在输入...]                   │
│                                     │
├─────────────────────────────────────┤
│ [📎]  Type your message...     [↑] │
└─────────────────────────────────────┘
```

**设计原则**:
- 极简界面,减少干扰
- 温暖色调(深蓝/灰)
- 夜间模式默认开启
- 无广告,无打扰

### 4.2 交互设计

**打字体验**:
- 流式输出,逐字显示
- 打字指示器("AI正在输入...")
- 平滑动画

**情绪反馈**(可选可视化):
- 检测到负面情绪时,界面微调(更温暖的色调)
- 危机检测时,顶部温和提示专业资源

**隐私保护**:
- 明显的"匿名模式"标识
- "保存对话"功能提示需要注册
- 随时删除历史的按钮

---

## 五、成本与资源规划

### 5.1 开发成本

**时间成本**:
- 总开发时间: 100-120小时
- 周投入: 10-15小时
- 总周期: 10周

**学习成本**:
- LangChain学习: $10-20 (API测试)
- 其他工具试用: $10

**总计**: $20-30

### 5.2 运营成本

**基础设施** (免费层):
- Vercel: $0
- Railway: $5/月(可选,有免费层)
- Supabase: $0 (免费500MB)
- Qdrant Cloud: $0 (免费1GB)

**AI API** (100活跃用户,每人每天10条消息):
- Claude Haiku(情绪检测): $5/月
- Claude Sonnet(主对话): $30-50/月
- OpenAI Embeddings: $10-15/月

**域名**(可选):
- .com域名: $12/年

**月度总成本**: $50-85/月
**年度总成本**: $600-1000/年

### 5.3 成本控制策略

**免费用户限制**:
- 每个IP每天最多30条消息
- 超过后提示"明天再来"
- 或引导注册(注册用户50条/天)

**技术优化**:
- 缓存常见Prompt结果
- 使用Haiku处理简单对话
- 批量处理embedding

**应急方案**:
- 成本超$100/月 → 暂停新用户注册
- 或改为waitlist模式
- 或寻求sponsor

---

## 六、发布与增长策略

### 6.1 发布计划

**Soft Launch** (Week 10):
- 部署到生产环境
- 邀请5-10个朋友试用
- 收集初步反馈

**Public Launch** (Week 11-12):
- Reddit发布: r/lonely, r/socialanxiety
- Product Hunt发布
- 个人社交媒体分享

### 6.2 获客渠道

**主要渠道**:
1. **Reddit**: 目标社区精准投放
2. **Product Hunt**: Tech社区曝光
3. **口碑传播**: 引导用户分享

**内容策略**:
- 分享创建故事(为什么做这个)
- 强调隐私和匿名
- 不过度营销

### 6.3 成功指标

**技术指标**:
- ✅ 项目完成,可正常使用
- ✅ 部署成功,稳定运行
- ✅ 代码质量良好

**用户指标**:
- 目标: 10-50个真实用户试用
- D7留存率: >20%即算成功
- 平均对话长度: >5条

**学习指标** (最重要):
- ✅ 掌握LangChain/LangGraph
- ✅ 理解RAG架构
- ✅ 全栈开发经验
- ✅ AI产品设计思维

---

## 七、风险与应对

### 7.1 技术风险

**风险1: 技术学习曲线陡**
- 应对: 分阶段学习,先基础后高级
- 每周预留学习时间

**风险2: API成本失控**
- 应对: 严格限流,监控成本
- 设定$100/月硬上限

**风险3: 性能问题**
- 应对: 早期用户少,不会有问题
- 后期优化:缓存、CDN

### 7.2 产品风险

**风险1: 无人使用**
- 应对: 这本来就是学习项目
- 重点是完成开发,用户是bonus

**风险2: 负面反馈**
- 应对: 谦虚接受,快速迭代
- 强调"学习项目,持续改进"

**风险3: 法律/隐私问题**
- 应对: 明确免责声明
- 不存储敏感信息
- 提供删除功能

### 7.3 时间风险

**风险1: 开发时间超预期**
- 应对: MVP功能可以再砍
- 核心保留:对话+基础记忆
- 高级功能(LangGraph)可后加

**风险2: 工作繁忙,无法投入**
- 应对: 弹性计划,允许延期
- 最差情况:做成Demo,不发布

---

## 八、简历呈现

### 8.1 项目描述

**简历项目条目**:
```
Listener - 基于LangChain的AI情感陪伴系统
Personal Project | 2026.02 - 2026.05

• 独立设计并开发全栈AI对话应用,为用户提供情感倾听支持
• 使用LangChain/LangGraph构建多层次对话系统,实现情绪感知和危机检测
• 实现RAG架构,通过Qdrant向量数据库实现长期记忆和语义搜索
• 使用LCEL构建可组合的对话流,实现流式响应提升用户体验
• 全栈开发:Next.js 14 (App Router) + FastAPI + PostgreSQL
• 部署上线,服务XX名用户,平均对话时长XX分钟

技术栈:
- AI Framework: LangChain, LangGraph, Claude API, OpenAI Embeddings
- Vector DB: Qdrant (语义搜索,RAG)
- Backend: Python FastAPI, PostgreSQL, SQLAlchemy
- Frontend: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- 部署: Vercel + Railway + Supabase

技术亮点:
- Production-ready的AI应用架构设计
- 向量数据库实现长期记忆系统
- LangGraph多Agent流程编排
- 情绪检测与危机预警系统
```

### 8.2 面试谈资

**可以讨论的技术点**:
1. LangChain的Memory管理机制
2. RAG架构的实现细节
3. 如何优化LLM成本
4. Streaming响应的技术实现
5. 向量数据库的选型考虑
6. Prompt工程的最佳实践
7. 如何处理用户隐私
8. 全栈开发的挑战

**项目故事**:
- 为什么做这个项目(个人动机)
- 最大的技术挑战是什么
- 如果重新做会怎么优化
- 学到了什么

---

## 九、后续扩展方向

**如果项目成功,未来可以加**:

### Phase 2 (3-6个月后):
- [ ] 移动App (React Native)
- [ ] 语音对话功能
- [ ] 多语言支持
- [ ] 情绪分析可视化

### Phase 3 (6-12个月后):
- [ ] 朋友圈功能(虚拟社交)
- [ ] 多角色管理
- [ ] 个性化AI训练
- [ ] 社区功能

**但现在不要想这些,专注MVP!**

---

## 十、总结

### 项目价值

**学习价值**: ⭐⭐⭐⭐⭐
- 完整的AI应用开发经验
- 前沿技术栈(LangChain/LangGraph)
- 全栈开发能力提升

**简历价值**: ⭐⭐⭐⭐⭐
- 技术含量高
- 可展示的完整产品
- 面试谈资丰富

**商业价值**: ⭐⭐
- 不期望赚钱
- 可能有小规模用户
- 主要是学习和作品集

### 核心原则

1. **学习优先**: 这是学习项目,不是商业项目
2. **可完成性**: 10周必须能做完MVP
3. **技术先进**: 用最新最好的技术栈
4. **务实态度**: 不期望火爆,完成即成功

---

**下一步**: 创建详细的实施计划(week-by-week任务分解)
