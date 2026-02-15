from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Jira Config Models
class JiraConfigUpdate(BaseModel):
    domain: str
    email: str
    api_token: str

class JiraConfigResponse(BaseModel):
    id: int
    domain: str
    email: str
    connection_status: str
    last_tested_at: Optional[str] = None

# LLM Config Models
class LLMConfigUpdate(BaseModel):
    provider: str  # "grok" or "ollama"
    grok_api_key: Optional[str] = None
    grok_model: str = "grok-2"
    grok_temperature: float = 0.7
    grok_max_tokens: int = 2000
    ollama_url: str = "http://localhost:11434"
    ollama_model: Optional[str] = None

class LLMConfigResponse(BaseModel):
    id: int
    provider: str
    connection_status: str
    last_tested_at: Optional[str] = None

# Template Config Models
class TemplateConfigUpdate(BaseModel):
    file_path: str

class TemplateConfigResponse(BaseModel):
    id: int
    file_path: str
    file_format: str
    validation_status: str

# Jira Issue Models
class JiraIssue(BaseModel):
    key: str
    summary: str
    description: Optional[str] = None
    acceptanceCriteria: Optional[str] = None
    priority: Optional[str] = None
    issueType: Optional[str] = None

# Generation Request/Response Models
class GenerateTestPlanRequest(BaseModel):
    jira_issue_id: str
    jira_details: JiraIssue
    template_content: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 2000

class GenerateTestPlanResponse(BaseModel):
    id: str
    jira_issue_id: str
    jira_summary: str
    content: str
    format: str
    provider_used: str
    metadata: dict
    exports: dict

# Health Check
class HealthResponse(BaseModel):
    status: str
    database: str
    jira: str
    llm: str
