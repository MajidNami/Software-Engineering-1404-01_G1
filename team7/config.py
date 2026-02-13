"""
Team 7 Configuration Module
Handles AI service settings for TOEFL evaluation (Writing & Speaking)
"""
import os
import environ
from pathlib import Path

# Initialize environ
env = environ.Env()

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / ".env")

# ==================== AI Generator Settings (for Writing & LLM) ====================
# OpenAI-compatible API for LLM services (Writing evaluation, Speaking scoring)
AI_GENERATOR_API_KEY = "g4a-1rcT4Qz2aq7XJT_qGXaoPavi8YyDzpuYfzHPzmEa8so"
AI_GENERATOR_BASE_URL = "https://api.gpt4-all.xyz/v1"
AI_GENERATOR_MODEL = "gpt-4o-mini"

# ==================== Soniox STT Settings (for Speaking ASR) ====================
# Soniox Speech-to-Text API for audio transcription
SONIOX_API_KEY = env("SONIOX_API_KEY", default="")
SONIOX_API_BASE_URL = env("SONIOX_API_BASE_URL", default="https://api.soniox.com")
SONIOX_MODEL = env("SONIOX_MODEL", default="stt-async-v4")

# ==================== Validation ====================
def validate_config():
    """Validate that required API keys are set."""
    missing = []
    
    if not AI_GENERATOR_API_KEY:
        missing.append("AI_GENERATOR_API_KEY (required for Writing & Speaking evaluation)")
    
    if not SONIOX_API_KEY:
        missing.append("SONIOX_API_KEY (required for Speaking transcription)")
    
    if missing:
        return False, missing
    
    return True, []

def get_ai_generator_config():
    """Get AI Generator configuration for LLM services."""
    return {
        "api_key": AI_GENERATOR_API_KEY,
        "base_url": AI_GENERATOR_BASE_URL,
        "model": AI_GENERATOR_MODEL,
    }

def get_soniox_config():
    """Get Soniox configuration for STT services."""
    return {
        "api_key": SONIOX_API_KEY,
        "base_url": SONIOX_API_BASE_URL,
        "model": SONIOX_MODEL,
    }
