@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
REM 启用错误处理，避免静默退出
set "ERRORLEVEL="

echo ========================================
echo HTML转EPUB电子书工具
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
echo 检查依赖包...
python -c "import ebooklib" >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 使用说明:
echo   1. 将HTML文件放在一个目录中
echo   2. 运行此脚本，按提示输入参数
echo ========================================
echo.

REM 获取输入目录
echo 请输入HTML文件所在目录:
set /p INPUT_DIR=
if "!INPUT_DIR!"=="" (
    echo [错误] 输入目录不能为空
    pause
    exit /b 1
)

REM 检查目录是否存在
if not exist "!INPUT_DIR!" (
    echo [错误] 目录不存在: !INPUT_DIR!
    pause
    exit /b 1
)

REM 获取输出文件
echo 请输入输出EPUB文件路径 (默认: output.epub):
set /p OUTPUT_FILE=
if "!OUTPUT_FILE!"=="" (
    set "OUTPUT_FILE=output.epub"
) else (
    REM 检查是否是目录（最简单可靠的方法：检查路径是否存在且是目录）
    set "IS_DIR=0"
    
    REM 如果路径存在且是目录
    if exist "!OUTPUT_FILE!\" (
        set "IS_DIR=1"
    )
    
    if "!IS_DIR!"=="1" (
        REM 是目录，添加默认文件名
        REM 确保路径以反斜杠结尾
        set "TEMP=!OUTPUT_FILE!"
        if not "!TEMP!"=="" (
            REM 检查最后一个字符（仅在非空时）
            set "LAST_CHAR=!TEMP:~-1!"
            if not "!LAST_CHAR!"=="\" (
                if not "!LAST_CHAR!"=="/" (
                    set "OUTPUT_FILE=!OUTPUT_FILE!\"
                )
            )
        )
        set "OUTPUT_FILE=!OUTPUT_FILE!output.epub"
    ) else (
        REM 检查是否有.epub扩展名
        echo "!OUTPUT_FILE!" | findstr /I ".epub" >nul 2>&1
        if errorlevel 1 (
            REM 检查是否有其他扩展名
            echo "!OUTPUT_FILE!" | findstr /R "\.[^.]*$" >nul 2>&1
            if errorlevel 1 (
                REM 没有扩展名，添加.epub
                set "OUTPUT_FILE=!OUTPUT_FILE!.epub"
            )
        )
    )
)

REM 获取标题
echo 请输入电子书标题 (默认: 电子书):
set /p TITLE_INPUT=
if "!TITLE_INPUT!"=="" (
    set "TITLE=电子书"
) else (
    REM 直接使用输入值，去除首尾空格（如果需要）
    set "TITLE=!TITLE_INPUT!"
    REM 如果为空，使用默认值
    if "!TITLE!"=="" (
        set "TITLE=电子书"
    )
)

REM 获取作者
echo 请输入作者 (默认: 未知作者):
set /p AUTHOR_INPUT=
if "!AUTHOR_INPUT!"=="" (
    set "AUTHOR=未知作者"
) else (
    REM 直接使用输入值，去除首尾空格（如果需要）
    set "AUTHOR=!AUTHOR_INPUT!"
    REM 如果为空，使用默认值
    if "!AUTHOR!"=="" (
        set "AUTHOR=未知作者"
    )
)

echo.
echo ========================================
echo 开始转换...
echo   输入目录: !INPUT_DIR!
echo   输出文件: !OUTPUT_FILE!
echo   标题: !TITLE!
echo   作者: !AUTHOR!
echo ========================================
echo.

REM 执行转换（使用临时变量确保参数正确传递）
set "ARG_INPUT_DIR=!INPUT_DIR!"
set "ARG_OUTPUT_FILE=!OUTPUT_FILE!"
set "ARG_TITLE=!TITLE!"
set "ARG_AUTHOR=!AUTHOR!"
python html_to_epub.py "!ARG_INPUT_DIR!" -o "!ARG_OUTPUT_FILE!" -t "!ARG_TITLE!" -a "!ARG_AUTHOR!"

if errorlevel 1 (
    echo.
    echo [错误] 转换失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 转换完成！
echo ========================================
echo.
pause

