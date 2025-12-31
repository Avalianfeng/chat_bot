"""简单内存记忆管理"""
from typing import List, Dict, Optional


class SimpleMemory:
    """简单内存记忆管理器，在内存中存储对话历史"""
    
    def __init__(self, max_length: int = 20):
        """
        初始化记忆管理器
        
        Args:
            max_length: 最大历史记录数量（避免token超限）
        """
        self.max_length = max_length
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加消息到历史记录
        
        Args:
            role: 角色（user, assistant, system）
            content: 消息内容
        """
        message = {"role": role, "content": content}
        self.history.append(message)
        
        # 如果超过最大长度，移除最旧的消息（但保留system消息）
        if len(self.history) > self.max_length:
            # 找到第一个非system消息的位置
            first_non_system = 0
            for i, msg in enumerate(self.history):
                if msg["role"] != "system":
                    first_non_system = i
                    break
            
            # 如果第一个非system消息存在，移除它
            if first_non_system < len(self.history):
                self.history.pop(first_non_system)
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取完整的对话历史
        
        Returns:
            消息历史列表
        """
        return self.history.copy()
    
    def clear(self) -> None:
        """清空历史记录（但保留system消息）"""
        system_messages = [msg for msg in self.history if msg["role"] == "system"]
        self.history = system_messages
    
    def set_system_message(self, content: str) -> None:
        """
        设置系统消息（人设、角色定义等）
        
        Args:
            content: 系统消息内容
        """
        # 移除旧的system消息
        self.history = [msg for msg in self.history if msg["role"] != "system"]
        # 在开头添加新的system消息
        self.history.insert(0, {"role": "system", "content": content})

