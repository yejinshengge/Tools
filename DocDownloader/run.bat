@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo 网页文档下载工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import requests, bs4" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 如果没有提供URL参数，提示用户输入
if "%~1"=="" (
    echo 使用方法: run.bat [URL] [选项]
    echo.
    echo 示例:
    echo   run.bat https://example.com/docs/ -o docs
    echo.
    set /p URL="请输入要下载的文档URL: "
    if "!URL!"=="" (
        echo [错误] 未提供URL
        pause
        exit /b 1
    )
    python doc_downloader.py "!URL!" %*
) else (
    python doc_downloader.py %*
)

pause

