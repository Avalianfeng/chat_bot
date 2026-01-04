"""密码加密和验证"""
from passlib.context import CryptContext

# 创建密码上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt 限制：密码最长 72 字节
BCRYPT_MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
        
    Note:
        bcrypt 限制密码最长 72 字节，超长密码会被截断
    """
    # 如果密码超过 72 字节，截断它（bcrypt 的限制）
    if len(password.encode('utf-8')) > BCRYPT_MAX_PASSWORD_LENGTH:
        password = password[:BCRYPT_MAX_PASSWORD_LENGTH]
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
        bcrypt 限制密码最长 72 字节，超长密码会被截断（与 hash_password 保持一致）
    """
    # 如果密码超过 72 字节，截断它（必须与 hash_password 保持一致）
    if len(plain_password.encode('utf-8')) > BCRYPT_MAX_PASSWORD_LENGTH:
        plain_password = plain_password[:BCRYPT_MAX_PASSWORD_LENGTH]
    return pwd_context.verify(plain_password, hashed_password)
