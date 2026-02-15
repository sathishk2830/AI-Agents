# TP Creator - Intelligence Test Plan Agent

🚀 **Automated Test Plan Generation using Jira + LLM**

An intelligent AI-powered test plan generator that fetches Jira issues, applies template structures, and generates comprehensive test plans using configurable LLMs (Grok or Ollama), with multi-format export (PDF, Word, Markdown).

## Features

✨ **Core Capabilities**
- 🔗 **Jira Integration**: Fetch issue details directly from Jira Cloud
- 🤖 **Dual LLM Support**: Generate test plans using Grok (Cloud) or Ollama (Local)
- 📋 **Template Support**: Use custom test plan templates (PDF, Markdown, Text)
- 📊 **Multi-Format Export**: Download as PDF, Word (.docx), or Markdown
- 💾 **Generation History**: Track all generated test plans with metadata
- ⚙️ **Easy Configuration**: Web-based settings for all integrations

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: React 18+ with TypeScript
- **LLM Providers**: Grok API & Ollama
- **Export**: reportlab (PDF), python-docx (Word)

### Project Structure
```
TP_Creator/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLite initialization
│   ├── models.py               # Pydantic data models
│   ├── requirements.txt         # Python dependencies
│   └── services/
│       ├── jira_service.py      # Jira API integration
│       ├── llm_service.py       # LLM provider abstraction
│       ├── template_service.py  # Template parsing
│       └── export_service.py    # PDF/Word export
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── api.ts               # API client
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx     # Generation interface
│   │   │   ├── Settings.tsx      # Configuration page
│   │   │   └── History.tsx       # Generations list
│   │   └── components/
│   │       └── Navigation.tsx
│   └── package.json
├── .env-example                 # Configuration template
├── docker-compose.yml          # Local development setup
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- (Optional) Ollama installed locally for local LLM generation

### 1. Clone and Setup Environment

```bash
cd TP_Creator
cp .env-example .env
# Edit .env with your actual credentials
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python -m uvicorn main:app --reload
```

Backend will be available at: `http://localhost:8000`
Swagger API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open at: `http://localhost:3000`

### 4. Configuration

1. **Dashboard** → **Settings** page
2. **Jira Configuration**
   - Enter your Jira Cloud domain (e.g., `your-domain.atlassian.net`)
   - Email and API Token
   - Test Connection
3. **LLM Configuration**
   - Choose provider: Grok or Ollama
   - Enter API keys or server URL
   - Test Connection
4. **Template Configuration** (Optional)
   - Upload custom test plan template (PDF/Markdown/Text)

### 5. Generate Test Plans

1. Go to **Dashboard**
2. Enter Jira issue key (e.g., `PROJ-123`)
3. Click **Fetch** to load issue details
4. Click **Generate Test Plan**
5. Download results (PDF, Word, or Markdown)

## API Endpoints

### Health
```
GET /api/health                 # Server status
```

### Jira Configuration
```
POST   /api/config/jira         # Save Jira config
GET    /api/config/jira         # Get Jira config
POST   /api/config/test-jira    # Test Jira connection
POST   /api/jira/issue/{id}    # Fetch Jira issue
```

### LLM Configuration
```
POST   /api/config/llm          # Save LLM config
GET    /api/config/llm          # Get LLM config
POST   /api/config/test-llm     # Test LLM connection
```

### Template Configuration
```
POST   /api/config/template     # Save template
GET    /api/config/template     # Get template
```

### Generation
```
POST   /api/generate/test-plan      # Generate test plan
GET    /api/export/{id}/pdf         # Export as PDF
GET    /api/export/{id}/docx        # Export as Word
GET    /api/export/{id}/md          # Export as Markdown
```

## Environment Variables

Create `.env` file with the following:

```env
# Jira
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_api_token

# Grok (if using Grok provider)
GROK_API_KEY=xai-your_api_key
GROK_MODEL=grok-1
GROK_TEMPERATURE=0.7
GROK_MAX_TOKENS=2000

# Ollama (if using Local LLM)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
```

## Configuration Guide

### Jira Cloud API Token
1. Login to Jira Cloud
2. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
3. Create API Token
4. Copy token to `.env` → `JIRA_API_TOKEN`

### Grok API Key
1. Visit: https://console.groq.com
2. Create API key
3. Copy to `.env` → `GROK_API_KEY`

### Ollama (Local)
```bash
# Install from: https://ollama.ai
ollama pull llama2
ollama serve  # Runs on http://localhost:11434
```

## Testing Connections

All integrations can be tested from Settings page:
- ✅ **Jira**: Validates domain, email, and API token
- ✅ **Grok**: Tests API connectivity and availability
- ✅ **Ollama**: Verifies server is running and models are available

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Clear Python cache
rm -rf __pycache__ .pytest_cache

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check CORS is enabled (should work by default)
- Check browser console for errors (F12)

### Jira connection fails
- Verify domain format: `company.atlassian.net` (not full URL)
- Ensure email matches Jira account email
- API token must be from https://id.atlassian.com/manage-profile/security/api-tokens

### LLM generation fails
- **Grok**: Verify API key starts with `xai-`
- **Ollama**: Ensure `ollama serve` is running on localhost:11434
- Check model is installed: `ollama list`

## Development

### Project Structure (BLAST Framework)

**Phase 0 - Initialization**: Project setup and discovery (✅ Complete)
**Phase 1 - Blueprint**: Schema definition and requirements (✅ Complete)
**Phase 2 - Link**: Connectivity layer and services (✅ Complete)
**Phase 3 - Architect**: SOP documentation (In progress)
**Phase 4 - Stylize**: Frontend UI/UX (✅ Complete)
**Phase 5 - Trigger**: Deployment and launch (✅ Complete)

### Key Files

- `backend/main.py` - FastAPI routes
- `backend/services/*.py` - Integration layers
- `frontend/src/pages/Dashboard.tsx` - Main UI
- `frontend/src/api.ts` - Frontend API client

## Future Enhancements

🔮 **Planned Features**
- [ ] Docker containerization for easy deployment
- [ ] Webhook support for Jira automation
- [ ] Template marketplace
- [ ] Test execution integration
- [ ] Batch test plan generation
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review API documentation at `http://localhost:8000/docs`
3. Check backend logs for detailed error messages

---

**Made with ❤️ for QA Engineers**

Built with FastAPI | React | SQLite | LLM Integration
