# SlideCraft - AI PPT Generator

<div align="center">

![Logo](https://img.shields.io/badge/SlideCraft-AI%20PPT-667eea?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-4BA?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-333?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**智能生成 PPT 大纲 | 支持多种 AI 模型 | 可下载可编辑 PPTX**

[English](README_EN.md) | [中文](README.md)

</div>

---

## 功能特点

- 🤖 **多 AI 模型支持** - OpenAI、DeepSeek、阿里千问、腾讯混元、字节豆包、智谱、百度文心、MiniMax
- 🎨 **多种主题风格** - 森林墨、墨水经典、靛蓝瓷等多种配色方案
- 🌈 **多套 UI 皮肤** - 科技风、植物所风、学术风自由切换，记住你的选择
- 📥 **可编辑 PPTX** - 一键下载标准 PPTX 文件，可用 PowerPoint/WPS 打开编辑
- 🌐 **HTML PPT 预览** - 即时预览效果，支持翻页动画
- 💾 **历史记录** - 自动保存生成历史，方便回顾和修改

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/slidecraft.git
cd slidecraft
```

### 2. 配置 API Key

```bash
# 复制配置示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
```

支持的模型和对应的环境变量：

| 模型 | 环境变量 | 获取地址 |
|------|----------|----------|
| OpenAI GPT-4o | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| DeepSeek | `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com/) |
| 阿里千问 | `DASHSCOPE_API_KEY` | [bailian.console.aliyun.com](https://bailian.console.aliyun.com/) |
| 腾讯混元 | `TENCENT_SECRET_ID` | [console.cloud.tencent.com](https://console.cloud.tencent.com/hunyuan) |
| 字节豆包 | `ARK_API_KEY` | [console.volcengine.com](https://console.volcengine.com/ark) |
| 智谱 GLM | `ZHIPU_API_KEY` | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| 百度文心 | `ERNIE_API_KEY` | [console.bce.baidu.com](https://console.bce.baidu.com/) |
| MiniMax | `MINIMAX_API_KEY` | 科技云 |

> 💡 **提示**: 只需要配置你想要使用的模型的 API Key，不需要全部配置。

### 3. 安装依赖

```bash
pip install flask flask-session requests
```

### 4. 启动服务

```bash
python server.py
```

打开浏览器访问 http://localhost:5000

---

## Docker 部署

```bash
# 构建镜像时传入 API Key
docker build -t slidecraft --build-arg OPENAI_API_KEY=sk-xxx .

# 或使用环境变量
docker run -d -p 5000:5000 \
  -e OPENAI_API_KEY=sk-xxx \
  slidecraft
```

## Nginx 反向代理（可选）

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 项目结构

```
slidecraft/
├── server.py          # Flask 后端服务
├── index.html         # 前端页面
├── session_data/      # Session 存储（自动创建）
├── .env.example       # 环境变量配置示例
├── .gitignore         # Git 忽略文件
├── LICENSE            # MIT 许可证
└── README.md          # 项目说明
```

## 开源协议

本项目采用 [MIT License](LICENSE) 开源。

### 你可以
- ✅ 自由使用、修改、分发本项目
- ✅ 用于商业项目
- ✅ 私有化部署

### 你需要
- 📝 保留原始版权声明

## 第三方引用与致谢

本项目引用了以下开源项目，感谢他们的贡献：

| 项目 | 用途 | 许可证 |
|------|------|--------|
| [Flask](https://github.com/pallets/flask) | Web 框架 | BSD-3-Clause |

> **关于 guizang-ppt**: 本项目的 HTML PPT 预览功能参考了其翻页动画设计理念。如需商用 guizang-ppt，请查阅其具体许可证条款。

## 常见问题

### Q: 如何添加新的 AI 模型？

A: 在 `server.py` 的 `PRESET_MODELS` 字典中添加即可：
```python
"my-model": {
    "name": "我的模型",
    "api_url": "https://api.example.com/v1/chat/completions",
    "api_key_env": "MY_MODEL_API_KEY",
    "supports_streaming": True
}
```

### Q: 如何修改 UI 配色？

A: 修改 `index.html` 中的 CSS 变量，或添加新的主题类。

### Q: 支持流式输出吗？

A: 当前版本暂不支持流式输出，API 返回后统一展示。

## 更新日志

### v3.0.0
- ✨ 支持多种 AI 模型（OpenAI、DeepSeek、阿里、腾讯、豆包、智谱、百度等）
- 🔒 移除硬编码 API Key，改为环境变量配置
- 🎨 UI 风格可切换并自动保存

### v2.0.0
- ✨ 全新 UI 设计，支持多风格切换

### v1.0.0
- 🚀 初始版本

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- **邮箱**: 441462071@qq.com
- **问题反馈**: [GitHub Issues](https://github.com/yourusername/slidecraft/issues)

---

<div align="center">

Made with ❤️ by SlideCraft Team

</div>
