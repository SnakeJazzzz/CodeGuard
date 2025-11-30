# Student 20 - Filter with Custom Predicates

"""
Using filter and separate predicate functions.
Functional decomposition approach.
"""

def is_fizz(n):
    """Check if number should print Fizz."""
    return n % 3 == 0

def is_buzz(n):
    """Check if number should print Buzz."""
    return n % 5 == 0

def format_number(n):
    """Format a number according to FizzBuzz rules."""
    parts = []
    if is_fizz(n):
        parts.append("Fizz")
    if is_buzz(n):
        parts.append("Buzz")
    return "".join(parts) if parts else str(n)

def fizzbuzz():
    numbers = range(1, 101)
    results = map(format_number, numbers)

    for result in results:
        print(result)

if __name__ == "__main__":
    fizzbuzz()
