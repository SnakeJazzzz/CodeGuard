"""
Greatest Common Divisor Calculator

Calculate GCD using Euclidean algorithm - the most efficient
method for finding the greatest common divisor of two numbers.

Author: Student O
Date: 2024-11-13
"""


def gcd(a, b):
    """
    Calculate greatest common divisor using Euclidean algorithm.

    The Euclidean algorithm uses the principle that GCD(a, b) = GCD(b, a % b).
    It repeatedly applies modulo operation until remainder is 0.

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: Greatest common divisor of a and b
    """
    # Make sure we work with positive numbers
    a = abs(a)
    b = abs(b)

    # Apply Euclidean algorithm
    while b != 0:
        # Store b value
        temp = b
        # b becomes remainder of a divided by b
        b = a % b
        # a becomes old b value
        a = temp

    return a


def lcm(a, b):
    """
    Calculate least common multiple using GCD.

    LCM(a, b) = (a * b) / GCD(a, b)

    Args:
        a (int): First number
        b (int): Second number

    Returns:
        int: Least common multiple of a and b
    """
    if a == 0 or b == 0:
        return 0

    return abs(a * b) // gcd(a, b)


def gcd_multiple(numbers):
    """
    Calculate GCD of multiple numbers.

    Args:
        numbers (list): List of integers

    Returns:
        int: GCD of all numbers in list
    """
    if not numbers:
        return 0

    result = numbers[0]

    for num in numbers[1:]:
        result = gcd(result, num)

    return result


if __name__ == "__main__":
    # Test GCD calculations
    print("GCD Tests:")
    print("GCD(48, 18) =", gcd(48, 18))
    print("GCD(100, 50) =", gcd(100, 50))
    print("GCD(17, 13) =", gcd(17, 13))

    print("\nLCM Tests:")
    print("LCM(12, 18) =", lcm(12, 18))
    print("LCM(21, 6) =", lcm(21, 6))

    print("\nMultiple numbers:")
    print("GCD([48, 18, 36, 12]) =", gcd_multiple([48, 18, 36, 12]))
