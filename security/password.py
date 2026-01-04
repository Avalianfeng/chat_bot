"""密码加密和验证"""
from passlib.context import CryptContext

# 创建密码上下文，使用 argon2 算法
# argon2 是当前最安全的密码哈希算法，获得密码哈希竞赛冠军
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
        
    Note:
        使用 argon2 算法，无密码长度限制（比 bcrypt 更安全）
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码哈希
        
    Returns:
        密码是否正确
        
    Note:
        使用 argon2 算法进行验证
    """
    return pwd_context.verify(plain_password, hashed_password)
