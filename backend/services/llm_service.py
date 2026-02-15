"""LLM Service - Abstracts Grok and Ollama providers"""
import requests
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class LLMService:
    """Unified interface for Grok and Ollama"""
    
    def __init__(self, provider: str, **config):
        self.provider = provider
        self.config = config
    
    def test_connection(self) -> Dict:
        """Test LLM provider connection"""
        if self.provider == "grok":
            return self._test_grok()
        elif self.provider == "ollama":
            return self._test_ollama()
        return {"status": "failed", "error": "Unknown provider"}
    
    def _test_grok(self) -> Dict:
        """Test Grok connection"""
        try:
            api_key = self.config.get("grok_api_key")
            if not api_key:
                return {"status": "failed", "error": "API key not provided"}
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config.get("grok_model", "grok-2"),
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "connected",
                    "provider": "grok",
                    "model": self.config.get("grok_model", "grok-2"),
                    "message": "✅ Grok connection successful"
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "message": "❌ Grok connection failed. Check API key."
                }
        except requests.exceptions.Timeout:
            return {"status": "failed", "error": "Request timeout", "message": "❌ Grok timeout"}
        except Exception as e:
            return {"status": "failed", "error": str(e), "message": f"❌ Error: {str(e)}"}
    
    def _test_ollama(self) -> Dict:
        """Test Ollama connection"""
        try:
            url = self.config.get("ollama_url", "http://localhost:11434")
            
            response = requests.get(
                f"{url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return {
                    "status": "connected",
                    "provider": "ollama",
                    "available_models": model_names,
                    "message": f"✅ Ollama connected ({len(model_names)} models available)"
                }
            else:
                return {"status": "failed", "error": "Ollama not responding"}
        except requests.exceptions.ConnectionError:
            return {
                "status": "failed",
                "error": "Connection refused",
                "message": "❌ Cannot connect to Ollama. Is it running?"
            }
        except Exception as e:
            return {"status": "failed", "error": str(e), "message": f"❌ Error: {str(e)}"}
    
    def generate_test_plan(self, prompt: str) -> Optional[str]:
        """Generate test plan using configured LLM provider"""
        if self.provider == "grok":
            return self._generate_grok(prompt)
        elif self.provider == "ollama":
            return self._generate_ollama(prompt)
        return None
    
    def _generate_grok(self, prompt: str) -> Optional[str]:
        """Generate using Grok"""
        try:
            api_key = self.config.get("grok_api_key")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.config.get("grok_model", "grok-2"),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.config.get("grok_temperature", 0.7),
                    "max_tokens": self.config.get("grok_max_tokens", 2000)
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Grok error: {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"Grok generation error: {e}")
            return None
    
    def _generate_ollama(self, prompt: str) -> Optional[str]:
        """Generate using Ollama"""
        try:
            url = self.config.get("ollama_url", "http://localhost:11434")
            model = self.config.get("ollama_model", "mistral")
            
            response = requests.post(
                f"{url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": self.config.get("grok_temperature", 0.7),
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return None
