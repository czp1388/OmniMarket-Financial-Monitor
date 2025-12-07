# 双模架构 - curl 测试示例
# 展示专家模式 vs 助手模式的API调用差异

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   双模架构 - API 调用演示" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

$API_BASE = "http://localhost:8000/api/v1"

Write-Host "提示：请确保后端服务正在运行（端口8000）" -ForegroundColor Yellow
Write-Host "如未启动，请运行: cd backend && uvicorn main:app --reload`n" -ForegroundColor Gray

# ==================== 专家模式 ====================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   专家模式：完全控制技术参数" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "curl命令：" -ForegroundColor Green
$expertCurl = @"
curl -X POST '$API_BASE/lean/backtest/start' \
  -H 'Content-Type: application/json' \
  -d '{
    "strategy_id": "moving_average_crossover",
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000.0,
    "parameters": {
      "fast_period": 8,
      "slow_period": 21,
      "stop_loss": 0.02,
      "take_profit": 0.05
    }
  }'
"@

Write-Host $expertCurl -ForegroundColor Gray

Write-Host "`n特点：" -ForegroundColor Cyan
Write-Host "  ✓ 暴露所有技术参数（fast_period, slow_period）" -ForegroundColor White
Write-Host "  ✓ 精确控制止损止盈（2%, 5%）" -ForegroundColor White
Write-Host "  ✓ 返回完整技术指标（夏普、Alpha、Beta）" -ForegroundColor White

# ==================== 助手模式 ====================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   助手模式：隐藏技术细节，目标化表达" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "curl命令：" -ForegroundColor Green
$assistantCurl = @"
curl -X POST '$API_BASE/assistant/strategies/activate' \
  -H 'Content-Type: application/json' \
  -d '{
    "user_goal": "stable_growth",
    "risk_tolerance": "low",
    "investment_amount": 5000,
    "investment_horizon": "long_term"
  }'
"@

Write-Host $assistantCurl -ForegroundColor Gray

Write-Host "`n特点：" -ForegroundColor Cyan
Write-Host "  ✓ 用白话表达目标（稳健增长，低风险）" -ForegroundColor White
Write-Host "  ✓ 系统自动选择策略和参数" -ForegroundColor White
Write-Host "  ✓ 返回通俗解读（'像超市促销时多买'）" -ForegroundColor White

# ==================== 对比 ====================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   核心差异对比" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$comparison = @"
┌─────────────────┬───────────────────────┬───────────────────────┐
│     维度        │      专家模式         │      助手模式         │
├─────────────────┼───────────────────────┼───────────────────────┤
│ 请求复杂度      │ 需要理解10+个参数     │ 只需3-4个简单选择     │
│ 技术门槛        │ 懂金融+编程           │ 零基础可用            │
│ 参数可见性      │ 完全暴露              │ 完全隐藏              │
│ 返回数据        │ 夏普/Alpha/Beta等     │ '预期收益8-12%'       │
│ 适用人群        │ 量化交易员            │ 普通投资者            │
│ 底层引擎        │ 同一个LEAN引擎        │ 同一个LEAN引擎        │
└─────────────────┴───────────────────────┴───────────────────────┘
"@

Write-Host $comparison -ForegroundColor White

Write-Host "`n💡 关键洞察：" -ForegroundColor Yellow
Write-Host "   - 同一个回测引擎，两种交互方式" -ForegroundColor Gray
Write-Host "   - 专家看参数，小白看目标" -ForegroundColor Gray
Write-Host "   - 这才是真正的产品创新！" -ForegroundColor Gray

# ==================== 实际测试 ====================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   是否执行实际测试？" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$response = Read-Host "输入 'y' 执行测试（需要后端运行中），或按Enter跳过"

if ($response -eq 'y') {
    Write-Host "`n开始测试..." -ForegroundColor Green
    
    # 测试1：助手模式
    Write-Host "`n[1/2] 测试助手模式API..." -ForegroundColor Yellow
    
    $assistantBody = @{
        user_goal = "stable_growth"
        risk_tolerance = "low"
        investment_amount = 5000
        investment_horizon = "long_term"
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$API_BASE/assistant/strategies/activate" `
            -Method Post `
            -ContentType "application/json" `
            -Body $assistantBody
        
        Write-Host "✅ 助手模式测试成功！" -ForegroundColor Green
        Write-Host "策略包: $($result.friendly_name)" -ForegroundColor Cyan
        Write-Host "解读: $($result.explanation.what_it_does)" -ForegroundColor Gray
        Write-Host "类比: $($result.explanation.analogy)" -ForegroundColor Gray
        
    } catch {
        Write-Host "❌ 助手模式测试失败" -ForegroundColor Red
        Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 测试2：获取策略包列表
    Write-Host "`n[2/2] 获取策略包列表..." -ForegroundColor Yellow
    
    try {
        $packages = Invoke-RestMethod -Uri "$API_BASE/assistant/strategies/packages"
        
        Write-Host "✅ 获取成功，共 $($packages.Count) 个策略包：" -ForegroundColor Green
        
        foreach ($pkg in $packages) {
            Write-Host "`n  $($pkg.icon) $($pkg.friendly_name)" -ForegroundColor Cyan
            Write-Host "     $($pkg.tagline)" -ForegroundColor Gray
            Write-Host "     风险: $($pkg.risk_score)/5 | 收益: $($pkg.expected_return)" -ForegroundColor White
        }
        
    } catch {
        Write-Host "❌ 获取失败" -ForegroundColor Red
        Write-Host "错误: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n跳过实际测试" -ForegroundColor Gray
}

# ==================== 总结 ====================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   测试完成！" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

Write-Host "📚 更多测试：" -ForegroundColor Yellow
Write-Host "  - API文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  - 助手界面: http://localhost:3001/assistant" -ForegroundColor Gray
Write-Host "  - 专家界面: http://localhost:3001/expert" -ForegroundColor Gray

Write-Host "`n💡 下一步开发：" -ForegroundColor Yellow
Write-Host "  1. 完善助手界面（AssistantDashboard.tsx）" -ForegroundColor Gray
Write-Host "  2. 添加更多策略包" -ForegroundColor Gray
Write-Host "  3. 实现市场机会推荐算法" -ForegroundColor Gray
Write-Host "  4. 用户目标跟踪功能" -ForegroundColor Gray

Write-Host ""
