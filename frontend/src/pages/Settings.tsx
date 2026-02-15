import React, { useState, useEffect } from 'react';
import { jiraAPI, llmAPI, templateAPI } from '../api';
import './Settings.css';

const Settings: React.FC = () => {
  // Jira state
  const [jiraConfig, setJiraConfig] = useState({
    domain: '',
    email: '',
    api_token: '',
  });
  const [jiraStatus, setJiraStatus] = useState('');
  const [jiraLoading, setJiraLoading] = useState(false);

  // LLM state
  const [llmProvider, setLlmProvider] = useState('grok');
  const [llmConfig, setLlmConfig] = useState({
    provider: 'grok',
    grok_api_key: '',
    grok_model: 'grok-1',
    grok_temperature: 0.7,
    grok_max_tokens: 2000,
    ollama_url: 'http://localhost:11434',
    ollama_model: 'llama2',
  });
  const [llmStatus, setLlmStatus] = useState('');
  const [llmLoading, setLlmLoading] = useState(false);

  // Template state
  const [templateFile, setTemplateFile] = useState('');
  const [templateStatus, setTemplateStatus] = useState('');
  const [templateLoading, setTemplateLoading] = useState(false);

  // Load configs on mount
  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const [jiraRes, llmRes, templateRes] = await Promise.all([
        jiraAPI.getConfig().catch(() => null),
        llmAPI.getConfig().catch(() => null),
        templateAPI.getConfig().catch(() => null),
      ]);

      if (jiraRes?.data && !jiraRes.data.status) {
        setJiraConfig(jiraRes.data);
      }

      if (llmRes?.data && !llmRes.data.status) {
        setLlmConfig(llmRes.data);
        setLlmProvider(llmRes.data.provider);
      }

      if (templateRes?.data && !templateRes.data.status) {
        setTemplateFile(templateRes.data.file_path);
      }
    } catch (error) {
      console.error('Failed to load configs', error);
    }
  };

  // Jira handlers
  const handleJiraSave = async () => {
    setJiraLoading(true);
    setJiraStatus('Saving...');
    try {
      await jiraAPI.saveConfig(jiraConfig);
      setJiraStatus('✅ Saved successfully');
      setTimeout(() => setJiraStatus(''), 3000);
    } catch (error: any) {
      setJiraStatus('❌ Save failed: ' + error.message);
    } finally {
      setJiraLoading(false);
    }
  };

  const handleJiraTest = async () => {
    setJiraLoading(true);
    setJiraStatus('Testing...');
    try {
      const response = await jiraAPI.testConnection();
      setJiraStatus('✅ ' + response.data.message);
      setTimeout(() => setJiraStatus(''), 3000);
    } catch (error: any) {
      setJiraStatus('❌ Test failed: ' + error.response?.data?.detail || error.message);
    } finally {
      setJiraLoading(false);
    }
  };

  // LLM handlers
  const handleLlmSave = async () => {
    setLlmLoading(true);
    setLlmStatus('Saving...');
    try {
      await llmAPI.saveConfig({ ...llmConfig, provider: llmProvider });
      setLlmStatus('✅ Saved successfully');
      setTimeout(() => setLlmStatus(''), 3000);
    } catch (error: any) {
      setLlmStatus('❌ Save failed: ' + error.message);
    } finally {
      setLlmLoading(false);
    }
  };

  const handleLlmTest = async () => {
    setLlmLoading(true);
    setLlmStatus('Testing...');
    try {
      const response = await llmAPI.testConnection();
      setLlmStatus('✅ Connected: ' + response.data.status);
      setTimeout(() => setLlmStatus(''), 3000);
    } catch (error: any) {
      setLlmStatus('❌ Test failed: ' + error.response?.data?.detail || error.message);
    } finally {
      setLlmLoading(false);
    }
  };

  // Template handlers
  const handleTemplateSave = async () => {
    if (!templateFile) {
      setTemplateStatus('❌ Please specify a template file path');
      return;
    }
    setTemplateLoading(true);
    setTemplateStatus('Validating...');
    try {
      const response = await templateAPI.saveConfig({ file_path: templateFile });
      setTemplateStatus('✅ Template validated and saved');
      setTimeout(() => setTemplateStatus(''), 3000);
    } catch (error: any) {
      setTemplateStatus('❌ Validation failed: ' + error.response?.data?.detail || error.message);
    } finally {
      setTemplateLoading(false);
    }
  };

  return (
    <div className="settings-page">
      <h2>Configuration Settings</h2>

      {/* Jira Settings */}
      <div className="settings-card">
        <div className="card-header">
          <h3>Jira Cloud Configuration</h3>
          <span className="badge">Required</span>
        </div>
        <div className="form-group">
          <label>Jira Domain (e.g., your-domain.atlassian.net)</label>
          <input
            type="text"
            placeholder="your-domain.atlassian.net"
            value={jiraConfig.domain}
            onChange={(e) => setJiraConfig({ ...jiraConfig, domain: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            placeholder="your-email@company.com"
            value={jiraConfig.email}
            onChange={(e) => setJiraConfig({ ...jiraConfig, email: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>API Token</label>
          <input
            type="password"
            placeholder="••••••••••••••••••"
            value={jiraConfig.api_token}
            onChange={(e) => setJiraConfig({ ...jiraConfig, api_token: e.target.value })}
          />
        </div>
        <div className="button-group">
          <button onClick={handleJiraSave} disabled={jiraLoading} className="btn btn-primary">
            {jiraLoading ? '⏳ Saving...' : '💾 Save'}
          </button>
          <button onClick={handleJiraTest} disabled={jiraLoading} className="btn btn-secondary">
            {jiraLoading ? '⏳ Testing...' : '🧪 Test Connection'}
          </button>
        </div>
        {jiraStatus && <div className="status-message">{jiraStatus}</div>}
      </div>

      {/* LLM Settings */}
      <div className="settings-card">
        <div className="card-header">
          <h3>LLM Configuration</h3>
          <span className="badge">Required</span>
        </div>
        <div className="form-group">
          <label>Provider</label>
          <select
            value={llmProvider}
            onChange={(e) => {
              setLlmProvider(e.target.value);
              setLlmConfig({ ...llmConfig, provider: e.target.value });
            }}
          >
            <option value="grok">Grok (Cloud API)</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
        </div>

        {llmProvider === 'grok' && (
          <>
            <div className="form-group">
              <label>Grok API Key</label>
              <input
                type="password"
                placeholder="xai-••••••••••••••••••"
                value={llmConfig.grok_api_key}
                onChange={(e) => setLlmConfig({ ...llmConfig, grok_api_key: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Model</label>
              <select
                value={llmConfig.grok_model}
                onChange={(e) => setLlmConfig({ ...llmConfig, grok_model: e.target.value })}
              >
                <option value="grok-1">Grok 1</option>
                <option value="grok-1.5">Grok 1.5</option>
              </select>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Temperature (0.0 - 2.0)</label>
                <input
                  type="number"
                  min="0"
                  max="2"
                  step="0.1"
                  value={llmConfig.grok_temperature}
                  onChange={(e) =>
                    setLlmConfig({ ...llmConfig, grok_temperature: parseFloat(e.target.value) })
                  }
                />
              </div>
              <div className="form-group">
                <label>Max Tokens</label>
                <input
                  type="number"
                  min="100"
                  max="8192"
                  value={llmConfig.grok_max_tokens}
                  onChange={(e) =>
                    setLlmConfig({ ...llmConfig, grok_max_tokens: parseInt(e.target.value) })
                  }
                />
              </div>
            </div>
          </>
        )}

        {llmProvider === 'ollama' && (
          <>
            <div className="form-group">
              <label>Ollama Server URL</label>
              <input
                type="text"
                placeholder="http://localhost:11434"
                value={llmConfig.ollama_url}
                onChange={(e) => setLlmConfig({ ...llmConfig, ollama_url: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Model Name</label>
              <input
                type="text"
                placeholder="llama2, mistral, etc."
                value={llmConfig.ollama_model}
                onChange={(e) => setLlmConfig({ ...llmConfig, ollama_model: e.target.value })}
              />
            </div>
          </>
        )}

        <div className="button-group">
          <button onClick={handleLlmSave} disabled={llmLoading} className="btn btn-primary">
            {llmLoading ? '⏳ Saving...' : '💾 Save'}
          </button>
          <button onClick={handleLlmTest} disabled={llmLoading} className="btn btn-secondary">
            {llmLoading ? '⏳ Testing...' : '🧪 Test Connection'}
          </button>
        </div>
        {llmStatus && <div className="status-message">{llmStatus}</div>}
      </div>

      {/* Template Settings */}
      <div className="settings-card">
        <div className="card-header">
          <h3>Template Configuration</h3>
          <span className="badge">Optional</span>
        </div>
        <div className="form-group">
          <label>Template File Path (PDF, Markdown, or Text)</label>
          <input
            type="text"
            placeholder="C:\\templates\\test-plan-template.pdf"
            value={templateFile}
            onChange={(e) => setTemplateFile(e.target.value)}
          />
          <small>Upload your custom test plan template file for use in generation</small>
        </div>
        <div className="button-group">
          <button onClick={handleTemplateSave} disabled={templateLoading} className="btn btn-primary">
            {templateLoading ? '⏳ Validating...' : '✅ Validate & Save'}
          </button>
        </div>
        {templateStatus && <div className="status-message">{templateStatus}</div>}
      </div>
    </div>
  );
};

export default Settings;
