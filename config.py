"""配置管理模块"""
import os
from dotenv import load_dotenv
from typing import Optional

# 加载环境变量
load_dotenv()


class Config:
    """配置类，管理所有配置项"""
    
    # API提供者选择
    API_PROVIDER: str = os.getenv("API_PROVIDER", "deepseek").lower()
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Anthropic Claude配置
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    
    # 记忆配置
    MAX_HISTORY_LENGTH: int = int(os.getenv("MAX_HISTORY_LENGTH", "20"))
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        验证配置是否完整
        
        Returns:
            (is_valid, error_message): 配置是否有效，错误信息（如果有）
        """
        if cls.API_PROVIDER == "openai":
            if not cls.OPENAI_API_KEY:
                return False, "未设置 OPENAI_API_KEY，请在 .env 文件中配置"
        elif cls.API_PROVIDER == "deepseek":
            if not cls.DEEPSEEK_API_KEY:
                return False, "未设置 DEEPSEEK_API_KEY，请在 .env 文件中配置"
        elif cls.API_PROVIDER == "claude":
            if not cls.ANTHROPIC_API_KEY:
                return False, "未设置 ANTHROPIC_API_KEY，请在 .env 文件中配置"
        else:
            return False, f"不支持的API提供者: {cls.API_PROVIDER}，支持: openai, deepseek, claude"
        
        return True, None
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """获取当前API提供者的密钥"""
        if cls.API_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        elif cls.API_PROVIDER == "deepseek":
            return cls.DEEPSEEK_API_KEY
        elif cls.API_PROVIDER == "claude":
            return cls.ANTHROPIC_API_KEY
        return None

