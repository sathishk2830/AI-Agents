import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Jira endpoints
export const jiraAPI = {
  getConfig: () => apiClient.get('/config/jira'),
  saveConfig: (data: any) => apiClient.post('/config/jira', data),
  testConnection: () => apiClient.post('/config/test-jira'),
  fetchIssue: (issueId: string) => apiClient.post(`/jira/issue/${issueId}`),
};

// LLM endpoints
export const llmAPI = {
  getConfig: () => apiClient.get('/config/llm'),
  saveConfig: (data: any) => apiClient.post('/config/llm', data),
  testConnection: () => apiClient.post('/config/test-llm'),
};

// Template endpoints
export const templateAPI = {
  getConfig: () => apiClient.get('/config/template'),
  saveConfig: (data: any) => apiClient.post('/config/template', data),
};

// Generation endpoints
export const generationAPI = {
  generateTestPlan: (data: any) => apiClient.post('/generate/test-plan', data),
  downloadPDF: (generationId: string) => `${API_BASE_URL}/export/${generationId}/pdf`,
  downloadDOCX: (generationId: string) => `${API_BASE_URL}/export/${generationId}/docx`,
  downloadMarkdown: (generationId: string) => `${API_BASE_URL}/export/${generationId}/md`,
};

// Health check
export const healthAPI = {
  check: () => apiClient.get('/health'),
};
