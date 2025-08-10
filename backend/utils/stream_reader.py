"""
Enhanced stream reading utilities for complete response handling
"""
import asyncio
import json
import time
from typing import AsyncIterator, Optional, Callable, Awaitable

class StreamReader:
    """Enhanced stream reader with buffering and error recovery"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.buffer = bytearray()
        self.last_activity = time.time()
        
    async def read_sse_stream(
        self, 
        response,
        callback: Callable[[str, int], Awaitable[None]],
        index: int = 0
    ) -> str:
        """Read Server-Sent Events stream with enhanced error handling"""
        full_text = ""
        chunk_count = 0
        incomplete_line = ""
        
        try:
            # Read stream with proper buffering
            async for chunk in response.content.iter_chunked(8192):  # 8KB chunks
                self.last_activity = time.time()
                
                # Decode chunk
                try:
                    text = chunk.decode('utf-8')
                except UnicodeDecodeError:
                    # Try with error handling
                    text = chunk.decode('utf-8', errors='ignore')
                
                # Handle incomplete lines
                lines = (incomplete_line + text).split('\n')
                incomplete_line = lines[-1]  # Last line might be incomplete
                
                # Process complete lines
                for line in lines[:-1]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            print(f"[DEBUG] Stream completed. Chunks: {chunk_count}, Length: {len(full_text)}")
                            return full_text
                        
                        try:
                            # Parse JSON data
                            json_data = json.loads(data)
                            content = self._extract_content(json_data)
                            
                            if content:
                                chunk_count += 1
                                full_text += content
                                
                                # Send via callback
                                try:
                                    await callback(content, index)
                                except Exception as e:
                                    print(f"[WARNING] Callback error: {e}")
                                    if "close" in str(e).lower():
                                        return full_text
                                
                                # Progress logging
                                if chunk_count % 50 == 0:
                                    print(f"[DEBUG] Progress: {chunk_count} chunks, {len(full_text)} chars")
                                    
                        except json.JSONDecodeError as e:
                            if len(data) < 100:
                                print(f"[DEBUG] JSON error: {e}, data: {data}")
                
                # Check timeout
                if time.time() - self.last_activity > self.timeout:
                    print(f"[WARNING] Stream timeout after {self.timeout}s")
                    break
            
            # Process any remaining incomplete line
            if incomplete_line.strip():
                print(f"[DEBUG] Processing incomplete line: {incomplete_line[:100]}...")
                # Try to process it
                if incomplete_line.startswith("data: "):
                    try:
                        data = incomplete_line[6:]
                        json_data = json.loads(data)
                        content = self._extract_content(json_data)
                        if content:
                            full_text += content
                            await callback(content, index)
                    except:
                        pass
            
            print(f"[DEBUG] Final response length: {len(full_text)} chars")
            return full_text
            
        except Exception as e:
            print(f"[ERROR] Stream reading error: {e}")
            return full_text
    
    def _extract_content(self, json_data: dict) -> str:
        """Extract content from various API response formats"""
        # OpenAI format
        if "choices" in json_data:
            choices = json_data.get("choices", [])
            if choices and isinstance(choices, list):
                delta = choices[0].get("delta", {})
                return delta.get("content", "")
        
        # Anthropic format
        if json_data.get("type") == "content_block_delta":
            delta = json_data.get("delta", {})
            if delta.get("type") == "text_delta":
                return delta.get("text", "")
        
        # Generic formats
        if "delta" in json_data:
            delta = json_data["delta"]
            if isinstance(delta, dict):
                return delta.get("text", "") or delta.get("content", "")
            elif isinstance(delta, str):
                return delta
        
        if "text" in json_data:
            return json_data["text"]
        
        if "content" in json_data:
            return json_data["content"]
        
        return ""


async def read_complete_stream(
    response,
    callback: Callable[[str, int], Awaitable[None]],
    index: int = 0,
    timeout: int = 300
) -> str:
    """
    Read a complete stream with retry and error recovery
    """
    reader = StreamReader(timeout=timeout)
    return await reader.read_sse_stream(response, callback, index)