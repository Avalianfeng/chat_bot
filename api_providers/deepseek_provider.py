"""DeepSeek API提供者"""
from typing import List, Dict, Optional
from openai import OpenAI
from .base import BaseAPIProvider


class DeepSeekProvider(BaseAPIProvider):
    """DeepSeek API提供者实现（兼容OpenAI格式）"""
    
    # DeepSeek API端点
    BASE_URL = "https://api.deepseek.com"
    
    def __init__(self, api_key: str, model: str):
        """
        初始化DeepSeek提供者
        
        Args:
            api_key: DeepSeek API密钥
            model: 模型名称（如 deepseek-chat, deepseek-coder）
        """
        super().__init__(api_key, model)
        # 使用OpenAI SDK，但指向DeepSeek的端点
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL
        )
    
    def chat(self, messages: List[Dict[str, str]], api_key: Optional[str] = None, **kwargs) -> str:
        """
        发送聊天请求到DeepSeek API
        
        Args:
            messages: 消息列表
            api_key: 可选的 API 密钥，如果提供则优先使用，否则使用默认密钥
            **kwargs: 其他参数（temperature, max_tokens等）
        
        Returns:
            AI的回复文本
        
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            # 如果传入了 api_key，使用它创建临时 client；否则使用默认 client
            key_to_use = api_key or self.api_key
            if api_key and api_key != self.api_key:
                # 使用用户提供的 key 创建临时 client
                from openai import OpenAI
                client = OpenAI(api_key=key_to_use, base_url=self.BASE_URL)
            else:
                # 使用默认 client
                client = self.client
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """
        格式化消息为DeepSeek API所需的格式
        
        Args:
            role: 角色（user, assistant, system）
            content: 消息内容
        
        Returns:
            格式化后的消息字典
        """
        return {"role": role, "content": content}

