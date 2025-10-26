# 寰宇多市场金融监控系统 - 编码修复工具
Write-Host "🔧 修复文件编码问题..." -ForegroundColor Cyan

$ProjectRoot = "E:\OmniMarket-Financial-Monitor"
$BackendDir = "$ProjectRoot\backend\app"

# 创建UTF-8无BOM编码
$utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $false

# 要修复的文件列表
$filesToFix = @(
    "main.py",
    "routers\market.py", 
    "routers\alerts.py",
    "services\data_service.py",
    "services\alert_service.py"
)

Write-Host "正在修复以下文件的BOM编码:" -ForegroundColor Yellow
foreach ($file in $filesToFix) {
    $filePath = "$BackendDir\$file"
    if (Test-Path $filePath) {
        try {
            # 读取文件内容并重新保存为无BOM
            $content = Get-Content $filePath -Raw
            [System.IO.File]::WriteAllText($filePath, $content, $utf8NoBomEncoding)
            Write-Host "   ✅ $file" -ForegroundColor Green
        } catch {
            Write-Host "   ❌ $file - 修复失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ $file - 文件不存在" -ForegroundColor Yellow
    }
}

# 验证修复
Write-Host "`n验证编码修复..." -ForegroundColor Yellow
cd $BackendDir
try {
    python -c "import ast; ast.parse(open('main.py', encoding='utf-8').read()); print('✅ main.py 语法正确')"
    python -c "import ast; ast.parse(open('routers\market.py', encoding='utf-8').read()); print('✅ market.py 语法正确')"
    Write-Host "🎉 所有文件编码修复成功！" -ForegroundColor Green
} catch {
    Write-Host "❌ 编码修复验证失败: $($_.Exception.Message)" -ForegroundColor Red
}
