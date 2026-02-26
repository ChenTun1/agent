"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os

from backend.models_db import Base

# 数据库 URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/app.db')


class DatabaseManager:
    """数据库管理器 - 单例模式"""

    _instance = None
    _engine = None
    _SessionLocal = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._init_engine()

    def _init_engine(self):
        """初始化数据库引擎"""
        # SQLite 特殊配置
        if DATABASE_URL.startswith('sqlite'):
            self._engine = create_engine(
                DATABASE_URL,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self._engine = create_engine(DATABASE_URL, echo=False)

        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self._engine)
        print("[DB] Tables created successfully")

    def drop_tables(self):
        """删除所有表 (慎用!)"""
        Base.metadata.drop_all(bind=self._engine)
        print("[DB] Tables dropped")

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self._SessionLocal()

    @contextmanager
    def session_scope(self):
        """上下文管理器 - 自动提交和回滚"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 全局实例
db_manager = DatabaseManager()


# FastAPI 依赖注入
def get_db():
    """获取数据库会话 (用于 FastAPI Depends)"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()
