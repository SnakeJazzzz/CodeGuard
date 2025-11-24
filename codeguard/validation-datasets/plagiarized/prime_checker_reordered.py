"""
Prime Number Utilities - Student Submission

Functions for working with prime numbers including checking and counting.

Author: Student H
Date: 2024-11-06
"""

import math


def count_primes_in_range(start, end):
    """
    Count prime numbers in a given range.

    Args:
        start (int): Start of range (inclusive)
        end (int): End of range (inclusive)

    Returns:
        int: Number of primes in range
    """
    count = 0

    for number in range(start, end + 1):
        if is_prime(number):
            count += 1

    return count


def find_primes_up_to(limit):
    """
    Find all prime numbers up to a given limit.

    Args:
        limit (int): Upper bound (inclusive)

    Returns:
        list: List of prime numbers up to limit
    """
    primes = []

    for num in range(2, limit + 1):
        if is_prime(num):
            primes.append(num)

    return primes


def is_prime(number):
    """
    Check if a number is prime.

    A prime number is a natural number greater than 1 that has no
    positive divisors other than 1 and itself.

    Args:
        number (int): Number to check

    Returns:
        bool: True if number is prime, False otherwise
    """
    # Handle edge cases
    if number < 2:
        return False

    # 2 is the only even prime
    if number == 2:
        return True

    # All other even numbers are not prime
    if number % 2 == 0:
        return False

    # Check odd divisors up to sqrt(number)
    sqrt_num = int(math.sqrt(number))
    for divisor in range(3, sqrt_num + 1, 2):
        if number % divisor == 0:
            return False

    return True


if __name__ == "__main__":
    # Test prime checking
    print("Prime Number Checker Tests")
    print("=" * 40)

    test_numbers = [2, 3, 4, 5, 15, 17, 20, 23, 29, 30]

    for num in test_numbers:
        result = "is prime" if is_prime(num) else "is not prime"
        print(f"{num} {result}")

    # Find primes up to 50
    print("\nPrimes up to 50:")
    primes = find_primes_up_to(50)
    print(primes)

    # Count primes in range
    print(f"\nNumber of primes between 1 and 100: {count_primes_in_range(1, 100)}")
