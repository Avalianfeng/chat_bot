#!/usr/bin/env python3
"""
清空所有用户账户脚本（用于适配新的密码加密算法）

⚠️  警告：此脚本会删除数据库中所有用户记录和相关文件！
仅在需要清空所有账户以适配新的加密算法时使用。

使用说明：
1. 如果使用虚拟环境，先激活：source venv/bin/activate 或 conda activate chat_bot
2. 运行：python3 clear_all_users.py
"""

import sys
from pathlib import Path

# 尝试导入，如果失败给出友好提示
try:
    from db.database import init_db, SessionLocal
    from db import crud
    from db.models import User
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("\n请确保：")
    print("1. 已安装所有依赖: pip install -r requirements.txt")
    print("2. 如果使用虚拟环境，请先激活: source venv/bin/activate")
    print("3. 如果使用 conda，请先激活: conda activate chat_bot")
    sys.exit(1)


def cleanup_all_user_files():
    """
    清理所有用户相关的文件数据
    
    Returns:
        已删除的文件列表
    """
    deleted_files = []
    
    # 清理所有用户长期记忆文件
    memory_dir = Path("memory")
    if memory_dir.exists():
        for memory_file in memory_dir.glob("user_*_long_term_memory.json"):
            try:
                memory_file.unlink()
                deleted_files.append(str(memory_file))
            except Exception as e:
                print(f"⚠️  删除文件失败 {memory_file}: {e}")
    
    # 清理所有用户人设文件
    persona_dir = Path("persona")
    if persona_dir.exists():
        for persona_file in persona_dir.glob("user_*_persona.json"):
            try:
                persona_file.unlink()
                deleted_files.append(str(persona_file))
            except Exception as e:
                print(f"⚠️  删除文件失败 {persona_file}: {e}")
    
    return deleted_files


def clear_all_users():
    """清空所有用户"""
    print("=" * 80)
    print("清空所有用户账户")
    print("=" * 80)
    print("\n⚠️  警告：此操作将：")
    print("  - 删除数据库中所有用户记录")
    print("  - 删除所有用户会话记录（通过 cascade 自动删除）")
    print("  - 删除所有用户的长期记忆文件 (memory/user_*_long_term_memory.json)")
    print("  - 删除所有用户的人设文件 (persona/user_*_persona.json)")
    print("\n⚠️  此操作不可恢复！")
    print("=" * 80)
    
    confirm1 = input("\n确认继续？(输入 'YES' 继续): ").strip()
    if confirm1 != "YES":
        print("❌ 已取消操作")
        return
    
    confirm2 = input("再次确认，输入 'CLEAR ALL' 确认: ").strip()
    if confirm2 != "CLEAR ALL":
        print("❌ 已取消操作")
        return
    
    try:
        init_db()
        db = SessionLocal()
        
        # 获取所有用户
        users = crud.get_all_users(db, limit=10000)  # 获取所有用户
        
        if not users:
            print("\n✅ 数据库中没有用户记录，无需清理")
            db.close()
            return
        
        print(f"\n找到 {len(users)} 个用户，开始清理...")
        
        # 清理所有用户文件
        deleted_files = cleanup_all_user_files()
        
        # 删除数据库中的所有用户记录（Session 会通过 cascade 自动删除）
        deleted_count = 0
        for user in users:
            try:
                crud.delete_user(db, user.id)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  删除用户 {user.username} (ID: {user.id}) 失败: {e}")
        
        db.close()
        
        print("\n" + "=" * 80)
        print("清理完成")
        print("=" * 80)
        print(f"✅ 已删除 {deleted_count} 个用户账户")
        if deleted_files:
            print(f"✅ 已删除 {len(deleted_files)} 个用户文件")
            print("\n删除的文件：")
            for file in deleted_files:
                print(f"  - {file}")
        print("\n现在可以使用新的加密算法创建用户账户了。")
        
    except Exception as e:
        print(f"\n❌ 清理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    clear_all_users()
