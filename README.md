# AI聊天机器人 - 多用户Web版本

一个基于Python和FastAPI的智能AI聊天机器人系统，支持多用户账号管理、个性化人设配置、智能记忆系统等功能。

## 📋 项目概述

本项目是一个功能完整的AI聊天机器人系统，具有以下核心特性：
- ✅ **多用户支持**：完整的用户注册、登录、会话管理，**每个用户数据完全隔离**
- ✅ **用户API Key管理**：每个用户可配置自己的DeepSeek/OpenAI API Key，**普通用户必须配置才能使用**
- ✅ **Admin特权**：admin用户可使用系统默认API Key和默认人设，无需配置
- ✅ **智能记忆系统**：自动判断对话价值，提取并保存长期记忆，**每个用户独立的记忆文件**
- ✅ **人设系统**：可自定义AI角色的人设（任务、角色、外表、经历、性格等），**每个用户独立的人设文件**
- ✅ **多种API支持**：支持DeepSeek、OpenAI等AI API
- ✅ **Web界面**：现代化的Web界面，支持聊天、人设管理、记忆查看、API Key配置
- ✅ **命令行界面**：保留传统的CLI交互方式

## 📁 项目结构

```
my_chat_bot/
├── api_providers/          # API提供者模块
│   ├── base.py            # API提供者基类
│   ├── deepseek_provider.py  # DeepSeek API实现（支持动态API Key）
│   └── openai_provider.py    # OpenAI API实现（支持动态API Key）
├── db/                     # 数据库模块
│   ├── models.py          # 数据库模型（User、Session）
│   ├── database.py        # 数据库连接和配置
│   └── crud.py            # 数据库CRUD操作
├── security/              # 安全模块
│   ├── auth.py            # 认证和会话管理
│   └── password.py        # 密码加密和验证
├── memory/                # 记忆系统模块
│   ├── simple_memory.py   # 简单内存记忆（对话历史，每个用户独立）
│   ├── long_term_memory.py  # 长期记忆存储（按用户隔离：user_{user_id}_long_term_memory.json）
│   ├── memory_filter.py   # 记忆过滤器（判断是否值得存储）
│   └── memory_summarizer.py  # 记忆总结器（提取重要信息）
├── persona/               # 人设系统模块
│   ├── persona_manager.py # 人设管理器（按用户隔离：user_{user_id}_persona.json）
│   ├── persona_editor.py  # 人设编辑器（CLI）
│   └── persona.json       # 默认人设配置文件（仅admin使用）
├── static/                # Web静态文件
│   ├── index.html         # 前端页面（登录、聊天、人设、记忆、设置）
│   ├── app.js             # 前端JavaScript逻辑
│   └── style.css          # 前端样式
├── data/                  # 数据目录（自动创建）
│   └── data.db            # SQLite数据库文件
├── chat_bot.py            # 核心聊天机器人类（支持user_id参数）
├── chat_bot_manager.py    # ChatBot实例管理器（按用户隔离）
├── config.py              # 配置管理
├── main.py                # CLI主程序入口
├── web_app.py             # Web应用入口（FastAPI）
├── requirements.txt       # Python依赖
└── README.md              # 项目说明文档
```

## 🔧 各模块功能说明

### 1. 数据库模块 (`db/`)

#### `db/models.py` - 数据模型
定义了数据库表结构：
- **User表**：存储用户信息
  - `id`: 用户ID（主键）
  - `username`: 用户名（唯一）
  - `password_hash`: 加密后的密码（bcrypt）
  - `api_key`: 用户自定义的API密钥（JSON格式：`{"deepseek": "xxx", "openai": "yyy"}`）
  - `created_at`: 创建时间
- **Session表**：存储用户会话
  - `id`: 会话ID（主键）
  - `session_id`: 会话令牌（唯一，32字节随机字符串）
  - `user_id`: 关联的用户ID（外键）
  - `created_at`: 创建时间
  - `expires_at`: 过期时间（默认24小时）

#### `db/database.py` - 数据库配置
- 使用SQLite数据库（文件：`data/data.db`）
- 提供数据库连接和会话管理
- 自动创建数据表

#### `db/crud.py` - 数据库操作
提供用户相关的数据库操作：
- `create_user()`: 创建新用户（密码自动加密）
- `get_user_by_id()`: 根据ID获取用户
- `get_user_by_username()`: 根据用户名获取用户
- `get_all_users()`: 获取所有用户列表
- `update_user_api_key()`: 更新用户API密钥（支持JSON格式）

### 2. 安全模块 (`security/`)

#### `security/password.py` - 密码加密
- 使用`bcrypt`算法加密密码
- `hash_password()`: 密码加密
- `verify_password()`: 密码验证

#### `security/auth.py` - 认证管理
- `create_session()`: 创建用户会话（24小时有效期）
- `get_session_by_id()`: 根据会话ID获取会话（自动检查过期）
- `delete_session()`: 删除会话
- `get_current_user()`: 从Cookie中获取当前登录用户（FastAPI依赖注入，支持自动验证）

### 3. 记忆系统 (`memory/`)

#### `memory/simple_memory.py` - 简单记忆
- 内存中的对话历史管理
- **每个用户独立的实例**（通过ChatBot实例隔离）
- 限制最大历史记录数量（避免token超限）
- 自动保留system消息，移除最旧的对话

#### `memory/long_term_memory.py` - 长期记忆
- **按用户隔离存储**：`memory/user_{user_id}_long_term_memory.json`
- **Admin用户使用**：`memory/long_term_memory.json`（全局默认文件）
- 持久化存储重要记忆到JSON文件
- 记忆分类：个人档案、偏好、重要关系、重要事件、约定与计划、长期目标、其他
- 自动整合记忆到系统消息中，增强后续对话的上下文理解

#### `memory/memory_filter.py` - 记忆过滤器
- 使用AI判断对话是否值得存储
- 分析对话价值，避免存储无意义的闲聊

#### `memory/memory_summarizer.py` - 记忆总结器
- 自动提取对话中的重要信息
- 分类整理不同类型的记忆
- 生成未来对话建议

### 4. 人设系统 (`persona/`)

#### `persona/persona_manager.py` - 人设管理器
- **按用户隔离存储**：`persona/user_{user_id}_persona.json`
- **Admin用户使用**：`persona/persona.json`（全局默认文件）
- 支持字段：任务、角色、外表、经历、性格、经典台词、输出示例、喜好、备注
- 将人设转换为系统消息，指导AI回复风格
- 支持加载、保存、更新操作

#### `persona/persona_editor.py` - 人设编辑器
- 命令行交互式人设编辑工具
- 支持字段逐一编辑
- CLI版本使用（使用全局文件）

### 5. API提供者 (`api_providers/`)

#### `api_providers/base.py` - API基类
- 定义统一的API提供者接口
- `chat()` 方法支持可选的 `api_key` 参数（优先使用用户提供的Key）
- 各具体实现必须继承此类

#### `api_providers/deepseek_provider.py` - DeepSeek API
- DeepSeek API的具体实现（兼容OpenAI SDK）
- 支持动态API Key（每次调用时可传入不同的Key）
- 支持DeepSeek Chat模型

#### `api_providers/openai_provider.py` - OpenAI API
- OpenAI API的具体实现
- 支持动态API Key（每次调用时可传入不同的Key）
- 支持GPT-3.5/GPT-4等模型

### 6. ChatBot管理 (`chat_bot_manager.py`)

#### `ChatBotManager` - ChatBot实例管理器
- **核心功能**：为每个用户维护独立的ChatBot实例
- `get_bot_for_user()`: 获取或创建用户专用的ChatBot实例
  - Admin用户：传入 `is_admin=True`，使用全局人设和记忆文件
  - 普通用户：传入 `is_admin=False`，使用用户特定文件
- `remove_bot_for_user()`: 移除用户实例（登出时释放内存）
- `has_bot_for_user()`: 检查实例是否存在

### 7. Web应用 (`web_app.py` + `static/`)

#### 后端API路由（`web_app.py`）

**认证相关：**
- `POST /auth/login`: 用户登录（设置HTTP-only Cookie会话）
- `POST /auth/logout`: 用户登出（删除Cookie和会话）
- `GET /auth/me`: 获取当前登录用户信息

**管理接口（需登录）：**
- `POST /admin/create_user`: 创建新用户（需登录，所有用户可创建）
- `GET /admin/users`: 获取所有用户列表（需登录）
- `GET /admin/users/{user_id}`: 获取指定用户信息（需登录）

**聊天API：**
- `POST /api/chat`: 发送消息并获取AI回复
  - 自动使用用户配置的API Key（如果有）
  - Admin用户未配置Key时使用系统默认Key
  - 普通用户未配置Key时返回错误提示

**人设API：**
- `GET /api/persona`: 获取当前用户的人设
  - Admin用户返回默认人设
  - 普通用户返回用户特定人设
- `POST /api/persona`: 更新当前用户的人设
  - 自动重新加载并应用到ChatBot实例
  - 保存后立即生效

**Profile API（API Key管理）：**
- `GET /api/profile/api-key`: 获取API Key状态（是否已配置DeepSeek和OpenAI）
- `POST /api/profile/api-key`: 更新API Key（支持按provider分别配置）
- `GET /api/profile/api-key/{provider}`: 获取指定provider的Key部分显示（用于确认）

**其他API：**
- `GET /health`: 健康检查

#### 前端界面（`static/`）

**`static/index.html`** - 主页面
- **登录界面**：用户名/密码登录表单
- **主应用界面**：
  - 侧边栏：导航菜单、用户信息、登出按钮
  - **聊天页面**：消息显示区、输入框、发送按钮
  - **人设页面**：人设编辑表单（9个字段）、保存按钮
  - **记忆页面**：长期记忆展示（按类型分类）
  - **设置页面**：API Key配置界面（DeepSeek和OpenAI分别配置）

**`static/app.js`** - 前端逻辑
- 认证状态管理（自动检查登录状态）
- API调用封装（所有请求自动包含Cookie）
- 页面切换和状态管理
- 消息发送和显示
- 人设加载和保存
- 记忆加载和显示
- API Key状态管理和更新

**`static/style.css`** - 样式文件
- 现代化UI设计（渐变背景、卡片式布局）
- 响应式布局（支持移动端）
- 美观的登录界面和聊天界面
- 设置页面专用样式

### 8. 核心功能模块

#### `chat_bot.py` - 聊天机器人核心类
- 整合所有模块的核心类
- 支持 `user_id` 参数（用于数据隔离）
- 管理对话流程、记忆总结、人设应用
- `chat()` 方法支持可选的 `api_key` 参数（优先使用用户Key）
- 支持自动和手动触发记忆总结
- `reload_persona()`: 重新加载人设并更新系统消息
- `clear_history()`: 清空对话历史

#### `config.py` - 配置管理
- 从`.env`文件加载配置
- 支持多个API提供者切换（deepseek、openai、claude）
- 配置验证
- 提供默认API Key（仅admin用户使用）

#### `main.py` - CLI入口
- 命令行交互界面
- 使用全局人设和记忆文件（不区分用户）
- 支持命令：`persona`、`memory`、`summarize`、`exit`

## 🗄️ 数据库结构

### User表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    api_key VARCHAR,  -- JSON格式：{"deepseek": "xxx", "openai": "yyy"} 或 NULL
    created_at DATETIME NOT NULL
);
```

### Session表
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## 🔐 用户权限和数据隔离

### Admin用户（username == "admin"）

**特权：**
- ✅ 可使用系统默认API Key（无需配置）
- ✅ 使用默认人设文件（`persona/persona.json`）
- ✅ 使用默认长期记忆文件（`memory/long_term_memory.json`）
- ✅ 可直接使用聊天功能（无需配置API Key）

**使用场景：**
- 系统管理员
- 演示和测试账号
- 共享默认配置

### 普通用户

**限制：**
- ⚠️ **必须配置API Key才能使用聊天功能**
- ⚠️ 未配置Key时，聊天接口会返回错误："请先在设置页面配置 [Provider] API Key 后才能使用聊天功能"

**数据隔离：**
- ✅ 独立的人设文件：`persona/user_{user_id}_persona.json`
- ✅ 独立的长期记忆文件：`memory/user_{user_id}_long_term_memory.json`
- ✅ 独立的对话历史（内存中，每个ChatBot实例独立）
- ✅ 独立的API Key配置（存储在数据库中，JSON格式）

**使用流程：**
1. 登录系统
2. 前往设置页面配置API Key（DeepSeek或OpenAI，根据系统配置的Provider）
3. 配置完成后即可使用聊天功能
4. 每个人设和记忆数据完全独立，互不干扰

## 🌐 Web界面功能

### 登录界面
- 用户名/密码登录
- 登录成功后自动跳转到主界面
- 会话通过HTTP-only Cookie管理（24小时有效期）
- 自动检查登录状态（刷新页面时自动验证）

### 主界面功能

1. **聊天功能**
   - 实时消息发送和接收
   - 消息历史显示（当前会话）
   - 清空历史功能
   - 自动检查API Key配置状态
   - 未配置Key时提示前往设置页面

2. **人设管理**
   - 查看当前用户的人设（自动加载）
   - 编辑AI的角色设定（9个字段）
   - 保存后立即生效（自动更新ChatBot实例的系统消息）
   - Admin用户可编辑默认人设
   - 普通用户编辑自己独立的人设

3. **记忆查看**
   - 查看所有长期记忆
   - 按类型分类显示（个人档案、偏好、重要关系等）
   - 刷新记忆列表
   - 显示记忆的原因和创建时间

4. **API Key设置**
   - 分别配置DeepSeek和OpenAI的API Key
   - 查看配置状态（已配置/未配置）
   - 显示已配置Key的部分内容（前4位+****+后4位，用于确认）
   - 保存和清除功能
   - 支持扩展更多Provider（Claude等）

5. **对话总结**
   - 手动触发对话总结
   - 自动提取重要信息到长期记忆
