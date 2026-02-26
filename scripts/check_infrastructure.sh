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
