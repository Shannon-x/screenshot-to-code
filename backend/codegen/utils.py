import re


def extract_html_content(text: str):
    # Use regex to find content within <html> tags and include the tags themselves
    # Updated regex to handle both <html> and <html ...> formats
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
            print("[HTML Extraction] HTML tags found but regex failed, returning full text")
            return text
        
        # Otherwise, we just send the previous HTML over
        print(
            "[HTML Extraction] No <html> tags found in the generated content: " + text[:200] + "..."
        )
        return text
