"""
Logging Integration Helper - Convert print statements to async logging
"""
from logging import get_logger

logger = get_logger(__name__)

# Helper functions for common logging patterns
async def log_info(message: str):
    """Log info message"""
    await logger.info(message)

async def log_error(message: str):
    """Log error message"""
    await logger.error(message)

async def log_warning(message: str):
    """Log warning message"""
    await logger.warning(message)

async def log_debug(message: str):
    """Log debug message"""
    await logger.debug(message)

# Example usage for converting print statements:
# Before: print(f"Using {key} from client-side settings dialog")
# After: await log_info(f"Using {key} from client-side settings dialog")

# For synchronous code that can't use await, use the standard logger directly:
# logger._fallback_logger.info("message")