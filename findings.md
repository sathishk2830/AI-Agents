# Findings — TP_Creator Intelligence Test Plan Agent

**Updated:** 2026-02-15

---

## RESEARCH RESULTS (Phase 1 Discovery)

### Integration Environment

**Jira Cloud API**
- Endpoint: `https://{domain}.atlassian.net/rest/api/3/issues/{issueKey}`
- Authentication: Email + API Token (OAuth not required for basic integration)
- Rate Limit: ~100 requests per minute
- Required Fields Fetched: key, summary, description, acceptanceCriteria, priority, issueType
- Status: User must provide credentials in Settings; no pre-configuration

**Grok (Groq Cloud API)**
- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Authentication: API Key (`gsk_...`)
- Available Models: grok-2, grok-2-vision, etc.
- Rate Limit: ~10 concurrent requests (shared account)
- Status: User must provide API key; optional provider

**Ollama (Local LLM)**
- Endpoint: `http://localhost:11434/api/generate`
- Models: User must pull locally (e.g., `ollama pull mistral`)
- Rate Limit: Single instance (1-2 concurrent requests depending on hardware)
- Status: User must install Ollama locally; optional provider

---

## ARCHITECTURAL INSIGHTS

### Data Flow
```
Jira API ──────┐
                ├──▶ Backend (aggregation) ──▶ LLM Provider ──▶ Markdown Formatter
Template File ─┤                                               ↓
SQLite DB ─────┘                                         Output (PDF/DOCX/MD)
                                                               ↓
                                                         Saved to SQLite
```

### Three-Layer Architecture (per BLAST)
- **Layer 1 (Architecture):** SOPs in `architecture/` directory
  - Jira integration procedures
  - LLM generation logic
  - Template parsing
  - Export services
- **Layer 2 (Navigation):** Backend orchestration (FastAPI routes)
  - Route requests to correct tools
  - Handle errors gracefully
- **Layer 3 (Tools):** Deterministic Python scripts in `tools/`
  - Atomic, testable functions
  - Environment-based config (.env)
  - Use .tmp/ for intermediates

---

## BEHAVIORAL CONSTRAINTS

### Security (Absolute)
- Never log credentials, tokens, API keys
- Never include PII in generated test plans
- Encrypt sensitive data in SQLite (future hardening)
- Enforce HTTPS for production Jira API calls

### Error Handling (Mandatory)
- Max 3 retries per API call (exponential backoff: 1s, 2s, 4s)
- Catch and display user-friendly error messages
- Validate all inputs before execution
- Never crash on single API failure

### LLM Generation (Deterministic)
- Fixed, versioned prompt template (stored in `gemini.md`)
- Both Grok and Ollama return same response format
- User-configurable temperature (0.0-1.0; default 0.7)
- Max tokens limit (default 2000)
- Log provider used in generation_history

### User Experience (Essential)
- Show progress indicators during operations
- Auto-save configuration on change
- Step-by-step status display
- Optional real-time streaming of LLM output
- "Regenerate" button for retry

### Data Persistence (Non-negotiable)
- SQLite transactions (all-or-nothing)
- Audit trail in generation_history
- Clean up .tmp/ after success
- Keep exports in ./generated/ during session
- Never commit .db files to git

### Integration Constraints (Operational)
- Respect Jira rate limits (~100 req/min)
- Queue requests for Grok (max ~10 concurrent)
- Handle Ollama single-instance constraint
- Log rate limit errors and advise user
- Support PDF, Markdown, text templates

### Output Quality (Professional)
- Generate directly-usable test plans
- Include positive, negative, edge case scenarios
- Cover acceptance criteria explicitly
- Use QA terminology
- Never generate incomplete output

---

## OPEN QUESTIONS / FUTURE ENHANCEMENTS

- Should we cache LLM responses to avoid re-generation?
- Should we support Google Sheets or Confluence export (Phase 2)?
- Should we add Slack webhook notifications?
- Should we implement user authentication for multi-user deployments?
- Should we add template versioning/history?

---

## TECHNICAL DECISIONS

1. **Database:** SQLite (local, lightweight) — can upgrade to PostgreSQL for production
2. **Backend:** FastAPI (Python, async-ready, auto-generated docs)
3. **Frontend:** React 18+ with TypeScript (modern, component-based)
4. **LLM Abstraction:** Single interface for both Grok and Ollama (provider-agnostic)
5. **Delivery:** Markdown primary format (universal, easy to convert)
6. **Version Control:** Git (initialized, .gitignore configured)

---

**Status:** Phase 1 discovery complete. Ready for Phase 2 (Link) connectivity verification.

