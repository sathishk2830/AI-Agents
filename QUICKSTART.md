# 🚀 TP Creator - Quick Start Guide

## Step 1: Configure Environment Variables

Before running the application, create a `.env` file in the root directory with your credentials:

```bash
cp .env-example .env
```

Edit `.env` and add:

### For Jira Integration:
```
JIRA_DOMAIN=your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_api_token_from_atlassian
```

Get your Jira API Token from: https://id.atlassian.com/manage-profile/security/api-tokens

### For Grok (Cloud LLM):
```
GROK_API_KEY=xai-your_api_key_here
```

Get your Grok API Key from: https://console.groq.com

### For Ollama (Local LLM):
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

## Step 2: Automatic Setup

### Windows:
```bash
setup.bat
```

### macOS/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

This will install all dependencies for frontend and backend.

## Step 3: Run the Application

### Terminal 1 - Start Backend:
```bash
cd backend
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

python -m uvicorn main:app --reload
```

✅ Backend runs on: **http://localhost:8000**

### Terminal 2 - Start Frontend:
```bash
cd frontend
npm start
```

✅ Frontend opens automatically at: **http://localhost:3000**

## Step 4: Test the Integration

1. **Open http://localhost:3000** in your browser
2. Go to **⚙️ Settings** page
3. Configure:
   - ✅ Jira Connection (test it!)
   - ✅ LLM Provider (test it!)
   - ✅ Template (optional)
4. Go to **📊 Dashboard**
5. Enter a Jira issue key (e.g., `PROJ-123`)
6. Click **Generate Test Plan**
7. Download PDF/Word/Markdown

## Troubleshooting

### Backend won't start
```bash
# Clear cache and reinstall
rm -rf backend/venv
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Frontend won't compile
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Can't connect to Jira
- Verify domain is `company.atlassian.net` (NOT full URL)
- Ensure API token is from https://id.atlassian.com/manage-profile/security/api-tokens
- Check email matches your Jira account

### Grok API key not working
- Get from: https://console.groq.com
- Should start with `xai-`

### Ollama not responding
```bash
# Install Ollama from https://ollama.ai
ollama pull llama2
ollama serve  # Leave running on localhost:11434
```

## Docker (Alternative)

```bash
docker-compose up
```

Then access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Documentation

Once backend is running, open: **http://localhost:8000/docs**

Interactive Swagger UI with all endpoints and test capabilities.

---

**Need help?** Check the full README.md for detailed documentation.
