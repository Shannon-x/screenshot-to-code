import json
import time
import traceback
from typing import Any, Callable, Coroutine, List, Awaitable

import aiohttp
from openai.types.chat import ChatCompletionMessageParam

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
    Calls a custom Language Model API.

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

    try:
        # Convert messages to a generic format, attempt to handle multimodal content placeholder
        formatted_messages = []
        for msg in prompt_messages:
            if msg["role"] == "user" and isinstance(msg["content"], list):
                text_parts = []
                image_parts_count = 0
                for content_part in msg["content"]:
                    if content_part["type"] == "text":
                        text_parts.append(content_part["text"])
                    elif content_part["type"] == "image_url":
                        # Actual image data handling would require knowing the custom API's spec
                        # For now, just count them as a placeholder.
                        image_parts_count += 1

                combined_text = "\n".join(text_parts)
                if image_parts_count > 0:
                    combined_text += f"\n\n[Image data for {image_parts_count} image(s) would be processed here if custom API supports it. This is a placeholder.]"

                formatted_messages.append({"role": "user", "content": combined_text})
            else:
                # Ensure content is string
                content_str = msg["content"] if isinstance(msg["content"], str) else str(msg["content"])
                formatted_messages.append({"role": msg["role"], "content": content_str})

        headers = {"Content-Type": "application/json"}
        
        # Handle Anthropic API specific authentication and format
        if "anthropic" in service_url.lower():
            print(f"[DEBUG] Detected Anthropic API endpoint: {service_url}")
            if api_key:
                headers["x-api-key"] = api_key  # Anthropic uses x-api-key header
                headers["anthropic-version"] = "2023-06-01"  # Required version header
                print(f"[DEBUG] Using Anthropic API key (ends with: ...{api_key[-4:] if len(api_key) > 4 else 'short'})")
            else:
                print("Warning: No API key provided for Anthropic API")
            
            # Anthropic API format
            system_prompts = [m["content"] for m in formatted_messages if m["role"] == "system"]
            user_messages = [m for m in formatted_messages if m["role"] != "system"]
            
            request_data: dict[str, Any] = {
                "model": model_id,
                "messages": user_messages,
                "max_tokens": 4000,
                "temperature": 0.1,
                "stream": True
            }
            
            if system_prompts:
                request_data["system"] = "\n".join(system_prompts)
                
            print(f"[DEBUG] Anthropic request data: {json.dumps(request_data, indent=2)}")
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
                "max_tokens": 4000
            }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                service_url,
                headers=headers,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=180)  # Increased timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"Custom model API request failed with status {response.status}: {error_text}"
                    )

                full_response_text = ""
                # Process streaming response (Server-Sent Events like format)
                async for line_bytes in response.content:
                    line = line_bytes.decode("utf-8").strip()
                    if not line:
                        continue

                    if line.startswith("data: "):
                        data_content = line[len("data: "):]
                        if data_content == "[DONE]":
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
                                full_response_text += content_chunk
                                await stream_callback(content_chunk, index)
                        except json.JSONDecodeError:
                            # print(f"Warning: Could not decode JSON from chunk: {data_content}")
                            pass # Ignore non-JSON data lines if any

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
            
        return {"duration": duration, "code": error_message}
