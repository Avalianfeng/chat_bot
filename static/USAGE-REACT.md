# React + TailwindCSS 前端使用说明

## 文件说明

1. **`index-react.html`** - 新的 HTML 入口文件
   - 使用 CDN 方式引入 React、TailwindCSS、Framer Motion
   - 包含主题样式定义
   - 根元素 `<div id="root"></div>`

2. **`app-react.jsx`** - React 应用主文件
   - 包含所有组件和业务逻辑
   - API 服务层（保留原有逻辑）
   - 主题系统（科技感、暖樱花感）
   - 所有页面组件

## 使用方法

### 方法 1：替换现有前端（推荐）

1. 备份原有文件：
   ```bash
   cp static/index.html static/index.html.backup
   cp static/app.js static/app.js.backup
   ```

2. 重命名新文件：
   ```bash
   mv static/index-react.html static/index.html
   mv static/app-react.jsx static/app.jsx
   ```

3. 修改 `web_app.py` 中的路由（如果需要）：
   - 确保静态文件路由指向正确的文件

### 方法 2：并存在不同路径

保持两个版本并存，通过修改后端路由来切换。

## 功能特性

### ✅ 已实现功能

1. **登录页面**
   - 美观的登录表单
   - 错误提示
   - 加载动画

2. **主应用界面**
   - 左侧侧边栏导航
   - 用户信息显示
   - 登出功能

3. **聊天页面**
   - 消息气泡（用户/AI）
   - 消息输入框（支持 Enter 发送、Shift+Enter 换行）
   - 加载状态动画
   - 消息滚动到底部

4. **人设页面**
   - 完整的人设表单
   - 保存功能
   - 加载/保存状态

5. **记忆页面**
   - 长期记忆展示
   - 按类型分组显示
   - 刷新功能

6. **设置页面**
   - 主题切换（科技感、暖樱花感）
   - API Key 配置（DeepSeek、OpenAI）
   - 保存/清除功能

7. **主题系统**
   - 科技感：蓝紫渐变、玻璃拟态、未来感
   - 暖樱花感：粉色、柔和、温暖
   - 主题切换自动保存到 localStorage

8. **动画效果**
   - 页面切换动画
   - 消息发送动画
   - 按钮悬停效果
   - 加载动画

## 技术栈

- **React 18** - UI 框架（CDN）
- **TailwindCSS** - 样式框架（CDN）
- **Framer Motion** - 动画库（CDN，有降级方案）
- **Babel Standalone** - JSX 转译（CDN）

## 浏览器兼容性

- Chrome/Edge（推荐）
- Firefox
- Safari
- 需要支持 ES6+ 和现代 JavaScript 特性

## 注意事项

1. **CDN 依赖**：应用依赖外部 CDN，确保网络连接正常
2. **Framer Motion**：如果 CDN 加载失败，会自动降级到简单动画
3. **主题切换**：主题偏好保存在 localStorage 中
4. **API 调用**：所有 API 调用逻辑与原有版本保持一致

## 扩展主题

要添加新主题，在 `app-react.jsx` 的 `themes` 对象中添加：

```javascript
const themes = {
    // ... 现有主题
    newTheme: {
        name: '新主题名称',
        gradient: 'from-color1 to-color2',
        cardBg: 'bg-white/10',
        // ... 其他样式配置
    }
};
```

## 故障排除

1. **页面空白**：检查浏览器控制台是否有错误
2. **样式未加载**：检查 TailwindCSS CDN 是否可访问
3. **动画不工作**：检查 Framer Motion CDN 是否加载成功（会自动降级）

## 后续优化建议

1. 将 React 应用构建为生产版本（使用 webpack/vite）
2. 将 TailwindCSS 编译为独立 CSS 文件
3. 添加更多主题选项
4. 优化移动端体验
5. 添加暗色模式
