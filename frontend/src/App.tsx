import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FinancialMonitoringSystem from './pages/FinancialMonitoringSystem';
import ProfessionalTradingDashboard from './pages/ProfessionalTradingDashboard';
import BloombergStyleDashboard from './pages/BloombergStyleDashboard';
import KlineStyleDashboard from './pages/KlineStyleDashboard';
import ChartPage from './pages/ChartPage';
import AlertsPage from './pages/AlertsPage';
import PortfolioPage from './pages/PortfolioPage';
import SettingsPage from './pages/SettingsPage';
import VirtualTradingPage from './pages/VirtualTradingPage';
import WarrantsMonitoringPage from './pages/WarrantsMonitoringPage';
import AutoTradingPage from './pages/AutoTradingPage';
import SemiAutoTradingPage from './pages/SemiAutoTradingPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<KlineStyleDashboard />} />
        <Route path="/dashboard" element={<KlineStyleDashboard />} />
        <Route path="/kline" element={<KlineStyleDashboard />} />
        <Route path="/financial-monitoring" element={<FinancialMonitoringSystem />} />
        <Route path="/professional" element={<ProfessionalTradingDashboard />} />
        <Route path="/bloomberg" element={<BloombergStyleDashboard />} />
        <Route path="/chart" element={<ChartPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/virtual-trading" element={<VirtualTradingPage />} />
        <Route path="/warrants" element={<WarrantsMonitoringPage />} />
        <Route path="/auto-trading" element={<AutoTradingPage />} />
        <Route path="/semi-auto-trading" element={<SemiAutoTradingPage />} />
      </Routes>
    </Router>
  );
}

export default App;
