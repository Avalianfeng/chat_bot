"""测试用户隔离功能"""
from chat_bot_manager import ChatBotManager


def test_user_isolation():
    """测试不同用户获得不同的 ChatBot 实例"""
    print("=" * 60)
    print("测试用户隔离功能")
    print("=" * 60)
    
    # 创建管理器
    manager = ChatBotManager()
    
    # 获取用户1的 ChatBot 实例
    print("\n1. 获取用户 1 的 ChatBot 实例...")
    bot_user1 = manager.get_bot_for_user(user_id=1)
    print(f"   ✓ 用户1 ChatBot ID: {id(bot_user1)}")
    print(f"   ✓ 用户1 user_id: {bot_user1.user_id}")
    
    # 获取用户2的 ChatBot 实例
    print("\n2. 获取用户 2 的 ChatBot 实例...")
    bot_user2 = manager.get_bot_for_user(user_id=2)
    print(f"   ✓ 用户2 ChatBot ID: {id(bot_user2)}")
    print(f"   ✓ 用户2 user_id: {bot_user2.user_id}")
    
    # 验证是不同的实例
    print("\n3. 验证实例隔离...")
    if id(bot_user1) != id(bot_user2):
        print("   ✓ 用户1和用户2获得了不同的 ChatBot 实例（隔离成功）")
    else:
        print("   ✗ 错误：两个用户获得了相同的实例！")
    
    # 验证再次获取返回相同实例（单例模式）
    print("\n4. 验证实例复用...")
    bot_user1_again = manager.get_bot_for_user(user_id=1)
    if id(bot_user1) == id(bot_user1_again):
        print("   ✓ 用户1再次获取时返回相同的实例（内存复用）")
    else:
        print("   ✗ 错误：用户1再次获取时返回了新实例！")
    
    # 验证内存隔离（对话历史独立）
    print("\n5. 验证对话历史隔离...")
    bot_user1.memory.add_message("user", "我是用户1")
    bot_user2.memory.add_message("user", "我是用户2")
    
    history1 = bot_user1.memory.get_history()
    history2 = bot_user2.memory.get_history()
    
    # 检查是否有对方的消息
    user1_messages = [msg["content"] for msg in history1 if msg.get("role") == "user"]
    user2_messages = [msg["content"] for msg in history2 if msg.get("role") == "user"]
    
    print(f"   用户1的历史: {user1_messages}")
    print(f"   用户2的历史: {user2_messages}")
    
    if "我是用户2" not in user1_messages and "我是用户1" not in user2_messages:
        print("   ✓ 对话历史完全隔离（用户1看不到用户2的消息）")
    else:
        print("   ✗ 错误：对话历史没有隔离！")
    
    # 验证文件路径隔离
    print("\n6. 验证文件路径隔离...")
    print(f"   用户1的长期记忆文件: {bot_user1.long_term_memory.MEMORY_FILE}")
    print(f"   用户2的长期记忆文件: {bot_user2.long_term_memory.MEMORY_FILE}")
    print(f"   用户1的人设文件: {bot_user1.persona_manager.PERSONA_FILE}")
    print(f"   用户2的人设文件: {bot_user2.persona_manager.PERSONA_FILE}")
    
    if bot_user1.long_term_memory.MEMORY_FILE != bot_user2.long_term_memory.MEMORY_FILE:
        print("   ✓ 长期记忆文件路径不同（数据隔离）")
    else:
        print("   ✗ 警告：长期记忆文件路径相同")
    
    if bot_user1.persona_manager.PERSONA_FILE != bot_user2.persona_manager.PERSONA_FILE:
        print("   ✓ 人设文件路径不同（数据隔离）")
    else:
        print("   ✗ 警告：人设文件路径相同")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_user_isolation()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

