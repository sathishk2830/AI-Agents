import React, { useState, useEffect } from 'react';
import './App.css';
import Navigation from './components/Navigation';
import Settings from './pages/Settings';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import { healthAPI } from './api';

type Page = 'dashboard' | 'settings' | 'history';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [isHealthy, setIsHealthy] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      await healthAPI.check();
      setIsHealthy(true);
      setLoading(false);
    } catch (error) {
      setIsHealthy(false);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Connecting to backend...</p>
        </div>
      </div>
    );
  }

  if (!isHealthy) {
    return (
      <div className="app">
        <div className="error-container">
          <h1>⚠️ Backend Unavailable</h1>
          <p>The backend server is not responding. Please ensure it's running on localhost:8000</p>
          <p style={{ fontSize: '0.9em', marginTop: '1em', opacity: 0.7 }}>
            Run: <code>cd backend && python -m uvicorn main:app --reload</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
      <main className="main-content">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'settings' && <Settings />}
        {currentPage === 'history' && <History />}
      </main>
    </div>
  );
}

export default App;
