// API 配置
const API_BASE = '/api';
const AUTH_BASE = '/auth';

// 创建 ThemeContext（在所有组件之前定义，确保只定义一次）
if (typeof ThemeContext === 'undefined') {
    var ThemeContext = React.createContext('light');
}

// 简单的动画组件（如果 Framer Motion 未加载）
const createMotionComponent = (tag) => {
    return ({ children, initial, animate, exit, className, style, ...props }) => {
        const combinedStyle = { ...style };
        if (initial && animate) {
            // 简单的动画支持
            combinedStyle.transition = 'all 0.3s ease';
        }
        return React.createElement(tag, { className, style: combinedStyle, ...props }, children);
    };
};

// 检查 Framer Motion 是否可用（延迟初始化函数）
function getMotionComponents() {
    if (window.Motion && window.Motion.motion && window.Motion.motion.div) {
        return {
            MotionDiv: window.Motion.motion.div,
            MotionButton: window.Motion.motion.button,
            AnimatePresence: window.Motion.AnimatePresence
        };
    }
    return {
        MotionDiv: createMotionComponent('div'),
        MotionButton: createMotionComponent('button'),
        AnimatePresence: (({ children }) => children)
    };
}

// 初始化为降级版本，后续会在组件中使用时检查
let { MotionDiv, MotionButton, AnimatePresence } = getMotionComponents();

// A2UI 风格主题配置（深色/浅色模式）
const themes = {
    light: {
        name: '浅色模式',
        bg: 'bg-white',
        bgSecondary: 'bg-gray-50',
        bgTertiary: 'bg-gray-100',
        border: 'border-gray-200',
        textPrimary: 'text-gray-900',
        textSecondary: 'text-gray-600',
        textTertiary: 'text-gray-400',
        accent: 'bg-blue-600',
        accentHover: 'hover:bg-blue-700',
        accentText: 'text-blue-600',
        buttonBase: 'bg-transparent hover:bg-gray-100 text-gray-900',
        buttonPrimary: 'bg-blue-600 hover:bg-blue-700 text-white',
        input: 'bg-white border-gray-200 text-gray-900',
        inputFocus: 'focus:border-blue-500 focus:ring-blue-500',
        card: 'bg-white border-gray-200',
        messageUser: 'bg-blue-600 text-white',
        messageAssistant: 'bg-gray-100 text-gray-900',
        shadow: 'shadow-sm hover:shadow-md',
        shadowHover: 'hover:shadow-lg',
    },
    dark: {
        name: '深色模式',
        bg: 'bg-gray-900',
        bgSecondary: 'bg-gray-800',
        bgTertiary: 'bg-gray-700',
        border: 'border-gray-700',
        textPrimary: 'text-white',
        textSecondary: 'text-gray-300',
        textTertiary: 'text-gray-500',
        accent: 'bg-blue-500',
        accentHover: 'hover:bg-blue-600',
        accentText: 'text-blue-400',
        buttonBase: 'bg-transparent hover:bg-gray-800 text-white',
        buttonPrimary: 'bg-blue-500 hover:bg-blue-600 text-white',
        input: 'bg-gray-800 border-gray-700 text-white',
        inputFocus: 'focus:border-blue-500 focus:ring-blue-500',
        card: 'bg-gray-800 border-gray-700',
        messageUser: 'bg-blue-600 text-white',
        messageAssistant: 'bg-gray-700 text-gray-100',
        shadow: 'shadow-sm hover:shadow-md',
        shadowHover: 'hover:shadow-lg',
    }
};

// API 服务层（保留原有逻辑）
const apiService = {
    async checkAuth() {
        const response = await fetch(`${AUTH_BASE}/me`, { credentials: 'include' });
        return response.ok ? await response.json() : null;
    },
    
    async login(username, password) {
        const response = await fetch(`${AUTH_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password }),
        });
        return await response.json();
    },
    
    async logout() {
        await fetch(`${AUTH_BASE}/logout`, {
            method: 'POST',
            credentials: 'include',
        });
    },
    
    async chat(message) {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ message }),
        });
        return await response.json();
    },
    
    async getPersona() {
        const response = await fetch(`${API_BASE}/persona`, { credentials: 'include' });
        return await response.json();
    },
    
    async savePersona(persona) {
        const response = await fetch(`${API_BASE}/persona`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ persona }),
        });
        return await response.json();
    },
    
    async getMemory() {
        const response = await fetch(`${API_BASE}/memory`, { credentials: 'include' });
        return await response.json();
    },
    
    async summarize() {
        const response = await fetch(`${API_BASE}/summarize`, {
            method: 'POST',
            credentials: 'include',
        });
        return await response.json();
    },
    
    async clearHistory() {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'POST',
            credentials: 'include',
        });
        return await response.json();
    },
    
    async getApiKeyStatus() {
        const response = await fetch(`${API_BASE}/profile/api-key`, { credentials: 'include' });
        return await response.json();
    },
    
    async getApiKeyMasked(provider) {
        const response = await fetch(`${API_BASE}/profile/api-key/${provider}`, { credentials: 'include' });
        return await response.json();
    },
    
    async saveApiKey(provider, apiKey) {
        const response = await fetch(`${API_BASE}/profile/api-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ provider, api_key: apiKey || null }),
        });
        return await response.json();
    },
};

// 登录组件
function LoginPage({ onLoginSuccess, theme = 'light' }) {
    const t = themes[theme] || themes['light'];
    const [username, setUsername] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [error, setError] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        try {
            const data = await apiService.login(username, password);
            if (data.success) {
                onLoginSuccess(data.user);
            } else {
                setError(data.detail || '登录失败，请检查用户名和密码');
            }
        } catch (err) {
            setError(`网络错误: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className={`min-h-screen flex items-center justify-center p-4 ${t.bg}`}>
            <MotionDiv
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`w-full max-w-md ${t.card} border rounded-3xl p-10 ${t.shadow}`}
            >
                <h1 className={`text-3xl font-semibold text-center mb-8 ${t.textPrimary}`}>
                    AI聊天机器人
                </h1>
                <form onSubmit={handleSubmit}>
                    <div className="mb-5">
                        <label className={`block mb-2 text-sm font-medium ${t.textPrimary}`}>
                            用户名
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className={`w-full px-4 py-3 rounded-xl ${t.input} ${t.inputFocus} border focus:outline-none focus:ring-2 transition-all`}
                            required
                            autoComplete="username"
                            placeholder="输入用户名"
                        />
                    </div>
                    <div className="mb-6">
                        <label className={`block mb-2 text-sm font-medium ${t.textPrimary}`}>
                            密码
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={`w-full px-4 py-3 rounded-xl ${t.input} ${t.inputFocus} border focus:outline-none focus:ring-2 transition-all`}
                            required
                            autoComplete="current-password"
                            placeholder="输入密码"
                        />
                    </div>
                    {error && (
                        <MotionDiv
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className={`mb-4 p-3 rounded-xl text-sm ${
                                theme === 'dark' 
                                    ? 'bg-red-900/30 border border-red-800 text-red-300' 
                                    : 'bg-red-50 border border-red-200 text-red-600'
                            }`}
                        >
                            {error}
                        </MotionDiv>
                    )}
                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 rounded-xl ${t.buttonPrimary} font-medium transition-all ${t.shadowHover} disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {loading ? (
                            <span className="flex items-center justify-center">
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                                登录中...
                            </span>
                        ) : (
                            '登录'
                        )}
                    </button>
                </form>
                <p className={`text-center mt-6 text-sm ${t.textSecondary}`}>
                    还没有账号？请联系管理员创建
                </p>
            </MotionDiv>
        </div>
    );
}

// 主应用组件
function App() {
    const [user, setUser] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [currentPage, setCurrentPage] = React.useState('chat');
    const [theme, setTheme] = React.useState(() => {
        const savedTheme = localStorage.getItem('theme');
        // 确保主题值是有效的
        return (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) ? savedTheme : 'light';
    });
    
    // 获取当前主题配置，添加安全检查
    const getThemeConfig = (themeName) => {
        if (!themeName || !themes[themeName]) {
            return themes['light']; // 默认使用浅色模式
        }
        return themes[themeName];
    };
    
    const t = getThemeConfig(theme);
    
    React.useEffect(() => {
        checkAuth();
    }, []);
    
    React.useEffect(() => {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);
    
    const checkAuth = async () => {
        try {
            const userData = await apiService.checkAuth();
            if (userData) {
                setUser(userData);
            }
        } catch (err) {
            console.error('检查认证状态失败:', err);
        } finally {
            setLoading(false);
        }
    };
    
    const handleLoginSuccess = (userData) => {
        setUser(userData);
    };
    
    const handleLogout = async () => {
        if (window.confirm('确定要登出吗？')) {
            await apiService.logout();
            setUser(null);
            setCurrentPage('chat');
        }
    };
    
    if (loading) {
        return (
            <div className={`min-h-screen flex items-center justify-center ${t.bg}`}>
                <div className={`${t.textPrimary} text-xl`}>加载中...</div>
            </div>
        );
    }
    
    if (!user) {
        return (
            <ThemeContext.Provider value={theme}>
                <LoginPage onLoginSuccess={handleLoginSuccess} theme={theme} />
            </ThemeContext.Provider>
        );
    }
    
    return (
        <ThemeContext.Provider value={theme}>
            <div className={`min-h-screen ${t.bg} transition-colors`}>
                <div className="flex h-screen">
                    {/* 侧边栏 */}
                    <Sidebar
                        user={user}
                        currentPage={currentPage}
                        onPageChange={setCurrentPage}
                        onLogout={handleLogout}
                        theme={theme}
                        setTheme={setTheme}
                    />
                    
                    {/* 主内容区 */}
                    <MainContent
                        currentPage={currentPage}
                        user={user}
                        theme={theme}
                        setTheme={setTheme}
                    />
                </div>
            </div>
        </ThemeContext.Provider>
    );
}

// Sidebar 组件（A2UI 风格）
function Sidebar({ user, currentPage, onPageChange, onLogout, theme, setTheme }) {
    const t = themes[theme];
    const menuItems = [
        { id: 'chat', label: '聊天', icon: '💬' },
        { id: 'persona', label: '人设', icon: '👤' },
        { id: 'memory', label: '记忆', icon: '💝' },
        { id: 'settings', label: '设置', icon: '⚙️' },
    ];
    
    return (
        <div className={`w-64 ${t.bgSecondary} border-r ${t.border} flex flex-col h-screen transition-colors`}>
            <div className={`p-6 border-b ${t.border}`}>
                <h2 className={`text-xl font-semibold ${t.textPrimary} mb-3`}>
                    AI聊天机器人
                </h2>
                <div className={`${t.textSecondary} text-sm mb-3`}>
                    用户: <span className={`${t.textPrimary} font-medium`}>{user.username}</span>
                </div>
                <button
                    onClick={onLogout}
                    className={`text-sm px-4 py-2 rounded-xl ${t.buttonBase} transition-all ${t.shadowHover}`}
                >
                    登出
                </button>
            </div>
            
            <nav className="flex-1 p-3">
                {menuItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => onPageChange(item.id)}
                        className={`w-full text-left px-4 py-3 mb-1 rounded-xl transition-all ${
                            currentPage === item.id
                                ? `${t.accent} text-white ${t.shadow}`
                                : `${t.buttonBase} ${t.shadowHover}`
                        }`}
                    >
                        <span className="mr-2">{item.icon}</span>
                        {item.label}
                    </button>
                ))}
            </nav>
            
            <div className={`p-3 border-t ${t.border} space-y-2`}>
                <ClearHistoryButton theme={theme} />
                <SummarizeButton theme={theme} currentPage={currentPage} />
            </div>
        </div>
    );
}

// 清空历史按钮（A2UI 风格）
function ClearHistoryButton({ theme }) {
    const [loading, setLoading] = React.useState(false);
    const t = themes[theme];
    
    const handleClear = async () => {
        if (!window.confirm('确定要清空对话历史吗？')) return;
        setLoading(true);
        try {
            const data = await apiService.clearHistory();
            if (data.success) {
                window.alert('历史已清空');
                window.location.reload();
            } else {
                window.alert('清空失败，请重试。');
            }
        } catch (err) {
            window.alert(`清空失败: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <button
            onClick={handleClear}
            disabled={loading}
            className={`w-full px-4 py-2.5 rounded-xl ${t.buttonBase} text-sm transition-all ${t.shadowHover} disabled:opacity-50`}
        >
            {loading ? '清空中...' : '清空历史'}
        </button>
    );
}

// 总结按钮（A2UI 风格）
function SummarizeButton({ theme, currentPage }) {
    const [loading, setLoading] = React.useState(false);
    const t = themes[theme];
    
    const handleSummarize = async () => {
        setLoading(true);
        try {
            const data = await apiService.summarize();
            window.alert(data.message || (data.success ? '总结完成' : '总结失败'));
            if (data.success && currentPage === 'memory') {
                window.location.reload();
            }
        } catch (err) {
            window.alert(`总结失败: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <button
            onClick={handleSummarize}
            disabled={loading}
            className={`w-full px-4 py-2.5 rounded-xl ${t.buttonBase} text-sm transition-all ${t.shadowHover} disabled:opacity-50`}
        >
            {loading ? '总结中...' : '总结对话'}
        </button>
    );
}

// 主内容区组件
function MainContent({ currentPage, user, theme, setTheme }) {
    const t = themes[theme];
    
    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            <AnimatePresence mode="wait">
                {currentPage === 'chat' && (
                    <ChatPage key="chat" theme={theme} />
                )}
                {currentPage === 'persona' && (
                    <PersonaPage key="persona" theme={theme} />
                )}
                {currentPage === 'memory' && (
                    <MemoryPage key="memory" theme={theme} />
                )}
                {currentPage === 'settings' && (
                    <SettingsPage key="settings" theme={theme} setTheme={setTheme} />
                )}
            </AnimatePresence>
        </div>
    );
}

// 聊天页面组件（A2UI 风格）
function ChatPage({ theme }) {
    const [messages, setMessages] = React.useState([
        { id: 'welcome', role: 'system', content: '欢迎使用 AI 聊天机器人！开始对话吧。' }
    ]);
    const [input, setInput] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const messagesEndRef = React.useRef(null);
    const t = themes[theme];
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    
    React.useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    const handleSend = async () => {
        if (!input.trim() || loading) return;
        
        const userMessage = { id: Date.now(), role: 'user', content: input.trim() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        
        const loadingMessage = { id: Date.now() + 1, role: 'assistant', content: '思考中...', loading: true };
        setMessages(prev => [...prev, loadingMessage]);
        
        try {
            const data = await apiService.chat(userMessage.content);
            setMessages(prev => {
                const newMessages = prev.filter(m => !m.loading);
                if (data.success) {
                    return [...newMessages, { id: Date.now() + 2, role: 'assistant', content: data.response }];
                } else {
                    const errorMsg = data.error || '未知错误';
                    return [...newMessages, { id: Date.now() + 2, role: 'assistant', content: `错误: ${errorMsg}` }];
                }
            });
        } catch (err) {
            setMessages(prev => {
                const newMessages = prev.filter(m => !m.loading);
                return [...newMessages, { id: Date.now() + 2, role: 'assistant', content: `网络错误: ${err.message}` }];
            });
        } finally {
            setLoading(false);
        }
    };
    
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };
    
    return (
        <div className="flex-1 flex flex-col h-full">
            <div className={`flex-1 overflow-y-auto p-6 ${t.bg} transition-colors`}>
                <div className="max-w-4xl mx-auto space-y-4">
                    {messages.map((msg) => (
                        <MotionDiv
                            key={msg.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                                    msg.role === 'user'
                                        ? `${t.messageUser}`
                                        : msg.role === 'system'
                                        ? `${t.bgSecondary} ${t.textSecondary} text-sm`
                                        : `${t.messageAssistant}`
                                }`}
                            >
                                {msg.loading ? (
                                    <div className="flex items-center">
                                        <div className={`w-4 h-4 border-2 ${theme === 'dark' ? 'border-gray-600' : 'border-gray-300'} ${t.accentText.replace('text-', 'border-t-')} rounded-full animate-spin mr-2`}></div>
                                        思考中...
                                    </div>
                                ) : (
                                    <div className="whitespace-pre-wrap">{msg.content}</div>
                                )}
                            </div>
                        </MotionDiv>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
            </div>
            
            <div className={`p-4 border-t ${t.border} ${t.bg} transition-colors`}>
                <div className="max-w-4xl mx-auto flex gap-3">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="输入消息... (Enter发送, Shift+Enter换行)"
                        rows="2"
                        disabled={loading}
                        className={`flex-1 px-4 py-3 rounded-xl ${t.input} ${t.inputFocus} border resize-none focus:outline-none focus:ring-2 transition-all disabled:opacity-50`}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className={`px-6 py-3 rounded-xl ${t.buttonPrimary} font-medium ${t.shadowHover} disabled:opacity-50 disabled:cursor-not-allowed transition-all`}
                    >
                        发送
                    </button>
                </div>
            </div>
        </div>
    );
}

// 人设页面组件（A2UI 风格）
function PersonaPage({ theme }) {
    const [persona, setPersona] = React.useState({
        任务: '', 角色: '', 外表: '', 经历: '', 性格: '', 喜好: '', 经典台词: '', 输出示例: '', 备注: ''
    });
    const [loading, setLoading] = React.useState(false);
    const [saving, setSaving] = React.useState(false);
    const t = themes[theme];
    
    React.useEffect(() => {
        loadPersona();
    }, []);
    
    const loadPersona = async () => {
        setLoading(true);
        try {
            const data = await apiService.getPersona();
            if (data.success && data.persona) {
                setPersona(data.persona);
            }
        } catch (err) {
            console.error('加载人设失败:', err);
        } finally {
            setLoading(false);
        }
    };
    
    const handleSave = async () => {
        setSaving(true);
        try {
            const data = await apiService.savePersona(persona);
            if (data.success) {
                window.alert('人设保存成功！新的对话将使用更新后的人设。');
                await loadPersona();
            } else {
                window.alert(`保存失败: ${data.message || '请重试'}`);
            }
        } catch (err) {
            window.alert(`保存失败: ${err.message}`);
        } finally {
            setSaving(false);
        }
    };
    
    const fields = [
        { key: '任务', rows: 2 },
        { key: '角色', rows: 2 },
        { key: '外表', rows: 2 },
        { key: '经历', rows: 3 },
        { key: '性格', rows: 2 },
        { key: '喜好', rows: 2 },
        { key: '经典台词', rows: 2 },
        { key: '输出示例', rows: 3 },
        { key: '备注', rows: 2 },
    ];
    
    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className={`${t.textPrimary} text-xl`}>加载中...</div>
            </div>
        );
    }
    
    return (
        <div className={`flex-1 overflow-y-auto p-6 ${t.bg} transition-colors`}>
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className={`text-2xl font-semibold ${t.textPrimary}`}>人设管理</h2>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className={`px-6 py-2.5 rounded-xl ${t.buttonPrimary} font-medium ${t.shadowHover} disabled:opacity-50 transition-all`}
                    >
                        {saving ? '保存中...' : '保存人设'}
                    </button>
                </div>
                
                <div className={`${t.card} border rounded-2xl p-6 space-y-5 transition-colors`}>
                    {fields.map((field) => (
                        <div key={field.key}>
                            <label className={`block mb-2 text-sm font-medium ${t.textPrimary}`}>
                                {field.key}
                            </label>
                            <textarea
                                value={persona[field.key] || ''}
                                onChange={(e) => setPersona({ ...persona, [field.key]: e.target.value })}
                                rows={field.rows}
                                className={`w-full px-4 py-3 rounded-xl ${t.input} ${t.inputFocus} border resize-none focus:outline-none focus:ring-2 transition-all`}
                            />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

// 记忆页面组件（A2UI 风格）
function MemoryPage({ theme }) {
    const [memories, setMemories] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const t = themes[theme];
    
    React.useEffect(() => {
        loadMemory();
    }, []);
    
    const loadMemory = async () => {
        setLoading(true);
        try {
            const data = await apiService.getMemory();
            if (data.success) {
                setMemories(data.memories);
            } else {
                setMemories({});
            }
        } catch (err) {
            console.error('加载记忆失败:', err);
            setMemories({});
        } finally {
            setLoading(false);
        }
    };
    
    const typeNames = {
        personal_profile: '个人档案',
        preference: '偏好',
        relationship: '重要关系',
        important_event: '重要事件',
        plan: '约定与计划',
        long_term_goal: '长期目标',
        other: '其他',
        notes_for_future: '未来对话建议',
    };
    
    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className={`${t.textPrimary} text-xl`}>加载中...</div>
            </div>
        );
    }
    
    if (!memories) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <div className={`${t.textSecondary} text-lg`}>加载失败</div>
            </div>
        );
    }
    
    let hasContent = false;
    const memorySections = [];
    
    for (const [type, items] of Object.entries(memories)) {
        if (type === 'conversation_summaries') continue;
        
        if (type === 'notes_for_future') {
            if (items && items.trim()) {
                hasContent = true;
                memorySections.push(
                    <div key={type} className={`${t.card} border rounded-2xl p-6 mb-4 transition-colors`}>
                        <h3 className={`text-lg font-semibold mb-4 ${t.textPrimary}`}>
                            {typeNames[type] || type}
                        </h3>
                        <div className={`${t.textSecondary} whitespace-pre-wrap text-sm leading-relaxed`}>{items}</div>
                    </div>
                );
            }
        } else if (Array.isArray(items) && items.length > 0) {
            hasContent = true;
            memorySections.push(
                <div key={type} className={`${t.card} border rounded-2xl p-6 mb-4 transition-colors`}>
                    <h3 className={`text-lg font-semibold mb-4 ${t.textPrimary}`}>
                        {typeNames[type] || type}
                    </h3>
                    <div className="space-y-3">
                        {items.map((mem, idx) => (
                            <div key={idx} className={`${t.textSecondary} border-l-4 pl-4 ${theme === 'dark' ? 'border-l-blue-500' : 'border-l-blue-600'}`}>
                                <div className="mb-1 text-sm">{mem.content || ''}</div>
                                {mem.reason && (
                                    <div className={`text-xs ${t.textTertiary} mt-1`}>
                                        原因: {mem.reason}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            );
        }
    }
    
    return (
        <div className={`flex-1 overflow-y-auto p-6 ${t.bg} transition-colors`}>
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className={`text-2xl font-semibold ${t.textPrimary}`}>长期记忆</h2>
                    <button
                        onClick={loadMemory}
                        className={`px-4 py-2.5 rounded-xl ${t.buttonBase} text-sm transition-all ${t.shadowHover}`}
                    >
                        刷新
                    </button>
                </div>
                
                {hasContent ? (
                    <div>{memorySections}</div>
                ) : (
                    <div className={`${t.card} border rounded-2xl p-12 text-center transition-colors`}>
                        <div className={`${t.textSecondary} text-lg`}>暂无长期记忆</div>
                    </div>
                )}
            </div>
        </div>
    );
}

// 设置页面组件（A2UI 风格）
function SettingsPage({ theme, setTheme }) {
    const [apiKeys, setApiKeys] = React.useState({
        deepseek: { value: '', status: null, masked: null },
        openai: { value: '', status: null, masked: null },
    });
    const [loading, setLoading] = React.useState(true);
    const [saving, setSaving] = React.useState({});
    const t = themes[theme];
    
    React.useEffect(() => {
        loadApiKeyStatus();
    }, []);
    
    const loadApiKeyStatus = async () => {
        setLoading(true);
        try {
            const status = await apiService.getApiKeyStatus();
            const newKeys = { ...apiKeys };
            
            for (const provider of ['deepseek', 'openai']) {
                const hasKey = status[`has_${provider}_key`] || false;
                newKeys[provider].status = hasKey;
                if (hasKey) {
                    const masked = await apiService.getApiKeyMasked(provider);
                    newKeys[provider].masked = masked.masked_key;
                }
            }
            setApiKeys(newKeys);
        } catch (err) {
            console.error('加载 API Key 状态失败:', err);
        } finally {
            setLoading(false);
        }
    };
    
    const handleSave = async (provider) => {
        setSaving({ ...saving, [provider]: true });
        try {
            const data = await apiService.saveApiKey(provider, apiKeys[provider].value);
            if (data.success) {
                window.alert('API Key 保存成功！');
                setApiKeys({ ...apiKeys, [provider]: { ...apiKeys[provider], value: '' } });
                await loadApiKeyStatus();
            } else {
                window.alert(`保存失败: ${data.detail || '未知错误'}`);
            }
        } catch (err) {
            window.alert(`保存失败: ${err.message}`);
        } finally {
            setSaving({ ...saving, [provider]: false });
        }
    };
    
    const handleClear = async (provider) => {
        if (!window.confirm(`确定要清除 ${provider.toUpperCase()} API Key 吗？`)) return;
        setSaving({ ...saving, [provider]: true });
        try {
            const data = await apiService.saveApiKey(provider, null);
            if (data.success) {
                window.alert('API Key 已清除');
                await loadApiKeyStatus();
            } else {
                window.alert(`清除失败: ${data.detail || '未知错误'}`);
            }
        } catch (err) {
            window.alert(`清除失败: ${err.message}`);
        } finally {
            setSaving({ ...saving, [provider]: false });
        }
    };
    
    return (
        <div className={`flex-1 overflow-y-auto p-6 ${t.bg} transition-colors`}>
            <div className="max-w-4xl mx-auto space-y-6">
                <h2 className={`text-2xl font-semibold ${t.textPrimary}`}>设置</h2>
                
                {/* 主题选择 */}
                <div className={`${t.card} border rounded-2xl p-6 transition-colors`}>
                    <h3 className={`text-lg font-semibold mb-4 ${t.textPrimary}`}>主题设置</h3>
                    <div className="grid grid-cols-2 gap-3">
                        {Object.entries(themes).map(([key, themeData]) => (
                            <button
                                key={key}
                                onClick={() => setTheme(key)}
                                className={`p-4 rounded-xl border-2 transition-all ${
                                    theme === key
                                        ? `${t.accent} border-transparent text-white ${t.shadow}`
                                        : `${t.card} ${t.border} ${t.textPrimary} hover:${t.bgSecondary} ${t.shadowHover}`
                                }`}
                            >
                                <div className="font-medium">{themeData.name}</div>
                            </button>
                        ))}
                    </div>
                </div>
                
                {/* API Key 设置 */}
                {['deepseek', 'openai'].map((provider) => (
                    <div key={provider} className={`${t.card} border rounded-2xl p-6 transition-colors`}>
                        <h3 className={`text-lg font-semibold mb-2 ${t.textPrimary}`}>
                            {provider === 'deepseek' ? 'DeepSeek' : 'OpenAI'} API Key
                        </h3>
                        <p className={`text-sm mb-4 ${t.textSecondary}`}>
                            配置你的 {provider === 'deepseek' ? 'DeepSeek' : 'OpenAI'} API Key
                        </p>
                        <div className="space-y-4">
                            <div>
                                <input
                                    type="password"
                                    value={apiKeys[provider].value}
                                    onChange={(e) => setApiKeys({
                                        ...apiKeys,
                                        [provider]: { ...apiKeys[provider], value: e.target.value }
                                    })}
                                    placeholder={`输入 ${provider === 'deepseek' ? 'DeepSeek' : 'OpenAI'} API Key`}
                                    className={`w-full px-4 py-3 rounded-xl ${t.input} ${t.inputFocus} border focus:outline-none focus:ring-2 transition-all`}
                                />
                                {apiKeys[provider].status && apiKeys[provider].masked && (
                                    <div className={`mt-2 text-sm ${t.textSecondary}`}>
                                        已配置: {apiKeys[provider].masked}
                                    </div>
                                )}
                                {apiKeys[provider].status === false && (
                                    <div className={`mt-2 text-sm ${t.textSecondary}`}>
                                        未配置（将使用系统默认 Key）
                                    </div>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => handleSave(provider)}
                                    disabled={saving[provider]}
                                    className={`px-6 py-2.5 rounded-xl ${t.buttonPrimary} font-medium ${t.shadowHover} disabled:opacity-50 transition-all`}
                                >
                                    {saving[provider] ? '保存中...' : '保存'}
                                </button>
                                <button
                                    onClick={() => handleClear(provider)}
                                    disabled={saving[provider]}
                                    className={`px-6 py-2.5 rounded-xl ${t.buttonBase} font-medium ${t.shadowHover} disabled:opacity-50 transition-all`}
                                >
                                    清除
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// 渲染应用（React 18 方式）
// 等待所有脚本加载完成后再渲染
function renderApp() {
    try {
        const rootElement = document.getElementById('root');
        if (!rootElement) {
            console.error('Root element not found');
            return;
        }
        
        // 检查 React 是否已加载
        if (typeof React === 'undefined' || typeof ReactDOM === 'undefined') {
            console.error('React or ReactDOM not loaded');
            rootElement.innerHTML = '<div style="color: white; padding: 20px; text-align: center;"><h2>React 未加载</h2><p>请刷新页面重试</p></div>';
            return;
        }
        
        // 确保 ThemeContext 只定义一次
        if (!window.__ThemeContextInitialized) {
            window.__ThemeContextInitialized = true;
        }
        
        const root = ReactDOM.createRoot(rootElement);
        root.render(React.createElement(App));
    } catch (error) {
        console.error('Render error:', error);
        const rootElement = document.getElementById('root');
        if (rootElement) {
            rootElement.innerHTML = '<div style="color: white; padding: 20px; text-align: center;"><h2>应用加载错误</h2><p>请检查浏览器控制台</p><pre style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; text-align: left; overflow: auto;">' + error.toString() + '</pre></div>';
        }
    }
}

// 等待所有脚本加载完成
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // 延迟一点确保所有 CDN 脚本都加载完成
        setTimeout(renderApp, 200);
    });
} else {
    setTimeout(renderApp, 200);
}
