"""ChatBot 实例管理器 - 按用户隔离"""
from typing import Dict, Optional, Callable
from chat_bot import ChatBot
from api_providers.base import BaseAPIProvider


class ChatBotManager:
    """ChatBot 管理器，为每个用户维护独立的 ChatBot 实例"""
    
    def __init__(self):
        """初始化管理器"""
        self._bots: Dict[int, ChatBot] = {}
        # 存储用户信息查询函数（用于判断是否是 admin）
        self._user_checker: Optional[Callable[[int], bool]] = None
    
    def set_user_checker(self, checker: Callable[[int], bool]):
        """
        设置用户检查函数（用于判断用户是否是 admin）
        
        Args:
            checker: 函数，接收 user_id，返回是否是 admin
        """
        self._user_checker = checker
    
    def _is_admin_user(self, user_id: int) -> bool:
        """
        判断用户是否是 admin
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否是 admin
        """
        if self._user_checker:
            return self._user_checker(user_id)
        return False
    
    def get_bot_for_user(self, user_id: int, api_provider: Optional[BaseAPIProvider] = None, is_admin: bool = False) -> ChatBot:
        """
        获取指定用户的 ChatBot 实例（如果不存在则创建）
        
        Args:
            user_id: 用户ID
            api_provider: 可选的API提供者实例（如果为None，则使用默认配置创建）
            is_admin: 是否是 admin 用户（admin 用户使用默认人设和默认 Key）
        
        Returns:
            ChatBot实例
        """
        if user_id not in self._bots:
            # 为这个用户创建一个新的 ChatBot 实例
            self._bots[user_id] = self._create_bot_for_user(user_id, api_provider, is_admin)
        return self._bots[user_id]
    
    def _create_bot_for_user(self, user_id: int, api_provider: Optional[BaseAPIProvider] = None, is_admin: bool = False) -> ChatBot:
        """
        为指定用户创建一个新的 ChatBot 实例
        
        Args:
            user_id: 用户ID
            api_provider: 可选的API提供者实例
            is_admin: 是否是 admin 用户（admin 用户使用全局人设和记忆文件）
        
        Returns:
            ChatBot实例
        """
        # admin 用户使用全局文件（传入 None），其他用户使用用户特定文件（传入 user_id）
        effective_user_id = None if is_admin else user_id
        bot = ChatBot(user_id=effective_user_id, api_provider=api_provider)
        return bot
    
    def remove_bot_for_user(self, user_id: int) -> bool:
        """
        移除指定用户的 ChatBot 实例（用户登出时可以调用）
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否成功移除
        """
        if user_id in self._bots:
            del self._bots[user_id]
            return True
        return False
    
    def has_bot_for_user(self, user_id: int) -> bool:
        """
        检查是否已存在指定用户的 ChatBot 实例
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否存在
        """
        return user_id in self._bots

