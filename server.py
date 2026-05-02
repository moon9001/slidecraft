"""
SlideCraft - AI PPT 生成服务
技术联系：441462071@qq.com

支持多种 AI 模型：OpenAI、DeepSeek、腾讯混元、阿里千问、字节豆包、智谱 GLM、百度文心、MiniMax 等

使用前请在 .env 文件或环境变量中配置 API
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session, Response, make_response
from flask_session import Session
import requests
import secrets
import json
import zipfile
import io

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './session_data'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

os.makedirs('./session_data', exist_ok=True)

# ============================================
# 配置文件 - 用户自定义
# ============================================
# 可以通过环境变量或 .env 文件配置

class Config:
    """API 配置"""
    
    # 默认使用科技云（如果已配置）
    DEFAULT_API_URL = os.getenv("SLIDECRAFT_API_URL", "https://uni-api.cstcloud.cn/v1/chat/completions")
    DEFAULT_API_KEY = os.getenv("SLIDECRAFT_API_KEY", "")
    
    # 默认模型
    DEFAULT_MODEL = os.getenv("SLIDECRAFT_DEFAULT_MODEL", "minimax-m27")

# 预配置的模型列表（用户可自行添加更多）
PRESET_MODELS = {
    # MiniMax 系列
    "minimax-m27": {
        "name": "MiniMax M27（默认）",
        "api_url": "https://uni-api.cstcloud.cn/v1/chat/completions",
        "api_key_env": "MINIMAX_API_KEY",
        "supports_streaming": True
    },
    "deepseek-v4-flash": {
        "name": "DeepSeek V4 Flash（快速）",
        "api_url": "https://uni-api.cstcloud.cn/v1/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "supports_streaming": True
    },
    
    # OpenAI 系列
    "gpt-4o": {
        "name": "GPT-4o（强大）",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "supports_streaming": True
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini（快速）",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "supports_streaming": True
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo（专业）",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key_env": "OPENAI_API_KEY",
        "supports_streaming": True
    },
    
    # DeepSeek 系列
    "deepseek-chat": {
        "name": "DeepSeek V3（平衡）",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "supports_streaming": True
    },
    "deepseek-reasoner": {
        "name": "DeepSeek R1（推理）",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key_env": "DEEPSEEK_API_KEY",
        "supports_streaming": True
    },
    
    # 阿里通义千问
    "qwen-plus": {
        "name": "通义千问 Plus",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key_env": "DASHSCOPE_API_KEY",
        "supports_streaming": True
    },
    "qwen-max": {
        "name": "通义千问 Max",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key_env": "DASHSCOPE_API_KEY",
        "supports_streaming": True
    },
    "qwen-long": {
        "name": "通义千问 Long（长文本）",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key_env": "DASHSCOPE_API_KEY",
        "supports_streaming": True
    },
    
    # 腾讯混元
    "hunyuan": {
        "name": "腾讯混元（平衡）",
        "api_url": "https://hunyuan.cloud.tencent.com/v1/chat/completions",
        "api_key_env": "TENCENT_SECRET_ID",
        "supports_streaming": True
    },
    "hunyuan-pro": {
        "name": "腾讯混元 Pro（强大）",
        "api_url": "https://hunyuan.cloud.tencent.com/v1/chat/completions",
        "api_key_env": "TENCENT_SECRET_ID",
        "supports_streaming": True
    },
    
    # 字节豆包
    "doubao-pro": {
        "name": "豆包 Pro（平衡）",
        "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "api_key_env": "ARK_API_KEY",
        "supports_streaming": True
    },
    "doubao-lite": {
        "name": "豆包 Lite（快速）",
        "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "api_key_env": "ARK_API_KEY",
        "supports_streaming": True
    },
    
    # 智谱 GLM
    "glm-4": {
        "name": "智谱 GLM-4（强大）",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key_env": "ZHIPU_API_KEY",
        "supports_streaming": True
    },
    "glm-4-flash": {
        "name": "智谱 GLM-4 Flash（快速）",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key_env": "ZHIPU_API_KEY",
        "supports_streaming": True
    },
    
    # 百度文心一言
    "ernie-4": {
        "name": "文心一言 4.0（强大）",
        "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
        "api_key_env": "ERNIE_API_KEY",
        "supports_streaming": True
    },
    "ernie-speed": {
        "name": "文心一言 Speed（快速）",
        "api_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
        "api_key_env": "ERNIE_API_KEY",
        "supports_streaming": True
    },
}

# 获取有效的模型列表（根据配置的 API Key）
def get_available_models():
    """获取当前可用的模型列表"""
    available = {}
    for model_id, config in PRESET_MODELS.items():
        api_key = os.getenv(config["api_key_env"])
        if api_key:
            available[model_id] = config["name"]
    return available

# 获取模型配置
def get_model_config(model_id):
    """获取模型的完整配置"""
    if model_id in PRESET_MODELS:
        config = PRESET_MODELS[model_id].copy()
        api_key = os.getenv(config.pop("api_key_env"))
        config["api_key"] = api_key
        return config
    return None

# 主题色配置
THEMES = {
    "森林墨": {
        "bg": "#f5f7f2",
        "text": "#1a2e1a",
        "accent": "#2d5a2d",
        "secondary": "#4a7c4a",
        "muted": "#6b8e6b"
    },
    "墨水经典": {
        "bg": "#faf8f5",
        "text": "#1a1a1a",
        "accent": "#c75000",
        "secondary": "#6b5b4f",
        "muted": "#8a8a8a"
    },
    "靛蓝瓷": {
        "bg": "#f8f9fc",
        "text": "#1a1a2e",
        "accent": "#4a6fa5",
        "secondary": "#6b8cc4",
        "muted": "#8899bb"
    }
}

def generate_ppt_html(title, pages, theme="森林墨"):
    """生成 HTML PPT"""
    colors = THEMES.get(theme, THEMES["森林墨"])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg: {colors["bg"]};
            --text: {colors["text"]};
            --accent: {colors["accent"]};
            --secondary: {colors["secondary"]};
            --muted: {colors["muted"]};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg);
            color: var(--text);
            overflow: hidden;
        }}
        .slides-container {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }}
        .slide {{
            width: 100vw;
            height: 100vh;
            display: none;
            padding: 60px 80px;
            position: relative;
            background: var(--bg);
        }}
        .slide.active {{ display: flex; flex-direction: column; }}
        .slide-cover {{
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, var(--text) 0%, #333 100%);
            color: var(--bg);
        }}
        .slide-cover h1 {{
            font-size: 72px;
            font-weight: 700;
            letter-spacing: 4px;
            margin-bottom: 30px;
        }}
        .slide-cover .subtitle {{
            font-size: 28px;
            opacity: 0.8;
            margin-bottom: 60px;
        }}
        .slide-cover .meta {{
            font-size: 18px;
            opacity: 0.6;
        }}
        .slide-toc {{ justify-content: center; }}
        .slide-toc h2 {{
            font-size: 48px;
            margin-bottom: 60px;
            color: var(--accent);
        }}
        .toc-list {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            font-size: 28px;
        }}
        .toc-item {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .toc-num {{
            width: 48px;
            height: 48px;
            background: var(--accent);
            color: var(--bg);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 20px;
        }}
        .slide-content h2 {{
            font-size: 42px;
            color: var(--accent);
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid var(--accent);
        }}
        .slide-content .page-num {{
            position: absolute;
            bottom: 40px;
            right: 60px;
            font-size: 16px;
            color: var(--muted);
        }}
        .points {{ margin-top: 40px; }}
        .point {{
            display: flex;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 30px;
            font-size: 26px;
            line-height: 1.6;
        }}
        .point::before {{
            content: "●";
            color: var(--accent);
            font-size: 20px;
            margin-top: 4px;
        }}
        .slide-quote {{
            justify-content: center;
            align-items: center;
            text-align: center;
            background: var(--accent);
            color: var(--bg);
        }}
        .slide-quote blockquote {{
            font-size: 42px;
            line-height: 1.6;
            font-style: italic;
            max-width: 900px;
        }}
        .slide-data {{ justify-content: center; align-items: center; text-align: center; }}
        .big-number {{ font-size: 180px; font-weight: 700; color: var(--accent); line-height: 1; }}
        .big-number-label {{ font-size: 32px; margin-top: 20px; color: var(--secondary); }}
        .slide-end {{
            justify-content: center;
            align-items: center;
            text-align: center;
            background: var(--text);
            color: var(--bg);
        }}
        .slide-end h2 {{ font-size: 64px; color: var(--bg); }}
        .nav {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 12px;
            z-index: 100;
        }}
        .nav-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--muted);
            cursor: pointer;
            transition: all 0.3s;
        }}
        .nav-dot.active {{ background: var(--accent); transform: scale(1.3); }}
        .nav-arrows {{ position: fixed; bottom: 30px; right: 30px; display: flex; gap: 10px; z-index: 100; }}
        .nav-arrow {{
            width: 50px;
            height: 50px;
            border: 2px solid var(--muted);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 20px;
            color: var(--muted);
            transition: all 0.3s;
        }}
        .nav-arrow:hover {{ border-color: var(--accent); color: var(--accent); }}
        .page-indicator {{ position: fixed; top: 30px; right: 30px; font-size: 14px; color: var(--muted); z-index: 100; }}
        .progress-bar {{ position: fixed; top: 0; left: 0; height: 4px; background: var(--accent); z-index: 100; transition: width 0.3s; }}
        .slide.active .animate-in {{ animation: fadeInUp 0.6s ease-out forwards; }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-in:nth-child(1) {{ animation-delay: 0.1s; }}
        .animate-in:nth-child(2) {{ animation-delay: 0.2s; }}
        .animate-in:nth-child(3) {{ animation-delay: 0.3s; }}
        .animate-in:nth-child(4) {{ animation-delay: 0.4s; }}
    </style>
</head>
<body>
    <div class="progress-bar" id="progress"></div>
    <div class="page-indicator" id="indicator">1 / {len(pages)}</div>
    <div class="slides-container" id="slides">
'''

    for i, page in enumerate(pages):
        page_type = page.get("type", "content")

        if page_type == "cover":
            html += f'''
        <div class="slide slide-cover" data-slide="{i}">
            <h1 class="animate-in">{page.get("title", "")}</h1>
            <div class="subtitle animate-in">{page.get("subtitle", "")}</div>
            <div class="meta animate-in">{page.get("meta", "")}</div>
        </div>'''
        elif page_type == "toc":
            items_html = "".join(f'<div class="toc-item animate-in"><span class="toc-num">{j+1}</span>{item}</div>'
                              for j, item in enumerate(page.get("items", [])))
            html += f'''
        <div class="slide slide-toc" data-slide="{i}">
            <h2 class="animate-in">目录</h2>
            <div class="toc-list">{items_html}</div>
        </div>'''
        elif page_type == "quote":
            html += f'''
        <div class="slide slide-quote" data-slide="{i}">
            <blockquote class="animate-in">{page.get("quote", "")}</blockquote>
        </div>'''
        elif page_type == "data":
            html += f'''
        <div class="slide slide-data" data-slide="{i}">
            <div class="big-number animate-in">{page.get("number", "")}</div>
            <div class="big-number-label animate-in">{page.get("label", "")}</div>
        </div>'''
        elif page_type == "end":
            html += f'''
        <div class="slide slide-end" data-slide="{i}">
            <h2 class="animate-in">{page.get("title", "谢谢")}</h2>
            <div class="subtitle animate-in">{page.get("subtitle", "")}</div>
        </div>'''
        else:
            points_html = "".join(f'<div class="point animate-in">{p}</div>' for p in page.get("points", []))
            html += f'''
        <div class="slide slide-content" data-slide="{i}">
            <h2 class="animate-in">{page.get("title", "")}</h2>
            <div class="points">{points_html}</div>
            <div class="page-num">{page.get("page_num", i+1)}</div>
        </div>'''

    html += '''
    </div>
    <div class="nav" id="nav"></div>
    <div class="nav-arrows">
        <div class="nav-arrow" onclick="prevSlide()">←</div>
        <div class="nav-arrow" onclick="nextSlide()">→</div>
    </div>
    <script>
        const slides = document.querySelectorAll('.slide');
        const total = slides.length;
        let current = 0;
        const nav = document.getElementById('nav');
        slides.forEach((_, i) => {
            const dot = document.createElement('div');
            dot.className = 'nav-dot' + (i === 0 ? ' active' : '');
            dot.onclick = () => goTo(i);
            nav.appendChild(dot);
        });
        function updateSlide() {
            slides.forEach((s, i) => s.classList.toggle('active', i === current));
            document.querySelectorAll('.nav-dot').forEach((d, i) => d.classList.toggle('active', i === current));
            document.getElementById('indicator').textContent = (current + 1) + ' / ' + total;
            document.getElementById('progress').style.width = ((current + 1) / total * 100) + '%';
        }
        function nextSlide() { if (current < total - 1) { current++; updateSlide(); }}
        function prevSlide() { if (current > 0) { current--; updateSlide(); }}
        function goTo(n) { current = n; updateSlide(); }
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prevSlide();
        });
        document.addEventListener('wheel', (e) => { if (e.deltaY > 0) nextSlide(); else prevSlide(); });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') document.body.style.overflow = document.body.style.overflow === 'auto' ? 'hidden' : 'auto';
        });
        updateSlide();
    </script>
</body>
</html>'''
    return html

def parse_ppt_pages(content):
    """解析 AI 生成的内容为页面结构 - 支持 Markdown 格式"""
    import re
    pages = []
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    current_page = None
    current_type = None
    collecting = []

    def clean(s):
        """清理文本：去除空白、Markdown格式符号、页码标记等"""
        s = s.strip()
        # 去除 Markdown 标题标记 ### 
        s = re.sub(r'^#{1,6}\s+', '', s)
        s = re.sub(r'^-{3,}\s*$', '', s)  # 去除分隔线 ---
        # 去除 Markdown 格式符号 ** 和 __
        s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
        s = re.sub(r'__(.+?)__', r'\1', s)
        # 去除行首的星号列表标记
        s = re.sub(r'^[\*\-•]\s+', '', s)
        # 去除末尾的【】符号
        s = re.sub(r'[\u3010\u3011]+$', '', s)
        # 合并重复的"第"字（如"第第4页" -> "第4页"）
        s = re.sub(r'第+', '第', s)
        return s.strip()

    def save_page():
        nonlocal current_page, collecting
        if current_page is not None:
            for line in collecting:
                line = clean(line)
                if line and len(line) > 3:
                    if "points" not in current_page:
                        current_page["points"] = []
                    if line not in current_page["points"]:
                        current_page["points"].append(line)
            collecting = []
            if current_page.get("type") == "end" and pages and pages[-1].get("type") == "end":
                pass  # 跳过重复的结束页
            else:
                pages.append(current_page)
            current_page = None

    def detect_page(line, raw_line):
        """检测行是否为页面标题，返回(page_num, page_title)"""
        clean_line = clean(raw_line)
        # 检测页码格式 【第X页：标题】 或 第X页：标题 或 ##【第X页：标题】
        patterns = [
            r'#{1,6}\s*【?第?\s*(\d+)\s*页[：:\s]+(.+)',  # ### 第1页：xxx 或 ###【第1页：xxx】
            r'【?第?\s*(\d+)\s*页[：:\s]+(.+)',  # 第1页：xxx 或 【第1页：xxx】
        ]
        for pattern in patterns:
            m = re.match(pattern, clean_line)
            if m:
                return (m.group(1), m.group(2).strip())
        return (None, None)

    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()
        low = line.lower()

        # 检测是否为页面标题
        page_num, page_title = detect_page(line, raw_line)
        if page_title:
            clean_title = clean(page_title)
            sec_low = clean_title.lower()
            is_cover = '封面' in sec_low or 'cover' in sec_low
            
            # 如果当前是空的封面（只有前导文字），直接用它来填充
            if current_page and current_page["type"] == "cover" and not current_page["title"] and not current_page["subtitle"] and len(current_page.get("points", [])) == 0:
                # 空封面复用，继续填充内容
                if is_cover:
                    pass  # 继续使用当前封面
                else:
                    # 非封面页，需要先保存空封面
                    pages.append(current_page)
                    current_page = None
            else:
                save_page()
            
            if is_cover:
                current_page = {"type": "cover", "title": "", "subtitle": "", "meta": ""}
            elif '目录' in sec_low or 'toc' in sec_low:
                current_page = {"type": "toc", "title": "目录", "items": []}
            elif '结束' in sec_low or '谢谢' in sec_low or 'end' in sec_low or '结束页' in sec_low:
                current_page = {"type": "end", "title": "谢谢", "subtitle": "", "meta": ""}
            else:
                # 内容页：标题就是章节名称
                current_page = {"type": "content", "title": clean_title, "points": []}
            current_type = current_page["type"] if current_page else None
            collecting = []
            i += 1
            continue

        # 跳过无用的前导行（在没有当前页面时）
        if current_page is None:
            clean_line = clean(line)
            # 如果是"标题："或"副标题："开头的行，跳过（会在下一个页面处理）
            if clean_line.startswith('#') or clean_line.startswith('---') or not clean_line:
                i += 1
                continue
            # 跳过纯描述性文字
            if len(clean_line) < 10 and not ('：' in clean_line):
                i += 1
                continue
            # 否则作为封面页开始
            current_page = {"type": "cover", "title": "", "subtitle": "", "meta": ""}
            current_type = "cover"
            collecting = []
            i += 1
            continue

        # 处理当前页面的内容
        cleaned_line = clean(line)
        
        if current_type == "cover":
            # 封面页的标题和副标题提取
            cl = cleaned_line.lower()
            if '副标题' in cl:
                parts = re.split(r'[：:]', cleaned_line, 1)
                if len(parts) > 1:
                    current_page["subtitle"] = parts[1].strip()
            elif '标题' in cl:
                parts = re.split(r'[：:]', cleaned_line, 1)
                if len(parts) > 1:
                    current_page["title"] = parts[1].strip()
        elif current_type == "toc" and current_page:
            # 检测目录项：1. xxx 或 1 xxx
            m2 = re.match(r'^\s*[一二三四五六七八九十\d]+[.、：:\s]\s*(.+)', cleaned_line)
            if m2:
                it = m2.group(1).strip()
                if it and it not in current_page["items"]:
                    current_page["items"].append(it)
        elif current_type == "content" and current_page:
            # 检测要点
            cl = cleaned_line.lower()
            if '要点' in cl or '摘要' in cl or '说明' in cl:
                # 要点：xxx 或 要点 - xxx
                pt = re.sub(r'^(?:要点|摘要|说明)\s*[-：:：]?\s*', '', cleaned_line).strip()
                if pt and len(pt) > 3:
                    if "points" not in current_page:
                        current_page["points"] = []
                    if pt not in current_page["points"]:
                        current_page["points"].append(pt)
            elif re.match(r'^[•\-*]\s+.+', cleaned_line):
                pt = re.sub(r'^[\*\-•]\s+', '', cleaned_line).strip()
                if pt and len(pt) > 3:
                    if "points" not in current_page:
                        current_page["points"] = []
                    if pt not in current_page["points"]:
                        current_page["points"].append(pt)
        elif current_type == "end" and current_page:
            if '标题' in cleaned_line:
                parts = re.split(r'[：:]', cleaned_line, 1)
                if len(parts) > 1:
                    title = parts[1].strip()
                    if title and title != '谢谢！':
                        current_page["title"] = title
        i += 1

    save_page()

    # 如果没有页面，创建一个默认封面
    if not pages:
        pages = [{"type": "cover", "title": "PPT", "subtitle": "", "meta": ""}]
    # 确保第一页是封面
    if pages and pages[0]["type"] != "cover":
        pages.insert(0, {"type": "cover", "title": "PPT", "subtitle": "", "meta": ""})

    for i, page in enumerate(pages):
        page["page_num"] = i + 1

    return pages

def create_pptx_xml(title, pages, theme="森林墨"):
    """生成 PPTX 文件"""

    colors = {
        "森林墨": {"bg": "F5F7F2", "text": "1A2E1A", "accent": "2D5A2D", "secondary": "4A7C4A"},
        "墨水经典": {"bg": "FAF8F5", "text": "1A1A1A", "accent": "C75000", "secondary": "6B5B4F"},
        "靛蓝瓷": {"bg": "F8F9FC", "text": "1A1A2E", "accent": "4A6FA5", "secondary": "6B8CC4"},
    }.get(theme, {"bg": "F5F7F2", "text": "1A2E1A", "accent": "2D5A2D", "secondary": "4A7C4A"})

    num_slides = len(pages)

    # 动态生成 Content_Types.xml（包含所有 slide）
    slide_overrides = "".join(
        f'\n    <Override PartName="/ppt/slides/slide{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(num_slides)
    )
    content_types = f'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>{slide_overrides}
</Types>'''

    # 主 rels
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''

    # presentation rels（每个 slide 一个 relationship）
    pres_rels_items = "".join(
        f'\n    <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>'
        for i in range(num_slides)
    )
    pres_rels = f'''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{pres_rels_items}
</Relationships>'''

    # presentation.xml（所有 slide 的引用）
    slide_ids = "".join(f'<p:sldId id="{256+i}" r:id="rId{i+1}"/>' for i in range(num_slides))
    presentation = f'''<?xml version="1.0" encoding="UTF-8"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
    <p:sldIdLst>{slide_ids}</p:sldIdLst>
    <p:sldSz cx="9144000" cy="6858000"/>
</p:presentation>'''

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('ppt/_rels/presentation.xml.rels', pres_rels)
        zf.writestr('ppt/presentation.xml', presentation)

        for i, page in enumerate(pages):
            page_type = page.get("type", "content")
            slide_xml = generate_slide_xml(i+1, page, colors, page_type)
            zf.writestr(f'ppt/slides/slide{i+1}.xml', slide_xml)
            # 每个 slide 也要有 rels 文件
            zf.writestr(f'ppt/slides/_rels/slide{i+1}.xml.rels',
                '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')

    return zip_buffer.getvalue()

def generate_slide_xml(slide_num, page, colors, page_type):
    """生成单页幻灯片 XML"""

    if page_type == "cover":
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <p:cSld>
        <p:bg><p:bgFill><p:solidFill><a:srgbClr val="{colors["text"]}"/></p:solidFill></p:bgFill></p:bg>
        <p:spTree>
            <p:sp>
                <p:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="zh-CN" sz="5400" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{page.get("title", "")}</a:t></a:r></a:p>
                </p:txBody>
                <p:prstGeom prst="rect"><a:xfrm/><a:prstGeom/></p:sp>
            </p:sp>
            <p:sp>
                <p:txBody>
                    <a:bodyPr anchor="ctr"/>
                    <a:lstStyle/>
                    <a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="zh-CN" sz="2400"><a:solidFill><a:srgbClr val="FFFFFF"><a:alpha val="80%"/></a:srgbClr></a:solidFill></a:rPr><a:t>{page.get("subtitle", "")}</a:t></a:r></a:p>
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
</p:sld>'''

    elif page_type == "toc":
        items = page.get("items", [])
        toc_xml = ""
        for j, item in enumerate(items):
            toc_xml += f'''<p:sp>
                <p:txBody>
                    <a:lstStyle/>
                    <a:p><a:pPr algn="l"/><a:r><a:rPr lang="zh-CN" sz="2800" b="1"><a:solidFill><a:srgbClr val="{colors["accent"]}"/></a:solidFill></a:rPr><a:t>{j+1}. {item}</a:t></a:r></a:p>
                </p:txBody>
                <p:prstGeom prst="rect"><a:xfrm><a:off x="457200" y="{1500000 + j*700000}"/><a:ext cx="8229600" cy="600000"/></a:xfrm></p:prstGeom>
            </p:sp>'''
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <p:cSld><p:spTree>{toc_xml}</p:spTree></p:cSld>
</p:sld>'''

    elif page_type == "end":
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <p:cSld>
        <p:bg><p:bgFill><p:solidFill><a:srgbClr val="{colors["text"]}"/></p:solidFill></p:bgFill></p:bg>
        <p:spTree>
            <p:sp>
                <p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/>
                    <a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="zh-CN" sz="6000" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{page.get("title", "谢谢")}</a:t></a:r></a:p>
                </p:txBody>
            </p:sp>
        </p:spTree>
    </p:cSld>
</p:sld>'''

    else:
        title_text = page.get("title", "")
        points = page.get("points", [])

        content_xml = f'''<p:sp>
            <p:txBody><a:lstStyle/>
                <a:p><a:pPr algn="l"/><a:r><a:rPr lang="zh-CN" sz="3200" b="1"><a:solidFill><a:srgbClr val="{colors["accent"]}"/></a:solidFill></a:rPr><a:t>{title_text}</a:t></a:r></a:p>
            </p:txBody>
            <p:prstGeom prst="rect"><a:xfrm><a:off x="457200" y="457200"/><a:ext cx="8229600" cy="800000"/></a:xfrm></p:prstGeom>
        </p:sp>'''

        for k, point in enumerate(points[:6]):
            content_xml += f'''<p:sp>
            <p:txBody><a:lstStyle/>
                <a:p><a:pPr algn="l"/><a:r><a:rPr lang="zh-CN" sz="2000"><a:solidFill><a:srgbClr val="{colors["text"]}"/></a:solidFill></a:rPr><a:t>• {point}</a:t></a:r></a:p>
            </p:txBody>
            <p:prstGeom prst="rect"><a:xfrm><a:off x="457200" y="{1200000 + k*850000}"/><a:ext cx="8229600" cy="700000"/></a:xfrm></p:prstGeom>
        </p:sp>'''

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <p:cSld><p:spTree>{content_xml}</p:spTree></p:cSld>
</p:sld>'''

@app.route("/")
def index():
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(8)
        session['history'] = []
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading index.html: {str(e)}", 500

@app.route("/test123")
def test123():
    return "Test 123 - If you see this, the route is working!"

@app.route("/api_docs")
def api_docs():
    """API 文档页面"""
    try:
        # 使用绝对路径，基于当前文件的目录
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "api_docs.html")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"<h1>API 文档加载失败</h1><p>{str(e)}</p>", 500

@app.route("/api/generate", methods=["POST"])
def api_generate():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            # 尝试从 form 获取数据
            if request.form:
                data = dict(request.form)
            else:
                return jsonify({"error": "请求格式错误，需要 JSON body"}), 400
        
        topic = data.get("topic", "").strip()
        requirements = data.get("requirements", "").strip()
        user_content = data.get("user_content", "").strip()
        slides = int(data.get("slides", 8))
        style = data.get("style", "简洁明了")
        model = data.get("model", "minimax-m27")
    except Exception as e:
        return jsonify({"error": f"请求解析错误: {str(e)}"}), 400

    if not topic:
        return jsonify({"error": "请输入 PPT 主题"}), 400

    # 获取模型配置
    model_config = get_model_config(model)
    if not model_config:
        return jsonify({"error": f"未配置的模型: {model}"}), 400
    
    if not model_config["api_key"]:
        return jsonify({"error": f"请先配置 {model_config['name']} 的 API Key（环境变量: {PRESET_MODELS.get(model, {}).get('api_key_env', '')}）"}), 400

    content_section = f"\n\n**用户提供的内容（可参考或整合）：**\n{user_content}\n" if user_content else ""

    prompt = f"""你是一个专业的PPT内容策划专家。请为以下主题生成完整的PPT内容大纲。

**主题：** {topic}
**页数：** {slides} 页
**风格：** {style}
{content_section}
{f"**要求：**\n{requirements}" if requirements else ""}

请按以下格式生成（严格遵循）：
【第1页：封面】
标题：[主标题]
副标题：[副标题/汇报人]

【第2页：目录】
1. [章节1名称]
2. [章节2名称]
3. [章节3名称]

【第3页：[第一个章节标题]】
要点：[要点1]
要点：[要点2]
要点：[要点3]

【第4页：[第二个章节标题]】
要点：[要点1]
要点：[要点2]

【最后1页：结束页】
标题：谢谢

请确保内容专业、有深度、有数据支撑！"""

    try:
        resp = requests.post(
            model_config["api_url"],
            headers={"Authorization": f"Bearer {model_config['api_key']}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 8192},
            timeout=120
        )
        resp.raise_for_status()
        result_content = resp.json()["choices"][0]["message"]["content"]

        history_entry = {"topic": topic, "slides": slides, "style": style, "model": model, "content": result_content}
        if 'history' not in session:
            session['history'] = []
        session['history'].insert(0, history_entry)
        session['history'] = session['history'][:10]
        session.modified = True

        return jsonify({"content": result_content})
    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，请稍后重试"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API 请求失败: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate_ppt", methods=["POST"])
def api_generate_ppt():
    """生成 HTML PPT"""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "请求格式错误，需要 JSON body"}), 400
    topic = data.get("topic", "").strip()
    content = data.get("content", "").strip()
    theme = data.get("theme", "森林墨")

    if not content:
        return jsonify({"error": "请先生成 PPT 大纲"}), 400

    pages = parse_ppt_pages(content)
    html = generate_ppt_html(topic or "PPT", pages, theme)

    return jsonify({"success": True, "html": html})

@app.route("/api/download_pptx", methods=["POST"])
def api_download_pptx():
    """下载 PPTX 文件（使用PptxGenJS生成专业PPT）"""
    from urllib.parse import quote
    import subprocess
    import json as json_module
    import base64
    
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "请求格式错误，需要 JSON body"}), 400
    topic = data.get("topic", "").strip()
    content = data.get("content", "").strip()
    theme = data.get("theme", "森林墨")

    if not content:
        return jsonify({"error": "请先生成 PPT 大纲"}), 400

    try:
        # 将内容传给Node.js处理（generate_pptx.js会自行解析）
        data_json = json_module.dumps({
            "title": topic or "PPT",
            "content": content,
            "themeName": theme
        }, ensure_ascii=False)
        
        # 调用Node.js generate_pptx.js生成PPTX
        current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
        result = subprocess.run(
            ['node', 'generate_pptx.js', data_json],
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"Node.js error: {result.stderr}")
            raise Exception(result.stderr or "PPTX生成失败")
        
        pptx_base64 = result.stdout.strip()
        
        if not pptx_base64:
            raise Exception("PPTX生成返回空数据")
        
        pptx_data = base64.b64decode(pptx_base64)
        
        # 使用安全的文件名编码（支持中文）
        safe_filename = quote(topic or "PPT", safe='')
        response = make_response(pptx_data)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}.pptx"

        return response
        
    except Exception as e:
        print(f"PPTX generation error: {str(e)}")
        # 如果PptxGenJS失败，回退到手动XML方式
        try:
            pages = parse_ppt_pages(content)
            pptx_data = create_pptx_xml(topic or "PPT", pages, theme)
            safe_filename = quote(topic or "PPT", safe='')
            response = make_response(pptx_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}.pptx"
            return response
        except:
            return jsonify({"error": f"PPTX生成失败: {str(e)}"}), 500

@app.route("/api/history")
def api_history():
    return jsonify({"history": session.get('history', [])})

@app.route("/api/clear_history", methods=["POST"])
def api_clear_history():
    session['history'] = []
    return jsonify({"success": True})

@app.route("/api/models")
def api_models():
    """返回已配置的模型列表"""
    available = get_available_models()
    default_model = os.getenv("SLIDECRAFT_DEFAULT_MODEL", "minimax-m27")
    
    return jsonify({
        "models": available,
        "default": default_model if default_model in available else (list(available.keys())[0] if available else None),
        "configured_count": len(available)
    })

@app.route("/api/themes")
def api_themes():
    return jsonify({"themes": list(THEMES.keys())})

@app.route("/health")
def health():
    available_models = get_available_models()
    return {
        "status": "ok",
        "service": "SlideCraft - AI PPT Generator",
        "configured_models": list(available_models.keys()),
        "total_presets": len(PRESET_MODELS)
    }

if __name__ == "__main__":
    print("=" * 60)
    print("SlideCraft - AI PPT 生成服务")
    print("技术联系：441462071@qq.com")
    print("=" * 60)
    print("\n📋 支持的模型（请配置对应的环境变量）：")
    print("-" * 50)
    for model_id, config in PRESET_MODELS.items():
        env_var = config["api_key_env"]
        has_key = "✅" if os.getenv(env_var) else "❌"
        print(f"  {has_key} {config['name']} ({env_var})")
    
    available = get_available_models()
    if available:
        print(f"\n✅ 当前已配置 {len(available)} 个模型")
    else:
        print("\n⚠️  未配置任何 API Key，请设置环境变量！")
    print(f"\n🚀 访问地址：http://localhost:5000")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)
