#!/usr/bin/env python3
"""
Test URL validation for custom models
"""
import sys
sys.path.insert(0, '/opt/screenshot-to-code/backend')

from utils.url_validation import smart_validate_url

test_urls = [
    "https://api.127.pp.ua/v1",
    "https://api.127.pp.ua/v1/chat/completions",
    "api.example.com/v1",
    "localhost:8000",
    "http://localhost:11434/api",
    "https://api.openai.com/v1",
    "api.anthropic.com/v1/messages",
]

print("Testing URL validation:")
print("-" * 50)

for url in test_urls:
    try:
        result = smart_validate_url(url)
        print(f"Input:  {url}")
        print(f"Output: {result}")
        print()
    except Exception as e:
        print(f"Input:  {url}")
        print(f"Error:  {e}")
        print()

print("-" * 50)