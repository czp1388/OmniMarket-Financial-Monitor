// OmniMarket 统一主题系统
// 基于彭博终端 + TradingView 专业设计

export const theme = {
  // 颜色系统
  colors: {
    // 主背景
    background: {
      primary: '#0a0e17',      // 深蓝黑主背景
      secondary: '#141a2a',    // 卡片/面板背景
      tertiary: '#1a2332',     // 次级容器背景
      elevated: '#1f2937',     // 悬浮/弹出层背景
      hover: '#2a3a5a',        // 悬停状态
      input: '#0d1117',        // 输入框背景
    },
    
    // 边框
    border: {
      primary: '#2a3a5a',      // 主边框
      secondary: '#1f2937',    // 次级边框
      accent: '#00ccff',       // 强调边框
      divider: '#374151',      // 分隔线
    },
    
    // 文本
    text: {
      primary: '#e5e7eb',      // 主文本
      secondary: '#9ca3af',    // 次级文本
      tertiary: '#6b7280',     // 辅助文本
      inverse: '#ffffff',      // 反色文本
      muted: '#4b5563',        // 弱化文本
    },
    
    // 价格/趋势
    market: {
      up: '#00ff88',           // 上涨/买入
      down: '#ff4444',         // 下跌/卖出
      neutral: '#6b7280',      // 中性
      upBg: 'rgba(0, 255, 136, 0.1)',    // 上涨背景
      downBg: 'rgba(255, 68, 68, 0.1)',  // 下跌背景
    },
    
    // 功能色
    accent: {
      blue: '#00ccff',         // 信息蓝
      cyan: '#0ea5e9',         // 天蓝
      purple: '#a855f7',       // 紫色
      orange: '#fb923c',       // 橙色
      yellow: '#fbbf24',       // 黄色
      pink: '#ec4899',         // 粉色
    },
    
    // 状态色
    status: {
      success: '#10b981',      // 成功
      warning: '#f59e0b',      // 警告
      error: '#ef4444',        // 错误
      info: '#3b82f6',         // 信息
    },
    
    // 图表色
    chart: {
      candle: {
        up: '#00ff88',
        down: '#ff4444',
        upBorder: '#00ff88',
        downBorder: '#ff4444',
        upWick: '#00ff88',
        downWick: '#ff4444',
      },
      line: ['#00ccff', '#a855f7', '#fb923c', '#10b981', '#f59e0b'],
      volume: {
        up: 'rgba(0, 255, 136, 0.5)',
        down: 'rgba(255, 68, 68, 0.5)',
      },
      grid: '#1f2937',
    },
  },
  
  // 字体系统
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'JetBrains Mono', 'Courier New', monospace",
    display: "'SF Pro Display', -apple-system, sans-serif",
  },
  
  // 字体大小
  fontSize: {
    xs: '0.625rem',    // 10px
    sm: '0.75rem',     // 12px
    base: '0.875rem',  // 14px
    md: '0.875rem',    // 14px
    lg: '1rem',        // 16px
    xl: '1.125rem',    // 18px
    '2xl': '1.25rem',  // 20px
    '3xl': '1.5rem',   // 24px
    '4xl': '2rem',     // 32px
  },
  
  // 间距系统
  spacing: {
    xs: '0.25rem',     // 4px
    sm: '0.5rem',      // 8px
    md: '0.75rem',     // 12px
    lg: '1rem',        // 16px
    xl: '1.5rem',      // 24px
    '2xl': '2rem',     // 32px
    '3xl': '3rem',     // 48px
  },
  
  // 圆角
  borderRadius: {
    none: '0',
    sm: '0.25rem',     // 4px
    md: '0.375rem',    // 6px
    lg: '0.5rem',      // 8px
    xl: '0.75rem',     // 12px
    full: '9999px',
  },
  
  // 阴影
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.5)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.5)',
    glow: '0 0 20px rgba(0, 204, 255, 0.3)',
    glowGreen: '0 0 20px rgba(0, 255, 136, 0.3)',
    glowRed: '0 0 20px rgba(255, 68, 68, 0.3)',
  },
  
  // 过渡动画
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: '500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
  
  // Z-index 层级
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    modal: 1200,
    popover: 1300,
    tooltip: 1400,
    notification: 1500,
  },
  
  // 布局断点
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // 组件尺寸
  sizes: {
    header: {
      height: '60px',
    },
    sidebar: {
      width: '240px',
      collapsedWidth: '64px',
    },
    panel: {
      minHeight: '200px',
    },
  },
};

// 工具函数
export const rgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const formatPrice = (price: number, decimals: number = 2): string => {
  return price.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

export const formatPercent = (percent: number, decimals: number = 2): string => {
  const sign = percent >= 0 ? '+' : '';
  return `${sign}${percent.toFixed(decimals)}%`;
};

export const formatVolume = (volume: number): string => {
  if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`;
  if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`;
  if (volume >= 1e3) return `${(volume / 1e3).toFixed(2)}K`;
  return volume.toString();
};

export default theme;
