import os
from crewai import LLM
from dotenv import load_dotenv
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=".env", override=True)

def setup_gemini_config() -> tuple[LLM, Dict[str, Any]]:
    """
    Setup Gemini configuration correctly for CrewAI.
    Returns both LLM instance and config dict for RAG tools
    """
    
    # Ensure API key is set
    # Note: CrewAI/LiteLLM often prefers the GEMINI_API_KEY variable
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("API Key Missing")
        logger.error("Please set either GEMINI_API_KEY or GOOGLE_API_KEY in your .env file")
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
    
    if api_key == "API_KEY" or api_key == "your_actual_api_key_here":
        logger.error("Invalid API Key")
        logger.error("Please replace the placeholder API key with your actual Google AI API key")
        raise ValueError("Invalid API key - please use your actual Google AI API key")
    
    logger.info(f"✓ API Key found: {api_key[:10]}...")
    
    # Model configuration
    # The 'gemini/' prefix tells CrewAI which provider to use. This is crucial.
    model_name = "gemini/gemini-2.0-flash"
    logger.info(f"✓ Using model: {model_name}")
    
    try:
        # Create LLM instance using the correct pattern for CrewAI
        llm = LLM(
            model=model_name,
            api_key=api_key,
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "1024"))
        )
        logger.info("✓ LLM instance created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create LLM instance: {str(e)}")
        raise
    
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
    
    logger.info("✓ Configuration setup completed")
    return llm, config

# The rest of your code remains the same
def get_llm() -> LLM:
    """Get configured LLM instance"""
    try:
        llm, _ = setup_gemini_config()
        return llm
    except Exception as e:
        logger.error(f"Failed to get LLM: {str(e)}")
        raise

def get_config() -> Dict[str, Any]:
    """Get configuration dictionary for RAG tools"""
    try:
        _, config = setup_gemini_config()
        return config
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        raise