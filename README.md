# AI聊天机器人 - 多用户Web版本

一个基于Python和FastAPI的智能AI聊天机器人系统，支持多用户账号管理、个性化人设配置、智能记忆系统等功能。

🌐 **在线体验**：http://47.100.198.51:8000/

## 📋 核心特性

- ✅ **多用户支持**：完整的用户注册、登录、会话管理，每个用户数据完全隔离
- ✅ **用户API Key管理**：每个用户可配置自己的DeepSeek/OpenAI API Key
- ✅ **Admin特权**：admin用户可使用系统默认API Key和默认人设，无需配置
- ✅ **智能记忆系统**：自动判断对话价值，提取并保存长期记忆
- ✅ **人设系统**：可自定义AI角色的人设（任务、角色、外表、经历、性格等）
- ✅ **多种API支持**：支持DeepSeek、OpenAI等AI API
- ✅ **Web界面**：现代化的Web界面，支持聊天、人设管理、记忆查看、API Key配置
- ✅ **命令行界面**：保留传统的CLI交互方式

## 📁 项目结构

```
my_chat_bot/
├── api_providers/          # API提供者模块
│   ├── __init__.py
│   ├── base.py            # API提供者基类
│   ├── deepseek_provider.py  # DeepSeek API实现
│   └── openai_provider.py    # OpenAI API实现
├── db/                     # 数据库模块
│   ├── __init__.py
│   ├── models.py          # 数据库模型（User、Session）
│   ├── database.py        # 数据库连接和配置
│   └── crud.py            # 数据库CRUD操作
├── security/              # 安全模块
│   ├── __init__.py
│   ├── auth.py            # 认证和会话管理
│   └── password.py        # 密码加密和验证（argon2）
├── memory/                # 记忆系统模块
│   ├── __init__.py
│   ├── simple_memory.py   # 简单内存记忆
│   ├── long_term_memory.py  # 长期记忆存储
│   ├── memory_filter.py   # 记忆过滤器
│   ├── memory_summarizer.py  # 记忆总结器
│   └── long_term_memory.json  # 默认长期记忆文件
├── persona/               # 人设系统模块
│   ├── __init__.py
│   ├── persona_manager.py # 人设管理器
│   ├── persona_editor.py  # 人设编辑器（CLI）
│   └── persona.json       # 默认人设配置文件
├── static/                # Web静态文件
│   ├── index.html         # 前端页面
│   ├── index-react.html   # React版本前端页面
│   ├── app.jsx            # React前端逻辑
│   ├── style.css          # 前端样式
│   └── data/              # 静态数据目录
├── this_manage/           # 用户管理脚本目录
│   ├── manage_accounts.py # 账户管理脚本
│   ├── clear_all_users.py # 清空所有用户脚本
│   ├── new_account.py     # 创建新用户脚本
│   └── search_account.py  # 搜索用户脚本
├── data/                  # 数据目录
│   └── data.db            # SQLite数据库文件
├── chat_bot.py            # 核心聊天机器人类
├── chat_bot_manager.py    # ChatBot实例管理器
├── config.py              # 配置管理
├── main.py                # CLI主程序入口
├── web_app.py             # Web应用入口（FastAPI）
├── requirements.txt       # Python依赖
└── README.md              # 项目说明文档
```

## 🌐 在线体验

项目已部署在远程服务器，可直接访问：

**访问地址**：http://47.100.198.51:8000/

### 使用说明

1. **首次使用**：请联系管理员创建账号
2. **登录**：使用管理员提供的用户名和密码登录
3. **配置 API Key**：普通用户需要在"设置"页面配置自己的 DeepSeek 或 OpenAI API Key 后才能使用聊天功能
4. **Admin 用户**：admin 用户可使用系统默认配置，无需额外设置

### 功能说明

- **聊天**：与 AI 进行对话
- **人设管理**：自定义 AI 的角色设定
- **记忆查看**：查看长期记忆
- **设置**：配置 API Key 和主题

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件：

```env
API_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 运行Web应用

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

### 运行CLI版本

```bash
python main.py
```

### 远程部署

1. **上传代码到服务器**：
   ```bash
   scp -r . user@server:/path/to/chat_bot
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   # 或使用 conda
   conda env update -f environment.yml
   ```

3. **配置 systemd 服务**（推荐）：
   创建 `/etc/systemd/system/chat_bot.service`：
   ```ini
   [Unit]
   Description=AI Chat Bot Web Service
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/chat_bot
   Environment="PATH=/root/chat_bot/venv/bin"
   ExecStart=/root/chat_bot/venv/bin/uvicorn web_app:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **启动服务**：
   ```bash
   systemctl daemon-reload
   systemctl enable chat_bot.service
   systemctl start chat_bot.service
   systemctl status chat_bot.service
   ```

## 🔐 用户管理

### 创建用户

```bash
python this_manage/new_account.py
```

### 账户管理（后端）

```bash
python this_manage/manage_accounts.py
```

功能：
- 查找账户
- 修改密码
- 删除账户（包括相关文件）

### 搜索用户

```bash
python this_manage/search_account.py
```

### 清空所有用户（适配新加密算法）

```bash
python this_manage/clear_all_users.py
```

## 📝 主要功能

### Admin用户
- 可使用系统默认API Key（无需配置）
- 使用默认人设文件（`persona/persona.json`）
- 使用默认长期记忆文件（`memory/long_term_memory.json`）

### 普通用户
- 必须配置API Key才能使用聊天功能
- 独立的人设文件：`persona/user_{user_id}_persona.json`
- 独立的长期记忆文件：`memory/user_{user_id}_long_term_memory.json`

## 🛠️ 技术栈

- **后端**：Python 3.9+, FastAPI, SQLAlchemy, SQLite
- **前端**：React, TailwindCSS, Framer Motion
- **安全**：argon2密码加密，HTTP-only Cookie会话管理
- **AI API**：DeepSeek, OpenAI

## 👨‍💻 开发者

- **QQ**：2656927351
- **Email**：m19956272658@163.com
- **GitHub**：https://github.com/Avalianfeng/chat_bot

## 📄 许可证

本项目仅供学习和研究使用。
