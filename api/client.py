"""
Azure OpenAI client wrapper with logging capabilities.
"""

import time
import json
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
from config.settings import config
from api.logger import api_logger


class AzureOpenAIClient:
    """Wrapper around Azure OpenAI client with built-in logging."""
    
    def __init__(self, enable_logging: bool = True):
        self.client = AzureOpenAI(**config.get_client_config())
        self.enable_logging = enable_logging
        self.deployment_name = config.deployment_name
        self.chat_deployment_name = config.chat_deployment_name
    
    def create_completion(self, 
                         prompt: str, 
                         max_tokens: int = 100, 
                         temperature: float = 0.7,
                         top_p: float = 1.0,
                         **kwargs) -> Dict[str, Any]:
        """
        Create a text completion using the legacy completions API.
        
        Args:
            prompt: The text prompt to complete
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 2.0)
            top_p: Controls nucleus sampling (0.0 to 1.0)
            **kwargs: Additional parameters for the API call
        
        Returns:
            API response as dictionary
        """
        # Prepare request
        request_data = {
            "model": self.deployment_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            **kwargs
        }
        
        endpoint = f"{config.endpoint}openai/deployments/{self.deployment_name}/completions"
        headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json"
        }
        
        # Log request if enabled
        if self.enable_logging:
            api_logger.log_request(
                endpoint=endpoint,
                method="POST",
                headers=headers,
                request_body=request_data
            )
        
        # Make API call
        start_time = time.time()
        
        try:
            response = self.client.completions.create(**request_data)
            duration = time.time() - start_time
            
            # Convert response to dict for logging
            response_dict = response.model_dump()
            
            # Log response if enabled
            if self.enable_logging:
                api_logger.log_request(
                    endpoint=endpoint,
                    method="POST",
                    headers=headers,
                    request_body=request_data,
                    response_status=200,
                    response_headers={"content-type": "application/json"},
                    response_body=response_dict,
                    duration=duration
                )
            
            return response_dict
            
        except Exception as e:
            duration = time.time() - start_time
            error_response = {"error": str(e), "type": type(e).__name__}
            
            # Log error if enabled
            if self.enable_logging:
                api_logger.log_request(
                    endpoint=endpoint,
                    method="POST",
                    headers=headers,
                    request_body=request_data,
                    response_status=500,
                    response_headers={},
                    response_body=error_response,
                    duration=duration
                )
            
            raise
    
    def create_chat_completion(self,
                              messages: List[Dict[str, str]],
                              max_tokens: int = 100,
                              temperature: float = 0.7,
                              tools: Optional[List[Dict]] = None,
                              tool_choice: Optional[str] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        Create a chat completion using the chat completions API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 2.0)
            tools: List of tool/function definitions for function calling
            tool_choice: Controls which functions can be called ('auto', 'none', or specific function)
            **kwargs: Additional parameters for the API call
        
        Returns:
            API response as dictionary
        """
        # Prepare request
        request_data = {
            "model": self.chat_deployment_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Add tools if provided
        if tools:
            request_data["tools"] = tools
        
        # Add tool_choice if provided
        if tool_choice:
            request_data["tool_choice"] = tool_choice
        
        endpoint = f"{config.endpoint}openai/deployments/{self.chat_deployment_name}/chat/completions"
        headers = {
            "api-key": config.api_key,
            "Content-Type": "application/json"
        }
        
        # Log request if enabled
        if self.enable_logging:
            api_logger.log_request(
                endpoint=endpoint,
                method="POST",
                headers=headers,
                request_body=request_data
            )
        
        # Make API call
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(**request_data)
            duration = time.time() - start_time
            
            # Convert response to dict for logging
            response_dict = response.model_dump()
            
            # Log response if enabled
            if self.enable_logging:
                api_logger.log_request(
                    endpoint=endpoint,
                    method="POST",
                    headers=headers,
                    request_body=request_data,
                    response_status=200,
                    response_headers={"content-type": "application/json"},
                    response_body=response_dict,
                    duration=duration
                )
            
            return response_dict
            
        except Exception as e:
            duration = time.time() - start_time
            error_response = {"error": str(e), "type": type(e).__name__}
            
            # Log error if enabled
            if self.enable_logging:
                api_logger.log_request(
                    endpoint=endpoint,
                    method="POST",
                    headers=headers,
                    request_body=request_data,
                    response_status=500,
                    response_headers={},
                    response_body=error_response,
                    duration=duration
                )
            
            raise
    
    def test_connection(self) -> bool:
        """
        Test the connection to Azure OpenAI service.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Make a simple chat completion request
            response = self.create_chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
                temperature=0
            )
            print("✅ Connection to Azure OpenAI successful!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False


# Global client instance
azure_client = AzureOpenAIClient()
