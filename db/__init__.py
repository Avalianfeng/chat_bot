"""数据库模块

提供数据库模型、连接管理和CRUD操作。
"""

from db.models import Base, User, Session
from db.database import init_db, get_db, SessionLocal, engine, DATABASE_URL

__all__ = [
    # 模型
    'Base',
    'User',
    'Session',
    # 数据库连接
    'init_db',
    'get_db',
    'SessionLocal',
    'engine',
    'DATABASE_URL',
]

# 延迟导入 crud 模块，避免循环导入
# 使用时：from db import crud 或 from db.crud import create_user
