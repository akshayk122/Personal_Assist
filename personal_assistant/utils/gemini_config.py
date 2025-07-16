"""
Gemini AI Model Configuration
Following the pattern from the existing ACP demo setup
"""

import os
from crewai import LLM
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def setup_gemini_config() -> tuple[LLM, Dict[str, Any]]:
    """
    Setup Gemini configuration following the existing pattern
    Returns both LLM instance and config dict for RAG tools
    """
    
    # Ensure API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Model configuration
    model_name = os.getenv("MODEL_NAME", "gemini/gemini-2.0-flash")
    max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
    
    # Create LLM instance following the pattern
    llm = LLM(model=model_name, max_tokens=max_tokens)
    
    # Config dictionary for RAG tools (following the pattern)
    config = {
        "llm": {
            "provider": "google",
            "config": {
                "model": model_name,
            }
        },
        "embedding_model": {
            "provider": "google",
            "config": {
                "model": "models/embedding-001"
            }
        }
    }
    
    return llm, config

def get_llm() -> LLM:
    """Get configured LLM instance"""
    llm, _ = setup_gemini_config()
    return llm

def get_config() -> Dict[str, Any]:
    """Get configuration dictionary for RAG tools"""
    _, config = setup_gemini_config()
    return config 