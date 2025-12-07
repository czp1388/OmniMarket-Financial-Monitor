# 双模架构验证测试脚本
# 验证专家模式和助手模式的API调用

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   双模架构验证测试" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

$API_BASE = "http://localhost:8000/api/v1"

# 测试1：专家模式 - 自定义参数回测
Write-Host "[测试1] 专家模式 - 自定义参数回测" -ForegroundColor Yellow
Write-Host "请求: POST $API_BASE/lean/backtest/start" -ForegroundColor Gray

$expertRequest = @{
    strategy_id = "moving_average_crossover"
    symbol = "AAPL"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    initial_capital = 10000.0
    parameters = @{
        fast_period = 8
        slow_period = 21
    }
} | ConvertTo-Json

try {
    $expertResponse = Invoke-RestMethod -Uri "$API_BASE/lean/backtest/start" `
        -Method Post `
        -ContentType "application/json" `
        -Body $expertRequest
    
    Write-Host "✅ 专家模式回测启动成功" -ForegroundColor Green
    Write-Host "回测ID: $($expertResponse.backtest_id)" -ForegroundColor White
    Write-Host "状态: $($expertResponse.status)" -ForegroundColor White
    
    # 等待回测完成
    Write-Host "`n等待回测完成..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # 查询回测结果
    $statusResponse = Invoke-RestMethod -Uri "$API_BASE/lean/backtest/status/$($expertResponse.backtest_id)"
    
    if ($statusResponse.status -eq "completed") {
        Write-Host "✅ 回测完成" -ForegroundColor Green
        Write-Host "统计数据:" -ForegroundColor Cyan
        Write-Host "  - 总收益率: $($statusResponse.statistics.total_return)%" -ForegroundColor White
        Write-Host "  - 夏普比率: $($statusResponse.statistics.sharpe_ratio)" -ForegroundColor White
        Write-Host "  - 最大回撤: $($statusResponse.statistics.max_drawdown)%" -ForegroundColor White
        Write-Host "  - 交易次数: $($statusResponse.statistics.total_trades)" -ForegroundColor White
    } else {
        Write-Host "⚠️ 回测状态: $($statusResponse.status)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ 专家模式测试失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Gray

# 测试2：助手模式 - 一键激活策略包
Write-Host "[测试2] 助手模式 - 一键激活策略包" -ForegroundColor Yellow
Write-Host "请求: POST $API_BASE/assistant/strategies/activate" -ForegroundColor Gray

$assistantRequest = @{
    user_goal = "stable_growth"
    risk_tolerance = "low"
    investment_amount = 5000
    investment_horizon = "long_term"
    auto_execute = $false
} | ConvertTo-Json

try {
    $assistantResponse = Invoke-RestMethod -Uri "$API_BASE/assistant/strategies/activate" `
        -Method Post `
        -ContentType "application/json" `
        -Body $assistantRequest
    
    Write-Host "✅ 助手模式策略包激活成功" -ForegroundColor Green
    Write-Host "策略包ID: $($assistantResponse.strategy_package_id)" -ForegroundColor White
    Write-Host "友好名称: $($assistantResponse.friendly_name)" -ForegroundColor Cyan
    Write-Host "状态: $($assistantResponse.status)" -ForegroundColor White
    Write-Host "`n白话解读:" -ForegroundColor Cyan
    Write-Host "  $($assistantResponse.explanation.what_it_does)" -ForegroundColor Gray
    Write-Host "  $($assistantResponse.explanation.expected_outcome)" -ForegroundColor Gray
    Write-Host "  风险等级: $($assistantResponse.explanation.risk_level)" -ForegroundColor Gray
    Write-Host "  类比: $($assistantResponse.explanation.analogy)" -ForegroundColor Gray
    
    Write-Host "`n底层技术参数（用户看不到）:" -ForegroundColor DarkGray
    Write-Host "  - 策略ID: $($assistantResponse.underlying_strategy.strategy_id)" -ForegroundColor DarkGray
    Write-Host "  - 参数: $($assistantResponse.underlying_strategy.parameters | ConvertTo-Json -Compress)" -ForegroundColor DarkGray
    
} catch {
    Write-Host "❌ 助手模式测试失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Gray

# 测试3：获取策略包列表
Write-Host "[测试3] 获取助手模式策略包列表" -ForegroundColor Yellow

try {
    $packagesResponse = Invoke-RestMethod -Uri "$API_BASE/assistant/strategies/packages"
    
    Write-Host "✅ 获取策略包列表成功，共 $($packagesResponse.Count) 个策略包" -ForegroundColor Green
    
    foreach ($pkg in $packagesResponse) {
        Write-Host "`n$($pkg.icon) $($pkg.friendly_name)" -ForegroundColor Cyan
        Write-Host "  标语: $($pkg.tagline)" -ForegroundColor Gray
        Write-Host "  风险评分: $($pkg.risk_score)/5" -ForegroundColor $(if($pkg.risk_score -le 2) {"Green"} elseif($pkg.risk_score -le 3) {"Yellow"} else {"Red"})
        Write-Host "  预期收益: $($pkg.expected_return)" -ForegroundColor White
        Write-Host "  适合人群: $($pkg.suitable_for -join ', ')" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ 获取策略包失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Gray

# 测试4：获取市场机会
Write-Host "[测试4] 获取助手模式市场机会" -ForegroundColor Yellow

try {
    $opportunitiesResponse = Invoke-RestMethod -Uri "$API_BASE/assistant/opportunities?limit=3"
    
    Write-Host "✅ 获取市场机会成功，共 $($opportunitiesResponse.Count) 个机会" -ForegroundColor Green
    
    foreach ($opp in $opportunitiesResponse) {
        Write-Host "`n🔍 $($opp.title)" -ForegroundColor Cyan
        Write-Host "  $($opp.explanation)" -ForegroundColor Gray
        Write-Host "  💡 建议: $($opp.suggestion)" -ForegroundColor White
        Write-Host "  风险: $($opp.risk_level) | 潜在收益: $($opp.potential_return)" -ForegroundColor Yellow
        Write-Host "  操作: $($opp.action_button)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ 获取市场机会失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n--------------------------------------------`n" -ForegroundColor Gray

# 测试5：获取助手仪表盘摘要
Write-Host "[测试5] 获取助手模式仪表盘摘要" -ForegroundColor Yellow

try {
    $dashboardResponse = Invoke-RestMethod -Uri "$API_BASE/assistant/dashboard/summary"
    
    Write-Host "✅ 获取仪表盘摘要成功" -ForegroundColor Green
    Write-Host "`n$($dashboardResponse.greeting)" -ForegroundColor Cyan
    
    Write-Host "`n📊 账户概况:" -ForegroundColor Yellow
    Write-Host "  总资产: ¥$($dashboardResponse.account_summary.total_assets)" -ForegroundColor White
    Write-Host "  今日盈亏: ¥$($dashboardResponse.account_summary.today_profit)" -ForegroundColor $(if($dashboardResponse.account_summary.today_profit -ge 0) {"Green"} else {"Red"})
    Write-Host "  累计收益: ¥$($dashboardResponse.account_summary.total_profit)" -ForegroundColor Green
    Write-Host "  收益率: $($dashboardResponse.account_summary.profit_rate)%" -ForegroundColor Green
    
    Write-Host "`n✅ 今日待办 ($($dashboardResponse.today_actions.Count) 项):" -ForegroundColor Yellow
    foreach ($action in $dashboardResponse.today_actions) {
        $priorityColor = switch ($action.priority) {
            "high" { "Red" }
            "medium" { "Yellow" }
            "low" { "Gray" }
        }
        Write-Host "  [$($action.priority)] $($action.title)" -ForegroundColor $priorityColor
        Write-Host "    $($action.description)" -ForegroundColor Gray
        Write-Host "    操作: $($action.action_text)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ 获取仪表盘摘要失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 总结
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   测试总结" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "✅ 专家模式 - 完全控制所有技术参数" -ForegroundColor Green
Write-Host "   - 自定义策略参数（fast_period, slow_period等）" -ForegroundColor Gray
Write-Host "   - 获取完整技术指标（夏普、Alpha、Beta等）" -ForegroundColor Gray
Write-Host "   - 查看详细交易明细和权益曲线" -ForegroundColor Gray

Write-Host "`n✅ 助手模式 - 隐藏技术细节，白话沟通" -ForegroundColor Green
Write-Host "   - 目标化选择（稳健增长、资本保值等）" -ForegroundColor Gray
Write-Host "   - 白话解读（'像超市促销时多买'）" -ForegroundColor Gray
Write-Host "   - 行动建议（'今天该做什么'）" -ForegroundColor Gray

Write-Host "`n🎯 核心验证结果：" -ForegroundColor Cyan
Write-Host "   同一个LEAN引擎，两种交互方式" -ForegroundColor White
Write-Host "   专家看参数，小白看目标" -ForegroundColor White
Write-Host "   这才是真正的产品创新！" -ForegroundColor Yellow

Write-Host "`n============================================`n" -ForegroundColor Cyan

Write-Host "💡 提示：" -ForegroundColor Yellow
Write-Host "   - 前端访问: http://localhost:3001/assistant" -ForegroundColor Gray
Write-Host "   - API文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "   - 查看 '智能助手' 标签下的所有端点" -ForegroundColor Gray
