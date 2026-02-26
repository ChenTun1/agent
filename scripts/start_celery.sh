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
