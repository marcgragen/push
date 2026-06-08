"""
Settings and Environment Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment"""
    
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Default corporate policies
    DEFAULT_CORPORATE_POLICIES = (
        "1. Every DB must be in an isolated subnet. "
        "2. Mandatory use of WAF for external traffic."
    )
    
    # Session configuration
    THREAD_ID = "threat_modeling_session_01"
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        if not cls.TAVILY_API_KEY:
            print("[WARNING] TAVILY_API_KEY not configured. The agent will not have internet access.")


# Validate on import
Settings.validate()
