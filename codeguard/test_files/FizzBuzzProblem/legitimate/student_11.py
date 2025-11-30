# Student 11 - Pattern Matching (Python 3.10+)

"""
Modern Python solution using match-case statement.
Demonstrates knowledge of Python 3.10+ features.
"""

def classify_number(n):
    """Classify a number for FizzBuzz using pattern matching."""
    divisible_by_3 = (n % 3 == 0)
    divisible_by_5 = (n % 5 == 0)

    match (divisible_by_3, divisible_by_5):
        case (True, True):
            return "FizzBuzz"
        case (True, False):
            return "Fizz"
        case (False, True):
            return "Buzz"
        case _:
            return n

def fizzbuzz():
    for i in range(1, 101):
        print(classify_number(i))

if __name__ == "__main__":
    fizzbuzz()
