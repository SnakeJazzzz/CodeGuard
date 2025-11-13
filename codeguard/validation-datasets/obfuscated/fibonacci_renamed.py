"""
Fibonacci Sequence Generator - Obfuscated Version

This module computes the nth number in the Fibonacci sequence using iteration.
The sequence follows the pattern: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...

Author: Student E
Date: 2024-10-19
"""


def fibonacci(target):
    """
    Compute the nth Fibonacci number using an iterative method.

    The sequence follows the rule:
    F(0) = 0
    F(1) = 1
    F(n) = F(n-1) + F(n-2) when n > 1

    Args:
        target (int): The index in the Fibonacci sequence (0-indexed)

    Returns:
        int: The Fibonacci number at position target

    Raises:
        ValueError: When target is negative
    """
    # Check that target is non-negative
    if target < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")

    # Handle base cases: F(0) = 0 and F(1) = 1
    if target == 0:
        return 0
    if target == 1:
        return 1

    # Set up initial values for the first two numbers
    x = 0  # F(0)
    y = 1  # F(1)

    # Compute Fibonacci numbers using iteration
    for counter in range(2, target + 1):
        # Calculate the next number in the sequence
        swap = x + y
        # Update values: x takes y's value, y takes the new number
        x = y
        y = swap

    return y


def fibonacci_sequence(length):
    """
    Create a list of Fibonacci numbers.

    Args:
        length (int): How many Fibonacci numbers to generate

    Returns:
        list: A list with the first 'length' Fibonacci numbers
    """
    if length <= 0:
        return []

    sequence = []
    for counter in range(length):
        sequence.append(fibonacci(counter))

    return sequence


if __name__ == "__main__":
    # Demonstrate the Fibonacci function with different inputs
    print("Fibonacci Number Calculator")
    print("=" * 40)

    # Calculate specific Fibonacci numbers
    test_positions = [0, 1, 5, 10, 15]

    for target in test_positions:
        fib_number = fibonacci(target)
        print(f"F({target}) = {fib_number}")

    # Display a sequence of numbers
    print("\nFirst 10 Fibonacci numbers:")
    sequence = fibonacci_sequence(10)
    print(sequence)
