import re


def extract_html_content(text: str):
    # First, remove code block markers if present
    if text.strip().startswith("```html") and text.strip().endswith("```"):
        # Remove ```html from start and ``` from end
        text = text.strip()[7:-3].strip()
        print("[HTML Extraction] Removed code block markers")
    elif text.strip().startswith("```") and text.strip().endswith("```"):
        # Remove generic code blocks
        text = text.strip()[3:-3].strip()
        print("[HTML Extraction] Removed generic code block markers")
    
    # Use regex to find content within <html> tags and include the tags themselves
    # Updated regex to handle both <html> and <html ...> formats
    # First try to find complete HTML document
    match = re.search(r"(<html[^>]*>.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    else:
        # Try alternative patterns
        # Look for just the opening <html> tag without attributes
        match = re.search(r"(<html>.*?</html>)", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
        
        # If still no match, check if the text actually contains html tags
        if "<html" in text.lower() and "</html>" in text.lower():
            # Extract everything between first <html and last </html>
            start_idx = text.lower().find("<html")
            end_idx = text.lower().rfind("</html>") + 7  # Include the closing tag
            if start_idx >= 0 and end_idx > start_idx:
                extracted = text[start_idx:end_idx]
                print(f"[HTML Extraction] Extracted HTML using fallback method: {len(extracted)} chars")
                return extracted
            else:
                print("[HTML Extraction] HTML tags found but extraction failed, returning full text")
                return text
        
        # Check if it's a partial HTML that got cut off
        if "<html" in text.lower() and "</html>" not in text.lower():
            print("[HTML Extraction] Incomplete HTML detected (missing closing tag)")
            # Try to add closing tags
            html_with_closing = text
            if "</body>" not in text.lower():
                html_with_closing += "\n</body>"
            if "</html>" not in text.lower():
                html_with_closing += "\n</html>"
            return html_with_closing
        
        # If DOCTYPE is present but no html tags, it's likely complete HTML
        if "<!DOCTYPE html>" in text or "<!doctype html>" in text.lower():
            print("[HTML Extraction] Found DOCTYPE, assuming complete HTML document")
            return text
        
        # Otherwise, we just send the previous HTML over
        print(
            "[HTML Extraction] No <html> tags found in the generated content: " + text[:200] + "..."
        )
        return text
