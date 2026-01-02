"""数据库 CRUD 操作"""
from sqlalchemy.orm import Session
from typing import List, Optional
from db.models import User
from security.password import hash_password


def create_user(
    db: Session,
    username: str,
    password: str,
    api_key: Optional[str] = None
) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 明文密码（会被加密）
        api_key: 可选的 API Key
        
    Returns:
        创建的用户对象
        
    Raises:
        ValueError: 如果用户名已存在
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"用户名 '{username}' 已存在")
    
    # 加密密码
    password_hash = hash_password(password)
    
    # 创建用户
    user = User(
        username=username,
        password_hash=password_hash,
        api_key=api_key
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        
    Returns:
        用户对象，如果不存在则返回 None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        用户对象，如果不存在则返回 None
    """
    return db.query(User).filter(User.username == username).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    获取所有用户列表
    
    Args:
        db: 数据库会话
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        用户列表
    """
    return db.query(User).offset(skip).limit(limit).all()


def update_user_api_key(db: Session, user_id: int, api_key: Optional[str]) -> Optional[User]:
    """
    更新用户的 API Key
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        api_key: 新的 API Key
        
    Returns:
        更新后的用户对象，如果用户不存在则返回 None
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.api_key = api_key
    db.commit()
    db.refresh(user)
    
    return user
