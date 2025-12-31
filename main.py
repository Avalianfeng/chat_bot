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

