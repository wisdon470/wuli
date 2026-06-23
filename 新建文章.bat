@echo off
chcp 65001 >nul
title 新建博客文章
color 0E

echo ========================================
echo       新建博客文章
echo ========================================
echo.

set /p title=请输入文章标题: 

if "%title%"=="" (
    echo 标题不能为空！
    pause
    exit /b
)

set "filename=%title: =-%"

(
echo ---
echo title: %title%
echo date: %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%:%time:~3,2%:%time:~6,2%
echo categories:
echo   - 随笔
echo tags:
echo   - 感悟
echo ---
echo.
echo # %title%
echo.
echo 在这里写下你的文章内容...
echo.
echo ## 图片插入示例
echo.
echo ^![图片描述^](图片链接或路径)
echo.
) > "C:\Users\Administrator\myblog\source\_posts\%filename%.md"

echo.
echo 文章已创建: source\_posts\%filename%.md
echo.
echo 按任意键用记事本打开编辑...
pause >nul

notepad "C:\Users\Administrator\myblog\source\_posts\%filename%.md"
