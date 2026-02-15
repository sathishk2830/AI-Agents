import React, { useState, useEffect } from 'react';
import './History.css';

const History: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    // In a full implementation, this would fetch from the backend
    // For now, we'll show a placeholder
    loadHistoryFromLocalStorage();
  }, []);

  const loadHistoryFromLocalStorage = () => {
    // Store generation history in localStorage for demo purposes
    const stored = localStorage.getItem('tp-creator-history');
    if (stored) {
      setHistory(JSON.parse(stored));
    }
  };

  const filteredHistory = history.filter((item) =>
    item.jira_issue_id.toLowerCase().includes(filter.toLowerCase()) ||
    item.jira_summary.toLowerCase().includes(filter.toLowerCase())
  );

  if (history.length === 0) {
    return (
      <div className="history-page">
        <h2>Generation History</h2>
        <div className="empty-state">
          <p>📋 No test plans generated yet</p>
          <p style={{ marginTop: '1em', opacity: 0.8 }}>
            Go to the Dashboard to generate your first test plan
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <h2>Generation History</h2>

      <div className="history-controls">
        <input
          type="text"
          placeholder="Search by Jira issue or summary..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="search-input"
        />
        <span className="result-count">
          {filteredHistory.length} / {history.length} results
        </span>
      </div>

      <div className="history-list">
        {filteredHistory.length > 0 ? (
          filteredHistory.map((item, index) => (
            <div key={index} className="history-item">
              <div className="item-header">
                <div>
                  <h4>{item.jira_issue_id}</h4>
                  <p>{item.jira_summary}</p>
                </div>
                <span className="provider-badge">{item.provider_used}</span>
              </div>
              <div className="item-meta">
                <span>⏱️ {item.generation_time_seconds}s</span>
                <span>📅 {new Date(item.generated_at).toLocaleString()}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="no-results">
            No results found for "{filter}"
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
