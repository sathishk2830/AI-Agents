import React from 'react';
import './Navigation.css';

interface NavigationProps {
  currentPage: string;
  onPageChange: (page: any) => void;
}

const Navigation: React.FC<NavigationProps> = ({ currentPage, onPageChange }) => {
  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <h1>🚀 TP Creator</h1>
          <p>Intelligence Test Plan Agent</p>
        </div>
        <ul className="nav-links">
          <li>
            <button
              className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => onPageChange('dashboard')}
            >
              📊 Dashboard
            </button>
          </li>
          <li>
            <button
              className={`nav-link ${currentPage === 'settings' ? 'active' : ''}`}
              onClick={() => onPageChange('settings')}
            >
              ⚙️ Settings
            </button>
          </li>
          <li>
            <button
              className={`nav-link ${currentPage === 'history' ? 'active' : ''}`}
              onClick={() => onPageChange('history')}
            >
              📋 History
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
