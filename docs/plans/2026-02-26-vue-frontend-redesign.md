# AI PDF 问答系统 - 前端重构和功能扩展设计

**创建日期**: 2026-02-26
**设计目标**: 从Streamlit迁移到Vue 3,优化用户体验,扩展核心功能
**实施周期**: 3-4周

## 目录

1. [项目背景](#1-项目背景)
2. [整体架构](#2-整体架构)
3. [UI设计](#3-ui设计)
4. [数据流和状态管理](#4-数据流和状态管理)
5. [后端API设计](#5-后端api设计)
6. [实施计划](#6-实施计划)
7. [风险和缓解措施](#7-风险和缓解措施)

---

## 1. 项目背景

### 当前问题

**前端问题**:
- Streamlit CSS冲突严重,布局难以控制
- 页面刷新导致状态丢失
- UI定制能力有限,无法实现复杂交互
- 移动端体验差

**功能缺失**:
- 只能管理单个PDF,无法切换多文档
- 没有对话历史记录
- 缺少搜索和导出功能

### 设计目标

**优先级排序**:
1. **前端用户体验**(P0) - 极简对话 + 专业功能区
2. **功能扩展**(P1) - 多文档管理 > 对话历史 > 全文搜索
3. **后端性能**(P2) - 稳定性和错误处理

**技术选型**:
- 前端: Vue 3 + TypeScript + Element Plus
- 状态管理: Pinia
- 后端: FastAPI (保持) + SQLite (新增)
- 时间线: 3-4周

---

## 2. 整体架构

### 系统架构图

```
┌─────────────────────────────────────────────────────┐
│                   用户浏览器                          │
├─────────────────────────────────────────────────────┤
│              Vue 3 前端应用 (端口 5173)               │
│  ┌──────────────┬──────────────┬──────────────┐     │
│  │  布局组件     │  业务组件     │  工具函数      │     │
│  │ - Navbar     │ - Chat       │ - API Client  │     │
│  │ - Sidebar    │ - Upload     │ - Storage     │     │
│  │ - Layout     │ - History    │ - Utils       │     │
│  └──────────────┴──────────────┴──────────────┘     │
│              Pinia Store (状态管理)                   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP (Axios)
                     ↓
┌─────────────────────────────────────────────────────┐
│            FastAPI 后端 (端口 8000)                   │
│  ┌──────────────────────────────────────────────┐   │
│  │  /upload    - 上传PDF                         │   │
│  │  /chat      - 对话                            │   │
│  │  /documents - 文档管理 (新增)                  │   │
│  │  /history   - 历史记录 (新增)                  │   │
│  │  /search    - 全文搜索 (新增)                  │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  现有模块: PDFProcessor, Embeddings, VectorStore     │
│           QAService, Retrieval, Pipeline            │
└────────────┬──────────────────┬─────────────────────┘
             │                  │
             ↓                  ↓
    ┌────────────────┐   ┌─────────────┐
    │  Qdrant向量库   │   │  SQLite DB  │ (新增)
    │   (PDF内容)    │   │ (历史/元数据)│
    └────────────────┘   └─────────────┘
```

### 目录结构

```
agent/
├── frontend-vue/          # 新前端项目
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   │   ├── layout/    # 布局组件
│   │   │   ├── chat/      # 对话组件
│   │   │   └── document/  # 文档组件
│   │   ├── stores/        # Pinia状态管理
│   │   │   ├── document.ts
│   │   │   ├── chat.ts
│   │   │   └── history.ts
│   │   ├── api/           # API调用
│   │   │   ├── client.ts
│   │   │   ├── document.ts
│   │   │   ├── chat.ts
│   │   │   └── history.ts
│   │   ├── views/         # 页面视图
│   │   ├── utils/         # 工具函数
│   │   ├── types/         # TypeScript类型
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/               # 后端(优化)
│   ├── routers/           # 新增:路由模块化
│   │   ├── documents.py
│   │   ├── conversations.py
│   │   └── search.py
│   ├── database.py        # 新增:SQLite管理
│   ├── main.py            # 重构:模块化路由
│   └── (现有文件保持)
├── data/                  # 新增:数据目录
│   └── app.db             # SQLite数据库
├── frontend/              # 旧Streamlit(后期删除)
└── docs/
    └── plans/             # 设计文档
```

---

## 3. UI设计

### 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo] AI PDF 问答                    [设置] [主题切换]      │  60px
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  文档列表 │                对话区域                          │
│  ────────│                                                  │
│  📄 文档1 │  ┌────────────────────────────────────┐        │
│  📄 文档2 │  │ 🤖 欢迎!上传PDF开始对话              │        │
│  📄 文档3*│  └────────────────────────────────────┘        │
│          │                                                  │
│  历史记录 │  ┌────────────────────────────────────┐        │
│  ────────│  │ 👤 这份文档的主要内容是什么?          │        │
│  📝 今天  │  └────────────────────────────────────┘        │
│  📝 昨天  │                                                  │
│  📝 上周  │  ┌────────────────────────────────────┐        │
│          │  │ 🤖 根据第1页...                       │        │
│  [+ 上传] │  │    [📖 查看来源] ▼                   │        │
│          │  └────────────────────────────────────┘        │
│  260px   │                                                  │
│          │              (可滚动查看历史)                      │
│          │                                                  │
│          │  ┌──────────────────────────────────┐          │
│          │  │ 输入问题...              [发送]    │  固定底部 │
│          │  └──────────────────────────────────┘          │
└──────────┴──────────────────────────────────────────────────┘
```

### 核心组件

**1. Layout.vue (主布局)**
- 组件: Navbar, Sidebar, ChatArea, InputBox
- 状态: currentDocument, sidebarCollapsed
- 响应式: 移动端自动折叠侧边栏

**2. Sidebar.vue (侧边栏)**
- DocumentList: 文档列表,切换/删除
- HistoryList: 历史记录,按时间分组
- 可折叠,宽度260px

**3. ChatArea.vue (对话区)**
- WelcomeScreen: 空状态提示
- MessageList: 消息列表,虚拟滚动
- Message: 用户/AI消息气泡
  - SourceExpander: 展开查看来源

**4. InputBox.vue (输入框)**
- 多行输入,自动高度
- Shift+Enter换行, Enter发送
- 字数统计,发送按钮

### 设计规范

**颜色 (浅色模式)**:
```css
--primary: #409EFF       /* Element Plus蓝 */
--bg-main: #FFFFFF       /* 主背景 */
--bg-secondary: #F5F7FA  /* 次级背景 */
--text-primary: #303133  /* 主文字 */
--text-secondary: #909399/* 次文字 */
--border: #DCDFE6        /* 边框 */
```

**间距**: 16px/24px (组件间), 12px/16px/24px (内边距)
**圆角**: 8px (小组件), 12px (卡片)
**排版**: 标题18px/bold, 正文14px, 小字12px, 行高1.6

---

## 4. 数据流和状态管理

### Pinia Store 设计

**documentStore.ts (文档管理)**
```typescript
interface Document {
  id: string              // PDF ID
  filename: string        // 文件名
  pageCount: number       // 页数
  uploadTime: string      // 上传时间
  size: number           // 文件大小
}

state:
  - documents: Document[]
  - currentDocumentId: string | null

actions:
  - uploadDocument(file: File)
  - deleteDocument(id: string)
  - setCurrentDocument(id: string)
  - fetchDocuments()

getters:
  - currentDocument
  - documentCount
```

**chatStore.ts (对话管理)**
```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Source[]
  documentId: string
}

state:
  - messages: Message[]
  - isLoading: boolean
  - error: string | null

actions:
  - sendMessage(question: string)
  - loadMessages(documentId: string)
  - clearMessages()

getters:
  - currentMessages
  - messageCount
```

**historyStore.ts (历史记录)**
```typescript
interface Conversation {
  id: string
  documentId: string
  documentName: string
  title: string
  lastMessageTime: string
  messageCount: number
}

state:
  - conversations: Conversation[]
  - currentConversationId: string | null

actions:
  - fetchHistory()
  - loadConversation(id: string)
  - deleteConversation(id: string)
  - searchHistory(query: string)

getters:
  - groupedByTime (today/yesterday/thisWeek/older)
```

### 数据流示例

**上传PDF**:
```
用户选择文件
  → documentStore.uploadDocument(file)
  → POST /api/upload
  → 后端处理并向量化
  → 返回文档信息
  → 更新documents[], 切换到新文档
  → 清空聊天区
```

**发送问题**:
```
用户输入问题 → 点击发送
  → chatStore.sendMessage(question)
  → 添加用户消息到messages[]
  → isLoading = true
  → POST /api/chat
  → 后端检索 + Claude生成
  → 返回答案和来源
  → 添加AI消息到messages[]
  → isLoading = false
  → 后台保存历史(异步)
```

**切换文档**:
```
点击文档
  → documentStore.setCurrentDocument(id)
  → chatStore.loadMessages(id)
  → GET /api/conversations?document_id={id}
  → 返回该文档的最近对话
  → 更新messages[]
```

### 本地存储

- **LocalStorage**: theme, sidebarCollapsed, lastDocumentId
- **SessionStorage**: draftMessage (刷新不丢失)
- **IndexedDB** (可选): 缓存历史对话

---

## 5. 后端API设计

### 新增API端点

**文档管理**
```http
GET /api/documents
# 获取所有文档列表
Response: { "documents": [...] }

DELETE /api/documents/{document_id}
# 删除文档(级联删除向量和历史)
Response: { "status": "success" }

GET /api/documents/{document_id}/info
# 获取文档详情
Response: { "id", "filename", "metadata", "conversation_count" }
```

**对话历史**
```http
GET /api/conversations?document_id={id}&limit=20
# 获取指定文档的对话列表
Response: { "conversations": [...] }

GET /api/conversations/{conversation_id}/messages
# 获取对话的所有消息
Response: { "messages": [...] }

POST /api/conversations
# 创建新对话
Body: { "document_id": "uuid" }
Response: { "conversation_id": "uuid" }

DELETE /api/conversations/{conversation_id}
# 删除对话
Response: { "status": "success" }
```

**优化现有API**
```http
POST /api/chat
# 新增conversation_id参数
Body: {
  "document_id": "uuid",
  "conversation_id": "uuid",  // 新增,可选
  "question": "问题内容"
}
Response: {
  "answer": "...",
  "cited_pages": [1, 3],
  "sources": [...],
  "message_id": "uuid",       // 新增
  "conversation_id": "uuid"   // 新增
}
```

**搜索API (第4周)**
```http
POST /api/search
Body: {
  "document_id": "uuid",
  "query": "关键词",
  "page": 1
}
Response: {
  "results": [
    {
      "page": 5,
      "text": "...包含关键词...",
      "highlights": [{ "start": 10, "end": 15 }]
    }
  ],
  "total": 10
}
```

### SQLite数据库

**表结构**
```sql
-- 文档表
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    page_count INTEGER NOT NULL,
    file_size INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON格式
);

-- 对话表
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    title TEXT,  -- 第一个问题
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- 消息表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' 或 'assistant'
    content TEXT NOT NULL,
    sources TEXT,        -- JSON格式
    cited_pages TEXT,    -- JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_conversations_document ON conversations(document_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

### 后端模块调整

**新增文件**:
- `backend/database.py`: SQLite数据库管理
- `backend/routers/documents.py`: 文档路由
- `backend/routers/conversations.py`: 对话路由
- `backend/routers/search.py`: 搜索路由 (第4周)

**重构main.py**:
- 使用APIRouter模块化路由
- 添加中间件(CORS, 错误处理, 日志)
- 统一响应格式

**优化现有模块**:
- PDFPipeline: 集成database保存元数据
- 添加统一异常处理
- 添加结构化日志

---

## 6. 实施计划

### 第1周: 基础框架搭建

**Day 1-2: Vue项目初始化**
- 创建Vite + Vue3 + TS项目
- 安装依赖: vue-router, pinia, element-plus, axios
- 配置vite.config.ts (代理, 别名)
- 配置Element Plus中文语言

**Day 3-4: 基础布局**
- 实现Layout.vue主布局
- 实现Navbar, Sidebar, ChatArea骨架
- 配置路由和Pinia
- 配置Axios拦截器

**Day 5-7: 核心功能**
- 实现文件上传组件(拖拽)
- 实现消息列表展示
- 实现发送消息功能
- 对接现有后端/upload和/chat API
- 处理加载状态和错误

**交付物**:
- ✅ Vue项目可运行
- ✅ 基础UI布局完成
- ✅ PDF上传功能
- ✅ 基础对话功能

---

### 第2周: 多文档管理

**Day 8-9: 后端数据库**
- 实现database.py (SQLite管理)
- 创建数据库表(documents, conversations, messages)
- 实现routers/documents.py
- 集成到pipeline.py保存文档元数据

**Day 10-11: 前端文档列表**
- 实现DocumentList.vue组件
- 实现documentStore
- 对接GET /api/documents
- 实现删除确认对话框

**Day 12-13: 文档切换**
- 实现切换文档逻辑
- 切换时清空聊天,加载新文档
- 保存lastDocumentId到localStorage
- 处理删除当前文档的边界情况

**Day 14: UI优化**
- 移动端响应式适配
- 文件大小格式化显示
- 切换动画效果
- 测试边界情况

**交付物**:
- ✅ 多文档上传和管理
- ✅ 文档列表展示和切换
- ✅ 删除文档功能
- ✅ 响应式布局

---

### 第3周: 对话历史

**Day 15-17: 后端历史记录**
- 实现routers/conversations.py
- 修改/api/chat保存消息到数据库
- 实现GET /api/conversations (分页,筛选)
- 实现GET /api/conversations/{id}/messages

**Day 18-19: 前端历史列表**
- 实现HistoryList.vue
- 实现historyStore
- 按时间分组(今天/昨天/本周/更早)
- 实现搜索历史功能
- 点击加载历史对话

**Day 20-21: 导出功能**
- 实现exportToMarkdown工具函数
- 添加导出按钮(对话区顶部)
- 导出当前对话为Markdown
- 测试导出格式

**交付物**:
- ✅ 对话历史保存
- ✅ 历史列表展示
- ✅ 加载历史对话
- ✅ 搜索和导出功能

---

### 第4周: 搜索功能和优化

**Day 22-24: 全文搜索**
- 实现routers/search.py
- 在向量库中实现文本搜索
- 实现高亮算法
- 前端实现搜索界面
- 结果高亮显示

**Day 25-26: 性能优化**
- 消息列表虚拟滚动
- 图片懒加载
- API请求防抖/节流
- 代码分割和懒加载
- Lighthouse性能测试

**Day 27-28: 测试和修复**
- 端到端测试(上传→对话→切换→历史)
- 边界情况测试
- Bug修复
- 用户体验优化
- 部署文档

**交付物**:
- ✅ 全文搜索功能
- ✅ 性能优化完成
- ✅ 完整测试
- ✅ 部署就绪

---

## 7. 风险和缓解措施

### 技术风险

**风险1: Vue学习曲线**
- **影响**: 可能延迟第1周进度
- **缓解**:
  - 先学习Vue3官方文档(1-2天)
  - 使用Element Plus减少UI开发时间
  - 参考成熟的Vue Chat UI项目

**风险2: 数据迁移**
- **影响**: 现有Qdrant数据可能需要重建索引
- **缓解**:
  - 不删除现有向量数据
  - 新数据库只存元数据和历史
  - 提供迁移脚本(如需要)

**风险3: API兼容性**
- **影响**: 前端改动可能破坏现有API
- **缓解**:
  - 保持后向兼容,新增字段而非修改
  - 逐步废弃旧端点
  - 版本控制(/api/v1, /api/v2)

### 功能风险

**风险4: 时间不足**
- **影响**: 4周内无法完成所有功能
- **缓解**:
  - 优先级明确(P0 > P1 > P2)
  - 第4周可缩减为只做核心功能
  - 搜索功能可放到后续迭代

**风险5: 用户体验不如预期**
- **影响**: UI改版后用户不适应
- **缓解**:
  - 第1周完成demo尽早反馈
  - 参考ChatGPT/Notion等成熟产品
  - 保留旧Streamlit版本作备份

---

## 附录

### 技术栈版本

- Vue: 3.4+
- TypeScript: 5.0+
- Vite: 5.0+
- Element Plus: 2.5+
- Pinia: 2.1+
- Axios: 1.6+
- Python: 3.11
- FastAPI: 0.109+
- SQLite: 3.40+

### 参考资源

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Element Plus](https://element-plus.org/zh-CN/)
- [Pinia 文档](https://pinia.vuejs.org/zh/)
- [FastAPI 文档](https://fastapi.tiangolo.com/zh/)

### 成功标准

- [ ] Vue前端可独立运行
- [ ] 所有原有功能正常工作
- [ ] 多文档管理功能完整
- [ ] 对话历史保存和加载
- [ ] 响应式布局(桌面+移动)
- [ ] 性能优于Streamlit版本
- [ ] 完整的测试覆盖
- [ ] 部署文档完善

---

**文档状态**: 已批准
**下一步**: 创建实施计划 (使用writing-plans skill)
