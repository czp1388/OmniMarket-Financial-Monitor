import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();

  const navigation = [
    { name: '仪表板', href: '/', icon: '📊' },
    { name: '专业监控', href: '/financial-monitoring', icon: '📊' },
    { name: '图表分析', href: '/chart', icon: '📈' },
    { name: '预警管理', href: '/alerts', icon: '🔔' },
    { name: '投资组合', href: '/portfolio', icon: '💼' },
    { name: '系统设置', href: '/settings', icon: '⚙️' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={clsx(
          'shadow-lg transition-all duration-300',
          isSidebarOpen ? 'w-64' : 'w-20'
        )}
        style={{ background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' }}
      >
        <div className="p-4">
          <div className="flex items-center justify-between">
            {isSidebarOpen && (
              <h1 className="text-xl font-bold text-white">OmniMarket</h1>
            )}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-700 text-white"
            >
              {isSidebarOpen ? '←' : '→'}
            </button>
          </div>
        </div>

        <nav className="mt-8">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={clsx(
                'flex items-center px-4 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors',
                isActive(item.href) && 'bg-gray-700 text-white border-r-2 border-blue-500',
                isSidebarOpen ? 'justify-start' : 'justify-center'
              )}
            >
              <span className="text-lg">{item.icon}</span>
              {isSidebarOpen && (
                <span className="ml-3 font-medium text-xl">{item.name}</span>
              )}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="shadow-sm z-10" style={{ background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)' }}>
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h2 className="text-2xl font-semibold text-white">
                {navigation.find(item => item.href === location.pathname)?.name || '仪表板'}
              </h2>
              <p className="text-gray-300 text-sm">
                寰宇多市场金融监控系统
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-300">
                {new Date().toLocaleString('zh-CN')}
              </div>
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                U
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className={clsx(
          'flex-1 overflow-auto p-6',
          location.pathname === '/financial-monitoring' ? 'bg-transparent' : 'bg-gray-50'
        )}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
