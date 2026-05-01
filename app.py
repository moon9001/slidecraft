"""
MiniMax PPT 生成服务
简单网页 + 调用 minimax-m27 模型生成 PPT 大纲/内容
监听端口 5000
"""
from flask import Flask, request, jsonify, render_template_string, Response
import requests
import json
import os
import re

app = Flask(__name__)

# 科技云 API 配置
API_URL = "https://uni-api.cstcloud.cn/v1/chat/completions"
API_KEY = "58cd9849565fed86162b86fdfdc1a92fb81dd3f0d0d3fd206c3f96ce90a7a1cf"
MODEL = "minimax-m27"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI PPT 助手 - MiniMax</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .content { padding: 30px; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        #result {
            margin-top: 30px;
            display: none;
        }
        #result.show { display: block; }
        .result-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.8;
        }
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .loading.show { display: block; }
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #e1e1e1;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .error.show { display: block; }
        .tips {
            background: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 10px 10px 0;
            font-size: 14px;
            color: #1565C0;
        }
        .copy-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        .copy-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI PPT 助手</h1>
            <p>Powered by MiniMax M27 · 科技云</p>
        </div>
        <div class="content">
            <div class="tips">
                <strong>使用说明：</strong>输入 PPT 主题和内容要求，AI 将生成完整的 PPT 大纲和详细内容。生成的文本可以直接复制到 PowerPoint、WPS 或其他工具中使用。
            </div>
            <form id="pptForm">
                <div class="form-group">
                    <label>PPT 主题 *</label>
                    <input type="text" id="topic" placeholder="例如：人工智能在医疗领域的应用" required>
                </div>
                <div class="form-group">
                    <label>详细要求（可选）</label>
                    <textarea id="requirements" placeholder="例如：
- 需要包含行业背景介绍
- 重点突出3-4个应用场景
- 需要有数据支撑
- 适合学术汇报场景"></textarea>
                </div>
                <div class="row">
                    <div class="form-group">
                        <label>PPT 页数</label>
                        <select id="slides">
                            <option value="5">5 页（简洁版）</option>
                            <option value="8" selected>8 页（标准版）</option>
                            <option value="12">12 页（详细版）</option>
                            <option value="15">15 页（完整版）</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>内容风格</label>
                        <select id="style">
                            <option value="专业学术">专业学术</option>
                            <option value="商业汇报">商业汇报</option>
                            <option value="简洁明了" selected>简洁明了</option>
                            <option value="生动有趣">生动有趣</option>
                        </select>
                    </div>
                </div>
                <button type="submit" id="submitBtn">生成 PPT 内容</button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>AI 正在生成中，请稍候...</p>
            </div>

            <div class="error" id="error"></div>

            <div id="result">
                <label>生成结果：</label>
                <div class="result-box" id="resultContent"></div>
                <button class="copy-btn" onclick="copyResult()">复制全部内容</button>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('pptForm');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        const error = document.getElementById('error');
        const submitBtn = document.getElementById('submitBtn');
        const resultContent = document.getElementById('resultContent');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const topic = document.getElementById('topic').value.trim();
            const requirements = document.getElementById('requirements').value.trim();
            const slides = document.getElementById('slides').value;
            const style = document.getElementById('style').value;

            if (!topic) {
                showError('请输入 PPT 主题');
                return;
            }

            // 显示加载
            loading.classList.add('show');
            result.classList.remove('show');
            error.classList.remove('show');
            submitBtn.disabled = true;

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, requirements, slides, style })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || '生成失败');
                }

                resultContent.textContent = data.content;
                result.classList.add('show');
            } catch (err) {
                showError(err.message);
            } finally {
                loading.classList.remove('show');
                submitBtn.disabled = false;
            }
        });

        function showError(msg) {
            error.textContent = msg;
            error.classList.add('show');
        }

        function copyResult() {
            const text = resultContent.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '已复制！';
                setTimeout(() => btn.textContent = '复制全部内容', 2000);
            });
        }
    </script>
</body>
</html>
"""


def generate_ppt_content(topic: str, requirements: str, slides: int, style: str) -> str:
    """调用 MiniMax API 生成 PPT 内容"""

    prompt = f"""你是一个专业的 PPT 内容策划专家。请为以下主题生成一份完整的 PPT 内容。

**主题：** {topic}

**页数要求：** {slides} 页

**风格要求：** {style}

{f"**其他要求：**\\n{requirements}" if requirements else ""}

请按以下格式输出（严格遵循）：

【第1页：封面】
标题：[PPT标题]
副标题：[副标题/日期/汇报人]

【第2页：目录】
1. [章节一]
2. [章节二]
3. [章节三]
...（根据页数调整）

【第3页：内容页】
标题：[本页标题]
要点：
• [要点1]
• [要点2]
• [要点3]
详细内容：[200-300字的详细阐述]

[后续页面按同样格式继续...]

请确保：
1. 内容专业、准确、有深度
2. 每个要点都有具体的数据或案例支撑
3. 逻辑清晰，层层递进
4. 适合现场演示和汇报
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 8192
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    if not content:
        raise Exception("API 返回内容为空")

    return content


@app.route("/")
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """PPT 生成 API"""
    data = request.get_json()

    topic = data.get("topic", "").strip()
    requirements = data.get("requirements", "").strip()
    slides = int(data.get("slides", 8))
    style = data.get("style", "简洁明了")

    if not topic:
        return jsonify({"error": "请输入 PPT 主题"}), 400

    try:
        content = generate_ppt_content(topic, requirements, slides, style)
        return jsonify({"content": content})
    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，请稍后重试"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API 请求失败：{str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"生成失败：{str(e)}"}), 500


@app.route("/health")
def health():
    """健康检查"""
    return jsonify({"status": "ok", "model": MODEL})


if __name__ == "__main__":
    print(f"AI PPT 助手已启动，访问地址：http://localhost:5000")
    print(f"使用模型：{MODEL}")
    from werkzeug.serving import make_server
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()
