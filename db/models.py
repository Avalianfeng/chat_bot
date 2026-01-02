"""数据库模型定义"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    api_key = Column(String, nullable=True)  # 用户自己的 API Key（可选）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Session(Base):
    """会话模型"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, session_id='{self.session_id}', user_id={self.user_id})>"
