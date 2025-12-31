"""主程序入口 - CLI交互界面"""
import sys
from chat_bot import ChatBot
from persona.persona_editor import PersonaEditor


def main():
    """主函数"""
    print("=" * 50)
    print("AI聊天机器人 - 情感陪伴版")
    print("=" * 50)
    print("输入消息开始对话")
    print("输入 'persona' 或 'p' 编辑人设")
    print("输入 'memory' 或 'm' 查看长期记忆")
    print("输入 'summarize' 或 's' 立即总结当前对话")
    print("输入 'exit' 或 'quit' 退出")
    print("-" * 50)
    
    try:
        # 创建聊天机器人实例
        bot = ChatBot()
        print(f"✓ 已连接到 {bot.api_provider.__class__.__name__}")
        print()
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        print("\n请检查配置文件和API密钥设置。")
        sys.exit(1)
    
    # 交互循环
    while True:
        try:
            # 读取用户输入
            user_input = input("你: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['exit', 'quit', '退出']:
                # 退出前强制总结
                if bot.pending_conversation:
                    print("\n[记忆系统] 正在保存对话记忆...")
                    bot.force_summarize()
                print("\n再见啦。")
                break
            
            # 检查人设编辑命令
            if user_input.lower() in ['persona', 'p', '人设']:
                editor = PersonaEditor()
                editor.edit_interactive()
                # 重新加载人设
                bot.reload_persona()
                print("\n✓ 人设已更新，新的对话将使用新的人设")
                continue
            
            # 检查记忆查看命令
            if user_input.lower() in ['memory', 'm', '记忆']:
                memories = bot.long_term_memory.get_all_memories()
                print("\n" + "=" * 50)
                print("长期记忆")
                print("=" * 50)
                
                for mem_type, mem_list in memories.items():
                    if mem_type == "conversation_summaries":
                        continue
                    if mem_type == "notes_for_future":
                        if mem_list:
                            print(f"\n【未来对话建议】\n{mem_list}")
                        continue
                    
                    if mem_list:
                        type_names = {
                            "personal_profile": "个人档案",
                            "preference": "偏好",
                            "relationship": "重要关系",
                            "important_event": "重要事件",
                            "plan": "约定与计划",
                            "long_term_goal": "长期目标",
                            "other": "其他"
                        }
                        print(f"\n【{type_names.get(mem_type, mem_type)}】")
                        for i, mem in enumerate(mem_list, 1):
                            print(f"  {i}. {mem.get('content', '')}")
                            if mem.get('reason'):
                                print(f"     原因: {mem.get('reason')}")
                
                if not any(v for k, v in memories.items() if k not in ["conversation_summaries", "notes_for_future"]):
                    print("\n暂无长期记忆")
                
                print("=" * 50 + "\n")
                continue
            
            # 检查立即总结命令
            if user_input.lower() in ['summarize', 's', '总结']:
                if bot.pending_conversation:
                    bot.force_summarize()
                    print("\n✓ 对话已总结并保存")
                else:
                    print("\n暂无待总结的对话")
                continue
            
            # 忽略空输入
            if not user_input:
                continue
            
            # 获取AI回复
            response = bot.chat(user_input)
            
            # 输出AI回复
            print(f"AI: {response}\n")
            
        except KeyboardInterrupt:
            # 处理 Ctrl+C
            print("\n\n再见！")
            break
        except Exception as e:
            # 处理其他错误
            print(f"\n✗ 错误: {e}\n")
            # 询问是否继续
            continue_input = input("是否继续？(y/n): ").strip().lower()
            if continue_input != 'y':
                break


if __name__ == "__main__":
    main()

