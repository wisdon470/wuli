# Hexo 博客一键部署脚本
# 功能：生成静态文件并推送到 GitHub Pages

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      Hexo 博客一键部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置路径
$BlogPath = "C:\Users\Administrator\myblog"
$PublicPath = "$BlogPath\public"
$NodePath = "C:\Program Files\nodejs\node.exe"

# 检查是否在正确的目录
Set-Location $BlogPath

Write-Host "[1/4] 清理旧文件..." -ForegroundColor Yellow
& $NodePath "$BlogPath\node_modules\hexo\bin\hexo" clean 2>$null
Write-Host "      ✓ 清理完成" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] 生成静态文件..." -ForegroundColor Yellow
& $NodePath "$BlogPath\node_modules\hexo\bin\hexo" generate 2>$null
Write-Host "      ✓ 生成完成" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] 推送到 GitHub..." -ForegroundColor Yellow

# 进入 public 目录
Set-Location $PublicPath

# 获取当前时间作为提交信息
$CommitMsg = "更新博客 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# 添加、提交、推送
git add . 2>$null
git commit -m "$CommitMsg" 2>$null
git push origin gh-pages 2>$null

Write-Host "      ✓ 推送完成" -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] 部署状态检查..." -ForegroundColor Yellow

# 检查推送是否成功
$PushResult = git log -1 --oneline 2>$null
Write-Host "      最新提交: $PushResult" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      🎉 博客部署成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址: https://wisdon470.github.io/wuli" -ForegroundColor Cyan
Write-Host ""

# 询问是否打开浏览器
$OpenBrowser = Read-Host "是否打开博客查看? (y/n)"
if ($OpenBrowser -eq "y" -or $OpenBrowser -eq "Y") {
    Start-Process "https://wisdon470.github.io/wuli"
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
