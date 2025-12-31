# GitHub 上传指南

## 步骤 1: 在 GitHub 上创建仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 **+** 号，选择 **New repository**
3. 填写仓库信息：
   - **Repository name**: `my_chat_bot` (或你喜欢的名字)
   - **Description**: `AI聊天机器人 - 情感陪伴版，支持DeepSeek API、人设系统、记忆管理`
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 **Create repository**

## 步骤 2: 连接本地仓库到 GitHub

在终端中运行以下命令（将 `YOUR_USERNAME` 替换为你的 GitHub 用户名）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/my_chat_bot.git

# 或者使用 SSH（如果你配置了 SSH 密钥）
# git remote add origin git@github.com:YOUR_USERNAME/my_chat_bot.git

# 查看远程仓库
git remote -v
```

## 步骤 3: 推送代码到 GitHub

```bash
# 推送代码到 GitHub（首次推送）
git push -u origin master

# 或者如果你的默认分支是 main
git push -u origin main
```

如果遇到分支名称问题，可以运行：
```bash
# 重命名分支为 main（如果 GitHub 要求使用 main）
git branch -M main
git push -u origin main
```

## 步骤 4: 验证上传

1. 刷新 GitHub 网页，你应该能看到所有文件
2. 检查 `.env` 文件**不应该**出现在仓库中（已在 .gitignore 中排除）

## 后续更新代码

当你修改代码后，使用以下命令更新 GitHub：

```bash
# 查看修改的文件
git status

# 添加所有修改
git add .

# 提交修改
git commit -m "描述你的修改内容"

# 推送到 GitHub
git push
```

## 注意事项

⚠️ **重要安全提示：**
- ✅ `.env` 文件已被 `.gitignore` 排除，不会上传
- ✅ `__pycache__/` 等临时文件已被排除
- ⚠️ `persona/persona.json` 包含在仓库中，如果包含敏感信息，请手动从仓库中删除
- ⚠️ 确保没有在代码中硬编码 API 密钥

## 如果遇到问题

### 问题 1: 认证失败
如果推送时要求输入用户名和密码，GitHub 已不再支持密码认证，需要：
1. 使用 **Personal Access Token (PAT)**
2. 或配置 **SSH 密钥**

**创建 Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token"
3. 选择权限：至少勾选 `repo`
4. 生成后复制 token，在输入密码时使用 token 代替密码

### 问题 2: 分支名称冲突
如果提示分支名称问题：
```bash
# 重命名本地分支
git branch -M main
git push -u origin main
```

### 问题 3: 需要强制推送（谨慎使用）
```bash
git push -u origin master --force
```

