"""
Common Divisor and Multiple Calculator

Mathematical utilities for computing GCD and LCM.

Author: Student P
Date: 2024-11-14
"""


def greatest_common_divisor(num1, num2):
    """
    Find GCD using iterative Euclidean method.

    Args:
        num1 (int): First integer
        num2 (int): Second integer

    Returns:
        int: GCD of the two numbers
    """
    # Convert to positive values
    num1 = abs(num1)
    num2 = abs(num2)

    # Euclidean algorithm loop
    while num2 != 0:
        # Save num2
        saved = num2
        # Calculate new num2 as remainder
        num2 = num1 % num2
        # Update num1
        num1 = saved

    return num1


def gcd_for_list(number_list):
    """
    Compute GCD across list of integers.

    Args:
        number_list (list): Collection of integers

    Returns:
        int: GCD of all numbers
    """
    if not number_list:
        return 0

    current_gcd = number_list[0]

    for number in number_list[1:]:
        current_gcd = greatest_common_divisor(current_gcd, number)

    return current_gcd


def least_common_multiple(num1, num2):
    """
    Find LCM using GCD relationship.

    LCM formula: LCM(a,b) = (a*b) / GCD(a,b)

    Args:
        num1 (int): First integer
        num2 (int): Second integer

    Returns:
        int: LCM of the two numbers
    """
    if num1 == 0 or num2 == 0:
        return 0

    return abs(num1 * num2) // greatest_common_divisor(num1, num2)


if __name__ == "__main__":
    # Testing
    print("GCD Tests:")
    print("GCD(48, 18) =", greatest_common_divisor(48, 18))
    print("GCD(100, 50) =", greatest_common_divisor(100, 50))
    print("GCD(17, 13) =", greatest_common_divisor(17, 13))

    print("\nLCM Tests:")
    print("LCM(12, 18) =", least_common_multiple(12, 18))
    print("LCM(21, 6) =", least_common_multiple(21, 6))

    print("\nMultiple numbers:")
    print("GCD([48, 18, 36, 12]) =", gcd_for_list([48, 18, 36, 12]))
