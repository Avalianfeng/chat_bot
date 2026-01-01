# Web 服务使用说明

## 启动 Web 服务

### 方式一：使用 uvicorn 命令

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

### 方式二：直接运行 Python 文件

```bash
python web_app.py
```

### 方式三：使用 gunicorn（生产环境推荐）

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker web_app:app --bind 0.0.0.0:8000
```

## 访问 Web 界面

启动服务后，在浏览器中访问：

- 本地访问：http://localhost:8000
- 服务器访问：http://服务器IP:8000

## 功能说明

### 1. 聊天功能
- 在聊天页面输入消息与 AI 对话
- 支持 Enter 键发送（Shift+Enter 换行）
- 对话历史会保存在内存中，直到清空或重启服务

### 2. 人设管理
- 在"人设"页面可以查看和编辑 AI 的人设
- 修改后点击"保存人设"按钮保存
- 新的人设会在下次对话时生效

### 3. 记忆管理
- 在"记忆"页面可以查看长期记忆
- 长期记忆会自动从对话中提取并保存到文件
- 点击"刷新"按钮可以重新加载记忆

### 4. 其他功能
- **清空历史**：清空当前对话历史（长期记忆不受影响）
- **总结对话**：立即触发对话总结，将重要信息保存到长期记忆

## 注意事项

1. **单例模式**：Web 服务使用全局单例 ChatBot 实例，所有用户共享同一个对话历史
2. **长期记忆持久化**：长期记忆保存在 `memory/long_term_memory.json` 文件中
3. **人设持久化**：人设保存在 `persona/persona.json` 文件中
4. **API 密钥安全**：API 密钥只在后端使用，不会暴露到前端

## 开发说明

- 前端文件位于 `static/` 目录
- 后端 API 定义在 `web_app.py` 中
- API 端点前缀为 `/api/`
- 静态文件通过 `/static/` 路径访问

