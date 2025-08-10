"""
Model capability detection and message formatting
"""

def detect_multimodal_support(messages) -> bool:
    """
    Detect if the API actually supports multimodal by checking the first response
    This is a heuristic - if we get an error about message format, we know it doesn't support it
    """
    # Check if any message has multimodal content
    for msg in messages:
        if isinstance(msg.get("content"), list):
            return True  # Has multimodal content, let's try it
    return False

def format_messages_with_fallback(messages, force_string_content: bool = False):
    """
    Format messages with automatic fallback to string content
    
    Args:
        messages: Original messages
        force_string_content: If True, always convert to string (for known incompatible APIs)
    
    Returns:
        formatted_messages, has_multimodal_content
    """
    formatted = []
    has_multimodal = False
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        # Handle list content (multimodal)
        if isinstance(content, list):
            has_multimodal = True
            
            if force_string_content:
                # Convert to string
                text_parts = []
                has_image = False
                
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            has_image = True
                
                combined_text = " ".join(text_parts).strip()
                if has_image and not combined_text:
                    # No text content, just image
                    combined_text = "Please analyze the provided image and generate appropriate HTML/CSS code based on what you see."
                elif has_image:
                    # Add note about image
                    combined_text += "\n\n[Image provided - please generate code based on the visual content]"
                
                formatted.append({"role": role, "content": combined_text})
            else:
                # Keep as list for APIs that might support it
                formatted.append({"role": role, "content": content})
        else:
            # String content - ensure it's actually a string
            formatted.append({"role": role, "content": str(content)})
    
    return formatted, has_multimodal

def should_force_string_content(error_message: str) -> bool:
    """
    Check if an error indicates we should retry with string content
    """
    if not error_message:
        return False
    
    error_lower = error_message.lower()
    
    # Common error patterns that indicate multimodal is not supported
    indicators = [
        "must be a string",
        "content must be string",
        "invalid content type",
        "expected string",
        "type.*string",
        "not.*string",
        "content.*string"
    ]
    
    return any(indicator in error_lower for indicator in indicators)