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
    model_name = "gemini-2.0-flash"  # Using flash model for faster responses
    max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Create LLM instance following the pattern
    llm = LLM(
        model=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        api_base="https://generativelanguage.googleapis.com/v1beta",  # Using v1beta for flash model
        api_version="v1beta"
    )
    
    # Config dictionary for RAG tools
    config = {
        "llm": {
            "provider": "google",
            "config": {
                "model": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "api_base": "https://generativelanguage.googleapis.com/v1beta",
                "api_version": "v1beta"
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
