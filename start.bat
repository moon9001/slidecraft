@echo off
chcp 65001 > nul
echo ============================================
echo  SlideCraft - AI PPT 生成服务启动器
echo ============================================
echo.

:: 检查是否配置了 API Key
if not defined DEEPSEEK_API_KEY (
    if not defined OPENAI_API_KEY (
        echo ⚠️  警告：未检测到 API Key 配置！
        echo.
        echo 请先配置以下环境变量之一：
        echo   - DEEPSEEK_API_KEY
        echo   - OPENAI_API_KEY
        echo   - DASHSCOPE_API_KEY
        echo   - ZHIPU_API_KEY
        echo.
        echo 或复制 .env.example 为 .env 并填入你的 Key
        echo.
        echo 详细信息请查看：.env.example
        echo ============================================
        echo.
    )
)

:: 启动服务
echo 正在启动服务...
start "" "D:\ProgramData\anaconda3\python.exe" "f:\ai\ppt_server\server.py"

echo 服务已在后台启动
echo 访问地址：http://localhost:5000
echo 按任意键关闭此窗口...
pause > nul
