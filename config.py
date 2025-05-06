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

# OpenAI API settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

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

# Color settings for token visualization
COLOR_HIGH_PROB = "#00cc00"  # Bright green
COLOR_MEDIUM_HIGH_PROB = "#66cc33"  # Light green
COLOR_MEDIUM_PROB = "#cccc00"  # Yellow
COLOR_MEDIUM_LOW_PROB = "#cc6600"  # Orange
COLOR_LOW_PROB = "#cc0000"  # Red
COLOR_UNKNOWN = "#808080"  # Gray
