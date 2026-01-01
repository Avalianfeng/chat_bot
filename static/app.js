// API 基础 URL
const API_BASE = '/api';

// 当前页面
let currentPage = 'chat';

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadPersona();
    loadMemory();
});

// 初始化事件监听器
function initEventListeners() {
    // 菜单切换
    document.querySelectorAll('.menu-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            switchPage(page);
        });
    });

    // 发送消息
    const sendBtn = document.getElementById('sendBtn');
    const chatInput = document.getElementById('chatInput');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 保存人设
    document.getElementById('savePersonaBtn').addEventListener('click', savePersona);

    // 刷新记忆
    document.getElementById('refreshMemoryBtn').addEventListener('click', loadMemory);

    // 清空历史
    document.getElementById('clearBtn').addEventListener('click', clearHistory);

    // 总结对话
    document.getElementById('summarizeBtn').addEventListener('click', summarizeConversation);
}

// 切换页面
function switchPage(page) {
    currentPage = page;
    
    // 更新菜单按钮状态
    document.querySelectorAll('.menu-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === page);
    });

    // 显示对应页面
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `${page}-page`);
    });

    // 如果切换到记忆页面，刷新记忆
    if (page === 'memory') {
        loadMemory();
    }
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;

    // 禁用输入
    input.disabled = true;
    document.getElementById('sendBtn').disabled = true;

    // 添加用户消息到界面
    addMessage('user', message);
    input.value = '';

    // 显示加载状态
    const loadingId = addMessage('assistant', '思考中...', true);

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        // 移除加载消息
        removeMessage(loadingId);

        if (data.success) {
            addMessage('assistant', data.response);
        } else {
            addMessage('assistant', `错误: ${data.error || '未知错误'}`);
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('assistant', `网络错误: ${error.message}`);
    } finally {
        // 恢复输入
        input.disabled = false;
        document.getElementById('sendBtn').disabled = false;
        input.focus();
    }
}

// 添加消息到界面
function addMessage(role, content, isLoading = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const messageId = `msg-${Date.now()}-${Math.random()}`;
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

// 移除消息
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// 加载人设
async function loadPersona() {
    try {
        const response = await fetch(`${API_BASE}/persona`);
        const data = await response.json();
        
        if (data.success) {
            const persona = data.persona;
            document.getElementById('persona-task').value = persona.任务 || '';
            document.getElementById('persona-role').value = persona.角色 || '';
            document.getElementById('persona-appearance').value = persona.外表 || '';
            document.getElementById('persona-experience').value = persona.经历 || '';
            document.getElementById('persona-personality').value = persona.性格 || '';
            document.getElementById('persona-preference').value = persona.喜好 || '';
            document.getElementById('persona-catchphrase').value = persona.经典台词 || '';
            document.getElementById('persona-example').value = persona.输出示例 || '';
            document.getElementById('persona-note').value = persona.备注 || '';
        }
    } catch (error) {
        console.error('加载人设失败:', error);
    }
}

// 保存人设
async function savePersona() {
    const persona = {
        任务: document.getElementById('persona-task').value,
        角色: document.getElementById('persona-role').value,
        外表: document.getElementById('persona-appearance').value,
        经历: document.getElementById('persona-experience').value,
        性格: document.getElementById('persona-personality').value,
        喜好: document.getElementById('persona-preference').value,
        经典台词: document.getElementById('persona-catchphrase').value,
        输出示例: document.getElementById('persona-example').value,
        备注: document.getElementById('persona-note').value,
    };

    try {
        const response = await fetch(`${API_BASE}/persona`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ persona }),
        });

        const data = await response.json();
        
        if (data.success) {
            alert('人设保存成功！新的对话将使用更新后的人设。');
        } else {
            alert('保存失败，请重试。');
        }
    } catch (error) {
        alert(`保存失败: ' + error.message`);
    }
}

// 加载记忆
async function loadMemory() {
    const container = document.getElementById('memoryContainer');
    container.innerHTML = '<div class="loading">加载中...</div>';

    try {
        const response = await fetch(`${API_BASE}/memory`);
        const data = await response.json();
        
        if (data.success) {
            displayMemory(data.memories);
        } else {
            container.innerHTML = '<div class="memory-empty">加载失败</div>';
        }
    } catch (error) {
        container.innerHTML = `<div class="memory-empty">加载失败: ${error.message}</div>`;
    }
}

// 显示记忆
function displayMemory(memories) {
    const container = document.getElementById('memoryContainer');
    container.innerHTML = '';

    const typeNames = {
        personal_profile: '个人档案',
        preference: '偏好',
        relationship: '重要关系',
        important_event: '重要事件',
        plan: '约定与计划',
        long_term_goal: '长期目标',
        other: '其他',
        notes_for_future: '未来对话建议'
    };

    let hasContent = false;

    // 显示各类记忆
    for (const [type, items] of Object.entries(memories)) {
        if (type === 'conversation_summaries') continue;
        
        if (type === 'notes_for_future') {
            if (items && items.trim()) {
                hasContent = true;
                const section = createMemorySection(typeNames[type] || type);
                const item = document.createElement('div');
                item.className = 'memory-item';
                item.innerHTML = `<div class="memory-item-content">${escapeHtml(items)}</div>`;
                section.appendChild(item);
                container.appendChild(section);
            }
        } else if (Array.isArray(items) && items.length > 0) {
            hasContent = true;
            const section = createMemorySection(typeNames[type] || type);
            
            items.forEach(mem => {
                const item = document.createElement('div');
                item.className = 'memory-item';
                
                let html = `<div class="memory-item-content">${escapeHtml(mem.content || '')}</div>`;
                if (mem.reason) {
                    html += `<div class="memory-item-reason">原因: ${escapeHtml(mem.reason)}</div>`;
                }
                
                item.innerHTML = html;
                section.appendChild(item);
            });
            
            container.appendChild(section);
        }
    }

    if (!hasContent) {
        container.innerHTML = '<div class="memory-empty">暂无长期记忆</div>';
    }
}

// 创建记忆区块
function createMemorySection(title) {
    const section = document.createElement('div');
    section.className = 'memory-section';
    const h3 = document.createElement('h3');
    h3.textContent = title;
    section.appendChild(h3);
    return section;
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 清空历史
async function clearHistory() {
    if (!confirm('确定要清空对话历史吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'POST',
        });

        const data = await response.json();
        
        if (data.success) {
            // 清空聊天界面
            const messagesContainer = document.getElementById('chatMessages');
            messagesContainer.innerHTML = '<div class="message system-message"><div class="message-content">历史已清空，开始新的对话吧。</div></div>';
            alert('历史已清空');
        } else {
            alert('清空失败，请重试。');
        }
    } catch (error) {
        alert(`清空失败: ${error.message}`);
    }
}

// 总结对话
async function summarizeConversation() {
    const btn = document.getElementById('summarizeBtn');
    btn.disabled = true;
    btn.textContent = '总结中...';

    try {
        const response = await fetch(`${API_BASE}/summarize`, {
            method: 'POST',
        });

        const data = await response.json();
        alert(data.message || (data.success ? '总结完成' : '总结失败'));
        
        // 如果成功，刷新记忆页面
        if (data.success && currentPage === 'memory') {
            loadMemory();
        }
    } catch (error) {
        alert(`总结失败: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = '总结对话';
    }
}

