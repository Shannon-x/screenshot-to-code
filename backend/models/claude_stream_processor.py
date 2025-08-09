"""
Claude Stream Processor - Refactored to use BaseStreamProcessor
"""
import time
from typing import Awaitable, Callable, List, Optional, Dict, Any
from anthropic import AsyncAnthropic
from openai.types.chat import ChatCompletionMessageParam
from llm import Completion, Llm
# from config.model_configs import ComplexityLevel
from models.base_stream_processor import BaseStreamProcessor, StreamBuffer
# Import will be done later to avoid circular import
# from models.claude import convert_openai_messages_to_claude

class ClaudeStreamProcessor(BaseStreamProcessor):
    """Claude-specific implementation of BaseStreamProcessor"""
    
    async def create_client(self):
        """Create and return Anthropic client"""
        return AsyncAnthropic(api_key=self.api_key)
    
    async def prepare_request_params(
        self,
        messages: List[ChatCompletionMessageParam],
        model_name: str,
        base_config: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare Claude-specific request parameters"""
        # Import here to avoid circular import
        from models.claude import convert_openai_messages_to_claude
        
        if base_config is None:
            base_config = {}
        
        # Convert OpenAI format to Claude format
        system_prompt, claude_messages = convert_openai_messages_to_claude(messages)
        
        # Base parameters
        params = {
            "model": model_name,
            "system": system_prompt,
            "messages": claude_messages,
            "temperature": base_config.get("temperature", 0.0),
            "max_tokens": base_config.get("max_tokens", 8192),
        }
        
        # Model-specific adjustments
        if model_name == "claude-3-7-sonnet-20250219":
            params["max_tokens"] = 20000
        
        # Handle Claude 4 models with thinking
        if model_name in [Llm.CLAUDE_4_SONNET_2025_05_14.value, Llm.CLAUDE_4_OPUS_2025_05_14.value]:
            params["thinking"] = {"type": "enabled", "budget_tokens": 10000}
            params["max_tokens"] = 30000
            params.pop("temperature", None)  # Not compatible with thinking
        else:
            # Add beta for output-128k support
            params["betas"] = ["output-128k-2025-02-19"]
        
        return params
    
    async def _make_api_call(self, params: Dict[str, Any]):
        """Make the Claude API call"""
        model_name = params.pop("model")
        
        # Check if this is a thinking model
        if "thinking" in params:
            # Use the thinking-enabled stream
            return self._client.messages.stream(**params, model=model_name)
        else:
            # Use the beta stream
            betas = params.pop("betas", [])
            return self._client.beta.messages.stream(**params, model=model_name, betas=betas)
    
    async def process_stream(
        self,
        response_stream,
        callback: Callable[[str], Awaitable[None]]
    ) -> str:
        """Process Claude streaming response"""
        buffer = StreamBuffer(callback)
        full_response = ""
        
        async with response_stream as stream:
            # Check if this is a thinking-enabled stream
            if hasattr(stream, '__aiter__'):
                async for event in stream:
                    if hasattr(event, 'type') and event.type == "content_block_delta":
                        if event.delta.type == "thinking_delta":
                            # Skip thinking deltas (we don't send them to the client)
                            continue
                        elif event.delta.type == "text_delta":
                            content = event.delta.text
                            full_response += content
                            await buffer.add(content)
                    else:
                        # Regular text stream
                        async for text in stream.text_stream:
                            full_response += text
                            await buffer.add(text)
                        break
            else:
                # Non-streaming response (shouldn't happen with Claude)
                full_response = str(response_stream)
                await callback(full_response)
        
        # Final flush
        await buffer.finalize()
        return full_response
    
    async def cleanup(self):
        """Cleanup Claude client"""
        if self._client:
            await self._client.close()


# Legacy function for backward compatibility
async def stream_claude_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    callback: Callable[[str], Awaitable[None]],
    model_name: str,
    complexity_level: Optional['ComplexityLevel'] = None,
    framework: Optional[str] = None,
) -> Completion:
    """
    Legacy function maintained for backward compatibility.
    Uses the new ClaudeStreamProcessor internally.
    """
    processor = ClaudeStreamProcessor(api_key=api_key)
    return await processor.stream_response(
        messages=messages,
        callback=callback,
        model_name=model_name,
        complexity_level=complexity_level,
        framework=framework
    )