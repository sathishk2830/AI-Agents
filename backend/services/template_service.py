"""Template Parsing Service"""
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TemplateService:
    """Parse and validate test plan templates"""
    
    @staticmethod
    def validate_template(file_path: str) -> Dict:
        """Validate and test template file"""
        if not os.path.exists(file_path):
            return {
                "status": "failed",
                "error": "File not found",
                "message": f"❌ Template file '{file_path}' does not exist"
            }
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == ".pdf":
            return TemplateService._validate_pdf(file_path)
        elif file_ext == ".md" or file_ext == ".txt":
            return TemplateService._validate_text(file_path)
        else:
            return {
                "status": "failed",
                "error": "Unsupported format",
                "message": f"❌ Only PDF, Markdown (.md), and text (.txt) supported"
            }
    
    @staticmethod
    def _validate_pdf(file_path: str) -> Dict:
        """Validate PDF template"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
            return {
                "status": "valid",
                "format": "pdf",
                "pages": num_pages,
                "message": f"✅ PDF template valid ({num_pages} pages)"
            }
        except ImportError:
            logger.warning("PyPDF2 not installed, skipping PDF validation")
            return {
                "status": "valid",
                "format": "pdf",
                "message": "✅ PDF file exists (validation skipped)"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": f"❌ PDF validation error: {str(e)}"
            }
    
    @staticmethod
    def _validate_text(file_path: str) -> Dict:
        """Validate text or markdown template"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) < 10:
                return {
                    "status": "warning",
                    "format": "text",
                    "size": len(content),
                    "message": "⚠️ Template is very small (less than 10 characters)"
                }
            
            return {
                "status": "valid",
                "format": "text",
                "size": len(content),
                "message": f"✅ Template valid ({len(content)} characters)"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "message": f"❌ Error reading template: {str(e)}"
            }
    
    @staticmethod
    def load_template(file_path: str) -> Optional[str]:
        """Load template content"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".pdf":
                return TemplateService._load_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return None
    
    @staticmethod
    def _load_pdf(file_path: str) -> Optional[str]:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed, cannot extract PDF text")
            return "[PDF Template - Content extraction requires PyPDF2]"
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            return None
