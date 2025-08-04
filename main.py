"""
Main entry point for the Azure OpenAI Python tutorial application.
This interactive menu allows users to explore different API features.
"""

import sys
import os
from utils.helpers import print_divider, print_section


def show_menu():
    """Display the main menu options."""
    print_divider("AZURE OPENAI PYTHON TUTORIAL", 70)
    print("""
Welcome to the Azure OpenAI Python Tutorial Application!

This application demonstrates how to use Azure OpenAI API from basic 
to advanced features. All API requests are logged to logs/api_requests.txt
so you can see the raw HTTP calls.

Select an example to run:

1. Basic Text Completion - Legacy completions API
2. Chat Completion - Modern chat API with conversation history
3. Function Calling - Advanced AI function calling with tools
4. Streaming Responses - Real-time response streaming (Coming Soon)
5. Test Connection - Verify your Azure OpenAI setup
6. View API Logs - Display recent API request logs
7. Clear API Logs - Clear the API request log file

0. Exit

""")


def test_connection():
    """Test the Azure OpenAI connection."""
    try:
        from api.client import azure_client
        print_section("Testing Azure OpenAI Connection")
        
        if azure_client.test_connection():
            print("✅ Connection successful!")
            print(f"Endpoint: {azure_client.client.base_url}")
            print(f"Deployment: {azure_client.deployment_name}")
        else:
            print("❌ Connection failed. Please check your configuration.")
            print("\nMake sure you have:")
            print("1. Created a .env file based on .env.example")
            print("2. Set your Azure OpenAI API key and endpoint")
            print("3. Specified your deployment name")
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")


def view_logs():
    """View recent API logs."""
    log_file = "logs/api_requests.txt"
    
    print_section("Recent API Request Logs")
    
    if not os.path.exists(log_file):
        print("No logs found. Run some examples first to generate logs.")
        return
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            print("Log file is empty.")
            return
        
        # Show last 2000 characters to avoid overwhelming output
        if len(content) > 2000:
            print("Showing last 2000 characters of log file:")
            print("..." + content[-2000:])
        else:
            print(content)
            
    except Exception as e:
        print(f"Error reading log file: {e}")


def clear_logs():
    """Clear API logs."""
    try:
        from api.logger import api_logger
        print_section("Clearing API Logs")
        api_logger.clear_logs()
        
    except Exception as e:
        print(f"Error clearing logs: {e}")


def run_basic_completion():
    """Run basic completion examples."""
    try:
        print_section("Running Basic Completion Examples")
        from examples.basic_completion import (
            demonstrate_basic_completion,
            demonstrate_stop_sequences,
            interactive_completion
        )
        
        demonstrate_basic_completion()
        demonstrate_stop_sequences()
        
        # Ask if user wants interactive mode
        while True:
            choice = input("\nWould you like to try interactive completion? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_completion()
                break
            elif choice in ['n', 'no']:
                break
            else:
                print("Please enter 'y' or 'n'")
                
    except Exception as e:
        print(f"Error running basic completion: {e}")


def run_chat_completion():
    """Run chat completion examples."""
    try:
        print_section("Running Chat Completion Examples")
        from examples.chat_completion import (
            demonstrate_basic_chat,
            demonstrate_system_message,
            demonstrate_multi_turn_chat,
            demonstrate_different_roles,
            interactive_chat
        )
        
        demonstrate_basic_chat()
        demonstrate_system_message()
        demonstrate_multi_turn_chat()
        demonstrate_different_roles()
        
        # Ask if user wants interactive mode
        while True:
            choice = input("\nWould you like to try interactive chat? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_chat()
                break
            elif choice in ['n', 'no']:
                break
            else:
                print("Please enter 'y' or 'n'")
                
    except Exception as e:
        print(f"Error running chat completion: {e}")


def run_function_calling():
    """Run function calling examples."""
    try:
        print_section("Running Function Calling Examples")
        from examples.function_calling import (
            demonstrate_basic_function_calling,
            demonstrate_math_function,
            demonstrate_multiple_functions,
            demonstrate_knowledge_search,
            demonstrate_function_choice,
            interactive_function_calling
        )
        
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
                
    except Exception as e:
        print(f"Error running function calling: {e}")


def coming_soon(feature_name):
    """Display coming soon message."""
    print_section(f"{feature_name} - Coming Soon!")
    print(f"The {feature_name} feature will be implemented in the next phase.")
    print("Stay tuned for updates!")


def main():
    """Main application loop."""
    # Check if configuration exists
    if not os.path.exists('.env'):
        print("⚠️  Configuration file (.env) not found!")
        print("Please create a .env file based on .env.example and configure your Azure OpenAI settings.")
        print("\nExample:")
        print("cp .env.example .env")
        print("# Then edit .env with your actual values")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-7): ").strip()
            
            if choice == '0':
                print("\nThank you for using the Azure OpenAI Python Tutorial!")
                print("Don't forget to check logs/api_requests.txt to see the raw API calls.")
                break
            
            elif choice == '1':
                run_basic_completion()
            
            elif choice == '2':
                run_chat_completion()
            
            elif choice == '3':
                run_function_calling()
            
            elif choice == '4':
                coming_soon("Streaming Responses")
            
            elif choice == '5':
                test_connection()
            
            elif choice == '6':
                view_logs()
            
            elif choice == '7':
                clear_logs()
            
            else:
                print("Invalid choice. Please enter a number between 0 and 7.")
            
            # Pause before showing menu again
            if choice != '0':
                input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
