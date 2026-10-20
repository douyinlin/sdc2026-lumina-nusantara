@echo off
chcp 65001 >nul
title SkillRadar MY
cd /d "%~dp0"
setlocal enabledelayedexpansion

cls
echo.
echo  ==========================================
echo    SkillRadar MY  -  Lumina Nusantara
echo    SDC 2026  Domain 1
echo  ==========================================
echo.
echo  正在启动，请不要关闭这个窗口...
echo  约 3 秒后浏览器会自动打开
echo.

set "PY="

if exist "%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" (
    set "PY=%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
)
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    where py >nul 2>nul && set "PY=py"
)

if not defined PY (
    echo  [错误] 没有找到 Python
    echo  请安装: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 安装依赖（已安装则很快跳过）
"!PY!" -m pip install -q --disable-pip-version-check streamlit pandas >nul 2>nul

REM 3 秒后自动打开浏览器
start "" cmd /c "timeout /t 3 >nul & start http://localhost:8501"

REM 启动应用（前台运行，关窗口即停止）
"!PY!" -m streamlit run app.py --server.port 8501 --server.headless true

echo.
echo  应用已停止。按任意键关闭窗口...
pause >nul
