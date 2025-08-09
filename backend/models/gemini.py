import base64
import time
from typing import Awaitable, Callable, Dict, List
from openai.types.chat import ChatCompletionMessageParam
from google import genai
from google.genai import types
from llm import Completion, Llm

# Re-export from the new stream processor for backward compatibility
from models.gemini_stream_processor import stream_gemini_response


def extract_image_from_messages(
    messages: List[ChatCompletionMessageParam],
) -> Dict[str, str]:
    """
    Extracts image data from OpenAI-style chat completion messages.

    Args:
        messages: List of ChatCompletionMessageParam containing message content

    Returns:
        Dictionary with mime_type and data keys for the first image found
    """
    for content_part in messages[-1]["content"]:  # type: ignore
        if content_part["type"] == "image_url":  # type: ignore
            image_url = content_part["image_url"]["url"]  # type: ignore
            if image_url.startswith("data:"):  # type: ignore
                # Extract base64 data and mime type for data URLs
                mime_type = image_url.split(";")[0].split(":")[1]  # type: ignore
                base64_data = image_url.split(",")[1]  # type: ignore
                return {"mime_type": mime_type, "data": base64_data}
            else:
                # Handle regular URLs - would need to download and convert to base64
                # For now, just return the URI
                return {"uri": image_url}  # type: ignore

    # No image found
    raise ValueError("No image found in messages")


# Original stream_gemini_response has been moved to gemini_stream_processor.py
# The function is now imported at the top of this file for backward compatibility
