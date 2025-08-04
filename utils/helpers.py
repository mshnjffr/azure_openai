"""
Utility functions for the Azure OpenAI tutorial application.
"""

import json
import re
from typing import Dict, Any, List


def format_response(response: Dict[str, Any], response_type: str = "completion") -> str:
    """
    Format API response for better readability.
    
    Args:
        response: API response dictionary
        response_type: Type of response ("completion" or "chat")
    
    Returns:
        Formatted string representation
    """
    if response_type == "completion":
        return format_completion_response(response)
    elif response_type == "chat":
        return format_chat_response(response)
    else:
        return json.dumps(response, indent=2)


def format_completion_response(response: Dict[str, Any]) -> str:
    """Format completion API response."""
    if 'choices' not in response or not response['choices']:
        return "No completion generated"
    
    choice = response['choices'][0]
    text = choice.get('text', '').strip()
    
    # Usage information
    usage = response.get('usage', {})
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)
    total_tokens = usage.get('total_tokens', 0)
    
    formatted = f"""
Completion: {text}

Token Usage:
- Prompt tokens: {prompt_tokens}
- Completion tokens: {completion_tokens}
- Total tokens: {total_tokens}
"""
    
    # Finish reason
    finish_reason = choice.get('finish_reason')
    if finish_reason:
        formatted += f"- Finish reason: {finish_reason}\n"
    
    return formatted.strip()


def format_chat_response(response: Dict[str, Any]) -> str:
    """Format chat completion API response."""
    if 'choices' not in response or not response['choices']:
        return "No response generated"
    
    choice = response['choices'][0]
    message = choice.get('message', {})
    content = message.get('content', '').strip()
    role = message.get('role', 'assistant')
    
    # Usage information
    usage = response.get('usage', {})
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)
    total_tokens = usage.get('total_tokens', 0)
    
    formatted = f"""
{role.title()}: {content}

Token Usage:
- Prompt tokens: {prompt_tokens}
- Completion tokens: {completion_tokens}
- Total tokens: {total_tokens}
"""
    
    # Finish reason
    finish_reason = choice.get('finish_reason')
    if finish_reason:
        formatted += f"- Finish reason: {finish_reason}\n"
    
    return formatted.strip()


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for a given text.
    Note: This is a simple approximation. For accurate counting, use tiktoken.
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    # Simple estimation: ~4 characters per token for English text
    return len(text) // 4


def truncate_text(text: str, max_tokens: int) -> str:
    """
    Truncate text to approximately fit within token limit.
    
    Args:
        text: Input text
        max_tokens: Maximum token limit
    
    Returns:
        Truncated text
    """
    estimated_tokens = estimate_tokens(text)
    
    if estimated_tokens <= max_tokens:
        return text
    
    # Calculate approximate character limit
    char_limit = max_tokens * 4
    
    # Truncate and add ellipsis
    if len(text) > char_limit:
        return text[:char_limit-3] + "..."
    
    return text


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and formatting.
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_messages(messages: List[Dict[str, str]]) -> bool:
    """
    Validate chat messages format.
    
    Args:
        messages: List of message dictionaries
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(messages, list) or not messages:
        return False
    
    valid_roles = {"system", "user", "assistant"}
    
    for message in messages:
        if not isinstance(message, dict):
            return False
        
        if "role" not in message or "content" not in message:
            return False
        
        if message["role"] not in valid_roles:
            return False
        
        if not isinstance(message["content"], str):
            return False
    
    return True


def calculate_cost(usage: Dict[str, int], model_type: str = "gpt-35-turbo") -> float:
    """
    Calculate approximate cost for API usage.
    Note: Prices are approximate and may vary. Check Azure pricing for actual costs.
    
    Args:
        usage: Usage dictionary from API response
        model_type: Model type for pricing calculation
    
    Returns:
        Estimated cost in USD
    """
    # Approximate pricing (per 1K tokens) - these are examples, check actual pricing
    pricing = {
        "gpt-35-turbo": {"prompt": 0.0015, "completion": 0.002},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-32k": {"prompt": 0.06, "completion": 0.12}
    }
    
    if model_type not in pricing:
        model_type = "gpt-35-turbo"  # Default
    
    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)
    
    prompt_cost = (prompt_tokens / 1000) * pricing[model_type]["prompt"]
    completion_cost = (completion_tokens / 1000) * pricing[model_type]["completion"]
    
    return prompt_cost + completion_cost


def print_divider(title: str = "", width: int = 60):
    """Print a formatted divider with optional title."""
    if title:
        title = f" {title} "
        print(title.center(width, "="))
    else:
        print("=" * width)


def print_section(title: str, content: str = ""):
    """Print a formatted section with title and content."""
    print(f"\n{title}")
    print("-" * len(title))
    if content:
        print(content)


def safe_json_load(text: str) -> Dict[str, Any]:
    """
    Safely load JSON from text, returning empty dict if invalid.
    
    Args:
        text: JSON text
    
    Returns:
        Parsed dictionary or empty dict if invalid
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}
