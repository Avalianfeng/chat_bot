"""OpenAI API提供者"""
from typing import List, Dict
from openai import OpenAI
from .base import BaseAPIProvider


class OpenAIProvider(BaseAPIProvider):
    """OpenAI API提供者实现"""
    
    def __init__(self, api_key: str, model: str):
        """
        初始化OpenAI提供者
        
        Args:
            api_key: OpenAI API密钥
            model: 模型名称（如 gpt-3.5-turbo, gpt-4）
        """
        super().__init__(api_key, model)
        self.client = OpenAI(api_key=api_key)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        发送聊天请求到OpenAI API
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            AI的回复文本
        
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """
        格式化消息为OpenAI API所需的格式
        
        Args:
            role: 角色（user, assistant, system）
            content: 消息内容
        
        Returns:
            格式化后的消息字典
        """
        return {"role": role, "content": content}

