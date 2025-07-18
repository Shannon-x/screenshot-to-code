from typing import Optional, Dict, Any
from pydantic import BaseModel, validator, HttpUrl, conint, constr
from urllib.parse import urlparse
import base64
import re
from typing import Literal

# Constants for validation
MAX_PROMPT_LENGTH = 10000
MAX_URL_LENGTH = 2048
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_STACKS = ["html_tailwind", "html_css", "react_tailwind", "vue_tailwind", "bootstrap", "ionic_tailwind", "svg"]
ALLOWED_INPUT_MODES = ["image", "video", "text", "url"]

class SanitizedUrl(HttpUrl):
    """Custom URL type that validates and sanitizes URLs"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not v:
            raise ValueError('URL cannot be empty')
        
        if len(v) > MAX_URL_LENGTH:
            raise ValueError(f'URL too long. Maximum {MAX_URL_LENGTH} characters allowed')
        
        # Parse and validate URL
        parsed = urlparse(v)
        
        # Only allow http and https protocols
        if parsed.scheme not in ['http', 'https']:
            raise ValueError('Only HTTP and HTTPS URLs are allowed')
        
        # Check for potentially malicious patterns
        dangerous_patterns = [
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'file://',
            r'about:',
            r'chrome:',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('URL contains potentially malicious content')
        
        return v

class ValidatedPrompt(BaseModel):
    """Validated user prompt with XSS protection"""
    prompt: constr(min_length=1, max_length=MAX_PROMPT_LENGTH)
    
    @validator('prompt')
    def sanitize_prompt(cls, v):
        # Remove any HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        
        # Remove potentially dangerous JavaScript patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onload, etc.
            r'eval\s*\(',
            r'expression\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            v = re.sub(pattern, '', v, flags=re.IGNORECASE | re.DOTALL)
        
        # Escape special characters
        v = v.replace('&', '&amp;')
        v = v.replace('<', '&lt;')
        v = v.replace('>', '&gt;')
        v = v.replace('"', '&quot;')
        v = v.replace("'", '&#x27;')
        
        return v.strip()

class ValidatedImageData(BaseModel):
    """Validated base64 image data"""
    data: str
    mime_type: str
    
    @validator('data')
    def validate_base64(cls, v):
        try:
            # Remove data URL prefix if present
            if ',' in v:
                v = v.split(',')[1]
            
            # Validate base64
            decoded = base64.b64decode(v)
            
            # Check size
            if len(decoded) > MAX_IMAGE_SIZE:
                raise ValueError(f'Image too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024}MB')
            
            return v
        except Exception as e:
            raise ValueError(f'Invalid base64 image data: {str(e)}')
    
    @validator('mime_type')
    def validate_mime_type(cls, v):
        if v not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f'Invalid image type. Allowed types: {", ".join(ALLOWED_IMAGE_TYPES)}')
        return v

class ValidatedGenerationParams(BaseModel):
    """Validated parameters for code generation"""
    generatedCodeConfig: Literal[tuple(ALLOWED_STACKS)]  # type: ignore
    inputMode: Literal[tuple(ALLOWED_INPUT_MODES)]  # type: ignore
    accessCode: Optional[str] = None
    
    # Image/URL inputs
    image: Optional[str] = None
    url: Optional[SanitizedUrl] = None
    
    # Text inputs
    description: Optional[ValidatedPrompt] = None
    
    # API keys (should not be sent from client in secure implementation)
    openAiApiKey: Optional[str] = None
    anthropicApiKey: Optional[str] = None
    
    # Custom model settings
    isCustomModel: Optional[bool] = False
    customModelId: Optional[constr(max_length=100)] = None
    customModelUrl: Optional[SanitizedUrl] = None
    customModelApiKey: Optional[str] = None
    
    # Other settings
    shouldGenerateImages: Optional[bool] = False
    openAiBaseURL: Optional[SanitizedUrl] = None
    
    @validator('image')
    def validate_image(cls, v, values):
        if v and values.get('inputMode') == 'image':
            # Basic validation - full validation would decode and check the image
            if not v.startswith('data:image/'):
                raise ValueError('Invalid image data URL')
        return v
    
    @validator('customModelUrl')
    def validate_custom_model_url(cls, v, values):
        if v and values.get('isCustomModel'):
            # Additional validation for custom model URLs
            if not v.startswith(('http://', 'https://')):
                raise ValueError('Custom model URL must use HTTP or HTTPS')
        return v

class FileUploadValidator:
    """Validates uploaded files"""
    
    @staticmethod
    def validate_image_file(file_content: bytes, filename: str) -> bool:
        """Validate an uploaded image file"""
        # Check file size
        if len(file_content) > MAX_IMAGE_SIZE:
            raise ValueError(f'File too large. Maximum size is {MAX_IMAGE_SIZE / 1024 / 1024}MB')
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{ext}' not in allowed_extensions:
            raise ValueError(f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}')
        
        # Check magic bytes (file signature)
        magic_bytes = {
            b'\xFF\xD8\xFF': 'image/jpeg',
            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
            b'\x47\x49\x46\x38': 'image/gif',
            b'RIFF': 'image/webp',  # Simplified check
        }
        
        file_header = file_content[:8]
        valid_type = False
        
        for magic, mime_type in magic_bytes.items():
            if file_header.startswith(magic):
                valid_type = True
                break
        
        if not valid_type:
            raise ValueError('File content does not match allowed image types')
        
        return True

def sanitize_html_output(html: str) -> str:
    """Sanitize generated HTML to prevent XSS"""
    # This is a simplified version - in production, use a proper HTML sanitizer like bleach
    
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove event handlers
    html = re.sub(r'\s*on\w+\s*=\s*["\'].*?["\']', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: URLs
    html = re.sub(r'javascript:', '', html, flags=re.IGNORECASE)
    
    # Remove data: URLs that could contain scripts
    html = re.sub(r'data:text/html[^"\']*', '', html, flags=re.IGNORECASE)
    
    return html

def validate_api_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize API responses"""
    # Ensure response has required fields
    required_fields = ['type', 'value']
    
    for field in required_fields:
        if field not in response:
            raise ValueError(f'Missing required field: {field}')
    
    # Sanitize based on response type
    if response['type'] == 'code' and isinstance(response['value'], str):
        response['value'] = sanitize_html_output(response['value'])
    
    return response