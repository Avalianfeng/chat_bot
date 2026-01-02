"""数据库连接和会话管理"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base

# 数据库文件路径
# 使用相对路径，数据库文件将保存在项目根目录下的 data/data.db
# 如需使用绝对路径（如 /root/my_chat_bot/data.db），可以修改此处
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "data.db"
DATABASE_URL = f"sqlite:///{DB_FILE.absolute()}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
    echo=False  # 设置为 True 可以查看 SQL 语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    获取数据库会话（用于依赖注入）
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
