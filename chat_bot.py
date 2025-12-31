"""核心聊天机器人类"""
from typing import Optional
from config import Config
from api_providers.base import BaseAPIProvider
from api_providers.openai_provider import OpenAIProvider
from api_providers.deepseek_provider import DeepSeekProvider
from memory.simple_memory import SimpleMemory
from persona.persona_manager import PersonaManager


class ChatBot:
    """聊天机器人核心类"""
    
    def __init__(self, api_provider: Optional[BaseAPIProvider] = None):
        """
        初始化聊天机器人
        
        Args:
            api_provider: API提供者实例，如果为None则根据配置自动创建
        """
        # 验证配置
        is_valid, error_msg = Config.validate()
        if not is_valid:
            raise ValueError(error_msg)
        
        # 创建API提供者
        if api_provider is None:
            api_provider = self._create_api_provider()
        self.api_provider = api_provider
        
        # 创建记忆管理器
        self.memory = SimpleMemory(max_length=Config.MAX_HISTORY_LENGTH)
        
        # 加载人设并设置系统消息
        self.persona_manager = PersonaManager()
        system_message = self.persona_manager.to_system_message()
        self.memory.set_system_message(system_message)
    
    def _create_api_provider(self) -> BaseAPIProvider:
        """根据配置创建API提供者"""
        if Config.API_PROVIDER == "openai":
            api_key = Config.OPENAI_API_KEY
            model = Config.OPENAI_MODEL
            return OpenAIProvider(api_key, model)
        elif Config.API_PROVIDER == "deepseek":
            api_key = Config.DEEPSEEK_API_KEY
            model = Config.DEEPSEEK_MODEL
            return DeepSeekProvider(api_key, model)
        elif Config.API_PROVIDER == "claude":
            # 后续实现Claude提供者时可以在这里添加
            raise NotImplementedError("Claude提供者尚未实现")
        else:
            raise ValueError(f"不支持的API提供者: {Config.API_PROVIDER}")
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入并返回AI回复
        
        Args:
            user_input: 用户输入的消息
        
        Returns:
            AI的回复
        """
        # 添加用户消息到历史
        self.memory.add_message("user", user_input)
        
        # 获取完整历史（包括system消息）
        messages = self.memory.get_history()
        
        # 格式化消息为API提供者所需的格式
        formatted_messages = [
            self.api_provider.format_message(msg["role"], msg["content"])
            for msg in messages
        ]
        
        try:
            # 调用API获取回复
            response = self.api_provider.chat(formatted_messages)
            
            # 添加AI回复到历史
            self.memory.add_message("assistant", response)
            
            return response
        except Exception as e:
            # 如果API调用失败，移除刚添加的用户消息
            if self.memory.history and self.memory.history[-1]["role"] == "user":
                self.memory.history.pop()
            raise e
    
    def set_system_message(self, content: str) -> None:
        """
        设置系统消息（自定义人设）
        
        Args:
            content: 系统消息内容
        """
        self.memory.set_system_message(content)
    
    def reload_persona(self) -> None:
        """重新加载人设并更新系统消息"""
        self.persona_manager.load_persona()
        system_message = self.persona_manager.to_system_message()
        self.memory.set_system_message(system_message)
    
    def clear_history(self) -> None:
        """清空对话历史（保留system消息）"""
        self.memory.clear()

