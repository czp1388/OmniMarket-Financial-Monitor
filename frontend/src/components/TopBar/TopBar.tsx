import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './TopBar.css';

interface TopBarProps {
  title?: string;
  showMarketSelector?: boolean;
  onMenuToggle?: () => void;
}

const TopBar: React.FC<TopBarProps> = ({ 
  title = 'OmniMarket',
  showMarketSelector = true,
  onMenuToggle 
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentTime, setCurrentTime] = useState(new Date());

  // 更新时间
  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const navigationItems = [
    { path: '/dashboard', label: '主控台', icon: '📊' },
    { path: '/kline', label: 'K线图', icon: '📈' },
    { path: '/bloomberg', label: '彭博风格', icon: '💹' },
    { path: '/virtual-trading', label: '虚拟交易', icon: '💰' },
    { path: '/auto-trading', label: '自动交易', icon: '🤖' },
    { path: '/warrants', label: '窝轮监控', icon: '🎯' },
    { path: '/alerts', label: '预警管理', icon: '🔔' },
    { path: '/portfolio', label: '投资组合', icon: '💼' },
  ];

  return (
    <div className="topbar">
      <div className="topbar-left">
        <button className="menu-toggle" onClick={onMenuToggle}>
          ☰
        </button>
        
        <div className="topbar-brand" onClick={() => navigate('/')}>
          <span className="brand-icon">📊</span>
          <span className="brand-text">{title}</span>
        </div>
        
        <div className="topbar-nav hide-mobile">
          {navigationItems.map((item) => (
            <button
              key={item.path}
              className={`topbar-nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
              title={item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="topbar-right">
        {showMarketSelector && (
          <div className="market-status">
            <div className="market-indicator">
              <span className="indicator-dot pulse"></span>
              <span className="indicator-text">实时数据</span>
            </div>
          </div>
        )}
        
        <div className="topbar-time text-mono">
          {currentTime.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          })}
        </div>
        
        <button className="topbar-settings" onClick={() => navigate('/settings')}>
          ⚙️
        </button>
      </div>
    </div>
  );
};

export default TopBar;
