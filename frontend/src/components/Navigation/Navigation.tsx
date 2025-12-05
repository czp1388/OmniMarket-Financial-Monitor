import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

interface NavItem {
  path: string;
  label: string;
  icon?: string;
}

interface NavigationProps {
  items: NavItem[];
  className?: string;
}

const Navigation: React.FC<NavigationProps> = ({ items, className = '' }) => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className={`navigation ${className}`}>
      {items.map((item) => (
        <button
          key={item.path}
          className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          onClick={() => navigate(item.path)}
        >
          {item.icon && <span className="nav-icon">{item.icon}</span>}
          <span className="nav-label">{item.label}</span>
        </button>
      ))}
    </nav>
  );
};

export default Navigation;
