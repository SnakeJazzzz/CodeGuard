"""
Fibonacci Sequence Generator - Original Implementation

This module calculates the nth Fibonacci number using an iterative approach.
The Fibonacci sequence is: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...

Author: Student D
Date: 2024-10-18
"""


def fibonacci(n):
    """
    Calculate the nth Fibonacci number using iteration.

    The Fibonacci sequence is defined as:
    F(0) = 0
    F(1) = 1
    F(n) = F(n-1) + F(n-2) for n > 1

    Args:
        n (int): The position in the Fibonacci sequence (0-indexed)

    Returns:
        int: The nth Fibonacci number

    Raises:
        ValueError: If n is negative
    """
    # Validate that n is non-negative
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")

    # Base cases: F(0) = 0 and F(1) = 1
    if n == 0:
        return 0
    if n == 1:
        return 1

    # Initialize the first two Fibonacci numbers
    a = 0  # F(0)
    b = 1  # F(1)

    # Calculate Fibonacci numbers iteratively
    for i in range(2, n + 1):
        # Store the next Fibonacci number
        temp = a + b
        # Shift values: a becomes b, b becomes the new Fibonacci number
        a = b
        b = temp

    return b


def fibonacci_sequence(length):
    """
    Generate a list of Fibonacci numbers.

    Args:
        length (int): Number of Fibonacci numbers to generate

    Returns:
        list: List containing the first 'length' Fibonacci numbers
    """
    if length <= 0:
        return []

    sequence = []
    for i in range(length):
        sequence.append(fibonacci(i))

    return sequence


if __name__ == "__main__":
    # Test the Fibonacci function with various inputs
    print("Fibonacci Number Calculator")
    print("=" * 40)

    # Test individual Fibonacci numbers
    test_positions = [0, 1, 5, 10, 15]

    for n in test_positions:
        fib_number = fibonacci(n)
        print(f"F({n}) = {fib_number}")

    # Generate a sequence
    print("\nFirst 10 Fibonacci numbers:")
    sequence = fibonacci_sequence(10)
    print(sequence)
