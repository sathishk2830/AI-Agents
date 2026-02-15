"""FastAPI Main Application - TP Creator Intelligence Test Plan Agent"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import json
import uuid
from datetime import datetime
import time
import logging

from database import init_db, get_db
from models import *
from services.jira_service import JiraService
from services.llm_service import LLMService
from services.template_service import TemplateService
from services.export_service import ExportService

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
init_db()

app = FastAPI(
    title="TP Creator - Intelligence Test Plan Agent",
    description="Automated test plan generation using Jira + LLM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "🚀 TP Creator - Intelligence Test Plan Agent",
        "docs": "/docs",
        "api_version": "1.0.0"
    }

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "jira": "ready",
        "llm": "ready"
    }

# ============== JIRA ENDPOINTS ==============

@app.post("/api/config/jira")
def save_jira_config(config: JiraConfigUpdate):
    """Save Jira configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM jira_config")
        cursor.execute("""
            INSERT INTO jira_config (domain, email, api_token, connection_status)
            VALUES (?, ?, ?, 'untested')
        """, (config.domain, config.email, config.api_token))
        
        conn.commit()
        conn.close()
        
        return {"status": "saved", "message": "Jira configuration saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/jira")
def get_jira_config():
    """Get Jira configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, domain, email, connection_status, last_tested_at FROM jira_config LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "domain": row[1],
                "email": row[2],
                "connection_status": row[3],
                "last_tested_at": row[4]
            }
        return {"status": "not_configured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/test-jira")
def test_jira_connection():
    """Test Jira connection"""
    try:
        config = get_jira_config()
        if "status" in config and config["status"] == "not_configured":
            raise HTTPException(status_code=400, detail="Jira not configured")
        
        service = JiraService(config["domain"], config["email"], "")
        result = service.test_connection()
        
        # Update status in DB
        if result["status"] == "connected":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jira_config SET connection_status = 'connected', last_tested_at = CURRENT_TIMESTAMP
            """)
            conn.commit()
            conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jira/issue/{issue_id}")
def fetch_jira_issue(issue_id: str):
    """Fetch Jira issue details"""
    try:
        config = get_jira_config()
        if "status" in config:
            raise HTTPException(status_code=400, detail="Jira not configured")
        
        service = JiraService(config["domain"], config["email"], "hidden_token")
        issue = service.fetch_issue(issue_id)
        
        if not issue:
            raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")
        
        return issue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== LLM ENDPOINTS ==============

@app.post("/api/config/llm")
def save_llm_config(config: LLMConfigUpdate):
    """Save LLM configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM llm_config")
        cursor.execute("""
            INSERT INTO llm_config 
            (provider, grok_api_key, grok_model, grok_temperature, grok_max_tokens, 
             ollama_url, ollama_model, connection_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'untested')
        """, (
            config.provider,
            config.grok_api_key,
            config.grok_model,
            config.grok_temperature,
            config.grok_max_tokens,
            config.ollama_url,
            config.ollama_model
        ))
        
        conn.commit()
        conn.close()
        
        return {"status": "saved", "message": f"LLM configuration saved ({config.provider})"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/llm")
def get_llm_config():
    """Get LLM configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, provider, grok_model, ollama_url, ollama_model, connection_status
            FROM llm_config LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "provider": row[1],
                "grok_model": row[2],
                "ollama_url": row[3],
                "ollama_model": row[4],
                "connection_status": row[5]
            }
        return {"status": "not_configured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config/test-llm")
def test_llm_connection():
    """Test LLM provider connection"""
    try:
        config = get_llm_config()
        if "status" in config:
            raise HTTPException(status_code=400, detail="LLM not configured")
        
        service = LLMService(config["provider"], **config)
        result = service.test_connection()
        
        if result["status"] == "connected":
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE llm_config SET connection_status = 'connected', last_tested_at = CURRENT_TIMESTAMP
            """)
            conn.commit()
            conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== TEMPLATE ENDPOINTS ==============

@app.post("/api/config/template")
def save_template_config(config: TemplateConfigUpdate):
    """Save template configuration"""
    try:
        validation = TemplateService.validate_template(config.file_path)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM template_config")
        
        file_ext = config.file_path.split('.')[-1].lower()
        cursor.execute("""
            INSERT INTO template_config (file_path, file_format, validation_status)
            VALUES (?, ?, ?)
        """, (config.file_path, file_ext, validation["status"]))
        
        conn.commit()
        conn.close()
        
        return {"status": "saved", "validation": validation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/template")
def get_template_config():
    """Get template configuration"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, file_path, file_format, validation_status FROM template_config LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "file_path": row[1],
                "file_format": row[2],
                "validation_status": row[3]
            }
        return {"status": "not_configured"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== TEST PLAN GENERATION ==============

@app.post("/api/generate/test-plan", response_model=GenerateTestPlanResponse)
def generate_test_plan(request: GenerateTestPlanRequest):
    """Generate test plan from Jira issue"""
    try:
        start_time = time.time()
        generation_id = str(uuid.uuid4())
        
        # Build prompt from Jira details and template
        template_config = get_template_config()
        template_content = ""
        if "file_path" in template_config:
            template_content = TemplateService.load_template(template_config["file_path"]) or ""
        
        prompt = f"""You are a QA expert creating a professional test plan.

JIRA ISSUE:
- Key: {request.jira_details.key}
- Summary: {request.jira_details.summary}
- Description: {request.jira_details.description}
- Acceptance Criteria: {request.jira_details.acceptanceCriteria}
- Priority: {request.jira_details.priority}

TEMPLATE STRUCTURE:
{template_content[:1000] if template_content else "[Default template: Create test plan with Overview, Scope, Test Scenarios, Exit Criteria]"}

Generate a comprehensive, professional test plan in Markdown format that:
1. Covers positive, negative, and edge case scenarios
2. Includes specific test steps and expected results
3. Addresses all acceptance criteria
4. Uses professional QA terminology
5. Is ready for immediate use by QA engineers"""
        
        # Generate using LLM
        llm_config = get_llm_config()
        if "status" in llm_config:
            raise HTTPException(status_code=400, detail="LLM not configured")
        
        service = LLMService(llm_config["provider"], **llm_config)
        content = service.generate_test_plan(prompt)
        
        if not content:
            raise HTTPException(status_code=500, detail="LLM generation failed")
        
        generation_time = time.time() - start_time
        
        # Save to history
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO generation_history 
            (id, jira_issue_id, jira_summary, generated_content, provider_used, generation_time_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            generation_id,
            request.jira_details.key,
            request.jira_details.summary,
            content,
            request.provider,
            round(generation_time, 2)
        ))
        conn.commit()
        conn.close()
        
        return {
            "id": generation_id,
            "jira_issue_id": request.jira_details.key,
            "jira_summary": request.jira_details.summary,
            "content": content,
            "format": "markdown",
            "provider_used": request.provider,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_time_seconds": round(generation_time, 2),
                "template_used": template_config.get("file_path", "default"),
                "token_usage": 0
            },
            "exports": {
                "pdf_url": f"/api/export/{generation_id}/pdf",
                "word_url": f"/api/export/{generation_id}/docx",
                "markdown_url": f"/api/export/{generation_id}/md"
            }
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== EXPORT ENDPOINTS ==============

@app.get("/api/export/{generation_id}/pdf")
def export_pdf(generation_id: str):
    """Export test plan as PDF"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT generated_content FROM generation_history WHERE id = ?", (generation_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        pdf_bytes = ExportService.markdown_to_pdf(row[0])
        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        return FileResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            filename="test_plan.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/{generation_id}/docx")
def export_docx(generation_id: str):
    """Export test plan as Word (.docx)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT generated_content FROM generation_history WHERE id = ?", (generation_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        docx_bytes = ExportService.markdown_to_docx(row[0])
        if not docx_bytes:
            raise HTTPException(status_code=500, detail="DOCX generation failed")
        
        from io import BytesIO
        return FileResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="test_plan.docx"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/{generation_id}/md")
def export_markdown(generation_id: str):
    """Export test plan as Markdown"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT generated_content FROM generation_history WHERE id = ?", (generation_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        from io import BytesIO
        return FileResponse(
            BytesIO(row[0].encode()),
            media_type="text/markdown",
            filename="test_plan.md"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
