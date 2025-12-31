# AI聊天机器人

一个基于Python的个人AI聊天机器人，专注于情感陪伴。

## 功能特性

- 支持多个AI API（DeepSeek、OpenAI、Claude等）
- **智能记忆系统**：自动判断对话价值，提取并保存长期记忆
- **人设系统**：可自定义角色人设（任务、角色、外表、经历、性格、经典台词、输出示例、喜好、备注）
- **长期记忆存储**：持久化保存用户信息、偏好、重要事件、计划等
- 命令行交互界面
- 可扩展架构，便于后续添加新功能

## 安装

1. 克隆或下载项目
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
   
   在项目根目录创建 `.env` 文件，内容如下：
   ```
   # AI API配置
   # 选择使用的API提供者: deepseek, openai 或 claude
   API_PROVIDER=deepseek
   
   # DeepSeek配置（推荐）
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_MODEL=deepseek-chat
   
   # OpenAI配置（如果使用OpenAI）
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   
   # Anthropic Claude配置（如果使用Claude）
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ANTHROPIC_MODEL=claude-3-sonnet-20240229
   
   # 记忆配置
   MAX_HISTORY_LENGTH=20
   MEMORY_SUMMARY_INTERVAL=600
   ```
   
   - `MAX_HISTORY_LENGTH`: 对话历史最大条数（避免token超限）
   - `MEMORY_SUMMARY_INTERVAL`: 记忆总结触发间隔（秒），默认600秒（10分钟）
   
   将 `your_deepseek_api_key_here` 替换为你的实际DeepSeek API密钥。
   
   **获取DeepSeek API密钥：**
   - 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
   - 注册并登录账户
   - 在控制台创建API密钥

## 使用方法

运行主程序：
```bash
python main.py
```

在命令行中输入消息与AI对话，输入 `exit` 或 `quit` 退出。

### 命令说明

- `persona` 或 `p` - 编辑人设
- `memory` 或 `m` - 查看长期记忆
- `summarize` 或 `s` - 立即总结当前对话
- `exit` 或 `quit` - 退出程序（退出前会自动保存记忆）

### 人设编辑

在对话过程中，输入 `persona` 或 `p` 进入人设编辑器，可以编辑以下字段：
- **任务**：角色的主要任务或职责
- **角色**：角色的身份定位
- **外表**：角色的外观描述
- **经历**：角色的背景经历
- **性格**：角色的性格特点
- **经典台词**：角色的标志性话语
- **输出示例**：期望的回复风格示例
- **喜好**：角色的兴趣爱好
- **备注**：其他需要说明的内容

人设信息保存在 `persona/persona.json` 文件中，可以手动编辑该文件，也可以使用交互式编辑器。

### 记忆总结功能

系统会自动分析对话，判断是否包含值得长期记忆的信息：

**自动触发时机：**
- 10分钟（可配置）无新消息时自动总结
- 退出程序时自动保存当前对话记忆
- 手动输入 `summarize` 或 `s` 立即总结

**记忆类型：**
- **个人档案**：姓名、年龄、职业、城市、学校等基本信息
- **稳定偏好**：喜欢的食物、音乐、游戏、作息习惯、聊天风格偏好
- **重要关系**：家人、伴侣、朋友、宠物等重要信息
- **重要事件**：换工作、考试、失恋、搬家、生病等人生大事
- **约定与计划**：未来的待办事项、约定（如"明天提醒我早起"）
- **长期目标**：学习计划、职业规划、习惯养成目标

**记忆存储：**
- 长期记忆保存在 `memory/long_term_memory.json`
- 记忆会自动整合到系统消息中，增强后续对话的上下文理解
- 使用 `memory` 或 `m` 命令查看所有保存的记忆

## 后续扩展方向

- 情绪系统（情绪分析和调整）
- 多模态支持（语音、图片）
- Web界面
- 多个人设切换
- 基于token数量的精确记忆管理

