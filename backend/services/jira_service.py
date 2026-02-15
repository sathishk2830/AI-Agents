"""Jira API Integration Service"""
import requests
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self, domain: str, email: str, api_token: str):
        self.domain = domain
        self.email = email
        self.api_token = api_token
        self.base_url = f"https://{domain}/rest/api/3"
        self.headers = {
            "Authorization": f"Basic {self._encode_credentials()}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _encode_credentials(self) -> str:
        """Encode email:token as base64"""
        import base64
        credentials = f"{self.email}:{self.api_token}"
        return base64.b64encode(credentials.encode()).decode()
    
    def test_connection(self) -> Dict:
        """Test Jira connection and return status"""
        try:
            response = requests.get(
                f"{self.base_url}/myself",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "status": "connected",
                    "user": user_data.get("displayName", "Unknown"),
                    "message": "✅ Jira connection successful"
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "message": "❌ Jira connection failed"
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "failed",
                "error": "Connection refused",
                "message": "❌ Cannot reach Jira domain. Check URL."
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": f"❌ Error: {str(e)}"
            }
    
    def fetch_issue(self, issue_key: str) -> Optional[Dict]:
        """Fetch Jira issue details by key"""
        try:
            response = requests.get(
                f"{self.base_url}/issues/{issue_key}",
                headers=self.headers,
                params={"fields": "key,summary,description,priority,issuetype"}
            )
            
            if response.status_code == 200:
                issue_data = response.json()
                fields = issue_data.get("fields", {})
                
                return {
                    "key": issue_data["key"],
                    "summary": fields.get("summary", ""),
                    "description": fields.get("description", ""),
                    "priority": fields.get("priority", {}).get("name", "Medium"),
                    "issueType": fields.get("issuetype", {}).get("name", "Task"),
                    "acceptanceCriteria": self._extract_acceptance_criteria(fields),
                }
            else:
                logger.error(f"Failed to fetch issue {issue_key}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching Jira issue: {e}")
            return None
    
    def _extract_acceptance_criteria(self, fields: Dict) -> str:
        """Extract acceptance criteria from description or custom field"""
        description = fields.get("description", "")
        if isinstance(description, dict) and "content" in description:
            # Jira rich text format
            return "\n".join([
                block.get("text", "")
                for block in description.get("content", [])
            ])
        return description or "Not specified"
