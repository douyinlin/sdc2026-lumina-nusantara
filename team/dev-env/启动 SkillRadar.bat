@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo 请先按照 README 安装 Python 并创建 .venv、安装 requirements.txt。
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501
if errorlevel 1 pause
