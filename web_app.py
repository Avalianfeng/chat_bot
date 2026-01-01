"""FastAPI Web 应用入口"""
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from chat_bot import ChatBot

# 创建 FastAPI 应用
app = FastAPI(title="AI聊天机器人", version="1.0.0")

# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局 ChatBot 实例（单例模式，所有用户共享对话历史）
bot_instance: Optional[ChatBot] = None


def get_bot() -> ChatBot:
    """获取或创建 ChatBot 实例"""
    global bot_instance
    if bot_instance is None:
        try:
            bot_instance = ChatBot()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"初始化聊天机器人失败: {str(e)}")
    return bot_instance


# ========== 请求/响应模型 ==========

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    success: bool
    error: Optional[str] = None


class PersonaResponse(BaseModel):
    """人设响应"""
    persona: Dict[str, str]
    success: bool


class PersonaUpdateRequest(BaseModel):
    """人设更新请求"""
    persona: Dict[str, str]


class MemoryResponse(BaseModel):
    """记忆响应"""
    memories: Dict
    success: bool


class SummarizeResponse(BaseModel):
    """总结响应"""
    success: bool
    message: str


# ========== API 端点 ==========

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>错误：找不到 index.html 文件</h1>",
            status_code=404
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求"""
    try:
        bot = get_bot()
        
        # 处理用户消息（chat 方法内部会自动检查并总结）
        response = bot.chat(request.message)
        
        return ChatResponse(
            response=response,
            success=True
        )
    except Exception as e:
        return ChatResponse(
            response="",
            success=False,
            error=str(e)
        )


@app.get("/api/persona", response_model=PersonaResponse)
async def get_persona():
    """获取当前人设"""
    try:
        bot = get_bot()
        persona = bot.persona_manager.get_persona()
        return PersonaResponse(
            persona=persona,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人设失败: {str(e)}")


@app.post("/api/persona", response_model=PersonaResponse)
async def update_persona(request: PersonaUpdateRequest):
    """更新人设"""
    try:
        bot = get_bot()
        success = bot.persona_manager.update_persona(request.persona)
        if success:
            # 重新加载人设到系统消息
            bot.reload_persona()
            return PersonaResponse(
                persona=bot.persona_manager.get_persona(),
                success=True
            )
        else:
            raise HTTPException(status_code=500, detail="更新人设失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新人设失败: {str(e)}")


@app.get("/api/memory", response_model=MemoryResponse)
async def get_memory():
    """获取长期记忆"""
    try:
        bot = get_bot()
        memories = bot.long_term_memory.get_all_memories()
        return MemoryResponse(
            memories=memories,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取记忆失败: {str(e)}")


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize():
    """强制总结当前对话"""
    try:
        bot = get_bot()
        if bot.pending_conversation:
            bot.force_summarize()
            return SummarizeResponse(
                success=True,
                message="对话已总结并保存"
            )
        else:
            return SummarizeResponse(
                success=True,
                message="暂无待总结的对话"
            )
    except Exception as e:
        return SummarizeResponse(
            success=False,
            message=f"总结失败: {str(e)}"
        )


@app.post("/api/clear")
async def clear_history():
    """清空对话历史"""
    try:
        bot = get_bot()
        bot.clear_history()
        return {"success": True, "message": "历史已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    try:
        bot = get_bot()
        return {
            "status": "healthy",
            "provider": bot.api_provider.__class__.__name__,
            "has_memory": len(bot.memory.get_history()) > 0
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

