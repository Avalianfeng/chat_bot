"""认证相关功能"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Cookie, Depends
from db import crud
from db.models import Session as SessionModel, User
from db.database import get_db


def generate_session_id() -> str:
    """生成随机的会话 ID"""
    return secrets.token_urlsafe(32)


def cleanup_expired_sessions(db: Session) -> int:
    """
    清理所有过期的会话
    
    Args:
        db: 数据库会话
        
    Returns:
        清理的会话数量
    """
    now = datetime.utcnow()
    expired_sessions = db.query(SessionModel).filter(SessionModel.expires_at <= now).all()
    count = len(expired_sessions)
    for session in expired_sessions:
        db.delete(session)
    db.commit()
    return count


def create_session(db: Session, user_id: int, expires_hours: int = 24, cleanup_old: bool = True) -> SessionModel:
    """
    创建新的会话
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        expires_hours: 过期时间（小时），默认 24 小时
        cleanup_old: 是否在创建新会话时清理过期会话，默认 True
        
    Returns:
        创建的会话对象
    """
    # 可选：清理过期会话（避免数据库累积太多过期记录）
    if cleanup_old:
        cleanup_expired_sessions(db)
    
    session_id = generate_session_id()
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    
    session = SessionModel(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def get_session_by_id(db: Session, session_id: str) -> Optional[SessionModel]:
    """
    根据会话 ID 获取会话
    
    Args:
        db: 数据库会话
        session_id: 会话 ID
        
    Returns:
        会话对象，如果不存在或已过期则返回 None
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    
    if not session:
        return None
    
    # 检查是否过期
    if datetime.utcnow() > session.expires_at:
        # 删除过期会话
        db.delete(session)
        db.commit()
        return None
    
    return session


def delete_session(db: Session, session_id: str) -> bool:
    """
    删除会话
    
    Args:
        db: 数据库会话
        session_id: 会话 ID
        
    Returns:
        是否删除成功
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False


def count_active_sessions_for_user(db: Session, user_id: int) -> int:
    """
    统计指定用户的活动会话数量（未过期的会话）
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        活动会话数量
    """
    now = datetime.utcnow()
    count = db.query(SessionModel).filter(
        SessionModel.user_id == user_id,
        SessionModel.expires_at > now
    ).count()
    return count


def delete_all_sessions_for_user(db: Session, user_id: int) -> int:
    """
    删除指定用户的所有会话
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        删除的会话数量
    """
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
    count = len(sessions)
    for session in sessions:
        db.delete(session)
    db.commit()
    return count


def get_current_user(
    session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """
    从 Cookie 中获取当前登录的用户（认证依赖）
    
    使用方式：
        from security.auth import get_current_user
        
        @app.get("/some_endpoint")
        async def some_endpoint(
            current_user: User = Depends(get_current_user)
        ):
            # current_user 就是当前登录的用户
            ...
    
    Args:
        session_id: 从 Cookie 中获取的会话 ID
        db: 数据库会话（通过依赖注入自动获取）
    
    Returns:
        当前用户对象
    
    Raises:
        HTTPException: 如果未登录或会话无效
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录，请先登录"
        )
    
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="会话已过期，请重新登录"
        )
    
    user = crud.get_user_by_id(db, session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return user
