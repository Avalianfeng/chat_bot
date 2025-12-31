"""核心聊天机器人类"""
import time
from typing import Optional
from config import Config
from api_providers.base import BaseAPIProvider
from api_providers.openai_provider import OpenAIProvider
from api_providers.deepseek_provider import DeepSeekProvider
from memory.simple_memory import SimpleMemory
from memory.memory_filter import MemoryFilter
from memory.memory_summarizer import MemorySummarizer
from memory.long_term_memory import LongTermMemory
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
        
        # 创建长期记忆管理器
        self.long_term_memory = LongTermMemory()
        
        # 创建记忆过滤器和总结器
        self.memory_filter = MemoryFilter(self.api_provider)
        self.memory_summarizer = MemorySummarizer(self.api_provider)
        
        # 加载人设并设置系统消息
        self.persona_manager = PersonaManager()
        system_message = self._build_system_message()
        self.memory.set_system_message(system_message)
        
        # 记录最后活动时间
        self.last_activity_time = time.time()
        self.pending_conversation = []  # 待总结的对话
    
    def _build_system_message(self) -> str:
        """
        构建系统消息（包含人设和长期记忆）
        
        Returns:
            完整的系统消息
        """
        # 获取人设
        persona_message = self.persona_manager.to_system_message()
        
        # 获取长期记忆上下文
        memory_context = self.long_term_memory.to_system_context()
        
        # 组合系统消息
        if memory_context:
            return f"{persona_message}\n\n【长期记忆】\n{memory_context}"
        else:
            return persona_message
    
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
        # 检查是否需要总结之前的对话
        self._check_and_summarize()
        
        # 更新活动时间
        self.last_activity_time = time.time()
        
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
            
            # 记录到待总结对话（排除system消息）
            self.pending_conversation.append({"role": "user", "content": user_input})
            self.pending_conversation.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            # 如果API调用失败，移除刚添加的用户消息
            if self.memory.history and self.memory.history[-1]["role"] == "user":
                self.memory.history.pop()
            raise e
    
    def _check_and_summarize(self) -> None:
        """
        检查是否需要总结对话（10分钟无新消息）
        """
        current_time = time.time()
        time_since_last_activity = current_time - self.last_activity_time
        
        # 如果超过设定时间且有待总结的对话
        if (time_since_last_activity >= Config.MEMORY_SUMMARY_INTERVAL and 
            len(self.pending_conversation) > 0):
            
            try:
                self._summarize_conversation()
            except Exception as e:
                print(f"记忆总结失败: {e}")
            finally:
                # 清空待总结对话
                self.pending_conversation = []
    
    def _summarize_conversation(self) -> None:
        """
        总结对话并保存到长期记忆
        """
        if not self.pending_conversation:
            return
        
        print("\n[记忆系统] 正在分析对话...")
        
        # Step 1: 判断是否值得存储
        filter_result = self.memory_filter.should_save(self.pending_conversation)
        
        if not filter_result.get("should_save", False):
            print(f"[记忆系统] 对话不值得存储: {filter_result.get('reason', '无重要信息')}")
            return
        
        print(f"[记忆系统] 对话值得存储: {filter_result.get('reason', '')}")
        print("[记忆系统] 正在提取记忆...")
        
        # Step 2: 提取和总结记忆
        summary_result = self.memory_summarizer.summarize(self.pending_conversation)
        
        # Step 3: 保存到长期记忆
        if summary_result.get("should_save_memory", False):
            self.long_term_memory.add_summary(summary_result)
            
            # 更新系统消息（包含新的长期记忆）
            new_system_message = self._build_system_message()
            self.memory.set_system_message(new_system_message)
            
            print(f"[记忆系统] ✓ 已保存 {len(summary_result.get('memories_to_add', []))} 条新记忆")
            if summary_result.get("memories_to_update"):
                print(f"[记忆系统] ✓ 已更新 {len(summary_result['memories_to_update'])} 条记忆")
        else:
            print("[记忆系统] 未提取到值得保存的记忆")
    
    def force_summarize(self) -> None:
        """
        强制立即总结当前对话（手动触发）
        """
        self._summarize_conversation()
        self.pending_conversation = []
    
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
        system_message = self._build_system_message()
        self.memory.set_system_message(system_message)
    
    def clear_history(self) -> None:
        """清空对话历史（保留system消息）"""
        self.memory.clear()

