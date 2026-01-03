"""长期记忆存储"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class LongTermMemory:
    """长期记忆管理器，持久化存储重要记忆"""
    
    def __init__(self, user_id: Optional[int] = None):
        """
        初始化长期记忆管理器
        
        Args:
            user_id: 用户ID，如果提供则使用用户特定的文件路径，否则使用全局路径（向后兼容）
        """
        self.user_id = user_id
        # 根据 user_id 确定文件路径
        if user_id is not None:
            self.MEMORY_FILE = Path(f"memory/user_{user_id}_long_term_memory.json")
        else:
            # 向后兼容：如果未提供 user_id，使用全局文件
            self.MEMORY_FILE = Path("memory/long_term_memory.json")
        
        # 确保目录存在
        self.MEMORY_FILE.parent.mkdir(exist_ok=True)
        self.memories = self.load_memories()
    
    def load_memories(self) -> Dict:
        """
        从文件加载长期记忆
        
        Returns:
            记忆字典
        """
        if self.MEMORY_FILE.exists():
            try:
                with open(self.MEMORY_FILE, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                # 确保所有必需的字段都存在（向后兼容旧版本文件）
                return self._ensure_memory_structure(memories)
            except Exception as e:
                print(f"加载长期记忆失败: {e}，使用空记忆")
                return self._create_empty_memory()
        else:
            return self._create_empty_memory()
    
    def _ensure_memory_structure(self, memories: Dict) -> Dict:
        """
        确保记忆字典包含所有必需的字段（向后兼容）
        
        Args:
            memories: 从文件加载的记忆字典
            
        Returns:
            补全后的记忆字典
        """
        # 获取标准的空记忆结构作为模板
        default_memory = self._create_empty_memory()
        
        # 如果 memories 缺少任何字段，使用默认值
        for key, default_value in default_memory.items():
            if key not in memories:
                memories[key] = default_value
            elif key == "conversation_summaries" and not isinstance(memories[key], list):
                # 确保 conversation_summaries 是列表
                memories[key] = []
            elif key == "notes_for_future" and not isinstance(memories[key], str):
                # 确保 notes_for_future 是字符串
                memories[key] = ""
            elif isinstance(default_value, list) and not isinstance(memories[key], list):
                # 其他列表字段如果不是列表，初始化为空列表
                memories[key] = []
        
        return memories
    
    def _create_empty_memory(self) -> Dict:
        """创建空的记忆结构"""
        return {
            "personal_profile": [],
            "preference": [],
            "relationship": [],
            "important_event": [],
            "plan": [],
            "long_term_goal": [],
            "other": [],
            "conversation_summaries": [],
            "notes_for_future": ""
        }
    
    def save_memories(self) -> bool:
        """
        保存记忆到文件
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存长期记忆失败: {e}")
            return False
    
    def add_memory(self, memory_type: str, content: str, reason: str) -> bool:
        """
        添加一条记忆
        
        Args:
            memory_type: 记忆类型
            content: 记忆内容
            reason: 为什么值得记忆
        
        Returns:
            是否添加成功
        """
        if memory_type not in self.memories:
            memory_type = "other"
        
        memory_item = {
            "content": content,
            "reason": reason,
            "created_at": datetime.now().isoformat()
        }
        
        self.memories[memory_type].append(memory_item)
        return self.save_memories()
    
    def update_memory(self, target: str, new_content: str, reason: str) -> bool:
        """
        更新已有记忆
        
        Args:
            target: 要更新的记忆描述
            new_content: 更新后的内容
            reason: 更新原因
        
        Returns:
            是否更新成功
        """
        # 在所有类型中查找匹配的记忆
        for memory_type, memories in self.memories.items():
            if memory_type == "conversation_summaries" or memory_type == "notes_for_future":
                continue
            
            for memory in memories:
                if target.lower() in memory.get("content", "").lower():
                    memory["content"] = new_content
                    memory["updated_at"] = datetime.now().isoformat()
                    memory["update_reason"] = reason
                    return self.save_memories()
        
        # 如果没找到，作为新记忆添加
        return self.add_memory("other", new_content, reason)
    
    def add_summary(self, summary: Dict) -> bool:
        """
        添加对话总结
        
        Args:
            summary: 总结字典（包含memories_to_add, memories_to_update等）
        
        Returns:
            是否添加成功
        """
        summary_item = {
            "summary": summary.get("summary", ""),
            "memories_added": summary.get("memories_to_add", []),
            "memories_updated": summary.get("memories_to_update", []),
            "notes": summary.get("notes_for_future_conversation", ""),
            "created_at": datetime.now().isoformat()
        }
        
        # 确保 conversation_summaries 字段存在
        if "conversation_summaries" not in self.memories:
            self.memories["conversation_summaries"] = []
        if not isinstance(self.memories["conversation_summaries"], list):
            self.memories["conversation_summaries"] = []
        
        self.memories["conversation_summaries"].append(summary_item)
        
        # 添加新记忆
        for memory in summary.get("memories_to_add", []):
            self.add_memory(
                memory.get("type", "other"),
                memory.get("content", ""),
                memory.get("reason", "")
            )
        
        # 更新已有记忆
        for memory in summary.get("memories_to_update", []):
            self.update_memory(
                memory.get("target", ""),
                memory.get("content", ""),
                memory.get("reason", "")
            )
        
        # 更新未来对话建议
        if summary.get("notes_for_future_conversation"):
            # 确保 notes_for_future 字段存在
            if "notes_for_future" not in self.memories:
                self.memories["notes_for_future"] = ""
            if not isinstance(self.memories["notes_for_future"], str):
                self.memories["notes_for_future"] = ""
            
            if self.memories["notes_for_future"]:
                self.memories["notes_for_future"] += "\n" + summary["notes_for_future_conversation"]
            else:
                self.memories["notes_for_future"] = summary["notes_for_future_conversation"]
        
        return self.save_memories()
    
    def get_all_memories(self) -> Dict:
        """获取所有记忆"""
        return self.memories.copy()
    
    def get_memories_by_type(self, memory_type: str) -> List[Dict]:
        """
        获取指定类型的记忆
        
        Args:
            memory_type: 记忆类型
        
        Returns:
            记忆列表
        """
        return self.memories.get(memory_type, []).copy()
    
    def to_system_context(self) -> str:
        """
        将长期记忆转换为系统上下文（用于增强对话）
        
        Returns:
            格式化的上下文字符串
        """
        parts = []
        
        # 个人档案
        if self.memories.get("personal_profile"):
            parts.append("【用户档案】")
            for mem in self.memories["personal_profile"]:
                parts.append(f"- {mem['content']}")
        
        # 偏好
        if self.memories.get("preference"):
            parts.append("\n【用户偏好】")
            for mem in self.memories["preference"]:
                parts.append(f"- {mem['content']}")
        
        # 重要关系
        if self.memories.get("relationship"):
            parts.append("\n【重要关系】")
            for mem in self.memories["relationship"]:
                parts.append(f"- {mem['content']}")
        
        # 重要事件
        if self.memories.get("important_event"):
            parts.append("\n【重要事件】")
            for mem in self.memories["important_event"]:
                parts.append(f"- {mem['content']}")
        
        # 计划
        if self.memories.get("plan"):
            parts.append("\n【约定与计划】")
            for mem in self.memories["plan"]:
                parts.append(f"- {mem['content']}")
        
        # 长期目标
        if self.memories.get("long_term_goal"):
            parts.append("\n【长期目标】")
            for mem in self.memories["long_term_goal"]:
                parts.append(f"- {mem['content']}")
        
        # 未来对话建议
        if self.memories.get("notes_for_future"):
            parts.append(f"\n【对话建议】\n{self.memories['notes_for_future']}")
        
        if not parts:
            return ""
        
        return "\n".join(parts)

