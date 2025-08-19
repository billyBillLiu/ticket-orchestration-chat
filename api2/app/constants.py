"""
Application constants
"""

PROVIDERS = ["ollama", "openai"]

MODELS = {
    "ollama": ["deepseek-r1:8b", "llama3:8b"],
    "openai": ["gpt-5"]
}

ACTIVE_PROVIDER = PROVIDERS[0]  # Options: "ollama", "openai"
ACTIVE_MODEL = MODELS[ACTIVE_PROVIDER][1]  # Options: "deepseek-r1:8b", "llama3:8b", "gpt-4"

# API Constants
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1000
