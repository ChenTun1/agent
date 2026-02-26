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
