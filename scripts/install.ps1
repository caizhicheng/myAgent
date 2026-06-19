# MyAgent 安装脚本 (Windows)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "MyAgent 安装脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 版本
Write-Host "[1/5] 检查 Python 版本..." -ForegroundColor Yellow

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

Write-Host "Python 版本: $pythonVersion" -ForegroundColor Green

# 创建虚拟环境
Write-Host ""
Write-Host "[2/5] 创建虚拟环境..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "虚拟环境已存在，跳过创建" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "虚拟环境创建成功" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host ""
Write-Host "[3/5] 激活虚拟环境..." -ForegroundColor Yellow

& .\venv\Scripts\Activate.ps1
Write-Host "虚拟环境已激活" -ForegroundColor Green

# 安装依赖
Write-Host ""
Write-Host "[4/5] 安装依赖..." -ForegroundColor Yellow

pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 依赖安装失败" -ForegroundColor Red
    exit 1
}

Write-Host "依赖安装成功" -ForegroundColor Green

# 创建配置文件
Write-Host ""
Write-Host "[5/5] 创建配置文件..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "已创建 .env 文件，请编辑并填入你的 API Key" -ForegroundColor Green
} else {
    Write-Host ".env 文件已存在，跳过创建" -ForegroundColor Yellow
}

# 创建必要目录
$directories = @("data\sqlite", "data\chroma", "logs", "data\example")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 编辑 .env 文件，填入你的 API Key" -ForegroundColor White
Write-Host "2. 运行: .\venv\Scripts\activate" -ForegroundColor White
Write-Host "3. 运行: python -m src.main" -ForegroundColor White
Write-Host ""
