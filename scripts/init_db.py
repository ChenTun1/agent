"""初始化数据库脚本"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import db_manager


def main():
    print("Initializing database...")

    # 创建表
    db_manager.create_tables()

    print("✓ Database initialized successfully!")
    print(f"  Location: data/app.db")
    print(f"  Tables: documents, conversations, messages")


if __name__ == '__main__':
    main()
