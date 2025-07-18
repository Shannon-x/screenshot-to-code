# Useful for debugging purposes when you don't want to waste GPT4-Vision credits
# Setting to True will stream a mock response instead of calling the OpenAI API
# TODO: Should only be set to true when value is 'True', not any abitrary truthy value
import os

NUM_VARIANTS = 4

# LLM-related
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", None)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", None)

# Image generation (optional)
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY", None)

# Debugging-related

SHOULD_MOCK_AI_RESPONSE = bool(os.environ.get("MOCK", False))
IS_DEBUG_ENABLED = bool(os.environ.get("IS_DEBUG_ENABLED", False))
DEBUG_DIR = os.environ.get("DEBUG_DIR", "")

# Set to True when running in production (on the hosted version)
# Used as a feature flag to enable or disable certain features
IS_PROD = os.environ.get("IS_PROD", False)

# CORS settings - Security configuration
# In production, set ALLOWED_ORIGINS to specific domains
# Example: ALLOWED_ORIGINS=https://example.com,https://app.example.com
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000").split(",")

# If running in development mode, allow localhost origins
if not IS_PROD and os.environ.get("ALLOW_ALL_ORIGINS", "false").lower() == "true":
    ALLOWED_ORIGINS = ["*"]

# Encryption key for secure storage
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", None)
