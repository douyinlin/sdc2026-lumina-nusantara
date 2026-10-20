@echo off
chcp 65001 >nul
title SkillRadar MY - Lumina Nusantara
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo.
echo ============================================
echo   SkillRadar MY  -  Lumina Nusantara
echo   SDC 2026  Domain 1
echo ============================================
echo.

set "PY="

REM --- 1. 优先使用本机已确认可用的 Python 运行时 ---
if exist "%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" (
    set "PY=%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
)

REM --- 2. 其次系统 python / py ---
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    where py >nul 2>nul && set "PY=py"
)

if not defined PY (
    echo [错误] 没有找到 Python。
    echo 请安装: https://www.python.org/downloads/
    echo 安装时勾选 "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

echo Python: !PY!
echo.
echo [1/2] 检查依赖（第一次会自动安装，约 1-2 分钟）...
"!PY!" -m pip install -q --disable-pip-version-check streamlit pandas >nul 2>nul

echo [2/2] 启动应用...
echo.
echo   浏览器打开:  http://localhost:8501
echo   关闭本窗口 = 停止应用
echo.

"!PY!" -m streamlit run app.py --server.port 8501 --server.headless false

echo.
echo 应用已停止。按任意键关闭窗口...
pause >nul
