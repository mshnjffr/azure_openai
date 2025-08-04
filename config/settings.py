"""
Configuration management for Azure OpenAI tutorial application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AzureOpenAIConfig:
    """Configuration class for Azure OpenAI settings."""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.chat_deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", self.deployment_name)
        
        # Validate required settings
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present."""
        required_fields = {
            "AZURE_OPENAI_API_KEY": self.api_key,
            "AZURE_OPENAI_ENDPOINT": self.endpoint,
            "AZURE_OPENAI_DEPLOYMENT_NAME": self.deployment_name
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        
        if missing_fields:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_fields)}\n"
                f"Please create a .env file based on .env.example and set these values."
            )
    
    def get_client_config(self):
        """Get configuration dictionary for Azure OpenAI client."""
        return {
            "api_key": self.api_key,
            "azure_endpoint": self.endpoint,
            "api_version": self.api_version
        }
    
    def __repr__(self):
        return (
            f"AzureOpenAIConfig("
            f"endpoint='{self.endpoint}', "
            f"api_version='{self.api_version}', "
            f"deployment='{self.deployment_name}'"
            f")"
        )


# Create global config instance
config = AzureOpenAIConfig()
