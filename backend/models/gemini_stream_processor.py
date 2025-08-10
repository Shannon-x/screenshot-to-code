"""
Gemini Stream Processor - Refactored to use BaseStreamProcessor
"""
import base64
import time
from typing import Awaitable, Callable, List, Optional, Dict, Any
from openai.types.chat import ChatCompletionMessageParam
from google import genai
from google.genai import types
from llm import Completion, Llm
# from config.model_configs import ComplexityLevel
from models.base_stream_processor import BaseStreamProcessor, StreamBuffer
# Import will be done later to avoid circular import
# from models.gemini import extract_image_from_messages

class GeminiStreamProcessor(BaseStreamProcessor):
    """Gemini-specific implementation of BaseStreamProcessor"""
    
    async def create_client(self):
        """Create and return Gemini client"""
        return genai.Client(api_key=self.api_key)
    
    async def prepare_request_params(
        self,
        messages: List[ChatCompletionMessageParam],
        model_name: str,
        base_config: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare Gemini-specific request parameters"""
        # Import here to avoid circular import
        from models.gemini import extract_image_from_messages
        
        if base_config is None:
            base_config = {}
        
        # Extract image data from messages
        image_data = extract_image_from_messages(messages)
        
        # Build content parts
        parts = [{"text": messages[0]["content"]}]  # System prompt
        
        # Add image part
        if "data" in image_data:
            parts.append(
                types.Part.from_bytes(
                    data=base64.b64decode(image_data["data"]),
                    mime_type=image_data["mime_type"],
                )
            )
        
        # Model-specific configuration
        if model_name == Llm.GEMINI_2_5_FLASH_PREVIEW_05_20.value:
            # Gemini 2.5 Flash supports thinking budgets
            config = types.GenerateContentConfig(
                temperature=base_config.get("temperature", 0),
                max_output_tokens=base_config.get("max_tokens", 30000),  # Increased from 20000
                thinking_config=types.ThinkingConfig(
                    thinking_budget=10000, include_thoughts=True  # Increased thinking budget
                ),
            )
        elif model_name == Llm.GEMINI_2_5_PRO_PREVIEW_05_06.value:
            config = types.GenerateContentConfig(
                temperature=base_config.get("temperature", 0),
                max_output_tokens=base_config.get("max_tokens", 30000),  # Increased from 20000
                thinking_config=types.ThinkingConfig(include_thoughts=True),
            )
        else:
            config = types.GenerateContentConfig(
                temperature=base_config.get("temperature", 0),
                max_output_tokens=base_config.get("max_tokens", 20000),  # Increased from 8000
            )
        
        return {
            "model": model_name,
            "contents": {"parts": parts},
            "config": config,
        }
    
    async def _make_api_call(self, params: Dict[str, Any]):
        """Make the Gemini API call"""
        return await self._client.aio.models.generate_content_stream(**params)
    
    async def process_stream(
        self,
        response_stream,
        callback: Callable[[str], Awaitable[None]]
    ) -> str:
        """Process Gemini streaming response"""
        buffer = StreamBuffer(callback)
        full_response = ""
        
        async for chunk in response_stream:
            if chunk.candidates and len(chunk.candidates) > 0:
                for part in chunk.candidates[0].content.parts:
                    if not part.text:
                        continue
                    elif part.thought:
                        # Log thoughts but don't send to client
                        # self.logger.debug(f"Gemini thought: {part.text}")
                        pass
                    else:
                        full_response += part.text
                        await buffer.add(part.text)
        
        # Final flush
        await buffer.finalize()
        return full_response


# Legacy function for backward compatibility
async def stream_gemini_response(
    messages: List[ChatCompletionMessageParam],
    api_key: str,
    callback: Callable[[str], Awaitable[None]],
    model_name: str,
    complexity_level: Optional['ComplexityLevel'] = None,
    framework: Optional[str] = None,
) -> Completion:
    """
    Legacy function maintained for backward compatibility.
    Uses the new GeminiStreamProcessor internally.
    """
    processor = GeminiStreamProcessor(api_key=api_key)
    return await processor.stream_response(
        messages=messages,
        callback=callback,
        model_name=model_name,
        complexity_level=complexity_level,
        framework=framework
    )