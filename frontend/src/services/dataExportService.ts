// 数据导出服务
export class DataExportService {
  // 导出为CSV格式
  static exportToCSV(data: any[], filename: string = 'market_data.csv') {
    if (!data || data.length === 0) {
      alert('没有可导出的数据');
      return;
    }

    // 获取列名
    const headers = Object.keys(data[0]);
    
    // 构建CSV内容
    let csvContent = headers.join(',') + '\n';
    
    data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        // 处理包含逗号的字段
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return value;
      });
      csvContent += values.join(',') + '\n';
    });

    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    this.downloadBlob(blob, filename);
  }

  // 导出为JSON格式
  static exportToJSON(data: any[], filename: string = 'market_data.json') {
    if (!data || data.length === 0) {
      alert('没有可导出的数据');
      return;
    }

    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    this.downloadBlob(blob, filename);
  }

  // 导出为Excel格式（简化版CSV）
  static exportToExcel(data: any[], filename: string = 'market_data.xlsx') {
    // 使用CSV格式，Excel可以打开
    const excelFilename = filename.replace('.xlsx', '.csv');
    this.exportToCSV(data, excelFilename);
  }

  // 导出K线数据
  static exportKlineData(chartData: any[], symbol: string = 'UNKNOWN') {
    const formattedData = chartData.map(candle => ({
      '时间': candle.time,
      '开盘价': candle.open.toFixed(2),
      '最高价': candle.high.toFixed(2),
      '最低价': candle.low.toFixed(2),
      '收盘价': candle.close.toFixed(2),
      '成交量': candle.volume.toFixed(0),
    }));

    const filename = `kline_${symbol}_${new Date().toISOString().split('T')[0]}.csv`;
    this.exportToCSV(formattedData, filename);
  }

  // 导出市场数据
  static exportMarketData(marketData: any[]) {
    const formattedData = marketData.map(item => ({
      '品种': item.symbol,
      '价格': item.price.toFixed(2),
      '涨跌幅': item.changePercent.toFixed(2) + '%',
      '成交量': item.volume || 'N/A',
      '类型': item.type,
      '数据源': item.source,
      '更新时间': item.lastUpdate,
    }));

    const filename = `market_data_${new Date().toISOString().split('T')[0]}.csv`;
    this.exportToCSV(formattedData, filename);
  }

  // 下载Blob
  private static downloadBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // 复制到剪贴板
  static copyToClipboard(data: any[]) {
    if (!data || data.length === 0) {
      alert('没有可复制的数据');
      return;
    }

    const text = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(text).then(() => {
      alert('数据已复制到剪贴板');
    }).catch(err => {
      console.error('复制失败:', err);
      alert('复制失败，请手动复制');
    });
  }
}

export default DataExportService;
