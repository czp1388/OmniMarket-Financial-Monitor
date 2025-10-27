// 寰宇金融监控系统 - 主应用JavaScript
class FinancialMonitor {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.marketData = {};
        
        this.init();
    }

    init() {
        this.initWebSocket();
        this.loadInitialData();
        this.setupEventListeners();
    }

    // 初始化WebSocket连接
    initWebSocket() {
        const wsUrl = 'ws://' + window.location.host + '/ws/realtime';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket连接已建立');
                this.updateConnectionStatus(true);
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMarketData(data);
                } catch (error) {
                    console.error('解析WebSocket数据失败:', error);
                }
            };

            this.ws.onclose = () => {
                console.log('❌ WebSocket连接已关闭');
                this.updateConnectionStatus(false);
                this.handleReconnection();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket错误:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('初始化WebSocket失败:', error);
        }
    }

    // 处理市场数据更新
    handleMarketData(data) {
        if (data.type === 'market_data' && data.data) {
            this.marketData = data.data;
            this.renderMarketData();
        }
    }

    // 渲染市场数据
    renderMarketData() {
        const container = document.getElementById('market-data');
        if (!container) return;

        const symbols = Object.keys(this.marketData);
        
        if (symbols.length === 0) {
            container.innerHTML = '<div class="loading">暂无市场数据</div>';
            return;
        }

        let html = '';
        
        symbols.forEach(symbol => {
            const item = this.marketData[symbol];
            const change = item.change || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSymbol = change >= 0 ? '+' : '';
            
            html += `
                <div class="market-card ${changeClass}">
                    <div class="symbol">${symbol}</div>
                    <div class="price">$${this.formatNumber(item.price)}</div>
                    <div class="change ${changeClass}">
                        ${changeSymbol}${change}%
                    </div>
                    <div class="volume">24h量: ${this.formatNumber(item.volume)}</div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    // 格式化数字
    formatNumber(num) {
        if (typeof num !== 'number') return '0';
        
        if (num >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(2) + 'K';
        } else if (num >= 1) {
            return num.toFixed(2);
        } else {
            return num.toFixed(6);
        }
    }

    // 更新连接状态
    updateConnectionStatus(connected) {
        let statusElement = document.getElementById('connection-status');
        
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'connection-status';
            document.body.appendChild(statusElement);
        }

        if (connected) {
            statusElement.className = 'connection-status connected';
            statusElement.textContent = '🟢 实时连接';
        } else {
            statusElement.className = 'connection-status disconnected';
            statusElement.textContent = '🔴 连接断开';
        }
    }

    // 处理重新连接
    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            
            console.log(`尝试重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.initWebSocket();
            }, delay);
        } else {
            console.error('达到最大重连次数，停止尝试');
        }
    }

    // 加载初始数据
    async loadInitialData() {
        try {
            const response = await fetch('/api/v1/realtime/prices');
            const data = await response.json();
            
            if (data.data) {
                this.marketData = data.data;
                this.renderMarketData();
            }
        } catch (error) {
            console.error('加载初始数据失败:', error);
        }
    }

    // 设置事件监听器
    setupEventListeners() {
        // 可以添加其他事件监听器
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    window.financialMonitor = new FinancialMonitor();
});

// 工具函数
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
