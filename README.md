# SlideCraft —— AI PPT 生成器

> 支持多种 AI 模型，一键生成专业 PPT 大纲、HTML 预览与 PPTX 下载

## ✨ 功能特性

- **多模型支持** —— MiniMax M27、DeepSeek V3/V4/R1 等，可扩展
- **三步生成** —— 输入主题 → AI 生成大纲 → 一键下载 PPTX / HTML
- **科技云 API 开箱即用** —— 内置科技云（uni-api.cstcloud.cn）配置
- **丰富主题** —— 森林墨 / 墨水经典 / 靛蓝瓷，可扩展
- **历史记录** —— 浏览器会话内保留最近 10 份大纲

## 本地部署

### 1. 克隆仓库

```bash
git clone https://github.com/moon9001/slidecraft.git
cd slidecraft
```

### 2. 安装依赖

```bash
pip install flask flask-session python-dotenv requests
```

### 3. 配置 API Key（可选）

复制 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env，填入 API Key
```

> 默认已预配置科技云 API Key，可直接使用

### 4. 启动服务

```bash
python server.py
```

浏览器访问 **http://localhost:5000**

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MINIMAX_API_KEY` | MiniMax API Key | 已预配置科技云 Key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 已预配置科技云 Key |
| `SLIDECRAFT_DEFAULT_MODEL` | 默认模型 | `minimax-m27` |
| `SLIDECRAFT_API_URL` | API 地址 | `https://uni-api.cstcloud.cn/v1/chat/completions` |

## 目录结构

```
slidecraft/
├── server.py          # Flask 后端服务
├── index.html         # 前端页面
├── .env              # 环境变量配置（不提交到 Git）
├── requirements.txt   # Python 依赖
└── session_data/     # 会话数据（自动创建）
```

## 支持的模型

| 模型 ID | 名称 | 需要 API Key |
|----------|------|-------------|
| `minimax-m27` | MiniMax M27（默认） | `MINIMAX_API_KEY` |
| `deepseek-v4-flash` | DeepSeek V4 Flash（快速） | `DEEPSEEK_API_KEY` |
| `deepseek-chat` | DeepSeek V3（平衡） | `DEEPSEEK_API_KEY` |
| `deepseek-reasoner` | DeepSeek R1（推理） | `DEEPSEEK_API_KEY` |

> 在 `.env` 中填入对应 Key 后，模型将自动出现在下拉列表中

## 技术栈

- 后端：`Flask` + `requests`
- 前端：原生 HTML / CSS / JavaScript
- PPTX 生成：纯 Python XML（无需安装 Microsoft Office）
- AI 模型：OpenAI 兼容接口

## 许可证

MIT License

## 联系

技术问题请联系：**wangpeng@mail.kib.ac.cn**

---

> 本服务由 **WorkBuddy AI** 辅助开发 🙌
