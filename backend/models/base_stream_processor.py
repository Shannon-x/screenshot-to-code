"""
Base Stream Processor - Unified base class for all LLM streaming implementations
"""
import time
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable, Awaitable, Optional, Union
from openai.types.chat import ChatCompletionMessageParam
from llm import Completion
# from config.model_configs import ComplexityLevel, get_model_config
# Temporarily define ComplexityLevel
from enum import Enum
class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

def get_model_config(model_name, complexity_level, framework):
    # Temporary stub
    return type('Config', (), {'to_dict': lambda: {}})()
import asyncio
import logging

# Configure logger
logger = logging.getLogger(__name__)

class BaseStreamProcessor(ABC):
    """
    Abstract base class for all LLM stream processors.
    Provides common functionality and enforces consistent interface.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 1200  # Increased timeout to 20 minutes
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = None
    
    @abstractmethod
    async def create_client(self):
        """Create and return the API client"""
        pass
    
    @abstractmethod
    async def prepare_request_params(
        self,
        messages: List[ChatCompletionMessageParam],
        model_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare request parameters specific to the model/provider"""
        pass
    
    @abstractmethod
    async def process_stream(
        self,
        response_stream,
        callback: Callable[[str], Awaitable[None]]
    ) -> str:
        """Process the streaming response and return full text"""
        pass
    
    async def stream_response(
        self,
        messages: List[ChatCompletionMessageParam],
        callback: Callable[[str], Awaitable[None]],
        model_name: str,
        complexity_level: Optional['ComplexityLevel'] = None,
        framework: Optional[str] = None,
        **kwargs
    ) -> Completion:
        """
        Main method to stream responses from LLM
        
        Args:
            messages: Chat messages
            callback: Async callback for streaming chunks
            model_name: Name of the model
            complexity_level: Complexity level for dynamic config
            framework: Target framework for fine-tuning
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Completion object with duration and full response
        """
        start_time = time.time()
        
        try:
            # Create client if not exists
            if not self._client:
                self._client = await self.create_client()
            
            # Get dynamic configuration
            if complexity_level:
                model_config = get_model_config(model_name, complexity_level, framework)
                base_config = model_config.to_dict()
            else:
                base_config = {}
            
            # Prepare request parameters
            params = await self.prepare_request_params(
                messages=messages,
                model_name=model_name,
                base_config=base_config,
                **kwargs
            )
            
            # Make the API call
            response_stream = await self._make_api_call(params)
            
            # Process the stream
            full_response = await self.process_stream(response_stream, callback)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log success
            logger.info(f"{model_name} completion took {duration:.2f} seconds")
            
            return Completion(
                duration=duration,
                model=model_name,
                content=full_response
            )
            
        except asyncio.CancelledError:
            logger.warning(f"Stream cancelled for {model_name}")
            raise
        except Exception as e:
            logger.error(f"Error in {model_name} stream: {str(e)}")
            logger.error(traceback.format_exc())
            # Return partial completion on error
            duration = time.time() - start_time
            return Completion(
                duration=duration,
                model=model_name,
                content=f"Error: {str(e)}",
                error=True
            )
    
    @abstractmethod
    async def _make_api_call(self, params: Dict[str, Any]):
        """Make the actual API call and return response stream"""
        pass
    
    async def handle_error(self, error: Exception, model_name: str):
        """Common error handling logic"""
        error_msg = f"Error in {model_name}: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Determine if error is retryable
        if self._is_retryable_error(error):
            logger.info(f"Retryable error for {model_name}, will retry...")
            return True
        return False
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable"""
        error_str = str(error).lower()
        retryable_patterns = [
            "timeout",
            "connection",
            "rate limit",
            "temporarily unavailable",
            "503",
            "502",
            "429"
        ]
        return any(pattern in error_str for pattern in retryable_patterns)
    
    def _extract_error_message(self, error: Exception) -> str:
        """Extract user-friendly error message"""
        error_str = str(error)
        
        # Common error mappings
        if "rate limit" in error_str.lower():
            return "API rate limit exceeded. Please try again later."
        elif "timeout" in error_str.lower():
            return "Request timed out. The model took too long to respond."
        elif "authentication" in error_str.lower() or "api key" in error_str.lower():
            return "Authentication failed. Please check your API key."
        elif "connection" in error_str.lower():
            return "Connection error. Please check your internet connection."
        else:
            # Return sanitized error message
            return f"An error occurred: {error_str[:200]}"


class StreamBuffer:
    """Helper class to buffer streaming responses"""
    
    def __init__(self, callback: Callable[[str], Awaitable[None]]):
        self.callback = callback
        self.buffer = ""
        self.last_flush = time.time()
        self.flush_interval = 0.5  # Increased flush interval to 500ms for better stability
        self.min_buffer_size = 100  # Minimum buffer size before flushing
    
    async def add(self, chunk: str):
        """Add chunk to buffer and flush if needed"""
        self.buffer += chunk
        
        # Flush if buffer is large or enough time has passed
        # Increased buffer size threshold for more stable streaming
        if len(self.buffer) > self.min_buffer_size or (time.time() - self.last_flush) > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        """Flush the buffer"""
        if self.buffer:
            try:
                await self.callback(self.buffer)
                self.buffer = ""
                self.last_flush = time.time()
            except Exception as e:
                logger.warning(f"Failed to flush buffer: {e}")
                # If WebSocket is closed, clear buffer anyway
                if "close" in str(e).lower() or "Cannot call" in str(e):
                    self.buffer = ""
                    raise  # Re-raise to stop processing
    
    async def finalize(self):
        """Final flush of any remaining data"""
        await self.flush()


class RetryHandler:
    """Helper class for handling retries with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ):
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retry attempt {attempt + 1} after {delay}s delay")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")
        
        raise last_error