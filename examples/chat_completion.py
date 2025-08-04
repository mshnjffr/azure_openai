"""
Chat completion example using Azure OpenAI.
This example demonstrates the modern chat completions API.
"""

from api.client import azure_client


class ChatSession:
    """Simple chat session manager to maintain conversation history."""
    
    def __init__(self, system_message: str = None):
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})
    
    def add_assistant_message(self, content: str):
        """Add an assistant response to the conversation."""
        self.messages.append({"role": "assistant", "content": content})
    
    def get_messages(self):
        """Get all messages in the conversation."""
        return self.messages.copy()
    
    def clear_history(self):
        """Clear conversation history, keeping only system message if present."""
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        self.messages = system_messages


def demonstrate_basic_chat():
    """Demonstrate basic chat completion functionality."""
    print("=" * 60)
    print("BASIC CHAT COMPLETION EXAMPLE")
    print("=" * 60)
    
    # Example 1: Single-turn conversation
    print("\n1. Single-turn conversation:")
    print("-" * 30)
    
    messages = [
        {"role": "user", "content": "What are the benefits of learning Python?"}
    ]
    
    try:
        response = azure_client.create_chat_completion(
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        assistant_message = response['choices'][0]['message']['content']
        print(f"User: {messages[0]['content']}")
        print(f"Assistant: {assistant_message}")
        print(f"Tokens used: {response['usage']['total_tokens']}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_system_message():
    """Demonstrate using system messages to set assistant behavior."""
    print("\n2. Using system messages:")
    print("-" * 30)
    
    # Example with different system messages
    system_messages = [
        "You are a helpful programming tutor who explains concepts clearly.",
        "You are a pirate who speaks in pirate language.",
        "You are a formal academic professor."
    ]
    
    user_question = "What is machine learning?"
    
    for i, system_msg in enumerate(system_messages, 1):
        print(f"\n2.{i} System: {system_msg}")
        print(f"User: {user_question}")
        
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_question}
        ]
        
        try:
            response = azure_client.create_chat_completion(
                messages=messages,
                max_tokens=100,
                temperature=0.8
            )
            
            assistant_message = response['choices'][0]['message']['content']
            print(f"Assistant: {assistant_message}")
            
        except Exception as e:
            print(f"Error: {e}")


def demonstrate_multi_turn_chat():
    """Demonstrate multi-turn conversation with history."""
    print("\n3. Multi-turn conversation:")
    print("-" * 30)
    
    # Create a chat session
    chat = ChatSession("You are a helpful coding assistant.")
    
    # Conversation turns
    conversation = [
        "I want to learn web development. Where should I start?",
        "I'm interested in backend development. What languages do you recommend?",
        "Tell me more about Python for web development.",
        "What frameworks should I learn?"
    ]
    
    for turn, user_input in enumerate(conversation, 1):
        print(f"\nTurn {turn}:")
        print(f"User: {user_input}")
        
        # Add user message to history
        chat.add_user_message(user_input)
        
        try:
            response = azure_client.create_chat_completion(
                messages=chat.get_messages(),
                max_tokens=120,
                temperature=0.7
            )
            
            assistant_message = response['choices'][0]['message']['content']
            
            # Add assistant response to history
            chat.add_assistant_message(assistant_message)
            
            print(f"Assistant: {assistant_message}")
            
        except Exception as e:
            print(f"Error: {e}")
            break


def demonstrate_different_roles():
    """Demonstrate different message roles and their effects."""
    print("\n4. Different message roles:")
    print("-" * 30)
    
    # Example showing how assistant messages can guide the conversation
    messages = [
        {"role": "system", "content": "You are a creative writing assistant."},
        {"role": "user", "content": "I want to write a story about space exploration."},
        {"role": "assistant", "content": "That's exciting! Space exploration offers rich possibilities for storytelling. What type of story interests you - hard science fiction with realistic technology, or something more fantastical?"},
        {"role": "user", "content": "I prefer realistic science fiction."},
    ]
    
    print("Conversation with pre-defined assistant message:")
    for msg in messages:
        print(f"{msg['role'].title()}: {msg['content']}")
    
    try:
        response = azure_client.create_chat_completion(
            messages=messages,
            max_tokens=150,
            temperature=0.8
        )
        
        assistant_message = response['choices'][0]['message']['content']
        print(f"Assistant: {assistant_message}")
        
    except Exception as e:
        print(f"Error: {e}")


def interactive_chat():
    """Interactive chat session with the user."""
    print("\n5. Interactive chat session:")
    print("-" * 30)
    print("Start chatting with the AI! (type 'quit' to exit, 'clear' to reset)")
    
    # Get system message from user
    system_msg = input("\nEnter system message (optional): ").strip()
    chat = ChatSession(system_msg if system_msg else "You are a helpful assistant.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if user_input.lower() == 'clear':
            chat.clear_history()
            print("Conversation history cleared!")
            continue
        
        if not user_input:
            continue
        
        # Add user message
        chat.add_user_message(user_input)
        
        try:
            response = azure_client.create_chat_completion(
                messages=chat.get_messages(),
                max_tokens=200,
                temperature=0.7
            )
            
            assistant_message = response['choices'][0]['message']['content']
            chat.add_assistant_message(assistant_message)
            
            print(f"Assistant: {assistant_message}")
            print(f"(Tokens: {response['usage']['total_tokens']})")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Test connection first
    if not azure_client.test_connection():
        print("Please check your configuration and try again.")
        exit(1)
    
    # Run demonstrations
    demonstrate_basic_chat()
    demonstrate_system_message()
    demonstrate_multi_turn_chat()
    demonstrate_different_roles()
    interactive_chat()
    
    print("\n" + "=" * 60)
    print("Check the logs/api_requests.txt file to see the raw API calls!")
    print("=" * 60)
