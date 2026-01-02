from db.database import init_db, SessionLocal
from db import crud

# 初始化数据库
init_db()

# 创建用户
db = SessionLocal()
try:
    user = crud.create_user(
        db=db,
        username="admin_1",
        password="admin_1_123",
        api_key=None
    )
    print(f"用户创建成功: {user.username}")
finally:
    db.close()