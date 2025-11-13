"""
Factorial Calculator - Original Implementation

This module provides a function to calculate the factorial of a positive integer
using an iterative approach. This is a student assignment submission.

Author: Student A
Date: 2024-10-15
"""


def calculate_factorial(n):
    """
    Calculate the factorial of a given number using iteration.

    The factorial of n (denoted as n!) is the product of all positive
    integers less than or equal to n.

    Args:
        n (int): A non-negative integer whose factorial is to be calculated

    Returns:
        int: The factorial of n

    Raises:
        ValueError: If n is negative
    """
    # Validate input - factorial is only defined for non-negative integers
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    # Base case: 0! = 1 and 1! = 1
    if n == 0 or n == 1:
        return 1

    # Initialize result variable to store the factorial
    result = 1

    # Iterate from 2 to n (inclusive) and multiply each number
    for i in range(2, n + 1):
        result *= i  # Multiply result by current number

    return result


if __name__ == "__main__":
    # Test the factorial function with various inputs
    test_values = [0, 1, 5, 10]

    print("Factorial Calculator - Test Results")
    print("=" * 40)

    for num in test_values:
        factorial = calculate_factorial(num)
        print(f"{num}! = {factorial}")

    # Additional example with user demonstration
    print("\nExample: 7! =", calculate_factorial(7))
