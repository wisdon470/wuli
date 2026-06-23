@echo off
chcp 65001 >nul
title Hexo博客一键部署
color 0A

echo ========================================
echo       Hexo 博客一键部署
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0deploy.ps1"

pause
