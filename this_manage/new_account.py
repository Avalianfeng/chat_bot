#!/usr/bin/env python3
"""
创建新用户脚本
使用说明：
1. 如果使用虚拟环境，先激活：source venv/bin/activate 或 conda activate chat_bot
2. 如果使用 conda，确保环境已激活
3. 运行：python3 new_account.py
"""

import sys
import os

# 尝试导入，如果失败给出友好提示
try:
    from db.database import init_db, SessionLocal
    from db import crud
    from getpass import getpass  # 用于隐藏密码输入
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("\n请确保：")
    print("1. 已安装所有依赖: pip install -r requirements.txt")
    print("2. 如果使用虚拟环境，请先激活: source venv/bin/activate")
    print("3. 如果使用 conda，请先激活: conda activate chat_bot")
    sys.exit(1)


def create_user_safe():
    """
    创建用户的安全版本：
    - 隐藏密码输入
    - 如果用户名已存在，友好提示用户，而不是抛异常让脚本退出
    - 检查密码长度（bcrypt 限制 72 字节）
    """
    try:
        init_db()
        db = SessionLocal()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("请检查数据库文件权限和路径")
        sys.exit(1)

    username = input("请输入用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空！")
        db.close()
        return

    password = getpass("请输入密码: ").strip()  # 改为隐藏密码
    password2 = getpass("请再次输入密码: ").strip()

    if not password:
        print("❌ 密码不能为空！")
        db.close()
        return

    if password != password2:
        print("❌ 两次输入的密码不一致，请重试！")
        db.close()
        return

    # 检查密码长度（bcrypt 限制 72 字节）
    password_bytes = len(password.encode('utf-8'))
    if password_bytes > 72:
        print(f"⚠️  警告：密码长度超过 72 字节（当前 {password_bytes} 字节）")
        print("⚠️  密码将被截断到 72 字节，请考虑使用更短的密码")
        confirm = input("是否继续？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消创建用户")
            db.close()
            return

    try:
        # 创建用户（crud.create_user 抛异常时捕获）
        user = crud.create_user(
            db=db,
            username=username,
            password=password,
            api_key=None  # API Key 可选
        )
        print(f"✅ 用户创建成功！")
        print(f"   用户名：{user.username}")
        print(f"   用户ID：{user.id}")
    except ValueError as e:
        # 捕获 "用户名已存在" 的异常，提示用户换个名字
        print(f"❌ 用户创建失败：{e}")
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_user_safe()