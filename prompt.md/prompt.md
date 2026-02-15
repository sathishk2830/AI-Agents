Here's a refined, structured prompt that will help generate a proper, production-ready web application for your intelligent test plan generator:

***

## **Enhanced Prompt for AI Code Generation: Intelligent Test Plan Generator**

### **Project Definition**
Create a full-stack web application that automatically generates professional test plans by fetching Jira issue details, applying a template-based structure, and processing through configurable LLM providers (Grok Cloud or local Ollama).

***

### **Application Architecture**

**Frontend (React-based Single Page Application):**
- **Technology:** React 18+ with TypeScript, Tailwind CSS, React Router
- **State Management:** Context API or Zustand for configuration state
- **UI Components:** Use shadcn/ui or Material-UI for consistent styling

**Backend (Python FastAPI):**
- **Framework:** FastAPI with Uvicorn server
- **API Structure:** RESTful endpoints with Pydantic validation
- **CORS:** Enable frontend at `localhost:3000` to access backend at `localhost:8000`

**Storage:**
- SQLite database for settings and configuration persistence
- Local filesystem for template storage and generated output

***

### **Feature Requirements**

#### **1. Settings/Configuration Module**
Create a settings page with the following sections:

**Jira Configuration Section:**
- Input fields: Jira Domain (e.g., `https://your-company.atlassian.net`), Email, API Token
- "Test Connection" button to validate credentials
- Save button to persist configuration to SQLite
- Display connection status (connected/disconnected)

**LLM Provider Configuration Section:**
- Radio toggle: "Grok (Cloud)" vs "Ollama (Local)"
- **Grok Settings (visible when selected):**
  - Input field for Grok API Key (`gsk_...`)
  - Model selection dropdown (`grok-2`, `grok-2-vision`, etc.)
  - Temperature slider (0.0 - 1.0)
  - Max tokens input
- **Ollama Settings (visible when selected):**
  - Server URL input (default: `http://localhost:11434`)
  - Model selection dropdown (fetch available models from `/api/tags`)
  - "Pull Model" button for downloading new models
- Save button to persist configuration
- Active provider indicator

**Template Configuration Section:**
- File path input for template location OR file upload
- Template preview viewer (display PDF/text content)
- Validation that template is accessible

***

#### **2. Test Plan Generation Module (Main Interface)**

**Jira Issue Input Section:**
- Input field for Jira Issue ID (e.g., "VW-1", "PROJ-123")
- "Fetch Details" button
- Display fetched issue summary in a card:
  - Issue Key, Summary, Description, Acceptance Criteria, Priority
  - Expandable section for full details

**Generation Section:**
- Preview selected template name
- "Generate Test Plan" button (disabled until Jira details fetched)
- Progress indicator with steps:
  1. Validating configuration
  2. Fetching Jira details
  3. Processing with LLM
  4. Formatting output
- Streaming display of LLM generation progress (optional)

**Output Section:**
- Rich text editor or preview pane showing generated test plan
- Export buttons: Download as PDF, Markdown, or Word (.docx)
- "Save to History" option
- "Regenerate" button to retry with same inputs

***

### **Backend API Endpoints (FastAPI)**

```python
# Configuration Endpoints
GET  /api/config/jira          # Get saved Jira config
POST /api/config/jira          # Save Jira credentials
GET  /api/config/llm           # Get LLM provider settings
POST /api/config/llm           # Save LLM settings (Grok/Ollama)
POST /api/config/test-jira     # Test Jira connection
POST /api/config/test-ollama   # Test Ollama connection

# Jira Integration Endpoints
GET  /api/jira/issue/{issue_id} # Fetch Jira issue details

# LLM Generation Endpoints
POST /api/generate/test-plan   # Main generation endpoint
Request body: {
  "jira_issue_id": "VW-1",
  "jira_details": {...},
  "template_content": "...",
  "provider": "grok" | "ollama"
}
Response: {
  "id": "uuid",
  "content": "Generated test plan text",
  "format": "markdown",
  "metadata": {...}
}

# Template Endpoints
GET  /api/template             # Load/parse template from local folder
POST /api/template/parse-pdf   # Parse PDF template content

# Export Endpoints
POST /api/export/pdf           # Convert markdown to PDF
POST /api/export/word          # Convert markdown to Word
```

***

### **LLM Integration Logic**

**Prompt Template for Test Plan Generation:**
```
You are a QA engineer creating a professional test plan. Use the following inputs:

JIRA ISSUE DETAILS:
- Key: {issue_key}
- Summary: {summary}
- Description: {description}
- Acceptance Criteria: {acceptance_criteria}

TEST PLAN TEMPLATE STRUCTURE:
{template_content}

INSTRUCTIONS:
1. Generate a comprehensive test plan based on the template structure
2. Adapt generic template sections to this specific Jira issue
3. Create specific test scenarios that cover the acceptance criteria
4. Include positive, negative, and edge cases
5. Format the output in Markdown with clear headers

Generate the complete test plan now:
```

**Grok Integration:**
- Use Groq Python SDK or direct HTTP requests to `https://api.groq.com/openai/v1/chat/completions`
- Headers: `Authorization: Bearer {api_key}`
- Model parameter from user settings
- Handle streaming response for real-time generation display

**Ollama Integration:**
- Endpoint: `{ollama_url}/api/generate`
- Model parameter from user settings
- Stream option enabled for progress display
- Handle local model availability errors

***

### **Frontend UI Components Structure**

```
/src
  /components
    /settings
      JiraConfigForm.tsx
      LLMProviderSelector.tsx
      GrokSettings.tsx
      OllamaSettings.tsx
      TemplateUploader.tsx
    /dashboard
      JiraIssueInput.tsx
      IssueDetailsCard.tsx
      GenerationControls.tsx
      TestPlanViewer.tsx
      ExportButtons.tsx
    /common
      Header.tsx
      Sidebar.tsx
      StatusIndicator.tsx
  /context
    ConfigContext.tsx      # Global settings state
    GenerationContext.tsx  # Generation workflow state
  /services
    api.ts                 # Axios instance for backend calls
    jiraService.ts
    llmService.ts
    templateService.ts
  /pages
    Dashboard.tsx
    Settings.tsx
    History.tsx
  /types
    index.ts               # TypeScript interfaces
```

***

### **Database Schema (SQLite)**

```sql
CREATE TABLE jira_config (
    id INTEGER PRIMARY KEY,
    domain TEXT NOT NULL,
    email TEXT NOT NULL,
    api_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE llm_config (
    id INTEGER PRIMARY KEY,
    provider TEXT NOT NULL, -- 'grok' or 'ollama'
    grok_api_key TEXT,
    grok_model TEXT,
    grok_temperature REAL DEFAULT 0.7,
    ollama_url TEXT DEFAULT 'http://localhost:11434',
    ollama_model TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE template_config (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    file_content TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generation_history (
    id TEXT PRIMARY KEY,
    jira_issue_id TEXT,
    jira_summary TEXT,
    generated_content TEXT,
    provider_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

***

### **File System Structure**

```
/intelligent-test-plan-agent/
├── /backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment variables
│   ├── database.py          # SQLite connection
│   ├── models.py            # Pydantic models
│   ├── /services/
│   │   ├── jira_service.py
│   │   ├── llm_service.py   # Grok + Ollama abstraction
│   │   ├── template_service.py
│   │   └── export_service.py
│   ├── /templates/          # Default templates storage
│   ├── /generated/          # Output directory for exports
│   └── requirements.txt     # Python dependencies
├── /frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── /src/
│   └── /public/
├── /templates/              # User-provided templates folder
│   └── test-plan-template.pdf
├── .env                     # Environment variables
├── README.md                # Setup instructions
└── docker-compose.yml       # Optional containerization
```

***

### **Environment Variables (.env)**

```bash
# Backend
DATABASE_PATH=./app.db
GENERATED_DIR=./generated
TEMPLATES_DIR=./templates

# Frontend
REACT_APP_API_BASE_URL=http://localhost:8000
```

***

### **Setup & Run Instructions**

Include in your prompt for the AI to generate:
1. Requirements installation commands (`pip install -r requirements.txt`, `npm install`)
2. Database initialization script
3. Backend startup: `uvicorn main:app --reload --port 8000`
4. Frontend startup: `npm start` (runs on port 3000)
5. Ollama setup instructions for local LLM (install Ollama, pull models)

***

### **Key Implementation Notes for the AI**

1. **Error Handling:** Implement comprehensive error handling for:
   - Jira API authentication failures
   - LLM provider connection errors
   - Missing or invalid templates
   - Network connectivity issues

2. **Security:** 
   - Never log API keys
   - Use HTTPS in production
   - Encrypt sensitive data in database (optional improvement)

3. **User Experience:**
   - Add loading states for all async operations
   - Provide clear error messages
   - Auto-save configuration changes
   - Keyboard shortcuts (Ctrl+Enter to generate)

4. **LLM Abstraction:**
   - Create a unified interface so switching between Grok and Ollama requires minimal code changes
   - Both should return the same response format

***

### **Expected Deliverables**

When you provide this prompt to an AI coding assistant, it should generate:
1. Complete working FastAPI backend with all endpoints
2. React frontend with all UI components
3. SQLite database setup and models
4. Integration code for Jira, Grok, and Ollama
5. Template parsing and output generation
6. Export functionality (PDF/Word)
7. README with setup instructions

***

This structured prompt provides clear, actionable requirements that will result in a proper, modular web application rather than a single script.