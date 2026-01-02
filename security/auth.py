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


def create_session(db: Session, user_id: int, expires_hours: int = 24) -> SessionModel:
    """
    创建新的会话
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        expires_hours: 过期时间（小时），默认 24 小时
        
    Returns:
        创建的会话对象
    """
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
