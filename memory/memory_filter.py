"""记忆过滤器 - 判断对话是否值得存储"""
import json
from typing import Dict, List, Optional
from api_providers.base import BaseAPIProvider


class MemoryFilter:
    """记忆过滤器，判断对话是否值得长期存储"""
    
    FILTER_PROMPT = """你是一个聊天机器人的"记忆过滤器"。

【任务】
给你一段用户与机器人的对话内容（纯文字），请判断这段对话是否包含"值得长期记忆"的信息。

【什么算值得长期记忆】
如果本次对话中，出现了下面任何一种信息，就认为"值得储存"：
1. 个人档案类：用户的基本信息，例：
   - 姓名/昵称、年龄、职业、城市、学校、专业、家庭情况等。
2. 稳定偏好类：很可能长期不变的偏好或习惯，例：
   - 喜欢/讨厌的食物、电影/游戏/音乐、兴趣爱好、作息习惯、价值观、聊天风格偏好（如"以后叫我XXX"，"别老讲大道理"等）。
3. 重要关系类：
   - 提到伴侣、家人、好朋友、宠物等的重要信息（如"我妈身体不好""我跟男朋友异地恋"等）。
4. 重要事件类：
   - 对人生或情绪有较大影响的事（如换工作、考试、失恋、搬家、生病、重大决定等）。
5. 约定与计划类：
   - 用户希望未来你记住/提醒/配合的事（如"明天提醒我早起""下周帮我复习""以后遇到这种情况要劝劝我"）。
6. 长期目标类：
   - 学习计划、职业规划、自我提升计划、习惯养成目标（如"我要坚持每天跑步""三个月内通过四级"）。
7. 对未来聊天方式的要求：
   - 用户明确说明以后希望你用什么称呼、什么语气、哪些话题要避开等。

【明确不需要长期记忆的情况】
如果对话主要是以下内容，请判定为"不需要储存"：
- 一次性的日常吐槽或感叹，如"好困啊""今天下雨了真烦"且没有明确说希望你以后记住；
- 一般性闲聊，没有透露新的个人信息、偏好、事件或计划；
- 技术/知识问答类（查资料、算题目），与用户长期画像无关；
- 之前已经记过、且本次对话没有新增或变化的信息重复提及。

【输出要求】
请只用 JSON 格式回答，不要多余解释，格式如下：

{
  "should_save": true 或 false,
  "reason": "一句话说明为什么（例如：包含新的职业信息 / 只是普通闲聊等）"
}"""
    
    def __init__(self, api_provider: BaseAPIProvider):
        """
        初始化记忆过滤器
        
        Args:
            api_provider: API提供者实例
        """
        self.api_provider = api_provider
    
    def should_save(self, conversation: List[Dict[str, str]], api_key: Optional[str] = None) -> Dict[str, any]:
        """
        判断对话是否值得存储
        
        Args:
            conversation: 对话历史列表，格式为 [{"role": "user", "content": "..."}, ...]
            api_key: 可选的 API 密钥，如果提供则优先使用，否则使用 provider 的默认 key
        
        Returns:
            {
                "should_save": bool,
                "reason": str
            }
        """
        # 构建对话文本
        conversation_text = self._format_conversation(conversation)
        
        # 构建消息
        messages = [
            self.api_provider.format_message("system", self.FILTER_PROMPT),
            self.api_provider.format_message("user", f"对话内容：\n{conversation_text}")
        ]
        
        try:
            # 调用API，传递 api_key（如果提供）
            response = self.api_provider.chat(messages, api_key=api_key)
            
            # 解析JSON响应
            # 尝试提取JSON（可能包含markdown代码块）
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response)
            
            # 验证结果格式
            if "should_save" not in result:
                result["should_save"] = False
            if "reason" not in result:
                result["reason"] = "无法判断"
            
            return result
            
        except json.JSONDecodeError as e:
            # JSON解析失败，默认不保存
            return {
                "should_save": False,
                "reason": f"解析失败: {str(e)}"
            }
        except Exception as e:
            # 其他错误，默认不保存
            return {
                "should_save": False,
                "reason": f"处理失败: {str(e)}"
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

