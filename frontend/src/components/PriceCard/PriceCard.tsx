import React from 'react';
import './PriceCard.css';

interface PriceCardProps {
  symbol: string;
  name?: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  high24h?: number;
  low24h?: number;
  marketCap?: string;
  onClick?: () => void;
  className?: string;
}

const PriceCard: React.FC<PriceCardProps> = ({
  symbol,
  name,
  price,
  change,
  changePercent,
  volume,
  high24h,
  low24h,
  marketCap,
  onClick,
  className = '',
}) => {
  const isPositive = changePercent >= 0;
  const changeClass = isPositive ? 'positive' : 'negative';

  const formatPrice = (value: number): string => {
    if (value >= 1000) {
      return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return value.toFixed(value < 1 ? 6 : 2);
  };

  const formatVolume = (vol: number): string => {
    if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`;
    if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`;
    if (vol >= 1e3) return `${(vol / 1e3).toFixed(2)}K`;
    return vol.toString();
  };

  return (
    <div 
      className={`price-card ${changeClass} ${onClick ? 'clickable' : ''} ${className}`}
      onClick={onClick}
    >
      <div className="price-card-header">
        <div className="symbol-info">
          <div className="symbol-main">
            <span className="symbol-text">{symbol}</span>
            {name && <span className="symbol-name">{name}</span>}
          </div>
        </div>
        
        <div className={`change-indicator ${changeClass}`}>
          <span className="change-arrow">{isPositive ? '▲' : '▼'}</span>
        </div>
      </div>

      <div className="price-card-body">
        <div className="price-main">
          <span className="price-value text-mono">${formatPrice(price)}</span>
        </div>
        
        <div className={`price-change ${changeClass}`}>
          <span className="change-value text-mono">
            {isPositive ? '+' : ''}{formatPrice(change)}
          </span>
          <span className="change-percent text-mono">
            ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
          </span>
        </div>
      </div>

      {(volume || high24h || low24h || marketCap) && (
        <div className="price-card-footer">
          {volume !== undefined && (
            <div className="stat-item">
              <span className="stat-label">24h成交</span>
              <span className="stat-value text-mono">{formatVolume(volume)}</span>
            </div>
          )}
          
          {high24h !== undefined && low24h !== undefined && (
            <div className="stat-item">
              <span className="stat-label">24h区间</span>
              <span className="stat-value text-mono">
                {formatPrice(low24h)} - {formatPrice(high24h)}
              </span>
            </div>
          )}
          
          {marketCap && (
            <div className="stat-item">
              <span className="stat-label">市值</span>
              <span className="stat-value text-mono">{marketCap}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PriceCard;
