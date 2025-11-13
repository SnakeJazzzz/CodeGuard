"""
Recursive Factorial Implementation

A recursive approach to calculating factorials. This implementation uses
the mathematical definition of factorial where n! = n * (n-1)!

Author: Student B
Date: 2024-10-16
"""


def factorial(num):
    """
    Compute factorial using recursive method.

    This function implements the recursive definition:
    - Base case: factorial(0) = 1
    - Recursive case: factorial(n) = n * factorial(n-1)

    Args:
        num (int): Non-negative integer to compute factorial for

    Returns:
        int: Factorial of the input number

    Raises:
        ValueError: When num is negative
        RecursionError: When num is too large (default Python recursion limit)
    """
    # Check for invalid negative input
    if num < 0:
        raise ValueError("Cannot compute factorial of negative number")

    # Base case: factorial of 0 is 1
    if num == 0:
        return 1

    # Recursive case: n! = n * (n-1)!
    return num * factorial(num - 1)


def factorial_with_limit(num, max_depth=1000):
    """
    Recursive factorial with explicit recursion depth check.

    Args:
        num (int): Number to calculate factorial for
        max_depth (int): Maximum recursion depth allowed

    Returns:
        int: The factorial result

    Raises:
        ValueError: If num is negative or exceeds max_depth
    """
    if num < 0:
        raise ValueError("Negative numbers not allowed")

    if num > max_depth:
        raise ValueError(f"Input {num} exceeds maximum depth {max_depth}")

    # Use the main factorial function
    return factorial(num)


if __name__ == "__main__":
    # Demonstrate the recursive factorial function
    print("Recursive Factorial Demonstration")
    print("-" * 40)

    # Test with different values
    numbers_to_test = [0, 1, 5, 10, 12]

    for number in numbers_to_test:
        result = factorial(number)
        print(f"factorial({number}) = {result}")

    # Show a specific example
    print("\nSpecific example:")
    print(f"factorial(6) = {factorial(6)}")
