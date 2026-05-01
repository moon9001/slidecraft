# SlideCraft —— AI PPT 生成器

> 支持多种主流 AI 模型（ChatGPT / DeepSeek / MiniMax 等），一键生成专业 PPT 大纲、HTML 预览与 PPTX 下载

<p align="center">
  <img src="logo.svg" alt="SlideCraft Logo" width="200">
</p>

## ✨ 功能特性

- **多模型支持** —— ChatGPT、DeepSeek V3/V4/R1、MiniMax M27 等，灵活切换
- **三步生成** —— 输入主题 → AI 生成大纲 → 一键下载 PPTX / HTML
- **科技云 API 开箱即用** —— 内置科技云（uni-api.cstcloud.cn）配置，无需额外申请 Key
- **丰富主题** —— 森林墨 / 墨水经典 / 靛蓝瓷，可自由扩展
- **历史记录** —— 浏览器会话内保留最近 10 份大纲，随时回溯

## 🚀 本地部署

### 1. 克隆仓库

```bash
git clone https://github.com/moon9001/slidecraft.git
cd slidecraft
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key（可选）

默认已预配置**科技云 API Key**，可直接启动使用。

如需使用其他模型，复制 `.env.example` 为 `.env` 并填入对应 Key：

```bash
cp .env.example .env
# 编辑 .env，填入 API Key
```

> ⚠️ **注意**：`.env` 文件已被 `.gitignore` 保护，**私有 Key 永远不会被提交到 Git**。

### 4. 启动服务

```bash
python server.py
```

浏览器访问 **http://localhost:5000**

## 🔑 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MINIMAX_API_KEY` | MiniMax API Key | 已预配置科技云 Key ✅ |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 已预配置科技云 Key ✅ |
| `SLIDECRAFT_DEFAULT_MODEL` | 默认模型 | `minimax-m27` |
| `SLIDECRAFT_API_URL` | API 地址 | `https://uni-api.cstcloud.cn/v1/chat/completions` |

## 📂 目录结构

```
slidecraft/
├── server.py          # Flask 后端服务
├── index.html         # 前端页面（含 Favicon）
├── logo.svg          # 项目 Logo
├── .env.example      # 环境变量示例（无真实 Key）
├── .env              # 环境变量配置（不提交，已被 gitignore）
├── requirements.txt   # Python 依赖
└── session_data/     # 会话数据（自动创建）
```

## 🤖 支持的模型

| 模型 | 名称 | 需要 API Key |
|------|------|-------------|
| `minimax-m27` | MiniMax M27（默认，推荐） | ✅ 已预配置 |
| `deepseek-v4-flash` | DeepSeek V4 Flash（极速） | ✅ 已预配置 |
| `deepseek-chat` | DeepSeek V3（均衡） | ✅ 已预配置 |
| `deepseek-reasoner` | DeepSeek R1（推理） | ✅ 已预配置 |

> 在 `.env` 中填入对应 Key 后，模型将自动出现在前端下拉列表中。

## 🛠 技术栈

- **后端**：Flask + requests
- **前端**：原生 HTML / CSS / JavaScript（无框架依赖）
- **PPTX 生成**：纯 Python XML（无需安装 Microsoft Office）
- **AI 接口**：OpenAI 兼容接口（可接入任意兼容服务）

## 🔒 安全说明

- ✅ `.env` 文件已被 `.gitignore` 忽略，**真实 API Key 不会进入 Git 历史**
- ✅ 仓库中仅包含 `.env.example` 示例文件，无任何真实 Key
- ✅ 所有 API Key 均在服务器端读取，不会暴露给前端

## 📄 许可证

MIT License

## 📬 联系

技术问题请联系：**441462071@qq.com**
