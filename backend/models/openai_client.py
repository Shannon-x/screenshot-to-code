# Re-export from the new stream processor for backward compatibility
from models.openai_stream_processor import stream_openai_response

__all__ = ['stream_openai_response']