"""验证用户隔离实现"""
from chat_bot_manager import ChatBotManager
from pathlib import Path


def verify_implementation():
    """验证实现是否符合要求"""
    print("=" * 60)
    print("验证用户隔离实现")
    print("=" * 60)
    
    manager = ChatBotManager()
    
    # 测试用户1
    print("\n1. 创建用户1的ChatBot实例...")
    bot1 = manager.get_bot_for_user(user_id=1)
    print(f"   ✓ user_id: {bot1.user_id}")
    print(f"   ✓ 长期记忆文件: {bot1.long_term_memory.MEMORY_FILE}")
    print(f"   ✓ 人设文件: {bot1.persona_manager.PERSONA_FILE}")
    
    # 测试用户2
    print("\n2. 创建用户2的ChatBot实例...")
    bot2 = manager.get_bot_for_user(user_id=2)
    print(f"   ✓ user_id: {bot2.user_id}")
    print(f"   ✓ 长期记忆文件: {bot2.long_term_memory.MEMORY_FILE}")
    print(f"   ✓ 人设文件: {bot2.persona_manager.PERSONA_FILE}")
    
    # 验证隔离
    print("\n3. 验证文件路径隔离...")
    memory_file_1 = bot1.long_term_memory.MEMORY_FILE
    memory_file_2 = bot2.long_term_memory.MEMORY_FILE
    persona_file_1 = bot1.persona_manager.PERSONA_FILE
    persona_file_2 = bot2.persona_manager.PERSONA_FILE
    
    assert memory_file_1 != memory_file_2, "长期记忆文件路径应该不同"
    assert persona_file_1 != persona_file_2, "人设文件路径应该不同"
    print("   ✓ 文件路径完全隔离")
    
    # 验证实例隔离
    print("\n4. 验证实例隔离...")
    assert id(bot1) != id(bot2), "应该创建不同的ChatBot实例"
    print("   ✓ ChatBot实例隔离")
    
    # 验证内存隔离
    print("\n5. 验证内存隔离...")
    bot1.memory.add_message("user", "我是用户1")
    bot2.memory.add_message("user", "我是用户2")
    
    history1 = [msg["content"] for msg in bot1.memory.get_history() if msg.get("role") == "user"]
    history2 = [msg["content"] for msg in bot2.memory.get_history() if msg.get("role") == "user"]
    
    assert "我是用户2" not in history1, "用户1不应该看到用户2的消息"
    assert "我是用户1" not in history2, "用户2不应该看到用户1的消息"
    print("   ✓ 对话历史隔离")
    
    # 验证文件路径格式
    print("\n6. 验证文件路径格式...")
    assert "user_1" in str(memory_file_1), f"文件路径应包含user_1: {memory_file_1}"
    assert "user_2" in str(memory_file_2), f"文件路径应包含user_2: {memory_file_2}"
    print("   ✓ 文件路径格式正确")
    
    print("\n" + "=" * 60)
    print("✅ 所有验证通过！用户隔离实现正确。")
    print("=" * 60)
    print("\n文件结构：")
    print(f"  用户1长期记忆: {memory_file_1}")
    print(f"  用户2长期记忆: {memory_file_2}")
    print(f"  用户1人设: {persona_file_1}")
    print(f"  用户2人设: {persona_file_2}")


if __name__ == "__main__":
    try:
        verify_implementation()
    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

