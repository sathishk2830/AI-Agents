# Layer 2: Navigation & Routing SOP

## Overview

Layer 2 (Navigation) handles all HTTP routing, request validation, response formatting, and error handling. It serves as the bridge between the frontend (HTTP clients) and Layer 3 (service tools).

## Core Principles

1. **Single Responsibility**: Each endpoint handles one business operation
2. **Input Validation**: All requests validated against Pydantic models before processing
3. **Error Handling**: All errors caught, logged, and returned as JSON
4. **CORS Enabled**: Frontend can call from localhost:3000
5. **Stateless**: No session state, all data in requests/database

## HTTP Endpoints

### 1. Health Check

**Endpoint**: `GET /api/health`

**Purpose**: Server status verification

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "jira": "ready",
  "llm": "ready"
}
```

**Error Handling**: Always returns 200 with status object

---

### 2. Jira Configuration

#### Save Configuration
**Endpoint**: `POST /api/config/jira`

**Request Body**:
```json
{
  "domain": "company.atlassian.net",
  "email": "user@company.com",
  "api_token": "••••••••••••••"
}
```

**Response**: 
```json
{
  "status": "saved",
  "message": "Jira configuration saved"
}
```

**Validation**:
- domain: required, must contain "atlassian.net"
- email: required, valid email format
- api_token: required, non-empty

**Error Cases**:
- 400: Invalid input format
- 500: Database error

---

#### Get Configuration
**Endpoint**: `GET /api/config/jira`

**Response**:
```json
{
  "id": 1,
  "domain": "company.atlassian.net",
  "email": "user@company.com",
  "connection_status": "connected",
  "last_tested_at": "2026-02-15T10:30:00"
}
```

**Or** (if not configured):
```json
{
  "status": "not_configured"
}
```

---

#### Test Connection
**Endpoint**: `POST /api/config/test-jira`

**Purpose**: Validate Jira credentials without saving

**Internal Logic**:
1. Get current config from database
2. Call `jira_service.test_connection()`
3. If success, update database connection_status
4. Return result

**Response**:
```json
{
  "status": "connected",
  "message": "Connection successful",
  "user_email": "user@company.com"
}
```

**Error Response**:
```json
{
  "status": "failed",
  "message": "Invalid domain or token"
}
```

---

#### Fetch Jira Issue
**Endpoint**: `POST /api/jira/issue/{issue_id}`

**Purpose**: Retrieve issue details for test plan generation

**Parameters**:
- issue_id (path): Issue key, e.g., "PROJ-123"

**Response**:
```json
{
  "key": "PROJ-123",
  "summary": "User can login with email",
  "description": "As a user, I want to login using email...",
  "priority": "High",
  "issueType": "Story",
  "acceptanceCriteria": "Given valid email\nWhen clicking login\nThen should authenticate"
}
```

**Error Cases**:
- 400: Jira not configured
- 404: Issue not found
- 500: Jira API error

---

### 3. LLM Configuration

#### Save Configuration
**Endpoint**: `POST /api/config/llm`

**Request Body**:
```json
{
  "provider": "grok",
  "grok_api_key": "xai-••••••••",
  "grok_model": "grok-1",
  "grok_temperature": 0.7,
  "grok_max_tokens": 2000,
  "ollama_url": null,
  "ollama_model": null
}
```

**Or for Ollama**:
```json
{
  "provider": "ollama",
  "grok_api_key": null,
  "grok_model": null,
  "grok_temperature": 0.7,
  "grok_max_tokens": 2000,
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama2"
}
```

**Validation**:
- provider: "grok" or "ollama"
- If grok: grok_api_key required
- If ollama: ollama_url and ollama_model required

---

#### Get Configuration
**Endpoint**: `GET /api/config/llm`

**Response**:
```json
{
  "id": 1,
  "provider": "grok",
  "grok_model": "grok-1",
  "ollama_url": null,
  "ollama_model": null,
  "connection_status": "connected"
}
```

---

#### Test Connection
**Endpoint**: `POST /api/config/test-llm`

**Response**:
```json
{
  "status": "connected",
  "message": "Successfully connected to Grok",
  "available_models": ["grok-1"]
}
```

**Or for Ollama**:
```json
{
  "status": "connected",
  "message": "Ollama server responding",
  "available_models": ["llama2", "mistral"]
}
```

---

### 4. Template Configuration

#### Save Configuration
**Endpoint**: `POST /api/config/template`

**Request Body**:
```json
{
  "file_path": "C:\\templates\\test-plan.pdf"
}
```

**Response**:
```json
{
  "status": "saved",
  "validation": {
    "status": "valid",
    "message": "Template is valid PDF",
    "file_format": "pdf"
  }
}
```

---

#### Get Configuration
**Endpoint**: `GET /api/config/template`

**Response**:
```json
{
  "id": 1,
  "file_path": "C:\\templates\\test-plan.pdf",
  "file_format": "pdf",
  "validation_status": "valid"
}
```

---

### 5. Test Plan Generation

**Endpoint**: `POST /api/generate/test-plan`

**Request Body**:
```json
{
  "jira_details": {
    "key": "PROJ-123",
    "summary": "User can login",
    "description": "...",
    "priority": "High",
    "issueType": "Story",
    "acceptanceCriteria": "..."
  },
  "provider": "grok"
}
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "jira_issue_id": "PROJ-123",
  "jira_summary": "User can login",
  "content": "# Test Plan for PROJ-123\n\n...",
  "format": "markdown",
  "provider_used": "grok",
  "metadata": {
    "generated_at": "2026-02-15T10:35:22",
    "generation_time_seconds": 3.45,
    "template_used": "default",
    "token_usage": 1250
  },
  "exports": {
    "pdf_url": "/api/export/550e8400-e29b-41d4-a716-446655440000/pdf",
    "word_url": "/api/export/550e8400-e29b-41d4-a716-446655440000/docx",
    "markdown_url": "/api/export/550e8400-e29b-41d4-a716-446655440000/md"
  }
}
```

**Internal Logic**:
1. Validate jira_details object
2. Load template (if configured)
3. Build LLM prompt from issue details + template
4. Call `llm_service.generate_test_plan(prompt)`
5. Save to generation_history table
6. Return with export URLs

**Error Cases**:
- 400: LLM not configured
- 500: Generation failed

---

### 6. Export Endpoints

#### Export as PDF
**Endpoint**: `GET /api/export/{generation_id}/pdf`

**Purpose**: Download generated test plan as PDF file

**Response**: Binary PDF file with `application/pdf` MIME type

**Error Cases**:
- 404: Generation not found
- 500: PDF generation failed

---

#### Export as Word
**Endpoint**: `GET /api/export/{generation_id}/docx`

**Purpose**: Download generated test plan as Word document

**Response**: Binary DOCX file with `application/vnd.openxmlformats-officedocument.wordprocessingml.document` MIME type

---

#### Export as Markdown
**Endpoint**: `GET /api/export/{generation_id}/md`

**Purpose**: Download generated test plan as Markdown

**Response**: Text file with `text/markdown` MIME type

---

## Error Handling Strategy

### Standard Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes
- **200**: Request successful
- **400**: Client error (invalid input)
- **404**: Resource not found
- **500**: Server error (internal error)

### Logging
All errors logged with:
- Timestamp
- Endpoint
- User input (sanitized)
- Error message
- Stack trace (for debugging)

---

## Request/Response Flow

### For Test Plan Generation (Most Complex)

```
1. Frontend POST /api/generate/test-plan
   │
2. FastAPI validates request body
   ├─ Check: jira_details.key exists? ✓
   ├─ Check: provider is "grok" or "ollama"? ✓
   │
3. Retrieve LLM config from database
   ├─ If not configured → Return 400
   │
4. Call Layer 3: llm_service.generate_test_plan(prompt)
   ├─ If Grok selected → Call Grok API
   ├─ If Ollama selected → Call Ollama server
   ├─ Timeout after 30 seconds
   │
5. Save result to database: generation_history
   ├─ id (UUID)
   ├─ content (Markdown)
   ├─ provider_used
   └─ generation_time_seconds
   │
6. Format response with export URLs
   │
7. Return 200 JSON response
   │
8. Frontend displays content + download buttons
```

---

## Database Transactions

### Save Config Operations
All config saves are atomic:
```python
cursor.execute("DELETE FROM jira_config")
cursor.execute("INSERT INTO jira_config...")
conn.commit()  # All or nothing
```

### Generation Operations
Wrapped in try-except:
```python
try:
    cursor.execute("INSERT INTO generation_history...")
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

---

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Note**: Frontend-only origins allowed. Never allow `*` in production.

---

## Middleware Stack

1. **CORS Middleware**: Handle browser cross-origin requests
2. **Request Logger**: Log all incoming requests (optional)
3. **Error Handler**: Catch unhandled exceptions
4. **Response Formatter**: Consistent JSON format

---

## Configuration Patterns

### Environment Variables
```python
# Loaded from .env file
JIRA_DOMAIN = os.getenv('JIRA_DOMAIN')
GROK_API_KEY = os.getenv('GROK_API_KEY')
SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))
```

### Pydantic Models
All inputs validated against Pydantic models before processing:
- Type checking (str, int, float)
- Required field validation
- Custom validators (email format, etc.)

---

## Performance Optimizations

1. **Connection Pooling**: Reuse database connections
2. **Caching**: Cache template content in-memory (optional)
3. **Async Support**: FastAPI handles multiple concurrent requests
4. **Response Compression**: Gzip enabled for large responses

---

## Testing Layer 2

### Test Connectivity
```bash
python test_connectivity.py
```

### Manual Testing
```bash
# Test Jira config
curl -X POST http://localhost:8000/api/config/jira \
  -H "Content-Type: application/json" \
  -d '{"domain":"...","email":"...","api_token":"..."}'

# Test generation
curl -X POST http://localhost:8000/api/generate/test-plan \
  -H "Content-Type: application/json" \
  -d '{"jira_details":{...},"provider":"grok"}'
```

### Using Swagger UI
Open: http://localhost:8000/docs
- Interactive API documentation
- Try endpoints with example data
- See request/response examples

---

## Related Documentation

- [Architecture README](README.md) - Overall architecture
- [Layer 3 SOP](layer3_sop.md) - Service layer details
- [API Guide](../README.md#api-endpoints) - Complete endpoint reference
