# MyAgent 启动脚本 (Windows)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "启动 MyAgent" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "错误: 未找到虚拟环境，请先运行 install.ps1" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# 启动 Agent
Write-Host "启动 MyAgent..." -ForegroundColor Yellow
Write-Host ""

python -m src.main
