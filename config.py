"""
Configuration settings for the Token Probability Visualizer application.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Flask application settings
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-for-token-visualizer")
PORT = 5000

# OpenAI Service Type ('openai' or 'azure') - This is the service used at startup.
# User can switch in the UI.
STARTUP_SERVICE_TYPE = os.environ.get("STARTUP_SERVICE_TYPE", "openai").lower()

# OpenAI API settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Azure OpenAI API settings (used if STARTUP_SERVICE_TYPE is 'azure')
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_API_VERSION = os.environ.get("AZURE_API_VERSION", "")

# Default model settings
DEFAULT_MODEL = "gpt-3.5-turbo-instruct"
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 10
DEFAULT_LOGPROBS = 10

# Available models
AVAILABLE_MODELS = [
    "gpt-3.5-turbo-instruct",
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-3.5-turbo",
]

if STARTUP_SERVICE_TYPE == "azure":
    # Ensure required Azure variables are set if service type is Azure at startup
    if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_API_VERSION]):
        raise ValueError(
            "For Azure OpenAI, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, "
            "and AZURE_API_VERSION must be set in the environment."
        )

# Color settings for token visualization
COLOR_HIGH_PROB = "#00cc00"  # Bright green
COLOR_MEDIUM_HIGH_PROB = "#66cc33"  # Light green
COLOR_MEDIUM_PROB = "#cccc00"  # Yellow
COLOR_MEDIUM_LOW_PROB = "#cc6600"  # Orange
COLOR_LOW_PROB = "#cc0000"  # Red
COLOR_UNKNOWN = "#808080"  # Gray
