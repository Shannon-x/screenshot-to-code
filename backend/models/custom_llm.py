import json
import time
import traceback
from typing import Any, Callable, Coroutine, List, Awaitable

import aiohttp
from openai.types.chat import ChatCompletionMessageParam

# Import stream reader and message formatter
try:
    from utils.stream_reader import read_complete_stream
    from utils.message_formatter import format_messages_with_fallback, should_force_string_content
except ImportError:
    read_complete_stream = None
    format_messages_with_fallback = None
    should_force_string_content = None

# Assuming Completion is a dict-like structure, define it more concretely if possible
# For now, using Any
Completion = dict[str, Any]


async def call_custom_llm_api(
    prompt_messages: List[ChatCompletionMessageParam],
    model_id: str,
    service_url: str,
    api_key: str | None,
    # Callback to stream chunks: content_chunk, variant_index
    stream_callback: Callable[[str, int], Awaitable[None]],
    index: int,  # Variant index
    # TODO: Add other potential parameters like temperature, max_tokens if configurable by user
) -> Completion:
    """
    Calls a custom Language Model API with automatic format detection and retry.

    Args:
        prompt_messages: List of messages forming the prompt.
        model_id: The ID or name of the custom model.
        service_url: The full URL of the custom model's API endpoint.
        api_key: Optional API key for authorization.
        stream_callback: Asynchronous callback function to handle streaming content chunks.
                         It receives the content chunk (str) and variant index (int).
        index: The variant index, passed to the stream_callback.

    Returns:
        A Completion object (dictionary) with 'duration' and 'code' (full response text).
    """
    start_time = time.time()
    
    # Try with multimodal format first, then fallback to string if needed
    force_string = False
    max_attempts = 2
    
    for attempt in range(max_attempts):
        try:
            result = await _call_custom_llm_internal(
                prompt_messages=prompt_messages,
                model_id=model_id,
                service_url=service_url,
                api_key=api_key,
                stream_callback=stream_callback,
                index=index,
                force_string_content=force_string,
                start_time=start_time
            )
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG] Attempt {attempt + 1} failed: {error_msg}")
            
            # Check if we should retry with string content
            if attempt == 0 and should_force_string_content and should_force_string_content(error_msg):
                print(f"[INFO] Retrying with string-only content format")
                force_string = True
                continue
            else:
                # Final attempt failed or not a format error
                raise

async def _call_custom_llm_internal(
    prompt_messages: List[ChatCompletionMessageParam],
    model_id: str,
    service_url: str,
    api_key: str | None,
    stream_callback: Callable[[str, int], Awaitable[None]],
    index: int,
    force_string_content: bool = False,
    start_time: float = None
) -> Completion:
    """
    Internal implementation of custom LLM API call.
    """
    if start_time is None:
        start_time = time.time()

    try:
        # Determine API format
        api_format = "openai"  # Default
        if "anthropic" in service_url.lower() or "claude" in model_id.lower():
            api_format = "anthropic"
        
        # Format messages based on force_string_content flag
        if format_messages_with_fallback:
            formatted_messages, has_multimodal = format_messages_with_fallback(
                prompt_messages, 
                force_string_content=force_string_content
            )
            print(f"[DEBUG] Formatted messages - Multimodal: {has_multimodal}, Force string: {force_string_content}")
        else:
            # Fallback to basic formatting - ensure all content is string
            formatted_messages = []
            for msg in prompt_messages:
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Extract text from multimodal content
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                    content = " ".join(text_parts)
                formatted_messages.append({"role": msg.get("role", "user"), "content": str(content)})
            print(f"[DEBUG] Using fallback message formatter")

        headers = {"Content-Type": "application/json"}
    
    # Import model settings and handler
    try:
        from config.model_settings import get_custom_model_config
        from models.custom_model_handler import CustomModelHandler
        from utils.url_validation import smart_validate_url
    except ImportError:
        # Fallback if import fails
        def get_custom_model_config(model_id):
            return {"token_limit": 30000, "api_format": "openai"}
        def smart_validate_url(url):
            # Basic validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url
        CustomModelHandler = None
        
    # Validate and normalize URL
    try:
        if CustomModelHandler:
            # Use the intelligent handler
            config_result = CustomModelHandler.validate_configuration(model_id, service_url, api_key)
            service_url = config_result["service_url"]
            model_config = config_result["settings"]
            default_max_tokens = model_config.get("max_tokens", 30000)
            print(f"[DEBUG] Using CustomModelHandler - Provider: {config_result.get('provider')}, Max tokens: {default_max_tokens}")
        else:
            # Fallback to basic validation
            service_url = smart_validate_url(service_url)
            model_config = get_custom_model_config(model_id)
            default_max_tokens = model_config.get("token_limit", 30000)
        print(f"[DEBUG] Normalized service URL: {service_url}")
    except Exception as e:
        print(f"[WARNING] URL validation failed: {e}, using original URL")
        # Use safe defaults
        default_max_tokens = 30000
        model_config = {"api_format": "openai"}
    
    # Get model-specific configuration is already handled above
    
    # Handle Anthropic API specific authentication and format
        if api_format == "anthropic":
            print(f"[DEBUG] Detected Anthropic API endpoint: {service_url}")
            if api_key:
                headers["x-api-key"] = api_key  # Anthropic uses x-api-key header
                headers["anthropic-version"] = "2023-06-01"  # Required version header
                print(f"[DEBUG] Using Anthropic API key (ends with: ...{api_key[-4:] if len(api_key) > 4 else 'short'})")
            else:
                print("Warning: No API key provided for Anthropic API")
            
            # Anthropic API format - separate system messages
            system_prompts = [m["content"] for m in formatted_messages if m["role"] == "system"]
            user_messages = [m for m in formatted_messages if m["role"] != "system"]
            
            request_data: dict[str, Any] = {
                "model": model_id,
                "messages": user_messages,
                "max_tokens": default_max_tokens,  # Use dynamic token limit
                "temperature": 0.1,
                "stream": True
            }
            
            if system_prompts:
                request_data["system"] = "\n".join(system_prompts)
                
            print(f"[DEBUG] Anthropic request with {len(user_messages)} messages")
        else:
            # Default OpenAI-like format
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                print(f"[DEBUG] Using Bearer token for custom model (ends with: ...{api_key[-4:] if len(api_key) > 4 else 'short'})")
            else:
                print("Warning: No API key provided for custom model")

            request_data: dict[str, Any] = {
                "model": model_id,
                "messages": formatted_messages,
                "stream": True,
                "temperature": 0.1,
                "max_tokens": default_max_tokens  # Use dynamic token limit
            }

        print(f"[DEBUG] Final request URL: {service_url}")
        print(f"[DEBUG] Request data keys: {list(request_data.keys())}")
        print(f"[DEBUG] Model: {request_data.get('model')}")
        print(f"[DEBUG] Max tokens: {request_data.get('max_tokens')}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                service_url,
                headers=headers,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=300)  # Increased timeout to 5 minutes
            ) as response:
                print(f"[DEBUG] Response status: {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Custom model API request failed with status {response.status}: {error_text}"
                    )

                # Use enhanced stream reader if available
                if read_complete_stream:
                    print(f"[DEBUG] Using enhanced stream reader")
                    full_response_text = await read_complete_stream(
                        response, 
                        stream_callback, 
                        index,
                        timeout=300
                    )
                    duration = time.time() - start_time
                    return {"duration": duration, "code": full_response_text}
                else:
                    # Fallback to original implementation
                    print(f"[DEBUG] Using standard stream reader")

                full_response_text = ""
                buffer = ""
                chunk_count = 0
                last_chunk_time = time.time()
                
                # Process streaming response (Server-Sent Events like format)
                async for line_bytes in response.content:
                    try:
                        # Decode with error handling
                        line = line_bytes.decode("utf-8", errors="ignore").strip()
                        if not line:
                            continue
                        
                        # Add to buffer for partial line handling
                        buffer += line + "\n"
                        
                        # Process complete SSE events
                        if line.startswith("data: "):
                            data_content = line[len("data: "):]
                            if data_content == "[DONE]":
                                print(f"[DEBUG] Stream completed. Total chunks: {chunk_count}, Total chars: {len(full_response_text)}")
                                break
                            try:
                                chunk_json = json.loads(data_content)
                                content_chunk = ""
                                
                                # Handle Anthropic API streaming format
                                if "anthropic" in service_url.lower():
                                    if chunk_json.get("type") == "content_block_delta":
                                        delta = chunk_json.get("delta", {})
                                        if delta.get("type") == "text_delta":
                                            content_chunk = delta.get("text", "")
                                    elif chunk_json.get("type") == "message_delta":
                                        # Handle message-level deltas if needed
                                        pass
                                # OpenAI-like format
                                elif isinstance(chunk_json.get("choices"), list) and chunk_json["choices"]:
                                    delta = chunk_json["choices"][0].get("delta", {})
                                    content_chunk = delta.get("content", "")
                                # Generic fallbacks
                                elif isinstance(chunk_json.get("delta"), dict):
                                    content_chunk = chunk_json["delta"].get("text", "")
                                elif "text" in chunk_json:
                                    content_chunk = chunk_json["text"]
                                
                                if content_chunk:
                                    chunk_count += 1
                                    full_response_text += content_chunk
                                    last_chunk_time = time.time()
                                    try:
                                        await stream_callback(content_chunk, index)
                                    except Exception as callback_error:
                                        print(f"[WARNING] Failed to send chunk via callback: {callback_error}")
                                        # If WebSocket is closed, we should stop processing
                                        if "Cannot call" in str(callback_error) or "close" in str(callback_error):
                                            print(f"[INFO] WebSocket closed, stopping stream for variant {index}")
                                            break
                                    
                                    # Log progress periodically
                                    if chunk_count % 100 == 0:
                                        print(f"[DEBUG] Progress - Chunks: {chunk_count}, Chars: {len(full_response_text)}")
                                        
                            except json.JSONDecodeError as e:
                                # Log JSON decode errors for debugging
                                if len(data_content) < 200:
                                    print(f"[DEBUG] JSON decode error: {e}, data: {data_content}")
                                pass
                            
                            # Clear processed line from buffer
                            buffer = ""
                            
                    except Exception as e:
                        print(f"[ERROR] Error processing stream chunk: {e}")
                        continue
                
                # Check if stream ended prematurely
                time_since_last_chunk = time.time() - last_chunk_time
                if time_since_last_chunk < 1.0 and len(full_response_text) < 1000:
                    print(f"[WARNING] Stream may have ended prematurely. Last chunk was {time_since_last_chunk:.2f}s ago")
                
                print(f"[DEBUG] Stream processing complete. Total response: {len(full_response_text)} chars")
                duration = time.time() - start_time
                return {"duration": duration, "code": full_response_text}

    except Exception as e:
        print(f"Error calling custom LLM API for variant {index}: {e}")
        traceback.print_exc()
        duration = time.time() - start_time
        error_message = f"Custom Model API Call Failed: {str(e)}"
        
        # Try to send the error as a content chunk via callback
        # But catch any WebSocket errors to avoid cascading failures
        try:
            await stream_callback(error_message, index)
        except Exception as callback_error:
            print(f"Failed to send error message via callback: {callback_error}")
            # If it's a WebSocket error, just log it
            if "Cannot call" in str(callback_error) or "close" in str(callback_error):
                print(f"[INFO] WebSocket already closed for variant {index}")
            
        return {"duration": duration, "code": error_message}
