"""
Custom Model Handler - Enhanced support for various custom models
"""
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class CustomModelHandler:
    """
    Intelligent handler for custom models with auto-detection and optimization
    """
    
    # Known model providers and their characteristics
    KNOWN_PROVIDERS = {
        "openai": {
            "endpoints": ["/v1/chat/completions", "/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "anthropic": {
            "endpoints": ["/v1/messages", "/messages"],
            "max_tokens": 40000,
            "header_format": "x-api-key",
            "api_format": "anthropic"
        },
        "deepseek": {
            "endpoints": ["/v1/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "together": {
            "endpoints": ["/v1/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "groq": {
            "endpoints": ["/openai/v1/chat/completions", "/v1/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "mistral": {
            "endpoints": ["/v1/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "cohere": {
            "endpoints": ["/v1/chat"],
            "max_tokens": 30000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "ollama": {
            "endpoints": ["/api/chat", "/v1/chat/completions"],
            "max_tokens": 32000,
            "header_format": "Bearer",
            "api_format": "openai"
        },
        "local": {
            "endpoints": ["/v1/chat/completions", "/chat", "/generate"],
            "max_tokens": 30000,
            "header_format": "Bearer",
            "api_format": "openai"
        }
    }
    
    # Model name patterns for auto-detection
    MODEL_PATTERNS = {
        "gpt": {"provider": "openai", "max_tokens": 32000},
        "claude": {"provider": "anthropic", "max_tokens": 40000},
        "deepseek": {"provider": "deepseek", "max_tokens": 32000},
        "mixtral": {"provider": "mistral", "max_tokens": 32000},
        "llama": {"provider": "local", "max_tokens": 32000},
        "yi": {"provider": "local", "max_tokens": 32000},
        "qwen": {"provider": "local", "max_tokens": 32000},
        "gemma": {"provider": "local", "max_tokens": 30000},
        "mistral": {"provider": "mistral", "max_tokens": 32000},
        "command": {"provider": "cohere", "max_tokens": 30000},
    }
    
    @classmethod
    def detect_provider(cls, model_id: str, service_url: str) -> Optional[str]:
        """Detect the provider based on model ID and service URL"""
        # Check URL patterns
        url_lower = service_url.lower()
        for provider, config in cls.KNOWN_PROVIDERS.items():
            if provider in url_lower:
                return provider
        
        # Check model name patterns
        model_lower = model_id.lower()
        for pattern, info in cls.MODEL_PATTERNS.items():
            if pattern in model_lower:
                return info["provider"]
        
        # Check for localhost/local deployments
        parsed_url = urlparse(service_url)
        if parsed_url.hostname in ["localhost", "127.0.0.1"] or parsed_url.hostname.startswith("192.168"):
            return "local"
        
        return None
    
    @classmethod
    def normalize_url(cls, service_url: str, provider: Optional[str] = None) -> str:
        """Normalize and validate the service URL"""
        if not service_url:
            raise ValueError("Service URL is required")
        
        # Ensure protocol
        if not service_url.startswith(('http://', 'https://')):
            service_url = 'https://' + service_url
        
        # Check if URL already has a valid endpoint - if so, don't modify it
        url_path = urlparse(service_url).path
        valid_endpoints = []
        for p_config in cls.KNOWN_PROVIDERS.values():
            valid_endpoints.extend(p_config["endpoints"])
        
        # If URL already has a valid endpoint, return as is
        if any(endpoint in url_path for endpoint in valid_endpoints):
            print(f"[DEBUG] URL already has valid endpoint: {service_url}")
            return service_url
        
        # Check for partial endpoints that need completion
        if url_path.endswith('/v1') or url_path.endswith('/v1/'):
            # Complete the OpenAI-style endpoint
            if not service_url.endswith('/'):
                service_url = service_url.rstrip('/') + '/'
            return service_url + 'chat/completions'
        
        # If no valid endpoint found, add appropriate one based on provider
        if provider and provider in cls.KNOWN_PROVIDERS:
            endpoint = cls.KNOWN_PROVIDERS[provider]["endpoints"][0]
        else:
            # Default to OpenAI-compatible endpoint
            endpoint = "/v1/chat/completions"
        
        # Clean up URL
        service_url = service_url.rstrip('/')
        
        # Add endpoint
        return service_url + endpoint
    
    @classmethod
    def get_optimal_settings(cls, model_id: str, service_url: str, user_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get optimal settings for a custom model"""
        settings = {
            "max_tokens": 30000,  # Safe default
            "temperature": 0.1,
            "api_format": "openai",
            "header_format": "Bearer",
            "stream": True,
            "timeout": 1200
        }
        
        # Detect provider
        provider = cls.detect_provider(model_id, service_url)
        
        # Apply provider-specific settings
        if provider and provider in cls.KNOWN_PROVIDERS:
            provider_config = cls.KNOWN_PROVIDERS[provider]
            settings.update({
                "max_tokens": provider_config["max_tokens"],
                "api_format": provider_config["api_format"],
                "header_format": provider_config["header_format"]
            })
        
        # Check model patterns for token limits
        model_lower = model_id.lower()
        for pattern, info in cls.MODEL_PATTERNS.items():
            if pattern in model_lower and "max_tokens" in info:
                settings["max_tokens"] = info["max_tokens"]
                break
        
        # Apply user overrides
        if user_settings:
            settings.update(user_settings)
        
        return settings
    
    @classmethod
    def validate_configuration(cls, model_id: str, service_url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Validate and return complete configuration for custom model"""
        try:
            # Normalize URL
            normalized_url = cls.normalize_url(service_url)
            
            # Get optimal settings
            settings = cls.get_optimal_settings(model_id, normalized_url)
            
            # Validate API key requirement
            if settings["api_format"] == "anthropic" and not api_key:
                print("[WARNING] Anthropic API requires an API key")
            
            return {
                "valid": True,
                "service_url": normalized_url,
                "settings": settings,
                "provider": cls.detect_provider(model_id, service_url)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "service_url": service_url,
                "settings": cls.get_optimal_settings(model_id, service_url)
            }