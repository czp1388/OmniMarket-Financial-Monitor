import React, { ReactNode } from 'react';
import './MainLayout.css';

interface MainLayoutProps {
  children: ReactNode;
  sidebar?: ReactNode;
  header?: ReactNode;
  className?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({ 
  children, 
  sidebar, 
  header,
  className = '' 
}) => {
  return (
    <div className={`main-layout ${className}`}>
      {header && <header className="main-header">{header}</header>}
      
      <div className="main-content-wrapper">
        {sidebar && (
          <aside className="main-sidebar">
            {sidebar}
          </aside>
        )}
        
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
