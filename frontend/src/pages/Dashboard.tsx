import React, { useState } from 'react';
import { jiraAPI, generationAPI } from '../api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [issueName, setIssueName] = useState('');
  const [issueDetails, setIssueDetails] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [generationId, setGenerationId] = useState('');
  const [provider, setProvider] = useState('grok');

  const handleFetchIssue = async () => {
    if (!issueName.trim()) {
      setStatus('❌ Please enter an issue key');
      return;
    }

    setLoading(true);
    setStatus('Fetching issue...');
    try {
      const response = await jiraAPI.fetchIssue(issueName.toUpperCase());
      setIssueDetails(response.data);
      setStatus('✅ Issue fetched successfully');
      setTimeout(() => setStatus(''), 3000);
    } catch (error: any) {
      setStatus('❌ Failed to fetch issue: ' + error.response?.data?.detail || error.message);
      setIssueDetails(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTestPlan = async () => {
    if (!issueDetails) {
      setStatus('❌ Please fetch an issue first');
      return;
    }

    setLoading(true);
    setStatus('Generating test plan...');
    setGeneratedContent('');
    try {
      const response = await generationAPI.generateTestPlan({
        jira_details: issueDetails,
        provider,
      });

      setGeneratedContent(response.data.content);
      setGenerationId(response.data.id);
      setStatus('✅ Test plan generated successfully');
      setTimeout(() => setStatus(''), 3000);
    } catch (error: any) {
      setStatus('❌ Generation failed: ' + error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (format: 'pdf' | 'docx' | 'md') => {
    if (!generationId) {
      setStatus('❌ No content to export');
      return;
    }

    const urls: { [key: string]: string } = {
      pdf: generationAPI.downloadPDF(generationId),
      docx: generationAPI.downloadDOCX(generationId),
      md: generationAPI.downloadMarkdown(generationId),
    };

    window.open(urls[format], '_blank');
  };

  return (
    <div className="dashboard-page">
      <h2>Test Plan Generator</h2>

      <div className="dashboard-layout">
        {/* Issue Fetcher */}
        <div className="panel issue-panel">
          <h3>1️⃣ Fetch Jira Issue</h3>
          <div className="input-group">
            <input
              type="text"
              placeholder="e.g., PROJ-123"
              value={issueName}
              onChange={(e) => setIssueName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleFetchIssue()}
            />
            <button
              onClick={handleFetchIssue}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? '⏳ Fetching...' : '🔍 Fetch'}
            </button>
          </div>

          {issueDetails && (
            <div className="issue-details">
              <h4>Issue Details</h4>
              <div className="detail-row">
                <span className="label">Key:</span>
                <span className="value">{issueDetails.key}</span>
              </div>
              <div className="detail-row">
                <span className="label">Summary:</span>
                <span className="value">{issueDetails.summary}</span>
              </div>
              <div className="detail-row">
                <span className="label">Priority:</span>
                <span className="value badge-priority">{issueDetails.priority}</span>
              </div>
              <div className="detail-row">
                <span className="label">Type:</span>
                <span className="value">{issueDetails.issueType}</span>
              </div>
              {issueDetails.description && (
                <div className="detail-row">
                  <span className="label">Description:</span>
                  <span className="value description-text">{issueDetails.description}</span>
                </div>
              )}
              {issueDetails.acceptanceCriteria && (
                <div className="detail-row">
                  <span className="label">Acceptance Criteria:</span>
                  <span className="value description-text">{issueDetails.acceptanceCriteria}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Generation Panel */}
        <div className="panel generation-panel">
          <h3>2️⃣ Generate Test Plan</h3>

          {issueDetails && (
            <>
              <div className="form-group">
                <label>LLM Provider</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  disabled={loading}
                >
                  <option value="grok">Grok</option>
                  <option value="ollama">Ollama</option>
                </select>
              </div>

              <button
                onClick={handleGenerateTestPlan}
                disabled={loading || !issueDetails}
                className="btn btn-primary full-width"
              >
                {loading ? '⏳ Generating...' : '🤖 Generate Test Plan'}
              </button>
            </>
          )}

          {!issueDetails && (
            <div className="info-message">
              👆 Fetch a Jira issue first to generate a test plan
            </div>
          )}
        </div>
      </div>

      {/* Generated Content */}
      {generatedContent && (
        <div className="panel content-panel">
          <h3>3️⃣ Generated Test Plan</h3>

          <div className="export-buttons">
            <button
              onClick={() => handleDownload('pdf')}
              className="btn btn-export"
            >
              📄 Download PDF
            </button>
            <button
              onClick={() => handleDownload('docx')}
              className="btn btn-export"
            >
              📊 Download Word
            </button>
            <button
              onClick={() => handleDownload('md')}
              className="btn btn-export"
            >
              📝 Download Markdown
            </button>
          </div>

          <div className="content-preview">
            <h4>Preview</h4>
            <pre>{generatedContent.substring(0, 2000)}...</pre>
            <p style={{ textAlign: 'center', marginTop: '1em', opacity: 0.7 }}>
              (Showing first 2000 characters - download to see full content)
            </p>
          </div>
        </div>
      )}

      {status && (
        <div className="status-bar">
          {status}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
