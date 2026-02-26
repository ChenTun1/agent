# 第1周:Vue前端基础框架搭建 - 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标**: 搭建Vue 3前端项目,实现基础布局和核心对话功能

**架构**: Vue 3 + TypeScript + Vite + Element Plus,通过Axios对接现有FastAPI后端

**技术栈**:
- 前端: Vue 3.4, TypeScript 5.0, Vite 5.0, Element Plus 2.5, Pinia 2.1, Axios 1.6
- 开发工具: ESLint, Prettier
- 后端: 对接现有FastAPI (无需修改)

**参考文档**: docs/plans/2026-02-26-vue-frontend-redesign.md

---

## Task 1: 初始化Vue项目

**文件**:
- Create: `frontend-vue/` (新目录)
- Create: `frontend-vue/package.json`
- Create: `frontend-vue/vite.config.ts`
- Create: `frontend-vue/tsconfig.json`

**Step 1: 创建Vite项目**

运行命令:
```bash
cd /Users/mlamp/Desktop/agent
npm create vite@latest frontend-vue -- --template vue-ts
```

预期输出:
```
✔ Project created successfully!
```

**Step 2: 安装依赖**

```bash
cd frontend-vue
npm install
npm install vue-router@4 pinia axios element-plus
npm install @vueuse/core
npm install -D sass @types/node
```

预期输出:
```
added XXX packages
```

**Step 3: 配置Vite代理和别名**

修改 `frontend-vue/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Step 4: 配置TypeScript路径别名**

修改 `frontend-vue/tsconfig.json`,在 `compilerOptions` 中添加:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Step 5: 验证项目可运行**

```bash
npm run dev
```

预期输出:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

访问 http://localhost:5173 应该看到Vue默认页面。

**Step 6: 提交**

```bash
git add frontend-vue
git commit -m "feat: initialize Vue 3 project with Vite and TypeScript

- Setup Vite project with Vue 3 template
- Install vue-router, pinia, element-plus, axios
- Configure API proxy to backend
- Configure TypeScript path alias"
```

---

## Task 2: 配置Element Plus和全局样式

**文件**:
- Modify: `frontend-vue/src/main.ts`
- Create: `frontend-vue/src/styles/variables.scss`
- Create: `frontend-vue/src/styles/global.scss`

**Step 1: 在main.ts中引入Element Plus**

修改 `frontend-vue/src/main.ts`:

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import './styles/global.scss'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
```

**Step 2: 创建CSS变量文件**

创建 `frontend-vue/src/styles/variables.scss`:

```scss
// 颜色系统
$primary: #409EFF;
$bg-main: #FFFFFF;
$bg-secondary: #F5F7FA;
$text-primary: #303133;
$text-secondary: #909399;
$border: #DCDFE6;

// 间距系统
$spacing-xs: 8px;
$spacing-sm: 12px;
$spacing-md: 16px;
$spacing-lg: 24px;
$spacing-xl: 32px;

// 圆角
$radius-sm: 8px;
$radius-md: 12px;

// 排版
$font-size-base: 14px;
$font-size-large: 18px;
$font-size-small: 12px;
$line-height: 1.6;
```

**Step 3: 创建全局样式**

创建 `frontend-vue/src/styles/global.scss`:

```scss
@import './variables.scss';

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: $font-size-base;
  line-height: $line-height;
  color: $text-primary;
  background-color: $bg-main;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  height: 100vh;
  overflow: hidden;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;

  &:hover {
    background-color: rgba(0, 0, 0, 0.3);
  }
}
```

**Step 4: 测试样式生效**

```bash
npm run dev
```

检查浏览器,默认页面应该使用新的字体和样式。

**Step 5: 提交**

```bash
git add frontend-vue/src/main.ts frontend-vue/src/styles
git commit -m "feat: setup Element Plus and global styles

- Import Element Plus with Chinese locale
- Add CSS variables for design system
- Add global styles and scrollbar customization"
```

---

## Task 3: 创建TypeScript类型定义

**文件**:
- Create: `frontend-vue/src/types/index.ts`
- Create: `frontend-vue/src/types/api.ts`

**Step 1: 创建基础类型**

创建 `frontend-vue/src/types/index.ts`:

```typescript
// 文档类型
export interface Document {
  id: string
  filename: string
  pageCount: number
  uploadTime: string
  size: number
}

// 消息类型
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Source[]
  documentId: string
}

// 来源类型
export interface Source {
  page: number
  text: string
}

// 对话类型
export interface Conversation {
  id: string
  documentId: string
  documentName: string
  title: string
  lastMessageTime: string
  messageCount: number
}
```

**Step 2: 创建API响应类型**

创建 `frontend-vue/src/types/api.ts`:

```typescript
// 通用API响应
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  message?: string
  code?: string
}

// 上传响应
export interface UploadResponse {
  status: string
  pdf_id: string
  filename: string
  page_count: number
}

// 对话响应
export interface ChatResponse {
  answer: string
  cited_pages: number[]
  sources: Array<{
    page: number
    text: string
  }>
  message_id?: string
  conversation_id?: string
}

// 文档列表响应
export interface DocumentListResponse {
  documents: Array<{
    id: string
    filename: string
    page_count: number
    upload_time: string
    file_size: number
  }>
}
```

**Step 3: 验证类型文件无错误**

```bash
npx tsc --noEmit
```

预期输出: 无错误信息

**Step 4: 提交**

```bash
git add frontend-vue/src/types
git commit -m "feat: add TypeScript type definitions

- Add Document, Message, Source types
- Add Conversation type for history
- Add API response types"
```

---

## Task 4: 配置Axios和API客户端

**文件**:
- Create: `frontend-vue/src/api/client.ts`
- Create: `frontend-vue/src/api/document.ts`
- Create: `frontend-vue/src/api/chat.ts`

**Step 1: 创建Axios客户端**

创建 `frontend-vue/src/api/client.ts`:

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/api'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.message ||
                   error.response?.data?.detail ||
                   error.message ||
                   '请求失败'

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api
```

**Step 2: 创建文档API**

创建 `frontend-vue/src/api/document.ts`:

```typescript
import api from './client'
import type { UploadResponse, DocumentListResponse } from '@/types/api'

/**
 * 上传PDF文档
 */
export function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取文档列表
 */
export function getDocuments(): Promise<DocumentListResponse> {
  return api.get('/documents')
}

/**
 * 删除文档
 */
export function deleteDocument(documentId: string): Promise<{ status: string }> {
  return api.delete(`/documents/${documentId}`)
}
```

**Step 3: 创建对话API**

创建 `frontend-vue/src/api/chat.ts`:

```typescript
import api from './client'
import type { ChatResponse } from '@/types/api'

/**
 * 发送消息
 */
export function sendMessage(data: {
  pdf_id: string
  question: string
  conversation_id?: string
}): Promise<ChatResponse> {
  return api.post('/chat', data)
}
```

**Step 4: 提交**

```bash
git add frontend-vue/src/api
git commit -m "feat: setup Axios client and API modules

- Create Axios instance with interceptors
- Add request/response error handling
- Create document API (upload, list, delete)
- Create chat API (sendMessage)"
```

---

## Task 5: 配置Vue Router和Pinia

**文件**:
- Create: `frontend-vue/src/router/index.ts`
- Create: `frontend-vue/src/stores/index.ts`
- Modify: `frontend-vue/src/main.ts`

**Step 1: 创建路由配置**

创建 `frontend-vue/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**Step 2: 创建Pinia store**

创建 `frontend-vue/src/stores/index.ts`:

```typescript
import { createPinia } from 'pinia'

export const pinia = createPinia()
```

**Step 3: 在main.ts中注册**

修改 `frontend-vue/src/main.ts`:

```typescript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import './styles/global.scss'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'

const app = createApp(App)
app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.use(pinia)
app.mount('#app')
```

**Step 4: 创建临时Home视图**

创建 `frontend-vue/src/views/Home.vue`:

```vue
<template>
  <div class="home">
    <h1>AI PDF 问答系统</h1>
    <p>Vue 3 前端正在开发中...</p>
  </div>
</template>

<script setup lang="ts">
//
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

h1 {
  font-size: 32px;
  margin-bottom: 16px;
}
</style>
```

**Step 5: 修改App.vue使用路由**

修改 `frontend-vue/src/App.vue`:

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
//
</script>
```

**Step 6: 测试路由工作**

```bash
npm run dev
```

访问 http://localhost:5173 应该看到"AI PDF 问答系统"页面。

**Step 7: 提交**

```bash
git add frontend-vue/src/router frontend-vue/src/stores frontend-vue/src/views frontend-vue/src/main.ts frontend-vue/src/App.vue
git commit -m "feat: setup Vue Router and Pinia

- Create router with home route
- Setup Pinia store
- Register plugins in main.ts
- Create temporary Home view for testing"
```

---

## Task 6: 创建主布局组件

**文件**:
- Create: `frontend-vue/src/components/layout/Layout.vue`
- Create: `frontend-vue/src/components/layout/Navbar.vue`
- Create: `frontend-vue/src/components/layout/Sidebar.vue`
- Modify: `frontend-vue/src/views/Home.vue`

**Step 1: 创建Navbar组件**

创建 `frontend-vue/src/components/layout/Navbar.vue`:

```vue
<template>
  <div class="navbar">
    <div class="logo">
      <span class="logo-icon">📄</span>
      <span class="logo-text">AI PDF 问答</span>
    </div>
    <div class="navbar-actions">
      <!-- 预留设置和主题切换位置 -->
    </div>
  </div>
</template>

<script setup lang="ts">
//
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.navbar {
  height: 60px;
  background-color: $bg-main;
  border-bottom: 1px solid $border;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-lg;
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-large;
  font-weight: 600;
  color: $text-primary;
}

.logo-icon {
  font-size: 24px;
}
</style>
```

**Step 2: 创建Sidebar组件骨架**

创建 `frontend-vue/src/components/layout/Sidebar.vue`:

```vue
<template>
  <div class="sidebar">
    <div class="sidebar-section">
      <div class="section-title">文档列表</div>
      <div class="section-content">
        <!-- 文档列表将在后续任务实现 -->
        <p class="placeholder">暂无文档</p>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="section-title">历史记录</div>
      <div class="section-content">
        <!-- 历史记录将在后续任务实现 -->
        <p class="placeholder">暂无历史</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
//
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.sidebar {
  width: 260px;
  height: 100%;
  background-color: $bg-secondary;
  border-right: 1px solid $border;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-section {
  padding: $spacing-md;
  border-bottom: 1px solid $border;
}

.section-title {
  font-size: $font-size-small;
  font-weight: 600;
  color: $text-secondary;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: $spacing-sm;
}

.section-content {
  .placeholder {
    font-size: $font-size-small;
    color: $text-secondary;
    text-align: center;
    padding: $spacing-lg 0;
  }
}
</style>
```

**Step 3: 创建Layout主布局**

创建 `frontend-vue/src/components/layout/Layout.vue`:

```vue
<template>
  <div class="layout">
    <Navbar />
    <div class="layout-body">
      <Sidebar />
      <div class="layout-main">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Navbar from './Navbar.vue'
import Sidebar from './Sidebar.vue'
</script>

<style scoped lang="scss">
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  overflow-y: auto;
  background-color: #fff;
}
</style>
```

**Step 4: 在Home视图中使用Layout**

修改 `frontend-vue/src/views/Home.vue`:

```vue
<template>
  <Layout>
    <div class="home-content">
      <h1>欢迎使用AI PDF问答系统</h1>
      <p>请上传PDF文档开始对话</p>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/layout/Layout.vue'
</script>

<style scoped lang="scss">
.home-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;

  h1 {
    font-size: 24px;
    margin-bottom: 16px;
  }

  p {
    color: #909399;
  }
}
</style>
```

**Step 5: 测试布局**

```bash
npm run dev
```

应该看到带导航栏和侧边栏的完整布局。

**Step 6: 提交**

```bash
git add frontend-vue/src/components/layout frontend-vue/src/views/Home.vue
git commit -m "feat: create main layout components

- Add Navbar with logo
- Add Sidebar skeleton (documents and history sections)
- Create Layout component with flex layout
- Update Home view to use Layout"
```

---

## Task 7: 实现文件上传功能

**文件**:
- Create: `frontend-vue/src/components/upload/FileUpload.vue`
- Create: `frontend-vue/src/stores/document.ts`
- Modify: `frontend-vue/src/views/Home.vue`

**Step 1: 创建documentStore**

创建 `frontend-vue/src/stores/document.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Document } from '@/types'
import * as documentApi from '@/api/document'

export const useDocumentStore = defineStore('document', () => {
  // State
  const documents = ref<Document[]>([])
  const currentDocumentId = ref<string | null>(null)
  const uploading = ref(false)

  // Getters
  const currentDocument = computed(() =>
    documents.value.find(d => d.id === currentDocumentId.value) || null
  )

  const documentCount = computed(() => documents.value.length)

  // Actions
  async function uploadDocument(file: File) {
    uploading.value = true
    try {
      const res = await documentApi.uploadDocument(file)

      const newDoc: Document = {
        id: res.pdf_id,
        filename: res.filename,
        pageCount: res.page_count,
        uploadTime: new Date().toISOString(),
        size: file.size
      }

      documents.value.unshift(newDoc)
      setCurrentDocument(newDoc.id)

      return newDoc
    } finally {
      uploading.value = false
    }
  }

  function setCurrentDocument(id: string) {
    currentDocumentId.value = id
    localStorage.setItem('lastDocumentId', id)
  }

  async function deleteDocument(id: string) {
    await documentApi.deleteDocument(id)
    documents.value = documents.value.filter(d => d.id !== id)

    if (currentDocumentId.value === id) {
      currentDocumentId.value = documents.value[0]?.id || null
    }
  }

  return {
    documents,
    currentDocumentId,
    uploading,
    currentDocument,
    documentCount,
    uploadDocument,
    setCurrentDocument,
    deleteDocument
  }
})
```

**Step 2: 创建FileUpload组件**

创建 `frontend-vue/src/components/upload/FileUpload.vue`:

```vue
<template>
  <div class="file-upload">
    <el-upload
      drag
      :show-file-list="false"
      :before-upload="handleBeforeUpload"
      :http-request="handleUpload"
      :disabled="uploading"
      accept=".pdf"
    >
      <div class="upload-content">
        <el-icon class="upload-icon" :size="50">
          <Upload />
        </el-icon>
        <div class="upload-text">
          <p class="primary">拖拽PDF文件到此处 或 点击上传</p>
          <p class="secondary">支持最大 10MB 的 PDF 文件</p>
        </div>
      </div>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useDocumentStore } from '@/stores/document'
import { storeToRefs } from 'pinia'

const documentStore = useDocumentStore()
const { uploading } = storeToRefs(documentStore)

function handleBeforeUpload(file: File) {
  // 验证文件类型
  if (!file.name.endsWith('.pdf')) {
    ElMessage.error('只支持PDF文件')
    return false
  }

  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }

  return true
}

async function handleUpload({ file }: { file: File }) {
  try {
    await documentStore.uploadDocument(file)
    ElMessage.success('文档上传成功')
  } catch (error) {
    // 错误已在API拦截器中处理
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.file-upload {
  width: 100%;
  max-width: 500px;

  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    width: 100%;
    border: 2px dashed $border;
    border-radius: $radius-md;
    padding: $spacing-xl $spacing-lg;
    transition: all 0.3s ease;

    &:hover {
      border-color: $primary;
    }
  }
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-md;
}

.upload-icon {
  color: $primary;
}

.upload-text {
  text-align: center;

  .primary {
    font-size: $font-size-base;
    color: $text-primary;
    margin-bottom: $spacing-xs;
  }

  .secondary {
    font-size: $font-size-small;
    color: $text-secondary;
  }
}
</style>
```

**Step 3: 在Home视图中使用**

修改 `frontend-vue/src/views/Home.vue`:

```vue
<template>
  <Layout>
    <div class="home-content">
      <div v-if="!currentDocument" class="welcome-screen">
        <h1>AI PDF 问答</h1>
        <p>上传 PDF 文档开始对话</p>
        <FileUpload />
      </div>
      <div v-else class="chat-view">
        <p>文档已加载: {{ currentDocument.filename }}</p>
        <!-- 对话界面将在下一个任务实现 -->
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import Layout from '@/components/layout/Layout.vue'
import FileUpload from '@/components/upload/FileUpload.vue'
import { useDocumentStore } from '@/stores/document'

const documentStore = useDocumentStore()
const { currentDocument } = storeToRefs(documentStore)
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.home-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-lg;
  max-width: 600px;

  h1 {
    font-size: 32px;
    font-weight: 600;
  }

  p {
    font-size: $font-size-base;
    color: $text-secondary;
    margin-bottom: $spacing-md;
  }
}

.chat-view {
  width: 100%;
  padding: $spacing-lg;
}
</style>
```

**Step 4: 测试上传功能**

```bash
# 确保后端正在运行
cd /Users/mlamp/Desktop/agent
./start.sh

# 在另一个终端运行前端
cd frontend-vue
npm run dev
```

访问 http://localhost:5173,测试上传PDF文件。

**Step 5: 提交**

```bash
git add frontend-vue/src/stores/document.ts frontend-vue/src/components/upload frontend-vue/src/views/Home.vue
git commit -m "feat: implement PDF file upload

- Create documentStore with Pinia
- Add uploadDocument, setCurrentDocument actions
- Create FileUpload component with drag & drop
- Add file validation (type and size)
- Update Home view to show upload interface"
```

---

## Task 8: 实现对话功能

**文件**:
- Create: `frontend-vue/src/components/chat/ChatArea.vue`
- Create: `frontend-vue/src/components/chat/MessageList.vue`
- Create: `frontend-vue/src/components/chat/Message.vue`
- Create: `frontend-vue/src/components/chat/InputBox.vue`
- Create: `frontend-vue/src/stores/chat.ts`
- Modify: `frontend-vue/src/views/Home.vue`

**Step 1: 创建chatStore**

创建 `frontend-vue/src/stores/chat.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message } from '@/types'
import * as chatApi from '@/api/chat'
import { useDocumentStore } from './document'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const messageCount = computed(() => messages.value.length)

  // Actions
  async function sendMessage(question: string) {
    const documentStore = useDocumentStore()
    const currentDocId = documentStore.currentDocumentId

    if (!currentDocId) {
      throw new Error('No document selected')
    }

    // 添加用户消息
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
      documentId: currentDocId
    }
    messages.value.push(userMessage)

    // 调用API
    isLoading.value = true
    error.value = null

    try {
      const res = await chatApi.sendMessage({
        pdf_id: currentDocId,
        question
      })

      // 添加AI消息
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        timestamp: new Date().toISOString(),
        sources: res.sources,
        documentId: currentDocId
      }
      messages.value.push(assistantMessage)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
    } finally {
      isLoading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    isLoading,
    error,
    messageCount,
    sendMessage,
    clearMessages
  }
})
```

**Step 2: 创建Message组件**

创建 `frontend-vue/src/components/chat/Message.vue`:

```vue
<template>
  <div :class="['message', message.role]">
    <div class="message-avatar">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </div>
    <div class="message-content">
      <div class="message-text">{{ message.content }}</div>

      <div v-if="message.sources && message.sources.length" class="message-sources">
        <el-collapse>
          <el-collapse-item title="📖 查看来源" name="sources">
            <div v-for="(source, idx) in message.sources" :key="idx" class="source-item">
              <div class="source-page">第 {{ source.page }} 页</div>
              <div class="source-text">{{ source.text.substring(0, 150) }}...</div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message as MessageType } from '@/types'

defineProps<{
  message: MessageType
}>()
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.message {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md 0;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      align-items: flex-end;
    }

    .message-text {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
    }
  }
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  max-width: 70%;
}

.message-text {
  background: white;
  border: 1px solid $border;
  border-radius: $radius-md;
  padding: $spacing-md;
  line-height: $line-height;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-sources {
  font-size: $font-size-small;

  :deep(.el-collapse) {
    border: none;
  }

  :deep(.el-collapse-item__header) {
    background: transparent;
    border: none;
    color: $primary;
    font-weight: 500;
  }

  :deep(.el-collapse-item__wrap) {
    background: transparent;
    border: none;
  }
}

.source-item {
  background: #faf5ff;
  border-left: 3px solid $primary;
  border-radius: $radius-sm;
  padding: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.source-page {
  font-weight: 600;
  color: $primary;
  font-size: $font-size-small;
  margin-bottom: $spacing-xs;
}

.source-text {
  color: $text-secondary;
  font-size: $font-size-small;
  line-height: 1.5;
}
</style>
```

**Step 3: 创建MessageList组件**

创建 `frontend-vue/src/components/chat/MessageList.vue`:

```vue
<template>
  <div class="message-list" ref="listRef">
    <Message
      v-for="message in messages"
      :key="message.id"
      :message="message"
    />

    <div v-if="isLoading" class="loading-indicator">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>AI正在思考中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import Message from './Message.vue'
import type { Message as MessageType } from '@/types'

const props = defineProps<{
  messages: MessageType[]
  isLoading: boolean
}>()

const listRef = ref<HTMLElement>()

// 自动滚动到底部
watch(() => props.messages.length, async () => {
  await nextTick()
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight
  }
})

watch(() => props.isLoading, async (loading) => {
  if (loading) {
    await nextTick()
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-lg;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  color: $text-secondary;
  padding: $spacing-md;

  .el-icon {
    font-size: 18px;
  }
}
</style>
```

**Step 4: 创建InputBox组件**

创建 `frontend-vue/src/components/chat/InputBox.vue`:

```vue
<template>
  <div class="input-box">
    <el-input
      v-model="question"
      type="textarea"
      :rows="3"
      :autosize="{ minRows: 1, maxRows: 4 }"
      placeholder="输入问题... (Enter发送, Shift+Enter换行)"
      :disabled="disabled"
      @keydown.enter.exact.prevent="handleSend"
    />
    <el-button
      type="primary"
      :icon="Promotion"
      :loading="disabled"
      :disabled="!question.trim()"
      @click="handleSend"
    >
      发送
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'

const props = defineProps<{
  disabled?: boolean
}>()

const emit = defineEmits<{
  send: [question: string]
}>()

const question = ref('')

function handleSend() {
  if (!question.value.trim() || props.disabled) return

  emit('send', question.value.trim())
  question.value = ''
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.input-box {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md $spacing-lg;
  border-top: 1px solid $border;
  background: white;

  .el-input {
    flex: 1;
  }

  :deep(.el-textarea__inner) {
    border-radius: $radius-sm;
    resize: none;
  }
}
</style>
```

**Step 5: 创建ChatArea组件**

创建 `frontend-vue/src/components/chat/ChatArea.vue`:

```vue
<template>
  <div class="chat-area">
    <MessageList :messages="messages" :is-loading="isLoading" />
    <InputBox :disabled="isLoading" @send="handleSend" />
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import MessageList from './MessageList.vue'
import InputBox from './InputBox.vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const { messages, isLoading } = storeToRefs(chatStore)

async function handleSend(question: string) {
  await chatStore.sendMessage(question)
}
</script>

<style scoped lang="scss">
.chat-area {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
```

**Step 6: 在Home中使用ChatArea**

修改 `frontend-vue/src/views/Home.vue`:

```vue
<template>
  <Layout>
    <div class="home-content">
      <div v-if="!currentDocument" class="welcome-screen">
        <h1>AI PDF 问答</h1>
        <p>上传 PDF 文档开始对话</p>
        <FileUpload />
      </div>
      <ChatArea v-else />
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import Layout from '@/components/layout/Layout.vue'
import FileUpload from '@/components/upload/FileUpload.vue'
import ChatArea from '@/components/chat/ChatArea.vue'
import { useDocumentStore } from '@/stores/document'

const documentStore = useDocumentStore()
const { currentDocument } = storeToRefs(documentStore)
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.home-content {
  height: 100%;

  .welcome-screen {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: $spacing-lg;
    max-width: 600px;
    margin: 0 auto;

    h1 {
      font-size: 32px;
      font-weight: 600;
    }

    p {
      font-size: $font-size-base;
      color: $text-secondary;
      margin-bottom: $spacing-md;
    }
  }
}
</style>
```

**Step 7: 测试对话功能**

```bash
npm run dev
```

上传PDF后测试发送问题和查看回答。

**Step 8: 提交**

```bash
git add frontend-vue/src/stores/chat.ts frontend-vue/src/components/chat frontend-vue/src/views/Home.vue
git commit -m "feat: implement chat interface

- Create chatStore with sendMessage action
- Create Message component with user/assistant styles
- Create MessageList with auto-scroll
- Create InputBox with Enter to send
- Create ChatArea to compose chat UI
- Update Home view to show chat when document loaded"
```

---

## Task 9: 添加文档切换时清空聊天

**文件**:
- Modify: `frontend-vue/src/stores/document.ts`

**Step 1: 在setCurrentDocument中清空聊天**

修改 `frontend-vue/src/stores/document.ts`,在 `setCurrentDocument` 函数中:

```typescript
import { useChatStore } from './chat'

// ... 在 defineStore 内部

function setCurrentDocument(id: string) {
  currentDocumentId.value = id
  localStorage.setItem('lastDocumentId', id)

  // 切换文档时清空聊天记录
  const chatStore = useChatStore()
  chatStore.clearMessages()
}
```

**Step 2: 测试切换文档**

上传两个PDF,切换时聊天记录应该清空。

**Step 3: 提交**

```bash
git add frontend-vue/src/stores/document.ts
git commit -m "feat: clear chat when switching documents

- Call chatStore.clearMessages when setCurrentDocument
- Ensures clean slate for each document"
```

---

## Task 10: 添加README和第1周总结

**文件**:
- Create: `frontend-vue/README.md`

**Step 1: 创建前端README**

创建 `frontend-vue/README.md`:

```markdown
# AI PDF 问答系统 - Vue 3 前端

基于 Vue 3 + TypeScript + Element Plus 的现代化前端应用。

## 技术栈

- **框架**: Vue 3.4 (Composition API)
- **语言**: TypeScript 5.0
- **构建工具**: Vite 5.0
- **UI库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4
- **HTTP客户端**: Axios 1.6

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 项目结构

```
src/
├── api/           # API调用模块
├── components/    # Vue组件
│   ├── layout/    # 布局组件
│   ├── chat/      # 对话组件
│   └── upload/    # 上传组件
├── stores/        # Pinia状态管理
├── types/         # TypeScript类型定义
├── views/         # 页面视图
├── styles/        # 全局样式
├── router/        # 路由配置
└── main.ts        # 应用入口
```

## 已完成功能 (第1周)

- ✅ Vue 3 + TypeScript 项目初始化
- ✅ Element Plus UI库集成
- ✅ 主布局(导航栏 + 侧边栏)
- ✅ PDF文件上传(拖拽上传)
- ✅ 对话界面(消息列表 + 输入框)
- ✅ 对接后端API(/upload, /chat)
- ✅ 状态管理(documentStore, chatStore)

## 下一步计划 (第2周)

- [ ] 多文档管理
- [ ] 文档列表展示
- [ ] 文档切换功能
- [ ] 后端数据库集成

## 开发注意事项

- 后端需要在 http://localhost:8000 运行
- 使用 `/api` 前缀进行API请求(已配置Vite代理)
- 所有API错误会通过Element Plus的Message组件显示
```

**Step 2: 提交**

```bash
git add frontend-vue/README.md
git commit -m "docs: add frontend README

- Document tech stack
- Add development instructions
- List completed features for Week 1
- Add project structure overview"
```

**Step 3: 创建第1周总结**

```bash
git log --oneline --since="7 days ago"
```

验证所有提交已完成。

---

## 第1周完成总结

**已完成任务**:

1. ✅ Vue 3 + TypeScript + Vite 项目初始化
2. ✅ Element Plus 和全局样式配置
3. ✅ TypeScript类型定义
4. ✅ Axios客户端和API模块
5. ✅ Vue Router和Pinia配置
6. ✅ 主布局组件(Navbar, Sidebar, Layout)
7. ✅ PDF文件上传功能
8. ✅ 对话功能(MessageList, Message, InputBox, ChatArea)
9. ✅ 文档切换时清空聊天
10. ✅ README文档

**功能验证清单**:

- [ ] 访问 http://localhost:5173 看到欢迎页面
- [ ] 上传PDF文件成功
- [ ] 发送问题并收到AI回答
- [ ] 查看来源信息(展开折叠)
- [ ] 消息自动滚动到底部
- [ ] Enter发送,Shift+Enter换行
- [ ] 文件类型和大小验证
- [ ] 错误提示正常显示

**代码规范**:

- [x] 使用TypeScript严格模式
- [x] 使用Composition API
- [x] 使用SCSS变量系统
- [x] API错误统一处理
- [x] 组件职责单一
- [x] 频繁提交(每个任务一次)

**下周准备**:

1. 后端需要实现 `GET /api/documents` 接口
2. 后端需要添加SQLite数据库支持
3. 前端将实现文档列表和切换功能

---

## 执行方式选择

计划已完成并保存到 `docs/plans/2026-02-26-week1-vue-setup-implementation.md`。

**两种执行方式:**

**1. Subagent-Driven (当前会话)** - 我在这个会话中为每个任务分派新的subagent,任务间进行代码审查,快速迭代

**2. Parallel Session (独立会话)** - 你打开新会话使用executing-plans skill,批量执行任务并在检查点审查

你想用哪种方式执行这个计划?
