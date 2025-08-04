"""
Function calling example using Azure OpenAI.
This example demonstrates how to use function calling (tool calling) with the chat completions API.
"""

import json
import math
import random
from typing import Dict, Any, List
from api.client import azure_client


# Example functions that can be called by the AI
def get_weather(location: str, unit: str = "celsius") -> str:
    """
    Get the current weather for a location.
    
    Args:
        location: The city and state/country, e.g. 'San Francisco, CA'
        unit: Temperature unit - 'celsius' or 'fahrenheit'
    
    Returns:
        Weather information as a string
    """
    # Mock weather data for demonstration
    weather_data = {
        "san francisco": {"temp": 22, "condition": "sunny"},
        "new york": {"temp": 18, "condition": "cloudy"},
        "london": {"temp": 15, "condition": "rainy"},
        "tokyo": {"temp": 25, "condition": "partly cloudy"},
        "sydney": {"temp": 28, "condition": "sunny"}
    }
    
    location_key = location.lower().split(',')[0].strip()
    
    if location_key in weather_data:
        data = weather_data[location_key]
        temp = data["temp"]
        
        # Convert to fahrenheit if requested
        if unit.lower() == "fahrenheit":
            temp = (temp * 9/5) + 32
            unit_symbol = "°F"
        else:
            unit_symbol = "°C"
        
        return f"The weather in {location} is {data['condition']} with a temperature of {temp}{unit_symbol}."
    else:
        return f"Sorry, I don't have weather data for {location}."


def calculate_math(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
    
    Returns:
        Result of the calculation as a string
    """
    try:
        # Only allow safe mathematical operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"The result of {expression} is {result}"
    
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


def generate_random_number(min_value: int = 1, max_value: int = 100) -> str:
    """
    Generate a random number within a specified range.
    
    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
    
    Returns:
        Random number as a string
    """
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    
    number = random.randint(min_value, max_value)
    return f"Random number between {min_value} and {max_value}: {number}"


def search_knowledge_base(query: str, category: str = "general") -> str:
    """
    Search a mock knowledge base for information.
    
    Args:
        query: Search query
        category: Category to search in ('programming', 'science', 'general')
    
    Returns:
        Search results as a string
    """
    # Mock knowledge base
    knowledge_base = {
        "programming": {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "javascript": "JavaScript is a programming language commonly used for web development.",
            "machine learning": "Machine learning is a subset of AI that enables computers to learn without explicit programming."
        },
        "science": {
            "photosynthesis": "Photosynthesis is the process by which plants convert sunlight into energy.",
            "gravity": "Gravity is a fundamental force that attracts objects with mass toward each other.",
            "dna": "DNA is the genetic material that contains instructions for life."
        },
        "general": {
            "coffee": "Coffee is a popular caffeinated beverage made from roasted coffee beans.",
            "exercise": "Regular exercise helps maintain physical health and mental well-being.",
            "reading": "Reading is fundamental for learning and expanding knowledge."
        }
    }
    
    query_lower = query.lower()
    category_data = knowledge_base.get(category, knowledge_base["general"])
    
    # Find matching entries
    matches = []
    for key, value in category_data.items():
        if query_lower in key or key in query_lower:
            matches.append(f"{key.title()}: {value}")
    
    if matches:
        return f"Found {len(matches)} result(s) in {category}:\n" + "\n".join(matches)
    else:
        return f"No results found for '{query}' in {category} category."


# Function definitions for the AI
AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "calculate_math": calculate_math,
    "generate_random_number": generate_random_number,
    "search_knowledge_base": search_knowledge_base
}

# Function schemas for the API
FUNCTION_SCHEMAS = [
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
                        "description": "The city and state/country, e.g. 'San Francisco, CA'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
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
            "description": "Safely evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g. '2 + 3 * 4' or 'sqrt(16)'"
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
            "description": "Generate a random number within a specified range",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_value": {
                        "type": "integer",
                        "description": "Minimum value (inclusive)"
                    },
                    "max_value": {
                        "type": "integer",
                        "description": "Maximum value (inclusive)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search a knowledge base for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["programming", "science", "general"],
                        "description": "Category to search in"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


class FunctionCallingClient:
    """Extended client for function calling capabilities."""
    
    def __init__(self):
        self.client = azure_client
    
    def chat_with_functions(self, 
                           messages: List[Dict[str, str]], 
                           functions: List[Dict] = None,
                           auto_execute: bool = True,
                           max_iterations: int = 5) -> Dict[str, Any]:
        """
        Create a chat completion with function calling support.
        
        Args:
            messages: Conversation messages
            functions: Available function schemas
            auto_execute: Whether to automatically execute function calls
            max_iterations: Maximum number of function call iterations
        
        Returns:
            Final response with function call results
        """
        if functions is None:
            functions = FUNCTION_SCHEMAS
        
        current_messages = messages.copy()
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Make the API call with function definitions
            response = self.client.create_chat_completion(
                messages=current_messages,
                tools=functions,
                max_tokens=500,
                temperature=0.7
            )
            
            assistant_message = response['choices'][0]['message']
            
            # Check if the assistant wants to call a function
            if assistant_message.get('tool_calls'):
                print(f"🔧 Assistant wants to call {len(assistant_message['tool_calls'])} function(s)")
                
                # Add the assistant's message to conversation
                current_messages.append(assistant_message)
                
                # Process each function call
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"📞 Calling function: {function_name}({function_args})")
                    
                    if auto_execute and function_name in AVAILABLE_FUNCTIONS:
                        # Execute the function
                        try:
                            function_result = AVAILABLE_FUNCTIONS[function_name](**function_args)
                            print(f"✅ Function result: {function_result}")
                        except Exception as e:
                            function_result = f"Error executing function: {str(e)}"
                            print(f"❌ Function error: {function_result}")
                        
                        # Add function result to conversation
                        current_messages.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": function_result
                        })
                    else:
                        # Function not available or auto-execute disabled
                        current_messages.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "content": f"Function {function_name} is not available"
                        })
                
                # Continue the conversation with function results
                continue
            
            else:
                # No function call, we're done
                print("💬 Assistant provided final response")
                return response
        
        print(f"⚠️ Reached maximum iterations ({max_iterations})")
        return response


def demonstrate_basic_function_calling():
    """Demonstrate basic function calling."""
    print("=" * 60)
    print("BASIC FUNCTION CALLING EXAMPLE")
    print("=" * 60)
    
    client = FunctionCallingClient()
    
    # Example 1: Weather function
    print("\n1. Weather inquiry:")
    print("-" * 30)
    
    messages = [
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
    
    try:
        response = client.chat_with_functions(messages)
        final_message = response['choices'][0]['message']['content']
        print(f"Final response: {final_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_math_function():
    """Demonstrate math calculation function."""
    print("\n2. Math calculation:")
    print("-" * 30)
    
    client = FunctionCallingClient()
    
    messages = [
        {"role": "user", "content": "What's the square root of 144 plus 5 times 3?"}
    ]
    
    try:
        response = client.chat_with_functions(messages)
        final_message = response['choices'][0]['message']['content']
        print(f"Final response: {final_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_multiple_functions():
    """Demonstrate calling multiple functions in sequence."""
    print("\n3. Multiple function calls:")
    print("-" * 30)
    
    client = FunctionCallingClient()
    
    messages = [
        {"role": "user", "content": "Generate a random number between 1 and 10, then calculate its square root."}
    ]
    
    try:
        response = client.chat_with_functions(messages)
        final_message = response['choices'][0]['message']['content']
        print(f"Final response: {final_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_knowledge_search():
    """Demonstrate knowledge base search function."""
    print("\n4. Knowledge base search:")
    print("-" * 30)
    
    client = FunctionCallingClient()
    
    messages = [
        {"role": "user", "content": "Tell me about Python programming and then search for information about machine learning."}
    ]
    
    try:
        response = client.chat_with_functions(messages)
        final_message = response['choices'][0]['message']['content']
        print(f"Final response: {final_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_function_choice():
    """Demonstrate forcing specific function usage."""
    print("\n5. Forcing specific function usage:")
    print("-" * 30)
    
    # This would require modifying the API call to include tool_choice parameter
    print("Note: This example shows how you could force specific function usage")
    print("by using the 'tool_choice' parameter in the API call.")
    
    client = FunctionCallingClient()
    
    messages = [
        {"role": "user", "content": "I need some information"}
    ]
    
    # For demonstration, we'll just show a regular call
    try:
        response = client.chat_with_functions(
            messages, 
            functions=[FUNCTION_SCHEMAS[3]]  # Only knowledge search function
        )
        final_message = response['choices'][0]['message']['content']
        print(f"Final response: {final_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def interactive_function_calling():
    """Interactive function calling session."""
    print("\n6. Interactive function calling:")
    print("-" * 30)
    print("Chat with AI that can call functions! (type 'quit' to exit)")
    print("Available functions: weather, math, random numbers, knowledge search")
    
    client = FunctionCallingClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to several tools. Use them when appropriate to help the user."}
    ]
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            print("\n🤖 Processing your request...")
            response = client.chat_with_functions(messages.copy())
            
            final_message = response['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": final_message})
            
            print(f"\nAssistant: {final_message}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Test connection first
    if not azure_client.test_connection():
        print("Please check your configuration and try again.")
        exit(1)
    
    # Run demonstrations
    demonstrate_basic_function_calling()
    demonstrate_math_function()
    demonstrate_multiple_functions()
    demonstrate_knowledge_search()
    demonstrate_function_choice()
    
    # Ask if user wants interactive mode
    while True:
        choice = input("\nWould you like to try interactive function calling? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_function_calling()
            break
        elif choice in ['n', 'no']:
            break
        else:
            print("Please enter 'y' or 'n'")
    
    print("\n" + "=" * 60)
    print("Check the logs/api_requests.txt file to see the raw API calls!")
    print("=" * 60)
