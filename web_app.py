"""FastAPI Web 应用入口"""
from fastapi import FastAPI, Depends, HTTPException, Response, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict 
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from db.database import init_db, get_db
from db import crud
from db.models import User
from security.password import verify_password
from security.auth import create_session, delete_session, get_current_user
from chat_bot_manager import ChatBotManager
import json

# 创建 FastAPI 应用
app = FastAPI(title="AI聊天机器人 API", version="1.0.0")

# 创建 ChatBot 管理器（全局单例）
bot_manager = ChatBotManager()


def _is_admin_user(user: User) -> bool:
    """
    判断用户是否是管理员（admin）
    
    Args:
        user: 用户对象
    
    Returns:
        是否是管理员
    """
    return user.username.lower() == "admin"


def _get_user_api_key_for_provider(user: User, provider_class_name: str) -> Optional[str]:
    """
    从用户配置中获取指定 provider 的 API Key
    
    注意：
        - admin 用户如果没有配置 Key，会返回 None（使用系统默认 Key）
        - 非 admin 用户必须配置 Key，否则会抛出异常
    
    Args:
        user: 用户对象
        provider_class_name: Provider 类名（如 "DeepSeekProvider" 或 "OpenAIProvider"）
    
    Returns:
        API Key 字符串，如果是 admin 且未配置则返回 None（使用默认 Key）
    
    Raises:
        ValueError: 非 admin 用户未配置 API Key
    """
    is_admin = _is_admin_user(user)
    
    # 如果没有配置 api_key
    if not user.api_key:
        if is_admin:
            # admin 用户可以使用默认 Key
            return None
        else:
            # 非 admin 用户必须配置 Key
            provider_name = "DeepSeek" if "DeepSeek" in provider_class_name else "OpenAI"
            raise ValueError(f"请先在设置页面配置 {provider_name} API Key 后才能使用聊天功能")
    
    try:
        # 尝试解析为 JSON（新格式：{"deepseek": "xxx", "openai": "yyy"}）
        api_keys = json.loads(user.api_key) if isinstance(user.api_key, str) else user.api_key
        if isinstance(api_keys, dict):
            # 根据 provider 类名确定 key
            if "DeepSeek" in provider_class_name:
                key = api_keys.get("deepseek")
            elif "OpenAI" in provider_class_name:
                key = api_keys.get("openai")
            else:
                key = None
        else:
            # 旧格式：单个字符串（向后兼容）
            key = user.api_key if isinstance(user.api_key, str) else None
    except (json.JSONDecodeError, TypeError, AttributeError):
        # 如果不是 JSON，当作单个字符串（向后兼容）
        key = user.api_key if isinstance(user.api_key, str) else None
    
    # 检查是否获取到 Key
    if not key:
        if is_admin:
            # admin 用户可以使用默认 Key
            return None
        else:
            # 非 admin 用户必须配置 Key
            provider_name = "DeepSeek" if "DeepSeek" in provider_class_name else "OpenAI"
            raise ValueError(f"请先在设置页面配置 {provider_name} API Key 后才能使用聊天功能")
    
    return key

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


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("✓ 数据库已初始化")


# ========== 请求/响应模型 ==========

class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str
    password: str
    api_key: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    api_key: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None


class ApiKeyUpdateRequest(BaseModel):
    """API Key 更新请求"""
    provider: str  # "deepseek" 或 "openai"
    api_key: Optional[str] = None  # None 表示清除


class ApiKeyStatusResponse(BaseModel):
    """API Key 状态响应"""
    has_deepseek_key: bool
    has_openai_key: bool


class PersonaUpdateRequest(BaseModel):
    """人设更新请求"""
    persona: Dict[str, str]


class PersonaResponse(BaseModel):
    """人设响应"""
    success: bool
    persona: Optional[Dict[str, str]] = None
    message: Optional[str] = None


class PersonaUpdateRequest(BaseModel):
    """人设更新请求"""
    persona: Dict[str, str]


class PersonaResponse(BaseModel):
    """人设响应"""
    success: bool
    persona: Optional[Dict[str, str]] = None
    message: Optional[str] = None


# ========== 认证接口 ==========

@app.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    Args:
        request: 登录请求
        response: HTTP 响应对象（用于设置 Cookie）
        db: 数据库会话
        
    Returns:
        登录结果
    """
    # 查找用户
    user = crud.get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建会话
    session = create_session(db, user.id)
    
    # 设置 HTTP-only Cookie
    response.set_cookie(
        key="session_id",
        value=session.session_id,
        httponly=True,
        secure=False,  # 生产环境应设置为 True（HTTPS）
        samesite="lax",
        max_age=24 * 60 * 60  # 24 小时
    )
    
    return LoginResponse(
        success=True,
        message="登录成功",
        user=UserResponse(
            id=user.id,
            username=user.username,
            api_key=user.api_key,
            created_at=user.created_at.isoformat()
        )
    )


@app.post("/auth/logout")
async def logout(
    response: Response,
    session_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户登出
    
    Args:
        response: HTTP 响应对象（用于删除 Cookie）
        session_id: 会话 ID（从 Cookie 获取）
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        登出结果
    """
    if session_id:
        delete_session(db, session_id)
    
    # 移除该用户的 ChatBot 实例（释放内存）
    bot_manager.remove_bot_for_user(current_user.id)
    
    # 删除 Cookie
    response.delete_cookie(key="session_id")
    
    return {"success": True, "message": "已登出"}


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    
    Args:
        current_user: 当前用户（通过依赖注入获取）
        
    Returns:
        用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        api_key=current_user.api_key,
        created_at=current_user.created_at.isoformat()
    )


# ========== 管理接口（需要认证） ==========

@app.post("/admin/create_user", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 需要登录
):
    """
    创建新用户（管理接口，需要登录）
    
    Args:
        request: 创建用户请求
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的用户信息
    """
    try:
        user = crud.create_user(
            db=db,
            username=request.username,
            password=request.password,
            api_key=request.api_key
        )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            api_key=user.api_key,
            created_at=user.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@app.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 需要登录
):
    """
    获取所有用户列表（管理接口，需要登录）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        用户列表
    """
    try:
        users = crud.get_all_users(db=db, skip=skip, limit=limit)
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                api_key=user.api_key,
                created_at=user.created_at.isoformat()
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 需要登录
):
    """
    根据 ID 获取用户信息（管理接口，需要登录）
    
    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        用户信息
    """
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        api_key=user.api_key,
        created_at=user.created_at.isoformat()
    )


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


# ========== Profile API 接口 ==========

@app.get("/api/profile/api-key", response_model=ApiKeyStatusResponse)
async def get_api_key_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的 API Key 状态
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        API Key 状态（是否已配置 DeepSeek 和 OpenAI 的 Key）
    """
    # 解析 api_key 字段（可能是 JSON 字符串或单个字符串）
    api_keys = {}
    if current_user.api_key:
        try:
            # 尝试解析为 JSON
            api_keys = json.loads(current_user.api_key) if isinstance(current_user.api_key, str) else current_user.api_key
            if not isinstance(api_keys, dict):
                # 如果是单个字符串，转换为旧格式兼容
                api_keys = {"legacy": current_user.api_key}
        except (json.JSONDecodeError, TypeError):
            # 如果不是 JSON，当作单个字符串（向后兼容）
            api_keys = {"legacy": current_user.api_key}
    
    return ApiKeyStatusResponse(
        has_deepseek_key=bool(api_keys.get("deepseek")),
        has_openai_key=bool(api_keys.get("openai"))
    )


@app.post("/api/profile/api-key")
async def update_api_key(
    request: ApiKeyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的 API Key
    
    Args:
        request: API Key 更新请求（包含 provider 和 api_key）
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        更新结果
    """
    import json
    
    # 验证 provider
    if request.provider not in ["deepseek", "openai"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的 provider: {request.provider}，支持: deepseek, openai"
        )
    
    # 读取现有的 api_keys（如果有）
    api_keys = {}
    if current_user.api_key:
        try:
            api_keys = json.loads(current_user.api_key) if isinstance(current_user.api_key, str) else current_user.api_key
            if not isinstance(api_keys, dict):
                # 如果是单个字符串，转换为旧格式兼容
                api_keys = {"legacy": current_user.api_key}
        except (json.JSONDecodeError, TypeError):
            api_keys = {"legacy": current_user.api_key}
    
    # 更新指定 provider 的 key
    if request.api_key:
        api_keys[request.provider] = request.api_key
    else:
        # 清除该 provider 的 key
        api_keys.pop(request.provider, None)
        # 如果没有其他 key，清除 legacy key
        if not api_keys.get("deepseek") and not api_keys.get("openai") and "legacy" in api_keys:
            api_keys.pop("legacy", None)
    
    # 将 api_keys 转换为 JSON 字符串存储
    new_api_key_value = json.dumps(api_keys) if api_keys else None
    
    # 更新数据库
    try:
        user = crud.update_user_api_key(db, current_user.id, new_api_key_value)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return {"success": True, "message": f"{request.provider} API Key 已更新"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新 API Key 失败: {str(e)}"
        )


@app.get("/api/profile/api-key/{provider}")
async def get_api_key_for_provider(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取指定 provider 的 API Key（用于前端显示已配置的 key 的部分内容）
    
    Args:
        provider: provider 名称（deepseek 或 openai）
        current_user: 当前登录用户
    
    Returns:
        API Key 的部分显示（只显示前4位和后4位，中间用*代替）
    """
    if provider not in ["deepseek", "openai"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的 provider: {provider}"
        )
    
    api_keys = {}
    if current_user.api_key:
        try:
            api_keys = json.loads(current_user.api_key) if isinstance(current_user.api_key, str) else current_user.api_key
            if not isinstance(api_keys, dict):
                api_keys = {}
        except (json.JSONDecodeError, TypeError):
            api_keys = {}
    
    api_key = api_keys.get(provider)
    if not api_key:
        return {"has_key": False, "masked_key": None}
    
    # 只显示前4位和后4位
    if len(api_key) > 8:
        masked_key = f"{api_key[:4]}****{api_key[-4:]}"
    else:
        masked_key = "****"
    
    return {"has_key": True, "masked_key": masked_key}


# ========== 聊天API接口 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    聊天接口 - 发送消息并获取AI回复
    
    Args:
        request: 聊天请求（包含用户消息）
        current_user: 当前登录用户（通过依赖注入获取）
        
    Returns:
        聊天响应（包含AI回复或错误信息）
    """
    try:
        # 验证消息不为空
        if not request.message or not request.message.strip():
            return ChatResponse(
                success=False,
                error="消息不能为空"
            )
        
        # 判断是否是 admin 用户
        is_admin = _is_admin_user(current_user)
        
        # 获取该用户的 ChatBot 实例（admin 用户使用默认人设，传入 is_admin=True）
        bot = bot_manager.get_bot_for_user(current_user.id, is_admin=is_admin)
        
        # 从用户配置中获取对应 provider 的 API Key
        # 非 admin 用户必须配置 Key，否则会抛出 ValueError
        try:
            user_api_key = _get_user_api_key_for_provider(current_user, bot.api_provider.__class__.__name__)
        except ValueError as e:
            # 非 admin 用户未配置 Key
            return ChatResponse(
                success=False,
                error=str(e)
            )
        
        # 调用 ChatBot 处理消息（同步函数）
        # admin 用户如果没有配置 Key，user_api_key 为 None，会使用默认 Key
        # 非 admin 用户必须有 Key（已在上面检查）
        response_text = bot.chat(request.message.strip(), api_key=user_api_key)
        
        return ChatResponse(
            success=True,
            response=response_text
        )
        
    except Exception as e:
        # 记录错误日志（生产环境应使用 proper logging）
        print(f"聊天接口错误 (用户 {current_user.id}): {e}")
        return ChatResponse(
            success=False,
            error=f"处理消息时发生错误: {str(e)}"
        )


# ========== 人设API接口 ==========

@app.get("/api/persona", response_model=PersonaResponse)
async def get_persona(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的人设
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        人设信息
    """
    try:
        # 判断是否是 admin 用户
        is_admin = _is_admin_user(current_user)
        
        # 获取该用户的 ChatBot 实例（用于访问人设）
        bot = bot_manager.get_bot_for_user(current_user.id, is_admin=is_admin)
        
        # 获取人设
        persona = bot.persona_manager.get_persona()
        
        return PersonaResponse(
            success=True,
            persona=persona
        )
    except Exception as e:
        print(f"获取人设错误 (用户 {current_user.id}): {e}")
        return PersonaResponse(
            success=False,
            message=f"获取人设失败: {str(e)}"
        )


@app.post("/api/persona", response_model=PersonaResponse)
async def update_persona(
    request: PersonaUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户的人设
    
    Args:
        request: 人设更新请求
        current_user: 当前登录用户
    
    Returns:
        更新结果
    """
    try:
        # 判断是否是 admin 用户
        is_admin = _is_admin_user(current_user)
        
        # 获取该用户的 ChatBot 实例
        bot = bot_manager.get_bot_for_user(current_user.id, is_admin=is_admin)
        
        # 更新人设
        success = bot.persona_manager.update_persona(request.persona)
        
        if success:
            # 重新加载人设并更新系统消息
            bot.reload_persona()
            
            return PersonaResponse(
                success=True,
                persona=bot.persona_manager.get_persona(),
                message="人设已更新"
            )
        else:
            return PersonaResponse(
                success=False,
                message="更新人设失败"
            )
    except Exception as e:
        print(f"更新人设错误 (用户 {current_user.id}): {e}")
        return PersonaResponse(
            success=False,
            message=f"更新人设失败: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
