"""
Model Configuration Settings for Complete Code Generation
"""

# Token limits for different models
# For custom models, these can be overridden dynamically
MODEL_TOKEN_LIMITS = {
    # Custom model defaults (can be overridden)
    "deepseek": 32000,
    "mixtral": 32000,
    "llama": 32000,
    "yi": 32000,
    "qwen": 32000,
    # OpenAI Models
    "gpt-4-turbo-preview": 20000,
    "gpt-4o": 20000,
    "gpt-4o-2024-05-13": 8192,
    "gpt-4o-2024-11-20": 20000,
    "gpt-4.1-2025-04-14": 20000,
    "gpt-4.1-mini-2025-04-14": 20000,
    "gpt-4.1-nano-2025-04-14": 20000,
    "o1-2024-12-17": 30000,
    "o4-mini-2025-04-16": 30000,
    "o3-2025-04-16": 30000,
    
    # Claude Models
    "claude-3-opus-20240229": 20000,
    "claude-3-sonnet-20240229": 20000,
    "claude-3-5-sonnet-20240620": 30000,
    "claude-3-5-sonnet-20241022": 30000,
    "claude-3-7-sonnet-20250219": 40000,
    "claude-4-sonnet-20250514": 40000,
    "claude-4-opus-20250514": 40000,
    
    # Gemini Models
    "gemini-1.5-flash": 20000,
    "gemini-1.5-pro": 20000,
    "gemini-2.5-flash-preview-0520": 30000,
    "gemini-2.5-pro-preview-0506": 30000,
    
    # Custom Models (default) - increased for better compatibility
    "custom": 30000,  # Increased from 8000 to support most custom models
}

# Timeout settings (in seconds)
MODEL_TIMEOUTS = {
    "default": 1200,  # 20 minutes
    "fast": 600,      # 10 minutes
    "slow": 1800,     # 30 minutes
}

# Buffer settings
STREAM_BUFFER_CONFIG = {
    "flush_interval": 0.5,    # 500ms
    "min_buffer_size": 100,   # minimum characters before flush
    "max_buffer_size": 1000,  # force flush at this size
}

# WebSocket settings
WEBSOCKET_CONFIG = {
    "heartbeat_interval": 60,  # 60 seconds
    "send_timeout": 10,        # 10 seconds timeout for sending
    "max_retries": 3,          # retry failed sends
}

# HTML extraction settings
HTML_EXTRACTION_CONFIG = {
    "max_retries": 3,
    "fallback_on_incomplete": True,  # try to fix incomplete HTML
    "auto_close_tags": True,         # automatically close unclosed tags
}

# Custom model configuration
CUSTOM_MODEL_DEFAULTS = {
    "token_limit": 30000,
    "timeout": 1200,
    "temperature": 0.1,
    "stream": True,
    "api_format": "openai",  # openai, anthropic, or custom
}

# Known custom model patterns and their optimal settings
CUSTOM_MODEL_PATTERNS = {
    "deepseek": {"token_limit": 32000, "api_format": "openai"},
    "mixtral": {"token_limit": 32000, "api_format": "openai"},
    "llama": {"token_limit": 32000, "api_format": "openai"},
    "yi": {"token_limit": 32000, "api_format": "openai"},
    "qwen": {"token_limit": 32000, "api_format": "openai"},
    "claude": {"token_limit": 40000, "api_format": "anthropic"},
    "gemini": {"token_limit": 30000, "api_format": "custom"},
}

def get_model_token_limit(model_name: str, custom_settings: dict = None) -> int:
    """Get token limit for a specific model with custom override support"""
    # First check if custom settings override the token limit
    if custom_settings and "max_tokens" in custom_settings:
        return custom_settings["max_tokens"]
    
    # Check exact match first
    if model_name in MODEL_TOKEN_LIMITS:
        return MODEL_TOKEN_LIMITS[model_name]
    
    # Check custom model patterns
    model_lower = model_name.lower()
    for pattern, settings in CUSTOM_MODEL_PATTERNS.items():
        if pattern in model_lower:
            return settings["token_limit"]
    
    # Check partial matches in predefined limits
    for key, value in MODEL_TOKEN_LIMITS.items():
        if key in model_name or model_name in key:
            return value
    
    # Default for custom models
    return CUSTOM_MODEL_DEFAULTS["token_limit"]

def get_model_timeout(model_type: str = "default", custom_settings: dict = None) -> int:
    """Get timeout setting for model type with custom override support"""
    if custom_settings and "timeout" in custom_settings:
        return custom_settings["timeout"]
    return MODEL_TIMEOUTS.get(model_type, MODEL_TIMEOUTS["default"])

def get_custom_model_config(model_name: str, user_settings: dict = None) -> dict:
    """Get complete configuration for a custom model"""
    config = CUSTOM_MODEL_DEFAULTS.copy()
    
    # Apply pattern-based settings
    model_lower = model_name.lower()
    for pattern, settings in CUSTOM_MODEL_PATTERNS.items():
        if pattern in model_lower:
            config.update(settings)
            break
    
    # Apply user settings overrides
    if user_settings:
        config.update(user_settings)
    
    return config

def validate_custom_model_url(url: str) -> str:
    """Validate and normalize custom model URL"""
    if not url:
        raise ValueError("Model service URL is required")
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check if URL already has a valid endpoint path
    # Don't modify URLs that already have complete paths
    if any(endpoint in url for endpoint in ['/v1/chat/completions', '/v1/messages', '/api/chat', '/api/generate', '/chat/completions']):
        print(f"[DEBUG] URL already has valid endpoint: {url}")
        return url
    
    # Only add endpoint if URL looks incomplete
    if url.endswith('/v1') or url.endswith('/v1/'):
        # URL ends with /v1, add chat/completions
        if not url.endswith('/'):
            url += '/'
        url += 'chat/completions'
    elif not any(path in url for path in ['/v1/', '/api/', '/chat', '/messages', '/generate']):
        # URL has no API path at all, add default
        if not url.endswith('/'):
            url += '/'
        url += 'v1/chat/completions'
    
    return url