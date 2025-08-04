"""
Basic text completion example using Azure OpenAI.
This example demonstrates the legacy completions API.
"""

from api.client import azure_client


def demonstrate_basic_completion():
    """Demonstrate basic text completion functionality."""
    print("=" * 60)
    print("BASIC TEXT COMPLETION EXAMPLE")
    print("=" * 60)
    
    # Example 1: Simple completion
    print("\n1. Simple text completion:")
    print("-" * 30)
    
    prompt = "Write a creative tagline for a coffee shop:"
    print(f"Prompt: {prompt}")
    
    try:
        response = azure_client.create_completion(
            prompt=prompt,
            max_tokens=50,
            temperature=0.8
        )
        
        completion_text = response['choices'][0]['text'].strip()
        print(f"Completion: {completion_text}")
        print(f"Tokens used: {response['usage']['total_tokens']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Parameter exploration
    print("\n2. Exploring different parameters:")
    print("-" * 30)
    
    base_prompt = "The future of artificial intelligence is"
    
    # Low temperature (more focused)
    print(f"\nPrompt: {base_prompt}")
    print("With temperature=0.1 (focused):")
    
    try:
        response = azure_client.create_completion(
            prompt=base_prompt,
            max_tokens=30,
            temperature=0.1
        )
        completion_text = response['choices'][0]['text'].strip()
        print(f"Result: {completion_text}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # High temperature (more creative)
    print("\nWith temperature=1.5 (creative):")
    
    try:
        response = azure_client.create_completion(
            prompt=base_prompt,
            max_tokens=30,
            temperature=1.5
        )
        completion_text = response['choices'][0]['text'].strip()
        print(f"Result: {completion_text}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Different max_tokens
    print("\n3. Different max_tokens values:")
    print("-" * 30)
    
    story_prompt = "Once upon a time in a magical forest,"
    
    for tokens in [10, 25, 50]:
        print(f"\nWith max_tokens={tokens}:")
        try:
            response = azure_client.create_completion(
                prompt=story_prompt,
                max_tokens=tokens,
                temperature=0.7
            )
            completion_text = response['choices'][0]['text'].strip()
            print(f"Result: {completion_text}")
            
        except Exception as e:
            print(f"Error: {e}")


def demonstrate_stop_sequences():
    """Demonstrate using stop sequences to control completion."""
    print("\n4. Using stop sequences:")
    print("-" * 30)
    
    prompt = "List three benefits of exercise:\n1."
    
    try:
        response = azure_client.create_completion(
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            stop=["\n4.", "\n\n"]  # Stop at fourth item or double newline
        )
        
        completion_text = response['choices'][0]['text'].strip()
        print(f"Prompt: {prompt}")
        print(f"Result: {completion_text}")
        
    except Exception as e:
        print(f"Error: {e}")


def interactive_completion():
    """Interactive completion where user can input their own prompts."""
    print("\n5. Interactive completion:")
    print("-" * 30)
    print("Enter your own prompts (type 'quit' to exit)")
    
    while True:
        user_prompt = input("\nEnter prompt: ").strip()
        
        if user_prompt.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_prompt:
            continue
        
        try:
            # Get user preferences
            try:
                max_tokens = int(input("Max tokens (default 50): ") or "50")
                temperature = float(input("Temperature 0.0-2.0 (default 0.7): ") or "0.7")
            except ValueError:
                print("Using default values...")
                max_tokens = 50
                temperature = 0.7
            
            response = azure_client.create_completion(
                prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            completion_text = response['choices'][0]['text'].strip()
            print(f"\nCompletion: {completion_text}")
            print(f"Tokens used: {response['usage']['total_tokens']}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Test connection first
    if not azure_client.test_connection():
        print("Please check your configuration and try again.")
        exit(1)
    
    # Run demonstrations
    demonstrate_basic_completion()
    demonstrate_stop_sequences()
    interactive_completion()
    
    print("\n" + "=" * 60)
    print("Check the logs/api_requests.txt file to see the raw API calls!")
    print("=" * 60)
