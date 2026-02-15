# TP Creator - Architecture & Standard Operating Procedures

## Overview

The TP Creator application follows the **BLAST 3-Layer Architecture**:

1. **Layer 1 - SOPs**: Standard Operating Procedures (this documentation)
2. **Layer 2 - Navigation**: FastAPI routing and decision logic
3. **Layer 3 - Tools**: Deterministic service scripts (Jira, LLM, Template, Export)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│           Dashboard | Settings | History Pages              │
│                                                               │
│  Browser on localhost:3000                                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Layer 2: Navigation (FastAPI)                   │
│                                                               │
│  /api/config/jira          /api/config/llm                  │
│  /api/config/test-jira     /api/config/test-llm             │
│  /api/jira/issue/{id}      /api/generate/test-plan          │
│  /api/export/{id}/pdf      /api/export/{id}/docx            │
│                                                               │
│  Request Validation | Response Formatting | Error Handling   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         Layer 3: Tools (Service Scripts)                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ JiraService  │  │ LLMService   │  │ TemplateServ│       │
│  │ - fetch_issue│  │ - test_grok  │  │ - validate  │       │
│  │ - test_conn  │  │ - test_ollama│  │ - load      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌──────────────────────────────┐                           │
│  │   ExportService              │                           │
│  │   - markdown_to_pdf          │                           │
│  │   - markdown_to_docx         │                           │
│  └──────────────────────────────┘                           │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│         External Systems & Databases                         │
│                                                               │
│  Jira Cloud API | Grok API | Ollama | SQLite DB            │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow for Test Plan Generation

```
User Input (Issue Key)
        │
        ▼
    Layer 2: /api/jira/issue/{id}
        │
        ▼
    Layer 3: jira_service.fetch_issue()
        │
        ▼── calls ──► Jira Cloud API ──► returns ──► JiraIssue object
        │
        ├─────────────────────────────────────────────┐
        │                                             │
        ▼                                             ▼
    Layer 2: /api/generate/test-plan          Layer 3: template_service.load_template()
        │                                             │
        ├─────────────────────────────────────────────┤
        │
        ▼
    Layer 3: llm_service.generate_test_plan(prompt)
        │
        ├── routes to ──► Grok API
        │   or routes to ──► Ollama Server
        │
        ▼── returns ──► Markdown content
        │
        ├─────────────────────────────────────────────┐
        │                                             │
        ▼                                             ▼
    Layer 3: export_service.markdown_to_pdf()  export_service.markdown_to_docx()
        │
        ▼
    Layer 2: Response with exports URLs
        │
        ▼
    Frontend: Download buttons
```

## Layer 1: Standard Operating Procedures

See dedicated SOP files:
- [Layer 2 SOP: Navigation & Routing](layer2_sop.md)
- [Layer 3 SOP: Tools & Services](layer3_sop.md)

## Security Considerations

### Authentication
- Jira API Token: Stored in environment variables, never exposed to frontend
- Grok API Key: Stored in environment variables, validated on each request
- Ollama: Local network only, no credentials required

### Data Protection
- Tokens/keys never transmitted to frontend
- All API responses redact sensitive data
- Database stores only non-sensitive metadata
- Generated test plans stored in database without personal data

### Error Handling
- All external API calls wrapped in try-except
- Graceful degradation if any service unavailable
- User-friendly error messages (no stack traces)
- Detailed logging for debugging (not exposed to frontend)

## Performance Considerations

### Caching
- Jira issues: Not cached (always fresh from API)
- LLM responses: Stored in database with generation_id
- Templates: Loaded on demand, not cached

### Rate Limiting
- Jira API: Respects cloud rate limits (most queries < 100ms)
- Grok API: Respects provider limits (generation ~2-5 seconds)
- Ollama: Local, no rate limits

### Concurrent Requests
- FastAPI handles concurrent requests with uvicorn workers
- SQLite allows concurrent reads, serialized writes
- Frontend can generate multiple test plans in parallel

## Database Schema

Four tables with referential relationships:

```
jira_config
├─ domain (PRIMARY KEY, unique)
├─ email
├─ api_token (encrypted)
└─ connection_status

llm_config
├─ provider (grok | ollama, PRIMARY KEY)
├─ grok_api_key / ollama_url
└─ connection_status

template_config
├─ file_path (PRIMARY KEY, unique)
├─ file_format (pdf | md | txt)
└─ validation_status

generation_history
├─ id (UUID, PRIMARY KEY)
├─ jira_issue_id (FOREIGN KEY)
├─ generated_content (Markdown)
└─ metadata (provider, time, etc)
```

## Deployment Modes

### Development
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

### Production (Docker)
```bash
docker-compose up -d
# Both services run in containers on standard ports
```

### Testing
```bash
# Run connectivity tests
python test_connectivity.py

# Run unit tests (if implemented)
pytest backend/tests/
npm test  # frontend tests
```

## Troubleshooting Flowchart

```
Issue: Can't generate test plan
├─ Check: Is backend running?
│  └─ Restart: python -m uvicorn main:app --reload
├─ Check: Frontend logs (F12)
│  └─ Look for: API URL, response errors
├─ Check: Jira configured?
│  └─ Go to Settings, test Jira connection
├─ Check: LLM configured?
│  └─ Go to Settings, test LLM connection
└─ Check: Backend logs (terminal output)
   └─ Look for: Stack traces, error messages
```

## Maintenance & Monitoring

### Regular Tasks
- Monitor Jira API usage (check Atlassian dashboard)
- Monitor Grok API usage (check console.groq.com)
- Backup SQLite database (tp_creator.db)
- Review generation history (Database analyzer)

### Logs
- Frontend: Browser console (F12)
- Backend: Terminal output + application logs
- Database: Query logs in SQLite browser

## Extending the System

### Adding New LLM Providers
1. Create new provider method in `llm_service.py`: `_generate_<provider>()`
2. Add to provider selection in UI (Settings.tsx)
3. Add config fields to `models.py`
4. Test with `test_connectivity.py`

### Adding New Export Formats
1. Create new export method in `export_service.py`: `markdown_to_<format>()`
2. Create new endpoint in `main.py`: `/api/export/{id}/<format>`
3. Add download button in Dashboard.tsx

### Adding Template Types
1. Update `template_service.py` to handle new format
2. Add format validator in `_validate_<format>()`
3. Document in QUICKSTART.md

## Further Documentation

- [README.md](../README.md) - Full project overview
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [Layer 2 SOP](layer2_sop.md) - Navigation layer details
- [Layer 3 SOP](layer3_sop.md) - Tools layer details
