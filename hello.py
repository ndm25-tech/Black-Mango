#!/usr/bin/env python3
"""
A simple greeting application for the Black-Mango project.
Responds to various greetings including 'hi'.
"""

def greet(message):
    """
    Responds to greeting messages.
    
    Args:
        message (str): The input message
    
    Returns:
        str: Appropriate greeting response
    """
    message_lower = message.lower().strip()
    
    if message_lower in ['hi', 'hello', 'hey', 'greetings']:
        return "Hello! Welcome to Black-Mango! 🥭"
    elif message_lower in ['goodbye', 'bye', 'see you']:
        return "Goodbye! Thanks for using Black-Mango! 👋"
    elif message_lower in ['how are you', 'how are you?']:
        return "I'm doing great! Thanks for asking! 😊"
    else:
        return f"Hello! You said: '{message}'. Welcome to Black-Mango! 🥭"

def main():
    """Main interactive function."""
    print("Black-Mango Greeting App")
    print("========================")
    print("Type 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
                
            if user_input:
                response = greet(user_input)
                print(f"Black-Mango: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except EOFError:
            print("\nGoodbye! 👋")
            break

if __name__ == "__main__":
    main()