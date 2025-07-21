import os
from crewai import LLM
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def setup_gemini_config() -> tuple[LLM, Dict[str, Any]]:
    """
    Setup Gemini configuration correctly for CrewAI.
    Returns both LLM instance and config dict for RAG tools
    """
    
    # Ensure API key is set
    # Note: CrewAI/LiteLLM often prefers the GEMINI_API_KEY variable
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
    
    # Model configuration
    # The 'gemini/' prefix tells CrewAI which provider to use. This is crucial.
    model_name = "gemini/gemini-2.0-flash"
    
    # Create LLM instance using the correct pattern for CrewAI
    llm = LLM(
        model=model_name,
        api_key=api_key
    )
    
    # Your config dictionary for RAG tools looks fine conceptually
    config = {
        "llm": {
            "provider": "google",
            "config": {
                "model": model_name,
                "api_key": api_key,
                "temperature": float(os.getenv("TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("MAX_TOKENS", "1024"))
            }
        },
        "embedding_model": {
            "provider": "google",
            "config": {
                "model": "models/embedding-001",
                "api_key": api_key
            }
        }
    }
    
    return llm, config

# The rest of your code remains the same
def get_llm() -> LLM:
    """Get configured LLM instance"""
    llm, _ = setup_gemini_config()
    return llm

def get_config() -> Dict[str, Any]:
    """Get configuration dictionary for RAG tools"""
    _, config = setup_gemini_config()
    return config