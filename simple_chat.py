"""
Simple Azure OpenAI Chat Application with Tool Calling
A straightforward chat interface that demonstrates Azure OpenAI API usage.
"""

import json
import math
import random
import time
import logging
from typing import Dict, Any, List
from openai import AzureOpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for debugging (can be enabled via environment variable)
if os.getenv("DEBUG_AZURE_OPENAI", "").lower() in ["true", "1", "yes"]:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("openai").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)


class SimpleChatApp:
    """Simple chat application with Azure OpenAI and tool calling."""
    
    def __init__(self):
        # Validate configuration first
        self._validate_config()
        
        # Initialize Azure OpenAI client with exact parameters from documentation
        # Handle SSL certificate issues in corporate environments
        import ssl
        import httpx
        
        # Check if SSL verification should be disabled (corporate environments)
        disable_ssl = os.getenv("DISABLE_SSL_VERIFY", "").lower() in ["true", "1", "yes"]
        
        if disable_ssl:
            print("⚠️  SSL verification disabled (corporate environment)")
            # Create custom HTTP client that doesn't verify SSL
            http_client = httpx.Client(verify=False)
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
                http_client=http_client
            )
        else:
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
            )
        
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.conversation = []
        
        # Set up available tools
        self.tools = self._setup_tools()
        self.available_functions = {
            "get_weather": self._get_weather,
            "calculate_math": self._calculate_math,
            "generate_random_number": self._generate_random_number
        }
    
    def _validate_config(self):
        """Validate required environment variables."""
        required = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
        missing = [var for var in required if not os.getenv(var)]
        
        if missing:
            print(f"❌ Missing environment variables: {', '.join(missing)}")
            print("Please create a .env file with your Azure OpenAI credentials.")
            exit(1)
        
        # Show configuration for debugging
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', '')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
        api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        
        print(f"📋 Configuration loaded:")
        print(f"   Endpoint: {endpoint}")
        print(f"   Deployment: {deployment}")
        print(f"   API Version: {api_version}")
        print(f"   API Key: {'***' + api_key[-4:] if len(api_key) > 4 else 'Too Short or Missing'}")
        
        # Validate endpoint format (should end with / or be in correct format)
        if endpoint and not endpoint.endswith('/'):
            print(f"   ⚠️  Endpoint should end with '/' - current: {endpoint}")
        
        # Validate endpoint contains openai.azure.com
        if endpoint and 'openai.azure.com' not in endpoint:
            print(f"   ⚠️  Endpoint should contain 'openai.azure.com' - current: {endpoint}")
        
        print()
    
    def _setup_tools(self):
        """Define available tools for the AI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city name, e.g. 'San Francisco'"
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_math",
                    "description": "Calculate mathematical expressions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Math expression to evaluate, e.g. '2 + 3 * 4'"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_random_number",
                    "description": "Generate a random number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "min_value": {"type": "integer", "description": "Minimum value"},
                            "max_value": {"type": "integer", "description": "Maximum value"}
                        },
                        "required": []
                    }
                }
            }
        ]
    
    def _get_weather(self, location: str) -> str:
        """Mock weather function."""
        weather_data = {
            "san francisco": "sunny, 22°C",
            "new york": "cloudy, 18°C", 
            "london": "rainy, 15°C",
            "tokyo": "partly cloudy, 25°C"
        }
        
        location_key = location.lower()
        if location_key in weather_data:
            return f"The weather in {location} is {weather_data[location_key]}"
        else:
            return f"Sorry, I don't have weather data for {location}"
    
    def _calculate_math(self, expression: str) -> str:
        """Safely calculate math expressions."""
        try:
            # Only allow safe mathematical operations
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"
    
    def _generate_random_number(self, min_value: int = 1, max_value: int = 100) -> str:
        """Generate a random number."""
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        
        number = random.randint(min_value, max_value)
        return f"Random number between {min_value} and {max_value}: {number}"
    
    def _log_api_call(self, messages: List[Dict], response=None, error_details: Dict = None, duration: float = None):
        """Enhanced API logging with actual HTTP response details."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Build the request details
        request_data = {
            "model": self.deployment_name,
            "messages": messages,
            "tools": self.tools,
            "max_completion_tokens": 500,
            "temperature": 1
        }
        
        # Note: The actual API client handles the full URL construction internally
        # This is just for logging purposes to show what endpoint would be called
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
        endpoint = f"{os.getenv('AZURE_OPENAI_ENDPOINT')}openai/deployments/{self.deployment_name}/chat/completions?api-version={api_version}"
        headers = {
            "api-key": "[REDACTED]",
            "Content-Type": "application/json"
        }
        
        log_entry = f"\n=== API REQUEST [{timestamp}] ===\n"
        log_entry += f"Endpoint: {endpoint}\n"
        log_entry += f"Method: POST\n"
        log_entry += f"Headers: {json.dumps(headers, indent=2)}\n"
        log_entry += f"Request Body: {json.dumps(request_data, indent=2)}\n"
        
        if response:
            # Successful response
            log_entry += f"\n=== API RESPONSE ===\n"
            log_entry += f"Status Code: 200\n"
            log_entry += f"Response Headers: {json.dumps({'content-type': 'application/json'}, indent=2)}\n"
            log_entry += f"Response Body: {json.dumps(response, indent=2)}\n"
            if duration:
                log_entry += f"Duration: {duration:.3f}s\n"
        
        elif error_details:
            # Error response with actual HTTP details
            log_entry += f"\n=== API ERROR RESPONSE ===\n"
            log_entry += f"Status Code: {error_details.get('status_code', 500)}\n"
            log_entry += f"Error Type: {error_details.get('error_type', 'Unknown')}\n"
            log_entry += f"Error Details: {json.dumps(error_details.get('error_body', {}), indent=2)}\n"
            if duration:
                log_entry += f"Duration: {duration:.3f}s\n"
        
        log_entry += "=" * 50 + "\n"
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        with open("logs/api_requests.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def _call_function(self, function_name: str, arguments: Dict) -> str:
        """Execute a function call."""
        if function_name in self.available_functions:
            try:
                return self.available_functions[function_name](**arguments)
            except Exception as e:
                return f"Error executing {function_name}: {str(e)}"
        else:
            return f"Function {function_name} not available"
    
    def chat(self, user_message: str) -> str:
        """Send a message and get response, handling tool calls."""
        # Add user message to conversation
        self.conversation.append({"role": "user", "content": user_message})
        
        # Track timing for logging
        start_time = time.time()
        
        try:
            # Make API call with tools
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=self.conversation,
                tools=self.tools,
                max_completion_tokens=500,
                temperature=1
            )
            
            duration = time.time() - start_time
            
            # Log successful API call with timing
            self._log_api_call(self.conversation, response.model_dump(), duration=duration)
            
            assistant_message = response.choices[0].message
            
            # Check if AI wants to call functions
            if assistant_message.tool_calls:
                print("🔧 AI is using tools...")
                
                # Add assistant message with tool calls to conversation
                self.conversation.append(assistant_message.model_dump())
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"📞 Calling: {function_name}({function_args})")
                    
                    # Execute function
                    function_result = self._call_function(function_name, function_args)
                    
                    # Add function result to conversation
                    self.conversation.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": function_result
                    })
                
                # Get final response after function calls
                start_time2 = time.time()
                response2 = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=self.conversation,
                    max_completion_tokens=500,
                    temperature=1
                )
                duration2 = time.time() - start_time2
                
                # Log the second API call
                self._log_api_call(self.conversation, response2.model_dump(), duration=duration2)
                
                final_message = response2.choices[0].message.content
                self.conversation.append({"role": "assistant", "content": final_message})
                return final_message
            
            else:
                # No function calls, just return the response
                content = assistant_message.content
                self.conversation.append({"role": "assistant", "content": content})
                return content
        
        except Exception as e:
            duration = time.time() - start_time
            
            # Extract detailed error information
            error_details = self._extract_error_details(e)
            
            # Log error with actual HTTP details
            self._log_api_call(self.conversation, error_details=error_details, duration=duration)
            
            error_msg = f"Error: {str(e)}"
            return error_msg
    
    def _extract_error_details(self, exception) -> Dict:
        """Extract detailed error information from API exceptions."""
        error_details = {
            "status_code": 500,
            "error_type": type(exception).__name__,
            "error_body": {"error": str(exception)}
        }
        
        if isinstance(exception, APIError):
            # Get actual HTTP status and response from OpenAI API error
            if hasattr(exception, 'response') and exception.response:
                error_details["status_code"] = exception.response.status_code
                if hasattr(exception.response, 'headers'):
                    error_details["response_headers"] = dict(exception.response.headers)
            
            if hasattr(exception, 'body') and exception.body:
                error_details["error_body"] = exception.body
            elif hasattr(exception, 'message'):
                error_details["error_body"] = {
                    "error": exception.message, 
                    "code": getattr(exception, 'code', None)
                }
            
            print(f"🔍 Azure OpenAI API Error: Status {error_details['status_code']}")
            print(f"   Details: {error_details['error_body']}")
            
        elif isinstance(exception, APIConnectionError):
            error_details["status_code"] = 503
            error_details["error_body"] = {"error": "Connection failed to Azure OpenAI", "details": str(exception)}
            print(f"🔌 Connection Error: Cannot reach Azure OpenAI service")
            
        elif isinstance(exception, RateLimitError):
            error_details["status_code"] = 429
            error_details["error_body"] = {"error": "Rate limit exceeded", "details": str(exception)}
            print(f"⏱️ Rate Limit: Too many requests to Azure OpenAI")
            
        elif isinstance(exception, APITimeoutError):
            error_details["status_code"] = 408
            error_details["error_body"] = {"error": "Request timeout", "details": str(exception)}
            print(f"⏰ Timeout: Request to Azure OpenAI timed out")
        
        else:
            # Check for SSL certificate errors
            error_str = str(exception).lower()
            if "certificate" in error_str or "ssl" in error_str:
                error_details["status_code"] = 502
                error_details["error_body"] = {"error": "SSL Certificate Error", "details": str(exception)}
                print(f"🔒 SSL Certificate Error (Corporate Network)")
                print(f"   💡 Try: export DISABLE_SSL_VERIFY=true")
                print(f"   💡 Or run: DISABLE_SSL_VERIFY=true python simple_chat.py")
                print(f"   ⚠️  This disables SSL verification (use only in corporate environments)")
        
        return error_details
    
    def _show_logs(self):
        """Display recent API logs."""
        log_file = "logs/api_requests.txt"
        
        if not os.path.exists(log_file):
            print("📝 No logs found yet. Make an API call first to generate logs.\n")
            return
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if not content.strip():
                print("📝 Log file is empty.\n")
                return
            
            print("📝 Recent API Logs:")
            print("=" * 50)
            
            # Show last 2000 characters to avoid overwhelming output
            if len(content) > 2000:
                print("(Showing last 2000 characters)")
                print("..." + content[-2000:])
            else:
                print(content)
                
            print("=" * 50)
            print()
            
        except Exception as e:
            print(f"❌ Error reading log file: {e}\n")
    
    def run(self):
        """Run the chat application."""
        print("🤖 Azure OpenAI Chat with Tool Calling")
        print("=" * 50)
        print("Available tools: weather, math calculator, random numbers")
        print("Type 'quit' to exit, 'clear' to reset conversation, 'logs' to view API logs\n")
        
        # Test connection with detailed logging
        print("🔍 Testing connection to Azure OpenAI...")
        print(f"   Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"   Deployment: {self.deployment_name}")
        print(f"   API Version: {os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')}")
        
        test_messages = [{"role": "user", "content": "Hi"}]
        start_time = time.time()
        
        try:
            test_response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=test_messages,
                max_completion_tokens=5,
                temperature=1
            )
            duration = time.time() - start_time
            
            # Log successful connection test
            self._log_api_call(test_messages, test_response.model_dump(), duration=duration)
            
            print("✅ Connected to Azure OpenAI successfully!")
            print(f"   Response: {test_response.choices[0].message.content}")
            print(f"   Tokens used: {test_response.usage.total_tokens}")
            print(f"   Response time: {duration:.3f}s")
            print(f"   Logs saved to: logs/api_requests.txt")
            print()
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Extract and log detailed error information
            error_details = self._extract_error_details(e)
            self._log_api_call(test_messages, error_details=error_details, duration=duration)
            
            print(f"❌ Connection failed! Error: {str(e)[:100]}...")
            print(f"   Duration: {duration:.3f}s")
            print(f"   Full error logged to: logs/api_requests.txt")
            
            # Provide specific troubleshooting based on error type
            if isinstance(e, APIConnectionError):
                print(f"\n🔌 Connection Error Detected:")
                print(f"   This suggests network, firewall, or endpoint issues")
                print(f"   Run: python diagnose.py for detailed network diagnostics")
            elif isinstance(e, APIError):
                error_str = str(e)
                if "401" in error_str or "Unauthorized" in error_str:
                    print(f"\n🔑 Authentication Error:")
                    print(f"   Your API key may be invalid or expired")
                elif "404" in error_str or "NotFound" in error_str:
                    print(f"\n📍 Resource Not Found:")
                    print(f"   Check deployment name: '{self.deployment_name}'")
                    print(f"   Verify model is deployed in Azure portal")
                elif "429" in error_str:
                    print(f"\n⏱️ Rate Limit Exceeded:")
                    print(f"   Wait a few minutes or check quota limits")
                else:
                    print(f"\n❓ API Error:")
                    print(f"   Check Azure portal for resource status")
            
            print(f"\n🔧 Quick fixes to try:")
            print(f"   1. Run: python diagnose.py (comprehensive diagnostics)")
            print(f"   2. Set DEBUG_AZURE_OPENAI=true for verbose logging")
            print(f"   3. Try API version: 2024-02-15-preview or 2023-12-01-preview")
            print(f"   4. Test from different network (mobile hotspot)")
            print(f"   5. Verify Azure OpenAI resource is active in portal")
            
            print(f"\n📚 Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/supported-languages")
            return
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation = []
                    print("🗑️ Conversation cleared\n")
                    continue
                
                if user_input.lower() == 'logs':
                    self._show_logs()
                    continue
                
                if not user_input:
                    continue
                
                print("🤔 Thinking...")
                response = self.chat(user_input)
                print(f"🤖 Assistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == "__main__":
    app = SimpleChatApp()
    app.run()
