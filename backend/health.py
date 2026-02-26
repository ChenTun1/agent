"""健康检查工具"""
import redis
from qdrant_client import QdrantClient
from sqlalchemy import text
import os

from backend.database import db_manager


class HealthChecker:
    """基础设施健康检查器"""

    def check_redis(self) -> dict:
        """检查 Redis 连接"""
        try:
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0))
            )
            r.ping()
            info = r.info()

            return {
                'status': 'healthy',
                'version': info.get('redis_version'),
                'memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients')
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_qdrant(self) -> dict:
        """检查 Qdrant 连接"""
        try:
            client = QdrantClient(
                host=os.getenv('QDRANT_HOST', 'localhost'),
                port=int(os.getenv('QDRANT_PORT', 6333))
            )
            collections = client.get_collections()

            return {
                'status': 'healthy',
                'collections': len(collections.collections)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_database(self) -> dict:
        """检查 SQLite 数据库"""
        try:
            with db_manager.session_scope() as session:
                # 测试查询
                result = session.execute(text("SELECT 1"))
                result.scalar()

                # 检查表
                tables = session.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )).fetchall()

                return {
                    'status': 'healthy',
                    'tables': [t[0] for t in tables]
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    def check_all(self) -> dict:
        """执行所有健康检查"""
        return {
            'redis': self.check_redis(),
            'qdrant': self.check_qdrant(),
            'database': self.check_database()
        }


# 快捷函数
def health_check() -> dict:
    """执行健康检查"""
    checker = HealthChecker()
    return checker.check_all()
