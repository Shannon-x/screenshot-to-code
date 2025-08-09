"""
Cache Integration - Integrate Redis cache with code generation workflow
"""
import hashlib
import json
from typing import Optional, Dict, Any
from cache import cache
# from config.model_configs import DynamicModelConfigurator, ComplexityLevel
# Temporarily define ComplexityLevel
from enum import Enum
class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class DynamicModelConfigurator:
    pass
import logging

logger = logging.getLogger(__name__)

class CachedCodeGenerator:
    """
    Wrapper for code generation with caching support
    """
    
    def __init__(self):
        self.cache = cache
        self.configurator = DynamicModelConfigurator() if DynamicModelConfigurator else None
        
    async def initialize(self):
        """Initialize cache connection"""
        await self.cache.connect()
        logger.info("Cache initialized for code generation")
    
    async def cleanup(self):
        """Cleanup cache connection"""
        await self.cache.disconnect()
    
    def _generate_prompt_hash(self, prompt: str, model: str, framework: Optional[str] = None) -> str:
        """Generate hash for prompt + model + framework combination"""
        content = f"{prompt}|{model}|{framework or 'default'}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _generate_image_hash(self, image_data: str) -> str:
        """Generate hash for image data"""
        return hashlib.sha256(image_data.encode()).hexdigest()
    
    async def get_cached_generation(
        self,
        prompt: str,
        model: str,
        framework: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if we have a cached result for this prompt
        
        Args:
            prompt: The generation prompt
            model: Model name
            framework: Optional framework specification
            
        Returns:
            Cached result if available, None otherwise
        """
        prompt_hash = self._generate_prompt_hash(prompt, model, framework)
        
        result = await self.cache.get_generation_result(prompt_hash, model)
        if result:
            logger.info(f"Cache hit for model {model} with prompt hash {prompt_hash[:8]}...")
            
        return result
    
    async def cache_generation(
        self,
        prompt: str,
        model: str,
        result: str,
        framework: Optional[str] = None,
        ttl: int = 3600
    ) -> bool:
        """
        Cache a generation result
        
        Args:
            prompt: The generation prompt
            model: Model name
            result: Generation result
            framework: Optional framework specification
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully
        """
        prompt_hash = self._generate_prompt_hash(prompt, model, framework)
        
        success = await self.cache.cache_generation_result(
            prompt_hash,
            model,
            result,
            ttl
        )
        
        if success:
            logger.info(f"Cached result for model {model} with prompt hash {prompt_hash[:8]}...")
            
        return success
    
    async def get_cached_screenshot_analysis(
        self,
        image_data: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached screenshot analysis
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Cached analysis if available
        """
        image_hash = self._generate_image_hash(image_data)
        
        result = await self.cache.get_screenshot_analysis(image_hash)
        if result:
            logger.info(f"Cache hit for screenshot analysis with hash {image_hash[:8]}...")
            
        return result
    
    async def cache_screenshot_analysis(
        self,
        image_data: str,
        analysis: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """
        Cache screenshot analysis result
        
        Args:
            image_data: Base64 encoded image data
            analysis: Analysis result
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully
        """
        image_hash = self._generate_image_hash(image_data)
        
        success = await self.cache.cache_screenshot_analysis(
            image_hash,
            analysis,
            ttl
        )
        
        if success:
            logger.info(f"Cached screenshot analysis with hash {image_hash[:8]}...")
            
        return success
    
    async def clear_model_cache(self, model: str) -> int:
        """Clear all cached results for a specific model"""
        count = await self.cache.delete_by_tag(f"model:{model}")
        logger.info(f"Cleared {count} cached entries for model {model}")
        return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()

# Example integration with the existing code generation flow
async def generate_code_with_cache(
    prompt: str,
    model: str,
    image_data: Optional[str] = None,
    framework: Optional[str] = None,
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
) -> str:
    """
    Generate code with caching support
    
    This would be integrated into the existing stream_*_response functions
    """
    generator = CachedCodeGenerator()
    await generator.initialize()
    
    try:
        # Check cache first
        cached_result = await generator.get_cached_generation(prompt, model, framework)
        if cached_result:
            return cached_result
        
        # If we have image data, check for cached analysis
        if image_data:
            cached_analysis = await generator.get_cached_screenshot_analysis(image_data)
            if cached_analysis:
                # Use cached analysis to potentially modify the prompt
                logger.info("Using cached screenshot analysis")
        
        # Generate new result (this would call the actual LLM)
        # result = await actual_llm_generation(prompt, model, ...)
        result = "Generated code would go here"  # Placeholder
        
        # Cache the result
        await generator.cache_generation(prompt, model, result, framework)
        
        # If we had image analysis, cache that too
        if image_data and not cached_analysis:
            analysis = {"detected_elements": ["button", "form", "nav"]}  # Placeholder
            await generator.cache_screenshot_analysis(image_data, analysis)
        
        return result
        
    finally:
        await generator.cleanup()

# Middleware for automatic caching
class CacheMiddleware:
    """
    Middleware to automatically cache LLM responses
    """
    
    def __init__(self, cache_ttl: int = 3600):
        self.generator = CachedCodeGenerator()
        self.cache_ttl = cache_ttl
        self.enabled = True
    
    async def __aenter__(self):
        await self.generator.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.generator.cleanup()
    
    async def process_request(
        self,
        prompt: str,
        model: str,
        framework: Optional[str] = None
    ) -> Optional[str]:
        """Check cache before processing request"""
        if not self.enabled:
            return None
            
        return await self.generator.get_cached_generation(prompt, model, framework)
    
    async def process_response(
        self,
        prompt: str,
        model: str,
        response: str,
        framework: Optional[str] = None
    ):
        """Cache response after processing"""
        if not self.enabled:
            return
            
        await self.generator.cache_generation(
            prompt,
            model,
            response,
            framework,
            self.cache_ttl
        )