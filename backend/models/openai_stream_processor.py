"""
OpenAI Stream Processor - Refactored to use BaseStreamProcessor
"""
import time
from typing import Awaitable, Callable, List, Optional, Dict, Any
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionChunk
from llm import Completion
# from config.model_configs import ComplexityLevel
from models.base_stream_processor import BaseStreamProcessor, StreamBuffer

class OpenAIStreamProcessor(BaseStreamProcessor):
    """OpenAI-specific implementation of BaseStreamProcessor"""
    
    async def create_client(self):
        """Create and return OpenAI client"""
        return AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def prepare_request_params(
        self,
        messages: List[ChatCompletionMessageParam],
        model_name: str,
        base_config: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare OpenAI-specific request parameters"""
        if base_config is None:
            base_config = {}
            
        # Start with base configuration
        params = {
            "model": model_name,
            "messages": messages,
            "timeout": self.timeout,
            **base_config
        }
        
        # Model-specific adjustments
        if model_name not in ["o1-2024-12-17", "o4-mini-2025-04-16", "o3-2025-04-16"]:
            params.setdefault("temperature", 0)
            params["stream"] = True
        
        # Special handling for specific models
        if model_name in ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14"]:
            params["stream"] = True
            params.setdefault("max_tokens", 20000)  # Increased from 10000
        
        if model_name == "gpt-4o-2024-05-13":
            params.setdefault("max_tokens", 8192)  # Increased from 4096
        
        if model_name == "gpt-4o-2024-11-20":
            params.setdefault("max_tokens", 20000)  # Increased from 16384
        
        # O1 series special handling
        if model_name == "o1-2024-12-17":
            params["max_completion_tokens"] = 30000  # Increased from 20000
            params.pop("max_tokens", None)
            params.pop("temperature", None)
            params.pop("stream", None)
        
        if model_name in ["o4-mini-2025-04-16", "o3-2025-04-16"]:
            params["max_completion_tokens"] = 30000  # Increased from 20000
            params["reasoning_effort"] = "high"
            params.pop("max_tokens", None)
            params.pop("temperature", None)
        
        return params
    
    async def _make_api_call(self, params: Dict[str, Any]):
        """Make the OpenAI API call"""
        if params.get("stream", False):
            return await self._client.chat.completions.create(**params)
        else:
            # Non-streaming call for O1 models
            response = await self._client.chat.completions.create(**params)
            return response
    
    async def process_stream(
        self,
        response_stream,
        callback: Callable[[str], Awaitable[None]]
    ) -> str:
        """Process OpenAI streaming response"""
        # Check if this is a streaming response
        if hasattr(response_stream, '__aiter__'):
            # Streaming response
            return await self._process_streaming_response(response_stream, callback)
        else:
            # Non-streaming response (O1 models)
            content = response_stream.choices[0].message.content or ""
            await callback(content)
            return content
    
    async def _process_streaming_response(
        self,
        stream,
        callback: Callable[[str], Awaitable[None]]
    ) -> str:
        """Process streaming chunks"""
        buffer = StreamBuffer(callback)
        full_response = ""
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                await buffer.add(content)
        
        # Final flush
        await buffer.finalize()
        return full_response


# Legacy function for backward compatibility
async def stream_openai_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    base_url: str | None,
    callback: Callable[[str], Awaitable[None]],
    model_name: str,
    complexity_level: Optional['ComplexityLevel'] = None,
    framework: Optional[str] = None,
) -> Completion:
    """
    Legacy function maintained for backward compatibility.
    Uses the new OpenAIStreamProcessor internally.
    """
    processor = OpenAIStreamProcessor(api_key=api_key, base_url=base_url)
    return await processor.stream_response(
        messages=messages,
        callback=callback,
        model_name=model_name,
        complexity_level=complexity_level,
        framework=framework
    )