from db.database import init_db, SessionLocal
from db import crud
from getpass import getpass  # 用于隐藏密码输入

def create_user_safe():
    """
    创建用户的安全版本：
    - 隐藏密码输入
    - 如果用户名已存在，友好提示用户，而不是抛异常让脚本退出
    """
    init_db()
    db = SessionLocal()

    username = input("请输入用户名: ").strip()
    password = getpass("请输入密码: ").strip()  # 改为隐藏密码
    password2 = getpass("请再次输入密码: ").strip()

    if password != password2:
        print("两次输入的密码不一致，请重试！")
        return

    try:
        # 创建用户（crud.create_user 抛异常时捕获）
        user = crud.create_user(
            db=db,
            username=username,
            password=password,
            api_key=None  # API Key 可选
        )
        print(f"用户创建成功！用户名：{user.username}")
    except ValueError as e:
        # 捕获 "用户名已存在" 的异常，提示用户换个名字
        print(f"用户创建失败：{e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user_safe()