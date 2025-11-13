"""
Iterative Factorial Calculator

An independent implementation of factorial calculation using loops.
This version uses a while loop instead of for loop and different variable naming.

Author: Student C
Date: 2024-10-17
"""


def compute_factorial(num):
    """
    Calculate factorial using an iterative while-loop approach.

    Factorial (n!) is calculated by multiplying all integers from 1 to n.
    For example: 5! = 5 x 4 x 3 x 2 x 1 = 120

    Args:
        num (int): The number to calculate factorial for (must be >= 0)

    Returns:
        int: The computed factorial value

    Raises:
        ValueError: If the input is a negative integer
    """
    # Input validation
    if num < 0:
        raise ValueError("Factorial undefined for negative integers")

    # Handle edge cases
    if num <= 1:
        return 1

    # Start with factorial value of 1
    factorial_value = 1
    counter = 2

    # Multiply all numbers from 2 to num using while loop
    while counter <= num:
        factorial_value = factorial_value * counter
        counter += 1

    return factorial_value


def factorial_range(start, end):
    """
    Calculate factorials for a range of numbers.

    Args:
        start (int): Starting number (inclusive)
        end (int): Ending number (inclusive)

    Returns:
        dict: Dictionary mapping numbers to their factorials
    """
    results = {}

    for number in range(start, end + 1):
        if number >= 0:
            results[number] = compute_factorial(number)

    return results


if __name__ == "__main__":
    # Test cases for the factorial function
    print("Iterative Factorial Calculator")
    print("=" * 45)

    # Single value tests
    test_numbers = [0, 1, 5, 10]

    for value in test_numbers:
        output = compute_factorial(value)
        print(f"compute_factorial({value}) = {output}")

    # Range calculation demonstration
    print("\nFactorials from 3 to 8:")
    range_results = factorial_range(3, 8)
    for num, fact in range_results.items():
        print(f"  {num}! = {fact}")
