#!/bin/bash

# AI PDF Chat - Frontend启动脚本
# 用法: ./run_frontend.sh

echo "🚀 启动 AI PDF Chat 前端..."
echo ""

# 检查Python
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装,请先安装Python 3.11+"
    exit 1
fi

# 检查Streamlit
if ! python -c "import streamlit" &> /dev/null; then
    echo "⚠️  Streamlit未安装,正在安装依赖..."
    pip install -r requirements.txt
fi

# 设置环境变量(可选)
export BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "📊 配置信息:"
echo "   Backend URL: $BACKEND_URL"
echo ""

# 检查后端是否运行
echo "🔍 检查后端服务..."
if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  警告: 后端服务未运行 ($BACKEND_URL)"
    echo "   请先启动后端: uvicorn backend.main:app --reload"
    echo ""
    read -p "是否继续启动前端? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🎨 启动Streamlit前端..."
echo "   访问: http://localhost:8501"
echo ""

# 启动Streamlit
streamlit run frontend/app.py
