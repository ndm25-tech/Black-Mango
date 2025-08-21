#!/usr/bin/env python3
"""
Simple tests for the Black-Mango greeting application.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hello import greet

def test_basic_greetings():
    """Test basic greeting responses."""
    assert greet("hi") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet("hello") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet("hey") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet("greetings") == "Hello! Welcome to Black-Mango! 🥭"

def test_case_insensitive():
    """Test that greetings are case insensitive."""
    assert greet("HI") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet("Hello") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet("HEY") == "Hello! Welcome to Black-Mango! 🥭"

def test_goodbyes():
    """Test goodbye responses."""
    assert greet("goodbye") == "Goodbye! Thanks for using Black-Mango! 👋"
    assert greet("bye") == "Goodbye! Thanks for using Black-Mango! 👋"
    assert greet("see you") == "Goodbye! Thanks for using Black-Mango! 👋"

def test_how_are_you():
    """Test 'how are you' responses."""
    assert greet("how are you") == "I'm doing great! Thanks for asking! 😊"
    assert greet("how are you?") == "I'm doing great! Thanks for asking! 😊"

def test_unknown_messages():
    """Test responses to unknown messages."""
    response = greet("random message")
    assert "random message" in response
    assert "Welcome to Black-Mango!" in response

def test_whitespace_handling():
    """Test that whitespace is handled properly."""
    assert greet("  hi  ") == "Hello! Welcome to Black-Mango! 🥭"
    assert greet(" hello ") == "Hello! Welcome to Black-Mango! 🥭"

if __name__ == "__main__":
    try:
        test_basic_greetings()
        test_case_insensitive()
        test_goodbyes()
        test_how_are_you()
        test_unknown_messages()
        test_whitespace_handling()
        print("All tests passed! ✅")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)