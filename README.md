# SlideCraft —— AI PPT 生成器

> 支持多种主流 AI 模型（DeepSeek / MiniMax / OpenAI 等），一键生成专业 PPT 大纲、HTML 预览与 PPTX 下载

<p align="center">
  <img src="logo.svg" alt="SlideCraft Logo" width="200">
</p>

## ✨ 功能特性

- **多模型支持** —— DeepSeek V3/V4/R1、MiniMax M27、GPT-4 等，灵活切换
- **三步生成** —— 输入主题 → AI 生成大纲 → 一键下载 PPTX / HTML
- **丰富主题** —— 森林墨 / 樱粉 / 星空蓝，可自由扩展
- **历史记录** —— 浏览器会话内保留最近 10 份大纲，随时回溯
- **纯 Python 实现** —— 无需安装 Microsoft Office，跨平台运行

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/moon9001/slidecraft.git
cd slidecraft
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env，填入 API Key
```

#### 支持的服务商

**MiniMax（默认）**
- 官网：https://www.minimaxi.com/
- API Key：在 MiniMax 控制台获取
- 环境变量：`MINIMAX_API_KEY`

**DeepSeek**
- 官网：https://platform.deepseek.com/
- API Key：https://platform.deepseek.com/api_keys
- 环境变量：`DEEPSEEK_API_KEY`

**通义千问（阿里云）**
- 官网：https://dashscope.console.aliyun.com/
- API Key：在阿里云 DashScope 控制台获取
- 环境变量：`DASHSCOPE_API_KEY`

**硅基流动**
- 官网：https://www.siliconflow.cn/
- API Key：在硅基流动控制台获取
- 环境变量：`SILICONFLOW_API_KEY`

**讯飞星火**
- 官网：https://xinghuo.xfyun.cn/
- API Key：在讯飞开放平台获取
- 环境变量：`SPARK_API_KEY`

> 💡 **提示**：你可以使用任意 OpenAI 兼容的 API 服务，只需修改 `SLIDECRAFT_API_URL` 环境变量。

### 4. 启动服务

```bash
python server.py
```

浏览器访问 **http://localhost:5000**

## 🔑 环境变量说明

| 变量 | 说明 | 必填 | 示例 |
|------|------|------|------|
| `MINIMAX_API_KEY` | MiniMax API Key | ✅ 是 | `your-key` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | ❌ 否 | `sk-...` |
| `DASHSCOPE_API_KEY` | 阿里云通义千问 API Key | ❌ 否 | `sk-...` |
| `SILICONFLOW_API_KEY` | 硅基流动 API Key | ❌ 否 | `sk-...` |
| `SPARK_API_KEY` | 讯飞星火 API Key | ❌ 否 | `your-key` |
| `SLIDECRAFT_API_URL` | 自定义 API 地址 | ❌ 否 | `https://your-api.com/v1/chat/completions` |
| `SLIDECRAFT_DEFAULT_MODEL` | 默认模型 | ❌ 否 | `minimax-m27` |

### .env 示例

```bash
# MiniMax（默认，必需）
MINIMAX_API_KEY=your-minimax-key

# DeepSeek
DEEPSEEK_API_KEY=your-deepseek-key

# 阿里云通义千问
DASHSCOPE_API_KEY=your-dashscope-key

# 硅基流动
SILICONFLOW_API_KEY=your-siliconflow-key

# 讯飞星火
SPARK_API_KEY=your-spark-key

# 自定义 API 地址（可选，用于 OpenAI 兼容的服务）
# SLIDECRAFT_API_URL=https://api.openai.com/v1/chat/completions
```

> ⚠️ **注意**：`.env` 文件已被 `.gitignore` 保护，**私有 Key 永远不会被提交到 Git**。

## 🤖 支持的模型

在 `.env` 中配置对应 API Key 后，以下模型将自动出现在前端下拉列表中：

| 模型 ID | 名称 | 需要 API Key | 服务商 |
|---------|------|-------------|--------|
| `minimax-m27` | MiniMax M27（默认，推荐） | `MINIMAX_API_KEY` | MiniMax |
| `deepseek-v3` | DeepSeek V3（最新均衡） | `DEEPSEEK_API_KEY` | DeepSeek |
| `deepseek-r1` | DeepSeek R1（强推理） | `DEEPSEEK_API_KEY` | DeepSeek |
| `qwen-plus` | 通义千问 Qwen Plus | `DASHSCOPE_API_KEY` | 阿里云 |
| `qwen-max` | 通义千问 Qwen Max | `DASHSCOPE_API_KEY` | 阿里云 |
| `qwen-vl-plus` | 通义千问 VL Plus（视觉） | `DASHSCOPE_API_KEY` | 阿里云 |
| `qwen2.5-72b` | Qwen2.5 72B | `SILICONFLOW_API_KEY` | 硅基流动 |
| `deepseek-v3-0324` | DeepSeek V3 0324 | `SILICONFLOW_API_KEY` | 硅基流动 |
| `glm-4-flash` | GLM-4 Flash（智谱） | `SILICONFLOW_API_KEY` | 硅基流动 |
| `spark-4.0` | 讯飞星火 4.0 | `SPARK_API_KEY` | 讯飞星火 |
| `spark-5.0` | 讯飞星火 5.0 | `SPARK_API_KEY` | 讯飞星火 |

### 添加自定义模型

编辑 `server.py` 中的 `PRESET_MODELS` 字典，添加你的模型配置：

```python
PRESET_MODELS = {
    "your-model-id": {
        "name": "你的模型名称",
        "api_key_env": "YOUR_API_KEY_ENV",
        "api_url": "https://your-api.com/v1/chat/completions",
        "default": False
    },
    # ... 其他模型
}
```

## 📂 目录结构

```
slidecraft/
├── server.py          # Flask 后端服务
├── index.html         # 前端页面
├── api_docs.html      # API 文档页面
├── logo.svg           # 项目 Logo
├── static/            # 静态资源
│   └── logo.svg      # 浏览器 Favicon
├── .env.example       # 环境变量示例（无真实 Key）
├── .env               # 环境变量配置（不提交，已被 gitignore）
├── requirements.txt   # Python 依赖
└── README.md          # 本文件
```

## 🛠 技术栈

- **后端**：Flask + requests
- **前端**：原生 HTML / CSS / JavaScript（无框架依赖）
- **PPTX 生成**：纯 Python XML（无需安装 Microsoft Office）
- **AI 接口**：OpenAI 兼容接口（可接入任意兼容服务）

## 📖 API 文档

启动服务后，访问 **http://localhost:5000/api_docs** 查看完整的 API 文档。

### 快速 API 调用示例

**第一步：生成 PPT 内容**

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能应用",
    "slides": 8,
    "style": "专业严谨",
    "model": "deepseek-chat"
  }'
```

**第二步：下载 PPTX 文件**

```bash
curl -X POST http://localhost:5000/api/download_pptx \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能应用",
    "content": "[第一步返回的 content 字段]",
    "theme": "森林墨"
  }' \
  -o output.pptx
```

## 🔒 安全说明

- ✅ `.env` 文件已被 `.gitignore` 忽略，**真实 API Key 不会进入 Git 历史**
- ✅ 仓库中仅包含 `.env.example` 示例文件，无任何真实 Key
- ✅ 所有 API Key 均在服务器端读取，不会暴露给前端
- ✅ 会话 ID 使用 `secrets.token_hex()` 安全生成

## 🌟 特色功能

### 1. 多种 PPT 主题

内置多套专业主题，可在生成时选择：
- 森林墨（默认）
- 樱粉
- 星空蓝
- 向日葵
- 更多主题持续添加中...

### 2. HTML 预览

生成 PPTX 前，可先生成 HTML 预览，快速查看效果。

### 3. 历史记录

浏览器会话内自动保存最近 10 份生成的大纲，随时回溯和重新下载。

### 4. 提供内容

除了主题，你还可以提供参考资料，AI 会整合到 PPT 中。

## 🐛 常见问题

### Q: 为什么生成失败？

A: 请检查：
1. `.env` 文件中是否配置了正确的 API Key
2. API Key 是否有足够的额度
3. 网络连接是否正常

### Q: 为什么下载的 PPTX 打不开？

A: 可能是内容解析出错。请提交 Issue，并附上生成的大纲内容。

### Q: 如何添加新的 AI 模型？

A: 编辑 `server.py` 中的 `PRESET_MODELS` 字典，添加模型配置。

### Q: 是否支持本地 OAI 模型？

A: 支持！只需在 `.env` 中设置：
```bash
SLIDECRAFT_API_URL=http://localhost:11434/v1/chat/completions
DEEPSEEK_API_KEY=不需要真实Key  # OAI 兼容模型不需要
```

## 📄 许可证

MIT License

## 📬 联系

- **Issue**：https://github.com/moon9001/slidecraft/issues
- **Email**：441462071@qq.com

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！
