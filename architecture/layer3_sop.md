# Layer 3: Tools & Services SOP

## Overview

Layer 3 contains the deterministic service scripts that handle external system integration. Each service is self-contained and handles a specific domain: Jira, LLM, Templates, or Export.

## Core Design Principles

1. **Single Responsibility**: Each service handles one integration
2. **Provider Abstraction**: LLMService abstracts Grok and Ollama
3. **Error Resilience**: Graceful handling of external API failures
4. **Logging**: All operations logged for debugging
5. **Type Safety**: Type hints and validation throughout

---

## 1. Jira Service

**File**: `backend/services/jira_service.py`

**Purpose**: Fetches issue details from Jira Cloud API

### Class: JiraService

```python
class JiraService:
    def __init__(self, domain: str, email: str, api_token: str)
    def test_connection(self) -> dict
    def fetch_issue(self, issue_key: str) -> dict
```

### Methods

#### `__init__(domain, email, api_token)`

**Purpose**: Initialize with Jira credentials

**Parameters**:
- `domain` (str): Jira domain, e.g., "company.atlassian.net"
- `email` (str): User email for authentication
- `api_token` (str): API token from Atlassian

**Notes**: 
- Credentials stored in instance, not logged
- Base64 encoding handled internally

---

#### `test_connection() -> dict`

**Purpose**: Validate credentials without making destructive queries

**Logic**:
1. Encode email:api_token as base64
2. Create Authorization header
3. Call GET `/rest/api/3/myself` endpoint
4. If 200: Extract user email, return success
5. If 401/403: Return authentication error
6. If network error: Return connection error

**Response**:
```python
{
    "status": "connected",
    "message": "Connection successful",
    "user_email": "user@company.com"
}
```

**Error Response**:
```python
{
    "status": "failed",
    "message": "Invalid credentials or network error"
}
```

**Timeout**: 10 seconds

---

#### `fetch_issue(issue_key: str) -> dict`

**Purpose**: Retrieve full issue details for test plan generation

**Parameters**:
- `issue_key` (str): Issue identifier, e.g., "PROJ-123"

**Logic**:
1. Construct URL: `/rest/api/3/issues/{issue_key}`
2. Add query params: `fields=summary,description,priority,issuetype`
3. Make authenticated GET request
4. Parse response JSON
5. Extract acceptance criteria from description (if present)
6. Return normalized object

**Response**:
```python
{
    "key": "PROJ-123",
    "summary": "User can login with email",
    "description": "As a user, I want to login...",
    "priority": "High",
    "issueType": "Story",
    "acceptanceCriteria": "Given valid email\nWhen clicking login\nThen authenticate"
}
```

**Error Handling**:
- 404: Issue not found → Raise HTTPException
- 401: Credentials invalid → Raise HTTPException
- Network timeout → Retry once, then raise
- Malformed response → Log and return partial data

**Timeout**: 15 seconds per request

### Internal Methods

#### `_encode_credentials() -> str`

Encodes email:api_token as base64 for Basic Auth header

#### `_extract_acceptance_criteria(description: str) -> str`

Handles both plain text and Jira rich-text format acceptance criteria

---

## 2. LLM Service

**File**: `backend/services/llm_service.py`

**Purpose**: Unified abstraction for multiple LLM providers (Grok, Ollama)

### Class: LLMService

```python
class LLMService:
    def __init__(self, provider: str, **kwargs)
    def test_connection(self) -> dict
    def generate_test_plan(self, prompt: str) -> str
```

### Methods

#### `__init__(provider, **kwargs)`

**Parameters**:
- `provider` (str): "grok" or "ollama"
- kwargs: Provider-specific settings
  - For Grok: `grok_api_key`, `grok_model`, `grok_temperature`, `grok_max_tokens`
  - For Ollama: `ollama_url`, `ollama_model`

**Notes**: 
- Stores provider type internally
- Validates provider at initialization
- Caches configuration for later use

---

#### `test_connection() -> dict`

**Purpose**: Test provider connectivity without generating content

**Logic**:
1. Check provider type
2. Route to `_test_grok()` or `_test_ollama()`
3. Return connection status

**Response**:
```python
{
    "status": "connected",
    "message": "Connected to Grok",
    "available_models": ["grok-1"]
}
```

---

#### `generate_test_plan(prompt: str) -> str`

**Purpose**: Generate test plan using configured provider

**Parameters**:
- `prompt` (str): Full prompt including issue details and template

**Logic**:
1. Check provider type
2. Route to `_generate_grok()` or `_generate_ollama()`
3. Return generated markdown content

**Response**: Markdown string (2000+ characters typically)

**Error Handling**:
- API unavailable → Return empty string with logging
- Timeout → Retry once, then return partial content
- Invalid response → Return default template text

---

### Internal Methods

#### `_test_grok() -> dict`

**Purpose**: Verify Grok API connectivity

**Logic**:
1. Make lightweight API call with API key
2. If success: Extract available models
3. Return connection status

**Endpoint**: Uses Grok API health check

**Timeout**: 5 seconds

---

#### `_generate_grok(prompt: str) -> str`

**Purpose**: Generate test plan via Grok Cloud API

**Logic**:
1. Build request JSON with prompt
2. Set parameters: temperature, max_tokens
3. POST to Grok API endpoint
4. Parse response for generated text
5. Return content or empty string on error

**Request Body**:
```json
{
  "model": "grok-1",
  "messages": [
    {
      "role": "user",
      "content": "<prompt>"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Endpoint**: `https://api.groq.com/openai/v1/chat/completions`

**Auth**: Bearer token via Authorization header

**Timeout**: 30 seconds

---

#### `_test_ollama() -> dict`

**Purpose**: Verify Ollama local server connectivity

**Logic**:
1. GET to Ollama `/api/tags` endpoint
2. Parse response for list of available models
3. Return connection status with model list

**Endpoint**: `/api/tags` (usually http://localhost:11434)

**Timeout**: 5 seconds

---

#### `_generate_ollama(prompt: str) -> str`

**Purpose**: Generate test plan via local Ollama

**Logic**:
1. POST prompt to Ollama `/api/generate` endpoint
2. Stream response (text appears in chunks)
3. Concatenate chunks into full response
4. Return complete generated text

**Request Body**:
```json
{
  "model": "llama2",
  "prompt": "<full_prompt>",
  "stream": true
}
```

**Response Stream**:
```json
{"response": "# Test Plan"}
{" response": " for..."}
...
{"response": "", "done": true}
```

**Timeout**: 60 seconds (local generation can be slower)

---

## 3. Template Service

**File**: `backend/services/template_service.py`

**Purpose**: Load and validate custom test plan templates

### Class: TemplateService

```python
class TemplateService:
    @staticmethod
    def validate_template(file_path: str) -> dict
    @staticmethod
    def load_template(file_path: str) -> str
```

### Methods

#### `validate_template(file_path: str) -> dict`

**Purpose**: Verify template file exists and has valid format

**Parameters**:
- `file_path` (str): Path to template file

**Logic**:
1. Check file exists → Return error if not
2. Extract file extension
3. Route to format-specific validator:
   - `.pdf` → `_validate_pdf()`
   - `.md` → `_validate_text()`
   - `.txt` → `_validate_text()`
4. Return validation result

**Response**:
```python
{
    "status": "valid",
    "message": "PDF template is valid",
    "file_format": "pdf"
}
```

**Error Response**:
```python
{
    "status": "invalid",
    "message": "File not found at path",
    "file_format": None
}
```

---

#### `load_template(file_path: str) -> str`

**Purpose**: Extract content from template file for use in LLM prompt

**Parameters**:
- `file_path` (str): Path to template file

**Logic**:
1. Extract format from extension
2. Route to format-specific loader:
   - `.pdf` → `_load_pdf()`
   - `.md` / `.txt` → Read text file directly
3. Return text content

**Response**: Raw text content (up to 5000 chars for performance)

**Error Handling**: Return empty string on read error

---

### Internal Methods

#### `_validate_pdf(file_path: str) -> dict`

**Purpose**: Verify PDF file is readable

**Logic**:
1. Try to open PDF with PyPDF2
2. Check page count > 0
3. Return valid/invalid

**Uses**: PyPDF2 library for PDF validation

---

#### `_load_pdf(file_path: str) -> str`

**Purpose**: Extract text content from PDF

**Logic**:
1. Open PDF with PyPDF2
2. Extract text from all pages
3. Limit to first 5000 characters
4. Return extracted text

**Fallback**: If PyPDF2 unavailable, return empty string

---

#### `_validate_text(file_path: str) -> dict`

**Purpose**: Verify text file is readable

**Logic**:
1. Check file size < 1MB
2. Try to read first line
3. Return valid if readable

---

## 4. Export Service

**File**: `backend/services/export_service.py`

**Purpose**: Convert markdown test plans to professional document formats

### Class: ExportService

```python
class ExportService:
    @staticmethod
    def markdown_to_pdf(markdown: str) -> bytes
    @staticmethod
    def markdown_to_docx(markdown: str) -> bytes
```

### Methods

#### `markdown_to_pdf(markdown: str) -> bytes`

**Purpose**: Generate PDF from Markdown content

**Parameters**:
- `markdown` (str): Markdown-formatted test plan

**Logic**:
1. Parse markdown content:
   - `# Text` → H1 heading
   - `## Text` → H2 heading
   - `- Text` → Bullet point
   - Plain text → Paragraph
2. Build PDF using reportlab:
   - Set page size (Letter, 8.5x11)
   - Add margin (0.5 inches)
   - Format headings with larger font
   - Format bullets with indentation
3. Return PDF as bytes

**Response**: BytesIO buffer with PDF data

**Styling**:
- Title (H1): 18pt, bold, dark blue
- Heading (H2): 14pt, bold, medium blue
- Bullet: 11pt, indented
- Text: 11pt, justified

**Limitations**: 
- Only handles basic markdown
- Images not supported
- Tables converted to text

---

#### `markdown_to_docx(markdown: str) -> bytes`

**Purpose**: Generate Word (.docx) document from Markdown

**Parameters**:
- `markdown` (str): Markdown-formatted test plan

**Logic**:
1. Create Document object using python-docx
2. Parse markdown and add paragraphs:
   - H1 → Heading 1 style
   - H2 → Heading 2 style
   - H3 → Heading 3 style
   - `-` → List item
   - Plain text → Normal paragraph
3. Save to BytesIO buffer
4. Return bytes

**Response**: BytesIO buffer with DOCX data (OOXML format)

**Styling**:
- Uses built-in Word styles for compatibility
- Maintains document structure
- Preserves formatting on open in MS Word

**Advantages over PDF**:
- User can easily edit
- Preserves formatting on further edits
- Compatible with all Office versions

---

## Service Dependencies

```
JiraService
├─ Depends on: Jira Cloud API
├─ Input: Issue key
└─ Output: Issue object

LLMService
├─ Depends on: Grok API OR Ollama Server
├─ Input: Prompt text
└─ Output: Generated markdown

TemplateService
├─ Depends on: Local file system
├─ Input: File path
└─ Output: Template text

ExportService
├─ Depends on: reportlab, python-docx
├─ Input: Markdown text
└─ Output: PDF/DOCX bytes
```

## Error Handling Patterns

### Try-Except with Logging

```python
try:
    result = external_api_call()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    # Return fallback or raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Return fallback or raise
```

### Timeout Handling

```python
try:
    response = requests.get(url, timeout=10)
except requests.Timeout:
    # Retry or return error
```

### Graceful Degradation

- Jira unavailable → Can't fetch issues
- LLM unavailable → Can't generate (offer template instead)
- Template missing → Use default prompt
- Export error → Return partial data

---

## Configuration & Secrets

### Environment Variables Used

```python
JIRA_DOMAIN = os.getenv('JIRA_DOMAIN')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_MODEL = os.getenv('GROK_MODEL', 'grok-1')

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')
```

### Security Best Practices

1. **Never log API keys or tokens**
2. **Don't expose credentials to frontend**
3. **Use environment variables, not hardcoded values**
4. **Validate all external input**
5. **Use HTTPS for all external API calls**

---

## Testing Services

### Manual Testing

```python
# Test Jira
from services.jira_service import JiraService
jira = JiraService('domain', 'email', 'token')
print(jira.test_connection())
print(jira.fetch_issue('PROJ-123'))

# Test LLM
from services.llm_service import LLMService
llm = LLMService('grok', grok_api_key='...', ...)
print(llm.test_connection())
print(llm.generate_test_plan('...'))

# Test Template
from services.template_service import TemplateService
print(TemplateService.validate_template('./template.pdf'))
print(TemplateService.load_template('./template.pdf'))

# Test Export
from services.export_service import ExportService
pdf = ExportService.markdown_to_pdf('# Test Plan\n...')
docx = ExportService.markdown_to_docx('# Test Plan\n...')
```

### Automated Testing

```bash
python test_connectivity.py
```

---

## Performance Considerations

### Caching

- **Jira Issues**: Not cached (always fresh)
- **LLM Models**: Loaded once at service initialization
- **Templates**: Loaded on demand
- **Exports**: Generated on demand

### Optimization Opportunities

1. **Async Jira Calls**: Use aiohttp for concurrent requests
2. **LLM Caching**: Cache generation results for identical prompts
3. **PDF Streaming**: Stream large PDFs instead of buffering
4. **Template Preloading**: Cache template content in memory

---

## Future Enhancements

1. **Azure DevOps**: Add AzureDevOpsService
2. **More LLMs**: Add support for Claude, GPT-4, etc.
3. **Webhook Support**: Call services via webhooks
4. **Batch Operations**: Generate multiple test plans at once
5. **Advanced Templates**: Support for template variables/macros

---

## Related Documentation

- [Architecture README](README.md) - Overall architecture
- [Layer 2 SOP](layer2_sop.md) - Navigation layer details
- [API Guide](../README.md#api-endpoints) - Complete endpoint reference
