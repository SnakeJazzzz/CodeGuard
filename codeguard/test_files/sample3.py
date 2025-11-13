"""
Sample Python file 3 for testing CodeGuard
This file is completely different
"""

class Calculator:
    """A simple calculator class."""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def get_history(self):
        """Get calculation history."""
        return self.history

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.multiply(4, 2))
    print(calc.get_history())
