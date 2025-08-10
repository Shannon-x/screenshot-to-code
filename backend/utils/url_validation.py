"""
URL validation utilities for custom models
"""
import re
from urllib.parse import urlparse, urlunparse

def smart_validate_url(url: str) -> str:
    """
    Smart URL validation that preserves user intent
    """
    if not url:
        raise ValueError("Service URL is required")
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Ensure protocol
    if not parsed.scheme:
        url = 'https://' + url
        parsed = urlparse(url)
    
    # Get the path
    path = parsed.path
    
    # List of valid API endpoints (don't modify these)
    valid_endpoints = [
        '/v1/chat/completions',
        '/v1/messages',
        '/api/chat',
        '/api/generate', 
        '/chat/completions',
        '/completions',
        '/v1/completions',
        '/openai/v1/chat/completions',
        '/v1/engines/chat/completions',
    ]
    
    # Check if the URL already has a valid endpoint
    for endpoint in valid_endpoints:
        if endpoint in path:
            print(f"[DEBUG] URL has valid endpoint {endpoint}: {url}")
            return url
    
    # Special case: URL ends with /v1 or /v1/
    if path.endswith('/v1') or path == '/v1':
        # User likely wants OpenAI-compatible endpoint
        new_path = path.rstrip('/') + '/chat/completions'
        return urlunparse(parsed._replace(path=new_path))
    
    # Special case: URL has /api but no specific endpoint
    if '/api' in path and not any(ep in path for ep in ['/chat', '/generate', '/completions']):
        # Add /chat to complete the endpoint
        if path.endswith('/'):
            new_path = path + 'chat'
        else:
            new_path = path + '/chat'
        return urlunparse(parsed._replace(path=new_path))
    
    # If no API path at all, add default OpenAI-compatible endpoint
    if not any(marker in path for marker in ['/v1', '/api', '/chat', '/completions']):
        if path.endswith('/'):
            new_path = path + 'v1/chat/completions'
        else:
            new_path = path + '/v1/chat/completions'
        return urlunparse(parsed._replace(path=new_path))
    
    # Return original URL if we can't determine what to do
    print(f"[WARNING] Could not determine proper endpoint for URL: {url}")
    return url


def is_url_complete(url: str) -> bool:
    """Check if a URL already has a complete API endpoint"""
    if not url:
        return False
    
    complete_endpoints = [
        '/v1/chat/completions',
        '/v1/messages',
        '/api/chat',
        '/api/generate',
        '/chat/completions',
        '/completions',
    ]
    
    return any(endpoint in url for endpoint in complete_endpoints)