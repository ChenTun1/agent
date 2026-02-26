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
