# SlideCraft - AI PPT Generator

<div align="center">

![Logo](https://img.shields.io/badge/SlideCraft-AI%20PPT-667eea?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-4BA?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-333?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**AI-Powered PPT Outline Generator | Multiple Themes | Export to Editable PPTX**

[English](README.md) | [中文](README_zh.md)

</div>

---

## Features

- 🤖 **AI Smart Generation** - Enter a topic, get a professional PPT outline
- 🎨 **Multiple Theme Styles** - Forest Ink, Classic Ink, Indigo Porcelain & more
- 🌈 **Switchable UI Skins** - Tech, Plant Research, Academic styles with persistence
- 📥 **Editable PPTX Export** - Download standard PPTX files, open in PowerPoint/WPS
- 🌐 **HTML PPT Preview** - Instant preview with page flip animations
- 💾 **History** - Auto-save generation history

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **AI API**: Supports multiple LLM providers (MiniMax, DeepSeek, etc.)
- **File Format**: Standard OOXML (PPTX) + HTML5

## Quick Start

### Requirements

- Python 3.8+
- Network connection (for AI API)

### Installation & Run

```bash
# 1. Enter project directory
cd ppt_server

# 2. Install dependencies
pip install flask flask-session requests

# 3. Configure API
# Edit API_URL and API_KEY in server.py
API_URL = "https://your-api-endpoint.com/v1/chat/completions"
API_KEY = "your-api-key"

# 4. Start server
python server.py

# 5. Access
# Open browser: http://localhost:5000
```

## Project Structure

```
ppt_server/
├── server.py          # Flask backend
├── index.html         # Frontend
├── session_data/      # Session storage (auto-created)
├── LICENSE            # MIT License
└── README.md          # Documentation
```

## License

This project is open source under [MIT License](LICENSE).

### You Can
- ✅ Freely use, modify, distribute
- ✅ Use in commercial projects
- ✅ Private deployment

### You Must
- 📝 Keep the original copyright notice

## Third-Party Dependencies

| Project | Usage | License |
|---------|-------|---------|
| [Flask](https://github.com/pallets/flask) | Web framework | BSD-3-Clause |
| [guizang-ppt](https://github.com/op7418/guizang-ppt-skill) | PPT style reference | - |

## Contact

- **Email**: 441462071@qq.com
- **Issues**: [GitHub Issues](https://github.com/your-repo/slidecraft/issues)

---

<div align="center">

Made with ❤️ by SlideCraft Team

</div>
