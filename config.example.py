"""
Configuration Example for Ollama Intelligent Router
====================================================

Copy this to the MODELS section in router.py and customize for your setup.
"""

# Example 1: Standard Setup (Recommended)
# Works with most common Ollama models
MODELS = {
    "fast": "qwen2.5:3b",           # Quick responses
    "reasoning": "deepseek-r1:7b",   # Deep thinking
    "coding": "qwen2.5-coder:7b",    # Programming
    "vision": "llava:7b",            # Images
    "general": "qwen2.5:7b"          # Default
}

# Example 2: Llama-Only Setup
# If you prefer Meta's Llama models
MODELS = {
    "fast": "llama3.2:3b",
    "reasoning": "llama3.1:8b",
    "coding": "codellama:7b",
    "vision": "llava:7b",
    "general": "llama3.1:8b"
}

# Example 3: High-Performance Setup
# For systems with 32GB+ RAM
MODELS = {
    "fast": "qwen2.5:3b",
    "reasoning": "deepseek-r1:14b",  # Larger reasoning model
    "coding": "qwen2.5-coder:14b",   # Larger coding model
    "vision": "llava:13b",           # Larger vision model
    "general": "qwen2.5:14b"         # Larger general model
}

# Example 4: Minimalist Setup
# Use one model for everything (save RAM)
MODELS = {
    "fast": "qwen2.5:7b",
    "reasoning": "qwen2.5:7b",
    "coding": "qwen2.5:7b",
    "vision": "llava:7b",            # Keep vision separate
    "general": "qwen2.5:7b"
}

# Example 5: Speed-Optimized Setup
# Prioritize fast responses
MODELS = {
    "fast": "qwen2.5:3b",
    "reasoning": "qwen2.5:3b",       # Use fast model even for reasoning
    "coding": "qwen2.5-coder:3b",    # Fast coding model (if available)
    "vision": "llava:7b",
    "general": "qwen2.5:3b"          # Fast by default
}

# Example 6: Quality-Optimized Setup
# Prioritize response quality
MODELS = {
    "fast": "qwen2.5:7b",            # Use better model even for fast queries
    "reasoning": "deepseek-r1:14b",
    "coding": "qwen2.5-coder:14b",
    "vision": "llava:13b",
    "general": "qwen2.5:14b"
}

# Example 7: Mixed Setup (Balanced)
# Balance between speed and quality
MODELS = {
    "fast": "qwen2.5:1.5b",          # Smallest for speed
    "reasoning": "deepseek-r1:7b",   # Good reasoning
    "coding": "qwen2.5-coder:7b",    # Good coding
    "vision": "llava:7b",
    "general": "qwen2.5:7b"          # Good default
}

# Example 8: Specialized Domain Setup
# For specific use cases
MODELS = {
    "fast": "phi3:3.8b",             # Microsoft's fast model
    "reasoning": "deepseek-r1:7b",   # Math/logic
    "coding": "codestral:22b",       # Mistral's coding model
    "vision": "llava:13b",
    "general": "mistral:7b"          # Mistral's general model
}
