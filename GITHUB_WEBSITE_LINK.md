# GitHub 项目与网站关联指南

## 📌 概述

即使没有域名，也可以通过多种方式将 GitHub 项目与你的网站关联起来。以下是几种常用方法：

## 🔗 方法一：在 GitHub 仓库描述中添加网站链接（推荐）

### 步骤

1. **进入你的 GitHub 仓库页面**
   - 访问：https://github.com/Avalianfeng/chat_bot

2. **点击仓库名称旁边的设置图标（⚙️）或直接点击 "Settings"**

3. **在仓库描述中添加网站链接**
   - 在仓库主页的顶部，编辑仓库描述
   - 添加：`🌐 在线体验：http://47.100.198.51:8000/`
   - 或者使用更详细的描述：
     ```
     AI聊天机器人 - 多用户Web版本 | 🌐 在线体验：http://47.100.198.51:8000/
     ```

4. **在 README 顶部添加徽章（可选）**
   ```markdown
   ![Website](https://img.shields.io/website?url=http://47.100.198.51:8000&label=在线体验)
   [![GitHub](https://img.shields.io/github/license/Avalianfeng/chat_bot)](https://github.com/Avalianfeng/chat_bot)
   ```

## 🔗 方法二：使用 GitHub Topics（标签）

### 步骤

1. **在仓库页面点击 Topics 图标**（通常在仓库描述下方）
2. **添加相关标签**：
   - `ai-chatbot`
   - `fastapi`
   - `web-app`
   - `deployed`（表示已部署）

## 🔗 方法三：在 GitHub Pages 中创建简单的重定向页面（如果使用域名）

如果你将来有了域名，可以在 GitHub Pages 创建一个简单的重定向页面：

### 步骤

1. **在仓库中创建 `docs/index.html`**：
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="UTF-8">
       <meta http-equiv="refresh" content="0; url=http://47.100.198.51:8000/">
       <title>AI聊天机器人 - 正在跳转...</title>
   </head>
   <body>
       <p>正在跳转到在线版本...</p>
       <p>如果没有自动跳转，请点击 <a href="http://47.100.198.51:8000/">这里</a></p>
   </body>
   </html>
   ```

2. **启用 GitHub Pages**：
   - 进入仓库 Settings → Pages
   - Source 选择 `Deploy from a branch`
   - Branch 选择 `main`，文件夹选择 `/docs`
   - 保存后，访问 `https://avalianfeng.github.io/chat_bot/` 会自动跳转到你的网站

## 🔗 方法四：在 GitHub 仓库的 About 部分添加网站

### 步骤

1. **在仓库主页，点击右侧的 ⚙️ 图标（或直接点击仓库名称下方的齿轮图标）**
2. **在 About 部分勾选 "Website"**
3. **输入你的网站地址**：`http://47.100.198.51:8000/`
4. **保存**

这样网站的链接会显示在仓库主页的右侧边栏，非常显眼。

## 🔗 方法五：使用 GitHub Actions 自动部署状态徽章

创建一个 GitHub Actions 工作流来显示部署状态：

### 步骤

1. **创建 `.github/workflows/deploy-status.yml`**：
   ```yaml
   name: Deploy Status Check

   on:
     schedule:
       - cron: '*/30 * * * *'  # 每30分钟检查一次
     workflow_dispatch:

   jobs:
     check:
       runs-on: ubuntu-latest
       steps:
         - name: Check Website Status
           run: |
             if curl -f -s http://47.100.198.51:8000/health > /dev/null; then
               echo "✅ 网站运行正常"
             else
               echo "❌ 网站无法访问"
               exit 1
             fi
   ```

2. **添加状态徽章到 README**：
   ```markdown
   ![Deploy Status](https://github.com/Avalianfeng/chat_bot/workflows/Deploy%20Status%20Check/badge.svg)
   ```

## 🌐 没有域名也可以！

### 优势

- ✅ **IP 地址直接访问**：`http://47.100.198.51:8000/` 可以直接使用
- ✅ **GitHub 链接**：在 GitHub 上添加链接，用户可以轻松访问
- ✅ **二维码**：可以生成二维码，方便移动端访问
- ✅ **免费且简单**：无需购买域名和配置 DNS

### 注意事项

1. **IP 地址可能会变**：如果服务器 IP 改变，需要更新所有链接
2. **记忆困难**：IP 地址不如域名好记
3. **SSL 证书**：使用 IP 地址申请 SSL 证书会比较困难

### 如果将来要使用域名

1. **购买域名**（可选，如：阿里云、腾讯云等）
2. **配置 DNS 解析**：将域名解析到 `47.100.198.51`
3. **配置 Nginx 反向代理**：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
4. **申请 SSL 证书**（Let's Encrypt 免费）：
   ```bash
   certbot --nginx -d your-domain.com
   ```

## 📝 推荐配置清单

1. ✅ **仓库描述**：添加在线体验链接
2. ✅ **About 部分**：填写 Website 字段
3. ✅ **README.md**：在顶部添加在线体验链接和徽章
4. ✅ **Topics**：添加相关标签提高可发现性
5. ✅ **健康检查**：定期检查网站状态

## 🎯 快速操作步骤

### 在 GitHub 上添加网站链接（最快）

1. 打开 https://github.com/Avalianfeng/chat_bot
2. 点击仓库名称旁边的 ⚙️ 图标
3. 在 "About" 部分：
   - 勾选 "Website"
   - 输入：`http://47.100.198.51:8000/`
4. 保存

### 更新 README 顶部（已自动完成）

README 中已经添加了在线体验地址，用户可以直接看到。

完成这些步骤后，你的 GitHub 项目就与网站关联起来了！用户可以轻松地从 GitHub 仓库页面跳转到你的在线应用。
