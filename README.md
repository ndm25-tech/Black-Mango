# Black-Mango 🥭

A simple greeting application that responds to "hi" and other friendly messages.

## What it does

Black-Mango is a friendly greeting application that:
- Responds to various greetings like "hi", "hello", "hey"
- Provides appropriate responses to different types of messages
- Offers an interactive chat-like experience

## Usage

### Running the interactive application

```bash
python3 hello.py
```

### Using the greeting function programmatically

```python
from hello import greet

# Get a response to "hi"
response = greet("hi")
print(response)  # Output: Hello! Welcome to Black-Mango! 🥭
```

## Examples

```
You: hi
Black-Mango: Hello! Welcome to Black-Mango! 🥭

You: how are you?
Black-Mango: I'm doing great! Thanks for asking! 😊

You: goodbye
Black-Mango: Goodbye! Thanks for using Black-Mango! 👋
```

## Requirements

- Python 3.x

No additional dependencies required!