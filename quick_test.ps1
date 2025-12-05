# 快速测试K线API
Write-Host "`n=== 测试K线API ===" -ForegroundColor Cyan
try {
    $result = Invoke-RestMethod "http://localhost:8000/api/v1/market/klines?symbol=BTC/USDT&market_type=crypto&exchange=binance&timeframe=1h&limit=3"
    Write-Host "✅ K线API测试成功！" -ForegroundColor Green
    Write-Host "返回数据量: $($result.Count)" -ForegroundColor White
    if ($result.Count -gt 0) {
        Write-Host "`n第一条K线数据:" -ForegroundColor Yellow
        $result[0] | Format-List symbol, exchange, timeframe, open, close, high, low, volume, timestamp
    }
} catch {
    Write-Host "❌ K线API测试失败" -ForegroundColor Red
    Write-Host "错误: $($_.Exception.Message)" -ForegroundColor DarkRed
}
