"""人设编辑器 - CLI交互式编辑"""
from persona.persona_manager import PersonaManager


class PersonaEditor:
    """人设编辑器，提供交互式编辑界面"""
    
    # 字段列表
    FIELDS = ["任务", "角色", "外表", "经历", "性格", "经典台词", "输出示例", "喜好", "备注"]
    
    def __init__(self):
        """初始化编辑器"""
        self.manager = PersonaManager()
    
    def edit_interactive(self):
        """交互式编辑人设"""
        print("\n" + "=" * 50)
        print("人设编辑器")
        print("=" * 50)
        print("输入字段编号进行编辑，输入 'q' 退出，输入 's' 查看当前人设")
        print("-" * 50)
        
        while True:
            # 显示菜单
            print("\n可编辑字段：")
            for i, field in enumerate(self.FIELDS, 1):
                current_value = self.manager.persona.get(field, "")
                preview = current_value[:30] + "..." if len(current_value) > 30 else current_value
                status = f"({len(current_value)}字)" if current_value else "(未设置)"
                print(f"  {i}. {field} {status}")
                if preview:
                    print(f"     当前内容: {preview}")
            
            print("\n命令：")
            print("  s - 查看完整人设")
            print("  c - 清空所有人设")
            print("  q - 退出编辑器")
            
            # 获取用户输入
            choice = input("\n请选择 (1-9/s/c/q): ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 's':
                print("\n" + self.manager.display_persona())
            elif choice == 'c':
                if input("确定要清空所有人设吗？(y/n): ").strip().lower() == 'y':
                    self.manager.update_persona(self.manager.DEFAULT_PERSONA.copy())
                    print("✓ 已清空所有人设")
            elif choice.isdigit():
                field_index = int(choice) - 1
                if 0 <= field_index < len(self.FIELDS):
                    self._edit_field(self.FIELDS[field_index])
                else:
                    print("✗ 无效的选项")
            else:
                print("✗ 无效的选项")
    
    def _edit_field(self, field: str):
        """编辑单个字段"""
        current_value = self.manager.persona.get(field, "")
        
        print(f"\n编辑字段: {field}")
        if current_value:
            print(f"当前内容 ({len(current_value)}字):")
            print(f"  {current_value}")
        else:
            print("当前内容: (未设置)")
        
        print("\n请输入新内容（多行输入，输入单独一行的 'END' 结束）:")
        print("（如果想保持当前内容不变，直接输入 'END'）")
        
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        
        new_value = '\n'.join(lines).strip()
        
        if new_value or input("确定要清空此字段吗？(y/n): ").strip().lower() == 'y':
            if self.manager.update_field(field, new_value):
                print(f"✓ 已更新 {field} ({len(new_value)}字)")
            else:
                print(f"✗ 更新失败")
        else:
            print("已取消编辑")
    
    def quick_edit(self, field: str, value: str) -> bool:
        """
        快速编辑（非交互式）
        
        Args:
            field: 字段名
            value: 字段值
        
        Returns:
            是否成功
        """
        if field not in self.FIELDS:
            return False
        return self.manager.update_field(field, value)

