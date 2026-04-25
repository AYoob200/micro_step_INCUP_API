"""
Configuration module for Dopamine Coach with Gemini API.
Uses official Google GenAI SDK.
"""

import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigGemini:
    """Configuration for Gemini API provider."""

    # API Configuration for Gemini
    API_PROVIDER = "gemini"
    MODEL_ID = "gemini-2.5-flash"
    API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")

    # Agent Configuration
    TEMPERATURE = 0.7
    MAX_TOKENS = 5000
    TIMEOUT = 30

    # Task Decomposition Rules
    MIN_LAUNCH_TASK_MINUTES = 5
    MAX_LAUNCH_TASK_MINUTES = 10
    MIN_FLOW_MINUTES = 10
    MAX_FLOW_MINUTES = 25

    # System Behavior
    ENABLE_JSON_VALIDATION = True
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"


class ModelProviderGemini:
    """Factory class for Gemini API provider management."""

    @staticmethod
    def get_api_key() -> str:
        """Get Gemini API key from config or environment."""
        api_key = ConfigGemini.API_KEY
        if api_key == "your_gemini_api_key_here":
            raise ValueError(
                "Gemini API key not set. Set GEMINI_API_KEY environment variable or update config.py"
            )
        return api_key

    @staticmethod
    def validate_provider() -> bool:
        """Validate that the Gemini API provider is properly configured."""
        try:
            api_key = ModelProviderGemini.get_api_key()
            return api_key is not None and len(api_key) > 0
        except ValueError:
            raise ValueError(
                "Gemini API provider validation failed. Please set GEMINI_API_KEY."
            )


# Backwards compatibility
Config = ConfigGemini
ModelProvider = ModelProviderGemini
