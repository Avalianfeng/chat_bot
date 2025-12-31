"""人设管理器"""
import json
import os
from typing import Dict, Optional
from pathlib import Path


class PersonaManager:
    """人设管理器，负责保存、加载和编辑人设"""
    
    # 人设文件路径
    PERSONA_FILE = Path("persona/persona.json")
    
    # 默认人设模板
    DEFAULT_PERSONA = {
        "任务": "",
        "角色": "",
        "外表": "",
        "经历": "",
        "性格": "",
        "经典台词": "",
        "输出示例": "",
        "喜好": "",
        "备注": ""
    }
    
    def __init__(self):
        """初始化人设管理器"""
        # 确保persona目录存在
        self.PERSONA_FILE.parent.mkdir(exist_ok=True)
        self.persona = self.load_persona()
    
    def load_persona(self) -> Dict[str, str]:
        """
        从文件加载人设
        
        Returns:
            人设字典
        """
        if self.PERSONA_FILE.exists():
            try:
                with open(self.PERSONA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 确保所有字段都存在
                    persona = self.DEFAULT_PERSONA.copy()
                    persona.update(data)
                    return persona
            except Exception as e:
                print(f"加载人设文件失败: {e}，使用默认人设")
                return self.DEFAULT_PERSONA.copy()
        else:
            # 如果文件不存在，创建默认人设文件
            self.save_persona(self.DEFAULT_PERSONA.copy())
            return self.DEFAULT_PERSONA.copy()
    
    def save_persona(self, persona: Optional[Dict[str, str]] = None) -> bool:
        """
        保存人设到文件
        
        Args:
            persona: 人设字典，如果为None则保存当前人设
        
        Returns:
            是否保存成功
        """
        if persona is None:
            persona = self.persona
        
        try:
            with open(self.PERSONA_FILE, 'w', encoding='utf-8') as f:
                json.dump(persona, f, ensure_ascii=False, indent=2)
            self.persona = persona
            return True
        except Exception as e:
            print(f"保存人设文件失败: {e}")
            return False
    
    def get_persona(self) -> Dict[str, str]:
        """
        获取当前人设
        
        Returns:
            人设字典
        """
        return self.persona.copy()
    
    def update_field(self, field: str, value: str) -> bool:
        """
        更新单个字段
        
        Args:
            field: 字段名
            value: 字段值
        
        Returns:
            是否更新成功
        """
        if field not in self.DEFAULT_PERSONA:
            return False
        
        self.persona[field] = value
        return self.save_persona()
    
    def update_persona(self, persona: Dict[str, str]) -> bool:
        """
        更新整个人设
        
        Args:
            persona: 人设字典
        
        Returns:
            是否更新成功
        """
        # 只更新存在的字段
        for key in self.DEFAULT_PERSONA.keys():
            if key in persona:
                self.persona[key] = persona[key]
        
        return self.save_persona()
    
    def to_system_message(self) -> str:
        """
        将人设转换为系统消息
        
        Returns:
            系统消息字符串
        """
        parts = []
        
        # 构建人设描述
        if self.persona.get("任务"):
            parts.append(f"【任务】{self.persona['任务']}")
        
        if self.persona.get("角色"):
            parts.append(f"【角色】{self.persona['角色']}")
        
        if self.persona.get("外表"):
            parts.append(f"【外表】{self.persona['外表']}")
        
        if self.persona.get("经历"):
            parts.append(f"【经历】{self.persona['经历']}")
        
        if self.persona.get("性格"):
            parts.append(f"【性格】{self.persona['性格']}")
        
        if self.persona.get("喜好"):
            parts.append(f"【喜好】{self.persona['喜好']}")
        
        if self.persona.get("经典台词"):
            parts.append(f"【经典台词】{self.persona['经典台词']}")
        
        if self.persona.get("输出示例"):
            parts.append(f"【输出示例】{self.persona['输出示例']}")
        
        if self.persona.get("备注"):
            parts.append(f"【备注】{self.persona['备注']}")
        
        # 如果没有任何人设信息，使用默认提示
        if not parts:
            return (
                "你是一个温暖、友善的AI陪伴助手。"
                "你善于倾听，能够理解用户的情感需求，"
                "用温柔、关怀的语气与用户交流。"
                "你会记住对话的上下文，让交流更加自然流畅。"
            )
        
        # 组合成完整的系统消息
        system_msg = "\n".join(parts)
        system_msg += "\n\n请严格按照以上人设进行对话，保持角色的一致性。"
        
        return system_msg
    
    def display_persona(self) -> str:
        """
        显示当前人设（用于查看）
        
        Returns:
            格式化的字符串
        """
        lines = ["当前人设：", "=" * 50]
        for key, value in self.persona.items():
            if value:
                lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: (未设置)")
        lines.append("=" * 50)
        return "\n".join(lines)

