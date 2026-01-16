"""
Optimus Autonomous - Constants and default values
by itsJWill (BillyCoder)
"""

# Default LLM settings
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Execution settings
DEFAULT_MAX_ITERATIONS = 100
DEFAULT_TIMEOUT_MS = 30000

# Preview/truncation lengths
RESULT_PREVIEW_LENGTH = 500
RESULT_SHORT_PREVIEW_LENGTH = 100

# Cost per 1M tokens (approximate)
COST_RATES = {
    "anthropic": {"input": 3.0, "output": 15.0},  # Claude 3.5 Sonnet
    "openai": {"input": 2.5, "output": 10.0},     # GPT-4 Turbo
}

# Version
VERSION = "0.1.0"
