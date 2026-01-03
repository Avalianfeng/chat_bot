"""记忆总结器 - 提取和总结值得长期记忆的内容"""
import json
from typing import Dict, List, Optional
from api_providers.base import BaseAPIProvider


class MemorySummarizer:
    """记忆总结器，提取对话中的长期记忆"""
    
    SUMMARIZE_PROMPT = """你是一个为聊天机器人管理记忆的"记忆分析助手"。

【任务目标】
给你一段用户与机器人的文字聊天记录，请：
1. 总结本次对话的关键信息；
2. 从中提取"值得长期记忆"的内容（例如：用户的个人信息、偏好、重要事件、未来约定）；
3. 丢弃不重要的闲聊细节，不要把所有内容都当作记忆。

【记忆原则】
仅在信息满足以下任意条件时，才认为"值得长期记忆"：
- 个人档案类：用户的基本信息（如姓名/昵称、年龄、职业、城市、家庭情况）；
- 稳定偏好类：用户的长期喜好或习惯（如喜欢的游戏、音乐、作息、价值观）、聊天风格偏好（如希望你用什么称呼、说话语气）；
- 重要关系类：关于重要他人（伴侣、家人、宠物、朋友等）的关键信息；
- 重要事件类：对用户人生有明显影响的事情（如换工作、考试、失恋、搬家、生病等）；
- 约定与计划类：未来的待办事项、约定（如"明天提醒我早起运动"、"下周帮我复习考试"、"以后叫我XXX"）；
- 长期目标类：学习计划、职业规划、长期习惯养成（如"我打算三个月内坚持每日英语学习"）。

不需要记忆的内容包括但不限于：
- 一次性的小事、临时情绪发泄、不再会用到的细节；
- 纯闲聊碎片（如"哈哈哈""好困啊""今天好冷"这类无信息量句子）；
- 对于机器人内部实现无用的技术讨论（除非用户明确表示"今后都按这个规则和我聊天"）。

【输出格式】
请按以下 JSON 结构输出（不要多余解释）：

{
  "summary": "用 2-4 句话概括本次对话的主要内容和情绪基调。",
  "memories_to_add": [
    {
      "type": "personal_profile | preference | relationship | important_event | plan | long_term_goal | other",
      "content": "一句话描述要记住的内容，清晰简短。",
      "reason": "为什么这条值得长期记忆（1句话）。"
    }
  ],
  "memories_to_update": [
    {
      "target": "简要说明要更新的已有记忆的内容（例如：职业从学生更新为产品经理）。",
      "content": "更新后的记忆内容。",
      "reason": "为什么需要更新（例如：用户明确说自己换工作了）。"
    }
  ],
  "should_save_memory": true 或 false,
  "notes_for_future_conversation": "给未来的聊天机器人一些建议（语气偏好、禁忌话题、可用来关心/追问的话题），如果没有就留空字符串。"
}

【特别要求】
- 如果本次对话没有任何值得长期记忆的内容，请返回：
  - "memories_to_add": []，
  - "memories_to_update": []，
  - "should_save_memory": false。
- 严格使用上面的字段名和 JSON 格式输出。
- 所有内容用中文输出，即使用户使用了其他语言。
- 不要在 JSON 外输出任何其他文字。

【情绪与陪伴相关补充】
- 如果用户多次提到某个情绪困扰（如焦虑、孤独、失眠、工作压力大），可视为长期议题，记录为 long_term_goal 或 important_event（例如"希望我以后多关心他的睡眠情况"）。
- 如果用户对聊天风格提出要求（如"不要太严肃""别老讲大道理""多一点鼓励"），记录为 preference。
- 如果用户提到未来希望你"记得某个纪念日、考试时间、面试时间"等，记录为 plan，并在 reason 中标明"可以在临近时主动关心或询问"。"""
    
    def __init__(self, api_provider: BaseAPIProvider):
        """
        初始化记忆总结器
        
        Args:
            api_provider: API提供者实例
        """
        self.api_provider = api_provider
    
    def summarize(self, conversation: List[Dict[str, str]], api_key: Optional[str] = None) -> Dict[str, any]:
        """
        总结对话并提取记忆
        
        Args:
            conversation: 对话历史列表
            api_key: 可选的 API 密钥，如果提供则优先使用，否则使用 provider 的默认 key
        
        Returns:
            总结结果字典
        """
        # 构建对话文本
        conversation_text = self._format_conversation(conversation)
        
        # 构建消息
        messages = [
            self.api_provider.format_message("system", self.SUMMARIZE_PROMPT),
            self.api_provider.format_message("user", f"对话内容：\n{conversation_text}")
        ]
        
        try:
            # 调用API，传递 api_key（如果提供）
            response = self.api_provider.chat(messages, api_key=api_key)
            
            # 解析JSON响应
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            
            # 验证和填充默认值
            if "summary" not in result:
                result["summary"] = ""
            if "memories_to_add" not in result:
                result["memories_to_add"] = []
            if "memories_to_update" not in result:
                result["memories_to_update"] = []
            if "should_save_memory" not in result:
                result["should_save_memory"] = len(result.get("memories_to_add", [])) > 0 or len(result.get("memories_to_update", [])) > 0
            if "notes_for_future_conversation" not in result:
                result["notes_for_future_conversation"] = ""
            
            return result
            
        except json.JSONDecodeError as e:
            # JSON解析失败，返回空结果
            return {
                "summary": f"解析失败: {str(e)}",
                "memories_to_add": [],
                "memories_to_update": [],
                "should_save_memory": False,
                "notes_for_future_conversation": ""
            }
        except Exception as e:
            # 其他错误
            return {
                "summary": f"处理失败: {str(e)}",
                "memories_to_add": [],
                "memories_to_update": [],
                "should_save_memory": False,
                "notes_for_future_conversation": ""
            }
    
    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """
        格式化对话为文本（只包含user和assistant消息）
        
        Args:
            conversation: 对话历史列表
        
        Returns:
            格式化的对话文本
        """
        lines = []
        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # 只处理用户和助手的消息，跳过system消息
            if role == "user":
                lines.append(f"用户：{content}")
            elif role == "assistant":
                lines.append(f"机器人：{content}")
        
        return "\n".join(lines) if lines else ""

