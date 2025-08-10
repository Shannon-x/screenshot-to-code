"""
Enhanced Model Stream Processor with Retry and Completion Verification
"""
import asyncio
import time
import logging
from typing import Optional, Callable, Awaitable
from models.base_stream_processor import BaseStreamProcessor, RetryHandler

logger = logging.getLogger(__name__)

class EnhancedStreamProcessor:
    """
    Enhanced stream processor that ensures complete code generation
    """
    
    def __init__(self, base_processor: BaseStreamProcessor):
        self.base_processor = base_processor
        self.retry_handler = RetryHandler(max_retries=3, base_delay=2.0)
        
    async def stream_with_verification(
        self,
        messages,
        callback: Callable[[str], Awaitable[None]],
        model_name: str,
        **kwargs
    ):
        """Stream response with verification and retry on incomplete results"""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Track response completeness
                response_chunks = []
                chunk_count = 0
                last_chunk_time = time.time()
                
                # Create a wrapper callback to monitor chunks
                async def monitoring_callback(chunk: str):
                    nonlocal chunk_count, last_chunk_time
                    response_chunks.append(chunk)
                    chunk_count += 1
                    last_chunk_time = time.time()
                    await callback(chunk)
                
                # Stream the response
                result = await self.base_processor.stream_response(
                    messages=messages,
                    callback=monitoring_callback,
                    model_name=model_name,
                    **kwargs
                )
                
                # Verify response completeness
                full_response = "".join(response_chunks)
                
                # Check if response is complete
                if self._is_response_complete(full_response):
                    logger.info(f"Response complete for {model_name}: {len(full_response)} chars")
                    return result
                else:
                    logger.warning(f"Incomplete response detected for {model_name}, attempt {attempt + 1}")
                    
                    # If incomplete, retry with increased token limit
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        
                        # Append a continuation prompt
                        continuation_prompt = {
                            "role": "assistant",
                            "content": full_response
                        }
                        messages_with_continuation = messages + [
                            continuation_prompt,
                            {
                                "role": "user",
                                "content": "Please continue generating the code from where you left off. Make sure to complete the entire HTML document."
                            }
                        ]
                        messages = messages_with_continuation
                        
            except Exception as e:
                logger.error(f"Error in stream verification for {model_name}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            
            attempt += 1
        
        # If all attempts failed, return the last result
        return result
    
    def _is_response_complete(self, response: str) -> bool:
        """Check if the response contains complete HTML"""
        response_lower = response.lower()
        
        # Check for HTML completeness
        has_html_start = "<html" in response_lower
        has_html_end = "</html>" in response_lower
        has_body_end = "</body>" in response_lower
        
        # For HTML responses, check structure
        if has_html_start:
            return has_html_end and has_body_end
        
        # For non-HTML responses, check for common completion indicators
        # (This could be expanded based on your needs)
        if len(response.strip()) < 100:
            return False
        
        return True
    
    async def ensure_complete_generation(
        self,
        messages,
        callback: Callable[[str], Awaitable[None]],
        model_name: str,
        **kwargs
    ):
        """Ensure complete code generation with multiple strategies"""
        try:
            # First attempt with enhanced streaming
            result = await self.stream_with_verification(
                messages=messages,
                callback=callback,
                model_name=model_name,
                **kwargs
            )
            
            # Additional verification can be added here
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate complete code: {e}")
            # Send error message through callback
            error_msg = f"\\n\\n<!-- Error: Failed to generate complete code. Please try again. -->"
            await callback(error_msg)
            raise