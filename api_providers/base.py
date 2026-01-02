"""API提供者抽象基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseAPIProvider(ABC):
    """API提供者抽象基类"""
    
    def __init__(self, api_key: str, model: str):
        """
        初始化API提供者
        
        Args:
            api_key: API密钥
            model: 模型名称
        """
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], api_key: Optional[str] = None, **kwargs) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
            api_key: 可选的 API 密钥，如果提供则优先使用，否则使用默认密钥
            **kwargs: 其他参数（如temperature等）
        
        Returns:
            AI的回复文本
        
        Raises:
            Exception: API调用失败时抛出异常
        """
        pass
    
    @abstractmethod
    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """
        格式化消息为API所需的格式
        
        Args:
            role: 角色（user, assistant, system）
            content: 消息内容
        
        Returns:
            格式化后的消息字典
        """
        pass

