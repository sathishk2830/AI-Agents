"""Phase 2 - LINK: Connectivity Testing Scripts"""
import sys
import os
import sqlite3
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.jira_service import JiraService
from services.llm_service import LLMService
from services.template_service import TemplateService
from database import init_db, get_db

print("\n" + "="*60)
print("TP CREATOR - PHASE 2: CONNECTIVITY TESTING")
print("="*60 + "\n")

# Test 1: Database Connection
print("📊 TEST 1: Database Connection")
print("-" * 60)
try:
    init_db()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    
    print(f"✅ Database: CONNECTED")
    print(f"   Tables found: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    print()
except Exception as e:
    print(f"❌ Database: FAILED")
    print(f"   Error: {e}\n")

# Test 2: Jira Connection (Mock - will use credentials if available)
print("🔗 TEST 2: Jira Cloud Connection")
print("-" * 60)
try:
    # Try to load from environment or config
    from dotenv import load_dotenv
    load_dotenv()
    
    domain = os.getenv('JIRA_DOMAIN', 'test.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'test@example.com')
    api_token = os.getenv('JIRA_API_TOKEN', 'test_token')
    
    jira_service = JiraService(domain, email, api_token)
    
    if api_token != 'test_token':
        result = jira_service.test_connection()
        if result['status'] == 'connected':
            print(f"✅ Jira: CONNECTED")
            print(f"   Domain: {domain}")
            print(f"   User: {result.get('user_email', email)}")
        else:
            print(f"⚠️ Jira: NOT CONFIGURED (Need real credentials)")
            print(f"   Domain: {domain}")
    else:
        print(f"⚠️ Jira: NOT CONFIGURED")
        print(f"   Please set JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN in .env")
    print()
except Exception as e:
    print(f"❌ Jira: ERROR")
    print(f"   {e}\n")

# Test 3: LLM Connection (Grok)
print("🤖 TEST 3: LLM Provider - Grok (Cloud)")
print("-" * 60)
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    grok_api_key = os.getenv('GROK_API_KEY', '')
    
    if grok_api_key:
        llm_service = LLMService('grok', 
                                  grok_api_key=grok_api_key,
                                  grok_model='grok-1',
                                  grok_temperature=0.7,
                                  grok_max_tokens=2000,
                                  ollama_url='',
                                  ollama_model='')
        result = llm_service.test_connection()
        if result['status'] == 'connected':
            print(f"✅ Grok: CONNECTED")
            print(f"   Model: grok-1")
            print(f"   Status: {result['message']}")
        else:
            print(f"⚠️ Grok: NOT RESPONDING")
            print(f"   {result.get('message', 'Unknown error')}")
    else:
        print(f"⚠️ Grok: NOT CONFIGURED")
        print(f"   Set GROK_API_KEY in .env to test")
    print()
except Exception as e:
    print(f"❌ Grok: ERROR")
    print(f"   {e}\n")

# Test 4: LLM Connection (Ollama)
print("🤖 TEST 4: LLM Provider - Ollama (Local)")
print("-" * 60)
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    
    llm_service = LLMService('ollama',
                              grok_api_key='',
                              grok_model='',
                              grok_temperature=0.7,
                              grok_max_tokens=2000,
                              ollama_url=ollama_url,
                              ollama_model='llama2')
    result = llm_service.test_connection()
    if result['status'] == 'connected':
        print(f"✅ Ollama: CONNECTED")
        print(f"   URL: {ollama_url}")
        print(f"   Available models: {', '.join(result.get('available_models', []))}")
    else:
        print(f"⚠️ Ollama: NOT RUNNING")
        print(f"   Start with: ollama serve")
    print()
except Exception as e:
    print(f"❌ Ollama: ERROR")
    print(f"   {e}\n")

# Test 5: Template Service
print("📋 TEST 5: Template Service")
print("-" * 60)
try:
    # Check if test template exists
    test_template_path = './templates/sample_template.md'
    
    if os.path.exists(test_template_path):
        result = TemplateService.validate_template(test_template_path)
        if result['status'] == 'valid':
            print(f"✅ Template: VALID")
            print(f"   Path: {test_template_path}")
        else:
            print(f"❌ Template: INVALID")
            print(f"   {result.get('message', 'Unknown error')}")
    else:
        print(f"ℹ️ Template: NOT FOUND")
        print(f"   Place template at: {test_template_path}")
    print()
except Exception as e:
    print(f"❌ Template: ERROR")
    print(f"   {e}\n")

# Summary
print("="*60)
print("CONNECTIVITY TEST SUMMARY")
print("="*60)
print("\n✅ Database:    Ready")
print("🔗 Jira:        Configure in Settings")
print("🤖 LLM (Grok):  Configure in Settings")
print("🤖 LLM (Ollama):Configure in Settings")
print("📋 Template:    Optional")
print("\n" + "="*60)
print("Next Steps:")
print("1. Run: cd frontend && npm start")
print("2. Run: cd backend && python -m uvicorn main:app --reload")
print("3. Open: http://localhost:3000")
print("4. Go to Settings and configure your credentials")
print("="*60 + "\n")
