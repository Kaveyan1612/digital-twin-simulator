import React, { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import './App.css';

type Page = 'dashboard' | 'analytics' | 'history' | 'settings';

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const navigation = [
    { id: 'dashboard', label: 'DASHBOARD', icon: '📊' },
    { id: 'analytics', label: 'ANALYTICS', icon: '📈' },
    { id: 'history', label: 'HISTORY', icon: '📋' },
    { id: 'settings', label: 'SETTINGS', icon: '⚙️' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard': return <Dashboard />;
      case 'analytics': return <Analytics />;
      case 'history': return <History />;
      case 'settings': return <Settings />;
    }
  };

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>DIGITAL TWIN</h2>
        </div>
        <ul className="nav-menu">
          {navigation.map(item => (
            <li key={item.id}>
              <button
                className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id as Page)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="sidebar-footer">
          <div className="version">v1.0.0</div>
        </div>
      </nav>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
};