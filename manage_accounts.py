#!/usr/bin/env python3
"""
账户管理程序（仅后端使用）
提供账户查找、密码修改、账户删除功能

使用说明：
1. 如果使用虚拟环境，先激活：source venv/bin/activate 或 conda activate chat_bot
2. 运行：python3 manage_accounts.py
"""

import sys
import os
from pathlib import Path
from getpass import getpass

# 尝试导入，如果失败给出友好提示
try:
    from db.database import init_db, SessionLocal
    from db import crud
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("\n请确保：")
    print("1. 已安装所有依赖: pip install -r requirements.txt")
    print("2. 如果使用虚拟环境，请先激活: source venv/bin/activate")
    print("3. 如果使用 conda，请先激活: conda activate chat_bot")
    sys.exit(1)


def cleanup_user_files(user_id: int):
    """
    清理用户相关的文件数据
    
    Args:
        user_id: 用户 ID
    """
    deleted_files = []
    
    # 清理长期记忆文件
    memory_file = Path(f"memory/user_{user_id}_long_term_memory.json")
    if memory_file.exists():
        try:
            memory_file.unlink()
            deleted_files.append(str(memory_file))
        except Exception as e:
            print(f"⚠️  删除记忆文件失败: {e}")
    
    # 清理人设文件
    persona_file = Path(f"persona/user_{user_id}_persona.json")
    if persona_file.exists():
        try:
            persona_file.unlink()
            deleted_files.append(str(persona_file))
        except Exception as e:
            print(f"⚠️  删除人设文件失败: {e}")
    
    return deleted_files


def search_accounts(db):
    """查找账户"""
    username = input("请输入要搜索的用户名（支持部分匹配，留空显示所有）: ").strip()
    
    if username:
        users = crud.search_users_by_username(db, username)
    else:
        users = crud.get_all_users(db)
    
    if not users:
        print("❌ 未找到匹配的用户")
        return None
    
    print(f"\n找到 {len(users)} 个用户：")
    print("-" * 80)
    for i, user in enumerate(users, 1):
        print(f"{i}. ID: {user.id}, 用户名: {user.username}, 创建时间: {user.created_at}")
    print("-" * 80)
    
    return users


def change_password(db):
    """修改密码"""
    users = search_accounts(db)
    if not users:
        return
    
    if len(users) > 1:
        try:
            choice = int(input(f"\n请选择要修改密码的用户 (1-{len(users)}): ").strip())
            if choice < 1 or choice > len(users):
                print("❌ 无效的选择")
                return
            user = users[choice - 1]
        except ValueError:
            print("❌ 请输入有效数字")
            return
    else:
        user = users[0]
    
    print(f"\n修改用户 '{user.username}' (ID: {user.id}) 的密码")
    new_password = getpass("请输入新密码: ").strip()
    new_password2 = getpass("请再次输入新密码: ").strip()
    
    if not new_password:
        print("❌ 密码不能为空")
        return
    
    if new_password != new_password2:
        print("❌ 两次输入的密码不一致")
        return
    
    try:
        updated_user = crud.update_user_password(db, user.id, new_password)
        if updated_user:
            print(f"✅ 密码修改成功！用户: {updated_user.username}")
        else:
            print("❌ 密码修改失败：用户不存在")
    except Exception as e:
        print(f"❌ 密码修改失败: {e}")


def delete_account(db):
    """删除账户"""
    users = search_accounts(db)
    if not users:
        return
    
    if len(users) > 1:
        try:
            choice = int(input(f"\n请选择要删除的用户 (1-{len(users)}): ").strip())
            if choice < 1 or choice > len(users):
                print("❌ 无效的选择")
                return
            user = users[choice - 1]
        except ValueError:
            print("❌ 请输入有效数字")
            return
    else:
        user = users[0]
    
    print(f"\n⚠️  警告：即将删除用户 '{user.username}' (ID: {user.id})")
    print("这将删除：")
    print("  - 数据库中的用户记录")
    print("  - 所有关联的会话记录")
    print("  - 用户的长期记忆文件")
    print("  - 用户的人设文件")
    
    confirm = input("\n确认删除？(输入 'DELETE' 确认): ").strip()
    if confirm != "DELETE":
        print("❌ 已取消删除")
        return
    
    try:
        # 清理文件
        deleted_files = cleanup_user_files(user.id)
        
        # 删除数据库记录（Session 会通过 cascade 自动删除）
        success = crud.delete_user(db, user.id)
        
        if success:
            print(f"✅ 账户删除成功！用户: {user.username}")
            if deleted_files:
                print(f"   已删除文件: {', '.join(deleted_files)}")
        else:
            print("❌ 账户删除失败：用户不存在")
    except Exception as e:
        print(f"❌ 账户删除失败: {e}")
        import traceback
        traceback.print_exc()


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 80)
    print("账户管理程序")
    print("=" * 80)
    print("1. 查找账户")
    print("2. 修改密码")
    print("3. 删除账户")
    print("0. 退出")
    print("=" * 80)


def main():
    """主函数"""
    try:
        init_db()
        db = SessionLocal()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("请检查数据库文件权限和路径")
        sys.exit(1)
    
    try:
        while True:
            show_menu()
            choice = input("\n请选择操作 (0-3): ").strip()
            
            if choice == "0":
                print("退出程序")
                break
            elif choice == "1":
                search_accounts(db)
            elif choice == "2":
                change_password(db)
            elif choice == "3":
                delete_account(db)
            else:
                print("❌ 无效的选择，请输入 0-3")
            
            if choice != "0":
                input("\n按回车键继续...")
    
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
