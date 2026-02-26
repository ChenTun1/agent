"""
SQLAlchemy 数据库模型

用于存储文档元数据、对话历史等
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Document(Base):
    """文档表 - 存储 PDF 元数据"""
    __tablename__ = 'documents'

    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    page_count = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    meta_info = Column(Text)  # JSON 格式存储额外信息 (renamed from metadata to avoid conflict)

    # 关系
    conversations = relationship(
        'Conversation',
        back_populates='document',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"


class Conversation(Base):
    """对话表 - 存储对话会话"""
    __tablename__ = 'conversations'

    id = Column(String(36), primary_key=True)
    document_id = Column(
        String(36),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False
    )
    title = Column(String(255))  # 对话标题 (通常是第一个问题)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关系
    document = relationship('Document', back_populates='conversations')
    messages = relationship(
        'Message',
        back_populates='conversation',
        cascade='all, delete-orphan',
        order_by='Message.created_at'
    )

    # 索引
    __table_args__ = (
        Index('idx_conversation_document', 'document_id'),
        Index('idx_conversation_updated', 'updated_at'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """消息表 - 存储对话消息"""
    __tablename__ = 'messages'

    id = Column(String(36), primary_key=True)
    conversation_id = Column(
        String(36),
        ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON 格式存储来源
    cited_pages = Column(Text)  # JSON 格式存储引用页码
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    conversation = relationship('Conversation', back_populates='messages')

    # 索引
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
