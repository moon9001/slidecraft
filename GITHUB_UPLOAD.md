# SlideCraft GitHub 上传指南

## 方法一：使用 GitHub 网页（最简单）

### 1. 创建新仓库
1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写：
   - **Repository name**: `slidecraft`
   - **Description**: `AI PPT 生成器 - 智能生成 PPT 大纲，支持多种 AI 模型`
   - **Private/Public**: 选择 Public（公开）或 Private（私有）
   - ⚠️ **不要勾选** "Add a README file"（我们会用现有的）
4. 点击 "Create repository"

### 2. 上传文件
1. 在新建的仓库页面，点击 "uploading an existing file"
2. 将 `f:\ai\ppt_server\` 下的所有文件拖入上传区域
3. 需要上传的文件：
   - `server.py`
   - `index.html`
   - `LICENSE`
   - `README.md`
   - `README_EN.md`
   - `.env.example`
   - `.gitignore`
4. ⚠️ **不要上传**：
   - `session_data/` 目录
   - 任何包含真实 API Key 的文件
5. 点击 "Commit changes"

### 3. 完成！
恭喜！你的项目已经在 GitHub 上了。
- 仓库地址：`https://github.com/你的用户名/slidecraft`

---

## 方法二：使用 Git 命令行

### 1. 安装 Git
下载并安装 Git：https://git-scm.com/download/win

### 2. 配置 Git
```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱"
```

### 3. 初始化并上传
```bash
# 进入项目目录
cd f:\ai\ppt_server

# 初始化 Git
git init

# 添加所有文件（除了 .gitignore 忽略的）
git add .

# 提交
git commit -m "Initial commit: SlideCraft AI PPT Generator"

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/slidecraft.git

# 推送
git branch -M main
git push -u origin main
```

---

## 方法三：克隆后修改（推荐）

如果你想保持项目的同步更新：

### 1. 先 Fork 我的仓库
访问：https://github.com/yourusername/slidecraft
点击 "Fork" 按钮

### 2. 克隆你的 Fork
```bash
git clone https://github.com/YOUR_USERNAME/slidecraft.git
cd slidecraft
```

### 3. 配置你的 API Key
```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 4. 运行
```bash
pip install flask flask-session requests
python server.py
```

### 5. 保持同步
```bash
git remote add upstream https://github.com/原仓库地址/slidecraft.git
git pull upstream main  # 拉取更新
```

---

## 注意事项

### ⚠️ 安全提醒
- **绝对不要** 把真实的 API Key 上传到 GitHub！
- 所有敏感配置都通过环境变量设置
- `.gitignore` 已经配置忽略 `.env` 文件

### 📝 推荐的做法
1. 在 GitHub 上创建空的公开仓库
2. 使用网页界面上传文件（方法一）
3. 或者 clone 后在本地编辑，再用 git push

### 🎯 许可证选择
本项目使用 **MIT License**：
- 允许商用
- 允许修改和分发
- 只需保留版权声明

---

## 常见问题

### Q: 上传后报错 "push declined due to email privacy"
A: 在 GitHub 设置中关闭 "Block command line pushes that expose my email"

### Q: 如何让仓库更专业？
A: 建议：
- 添加 LICENSE 文件
- 完善 README.md
- 添加 CONTRIBUTING.md
- 设置 GitHub Pages 演示

### Q: 如何添加协作者？
A: Settings → Collaborators → Add people

---

## 联系方式
- 邮箱: 441462071@qq.com
- 问题反馈: https://github.com/yourusername/slidecraft/issues
