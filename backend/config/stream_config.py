"""
Stream processing configuration and utilities
"""

# Stream processing configuration
STREAM_CONFIG = {
    # Buffer sizes
    "read_chunk_size": 16384,  # 16KB chunks for better performance
    "max_buffer_size": 1048576,  # 1MB max buffer
    
    # Timeouts
    "chunk_timeout": 30,  # Max time between chunks
    "total_timeout": 600,  # 10 minutes total timeout
    
    # Retry settings
    "max_retries": 3,
    "retry_delay": 1.0,
    
    # Validation
    "min_response_length": 500,  # Minimum expected response length
    "html_validation": True,
}

def validate_html_completeness(content: str) -> dict:
    """Validate if HTML content is complete"""
    content_lower = content.lower()
    
    # Check for HTML structure
    has_doctype = "<!doctype" in content_lower
    has_html_open = "<html" in content_lower
    has_html_close = "</html>" in content_lower
    has_head = "<head" in content_lower
    has_body_open = "<body" in content_lower
    has_body_close = "</body>" in content_lower
    
    # Calculate completeness score
    score = 0
    if has_doctype: score += 1
    if has_html_open: score += 2
    if has_html_close: score += 3  # Most important
    if has_head: score += 1
    if has_body_open: score += 1
    if has_body_close: score += 2
    
    is_complete = has_html_close and has_body_close
    
    return {
        "is_complete": is_complete,
        "score": score,
        "has_doctype": has_doctype,
        "has_html_tags": has_html_open and has_html_close,
        "has_body_tags": has_body_open and has_body_close,
        "length": len(content),
        "likely_truncated": len(content) > 100 and not is_complete
    }

async def ensure_complete_response(
    response_text: str,
    callback: callable,
    index: int,
    attempt: int = 1
) -> str:
    """Ensure response is complete, attempt recovery if needed"""
    
    validation = validate_html_completeness(response_text)
    
    if validation["is_complete"]:
        print(f"[DEBUG] Response validated as complete: {validation}")
        return response_text
    
    if validation["likely_truncated"] and attempt < 3:
        print(f"[WARNING] Response appears truncated: {validation}")
        
        # Try to complete the response
        completion_prompt = "\n<!-- Response was truncated. Please continue from where you left off and complete the HTML document. -->"
        
        try:
            await callback(completion_prompt, index)
        except:
            pass
        
        # Add common closing tags if missing
        if not validation["has_body_tags"] and "<body" in response_text.lower():
            response_text += "\n</body>"
        
        if not validation["has_html_tags"] and "<html" in response_text.lower():
            response_text += "\n</html>"
        
        print(f"[DEBUG] Attempted to complete truncated response")
    
    return response_text