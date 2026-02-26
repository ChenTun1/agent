# Vue 前端设置说明

## 当前状态

✅ Vite项目已创建: `frontend-vue/`
⏳ 依赖正在后台安装中

## 快速完成设置

由于token限制,请按以下步骤手动完成剩余配置:

### 1. 等待依赖安装完成

```bash
cd ~/.config/superpowers/worktrees/agent/week1-vue-setup/frontend-vue

# 检查安装状态
ps aux | grep "npm install"

# 如果未完成,手动运行
npm install
npm install vue-router@4 pinia axios element-plus @vueuse/core
npm install -D sass @types/node
```

### 2. 配置文件

执行以下命令创建配置文件:

```bash
cd ~/.config/superpowers/worktrees/agent/week1-vue-setup

# 下载配置脚本
curl -o setup-vue.sh https://gist.githubusercontent.com/你的gist/setup-vue.sh
chmod +x setup-vue.sh
./setup-vue.sh
```

或者手动按照计划文档执行:
- 参考: `docs/plans/2026-02-26-week1-vue-setup-implementation.md`
- 从 Task 1 Step 3 开始

### 3. 关键修改

**vite.config.ts** - 添加代理和别名:
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

**tsconfig.json** - 添加路径别名:
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

### 4. 创建必需目录结构

```bash
cd frontend-vue/src
mkdir -p api components/{layout,chat,upload} stores types views styles
```

### 5. 启动开发服务器

```bash
npm run dev
```

应该在 http://localhost:5173 看到Vue默认页面

## 下一步

完成基础设置后,按照计划文档逐步实现:
1. Element Plus和样式
2. TypeScript类型
3. API客户端
4. Router和Pinia
5. 布局组件
6. 文件上传
7. 对话功能

## 自动化选项

如果您希望自动完成,可以:
1. 新开一个 Claude 会话
2. 使用 `/superpowers:execute-plan` 命令
3. 指向计划文档: `docs/plans/2026-02-26-week1-vue-setup-implementation.md`

这样会有新的 token 预算来完成所有任务。
