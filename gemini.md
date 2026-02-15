# gemini.md — Project Constitution

**Project:** Intelligent Test Plan Generator (TP_Creator_AIAgentWithJira)  
**Status:** Phase 1 (Blueprint) — COMPLETE  
**Created:** 2026-02-15

**Purpose:** Authoritative source for all data schemas, behavioral rules, and architectural invariants. All code changes must reflect updates to this file. `gemini.md` is law.

---

## PHASE 1 DISCOVERY ANSWERS (Complete)

**North Star:** Build a full-stack web application that automatically generates professional test plans by fetching Jira issue details, applying a template-based structure, and processing through configurable LLM providers (Grok Cloud or local Ollama).

**Integrations:** Jira Cloud API, Grok Cloud API (optional), Ollama Local (optional) — all user-configured in Settings

**Source of Truth:** Jira API (live issues), Template File (user-provided PDF/MD/TXT), SQLite (config + history)

**Delivery Payload:** In-app Markdown viewer + Export (PDF, .docx, .md) + SQLite audit trail

**Behavioral Rules:** See Section 2 below (7 categories, 40+ specific rules)

---

## 1) DATA SCHEMAS (DEFINITIVE)

### Jira Issue Input
```json
{
  "jira_issue_id": "string (e.g., 'VW-1')",
  "jira_domain": "string (HTTPS URL)",
  "jira_email": "string",
  "jira_api_token": "string"
}
```

### Jira API Response
```json
{
  "key": "string",
  "summary": "string",
  "description": "string",
  "acceptanceCriteria": "string",
  "priority": "Critical|High|Medium|Low",
  "issueType": "Story|Bug|Task|Feature",
  "created": "ISO-8601",
  "updated": "ISO-8601"
}
```

### LLM Configuration
```json
{
  "provider": "grok|ollama",
  "grok_api_key": "string (if grok)",
  "grok_model": "grok-2",
  "grok_temperature": 0.7,
  "grok_max_tokens": 2000,
  "ollama_url": "http://localhost:11434",
  "ollama_model": "string"
}
```

### Test Plan Generation Request
```json
{
  "jira_issue_id": "string",
  "jira_details": {...},
  "template_content": "string",
  "provider": "grok|ollama",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### Generated Test Plan (FINAL PAYLOAD)
```json
{
  "id": "UUIDv4",
  "jira_issue_id": "string",
  "jira_summary": "string",
  "content": "string (Markdown)",
  "format": "markdown",
  "provider_used": "grok|ollama",
  "metadata": {
    "generated_at": "ISO-8601",
    "generation_time_seconds": 5.2,
    "template_used": "string",
    "token_usage": 1200
  },
  "exports": {
    "pdf_url": "string",
    "word_url": "string",
    "markdown_url": "string"
  }
}
```

### SQLite Schema
```sql
CREATE TABLE jira_config (
  id INTEGER PRIMARY KEY,
  domain TEXT NOT NULL UNIQUE,
  email TEXT, api_token TEXT,
  connection_status TEXT DEFAULT 'untested',
  last_tested_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE llm_config (
  id INTEGER PRIMARY KEY,
  provider TEXT,
  grok_api_key TEXT,
  grok_model TEXT DEFAULT 'grok-2',
  grok_temperature REAL DEFAULT 0.7,
  grok_max_tokens INTEGER DEFAULT 2000,
  ollama_url TEXT DEFAULT 'http://localhost:11434',
  ollama_model TEXT,
  connection_status TEXT DEFAULT 'untested',
  last_tested_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE template_config (
  id INTEGER PRIMARY KEY,
  file_path TEXT NOT NULL UNIQUE,
  file_content TEXT,
  file_format TEXT,
  validation_status TEXT DEFAULT 'untested',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generation_history (
  id TEXT PRIMARY KEY,
  jira_issue_id TEXT,
  jira_summary TEXT,
  generated_content TEXT,
  provider_used TEXT,
  generation_time_seconds REAL,
  token_usage INTEGER,
  template_used TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2) BEHAVIORAL RULES (7 Categories)

### Security & Privacy
- Never log credentials, API keys, or passwords
- Never include PII in generated test plans
- Redact secrets in logs: `Token: ***...****`
- Validate output for accidental PII
- Enforce HTTPS for Jira API (production)

### Error Handling & Recovery
- Catch all API failures gracefully
- Implement retries: max 3 attempts, exponential backoff (1s, 2s, 4s)
- Display user-friendly error messages
- Validate all inputs before execution
- Never guess business logic

### LLM Generation
- Use fixed, versioned prompt template
- Ensure Grok and Ollama return same response format
- Allow user to set temperature (0.0-1.0; default 0.7)
- Set max_tokens to prevent runaway (default 2000)
- Log provider used in generation_history
- Warn if output was truncated

### User Experience
- Show progress indicators during long operations
- Auto-save configuration on change
- Display step-by-step progress (Validate → Fetch → Process → Format)
- Optional: stream LLM responses in real-time
- Provide "Regenerate" button to retry with same inputs

### Data & Persistence
- Use SQLite transactions (all-or-nothing)
- Store all generations in generation_history (audit trail)
- Clean up .tmp/ after successful generation
- Keep exports in ./generated/ during session
- Never commit .db files or generated outputs to git

### Integration Constraints
- Respect Jira rate limits (~100 req/min)
- Implement request queuing for Grok (max ~10 concurrent)
- Handle Ollama single-instance constraint
- Log rate limit errors and advise user
- Support PDF, Markdown, and text template formats

### Tone & Output Quality
- Generate professional, directly-usable test plans
- Include positive, negative, and edge case scenarios
- Cover acceptance criteria explicitly
- Use QA terminology (test scenario, step, expected result)
- Never generate unprofessional or incomplete output

---

## 3) OPERATIONAL CONVENTIONS

- Code in `tools/`, SOPs in `architecture/`, intermediates in `.tmp/`, outputs in `./generated/`
- Never commit secrets, `.db` files, or temp outputs to git
- If behavioral rules change, update this file first before code
- Production deployment is manual (Phase 5: Trigger)

---

## 4) MAINTENANCE LOG

**2026-02-15 (Phase 1 - Blueprint Complete)**
- All 5 discovery questions answered and documented
- Definitive JSON schemas for Jira, LLM config, test plan output, and SQLite
- 7 categories of behavioral rules with 40+ specific constraints
- Ready for Phase 2 (Link): Connectivity verification of Jira + LLM providers

**Change procedure:** Record schema or rule changes here with date, author, and rationale before coding.
