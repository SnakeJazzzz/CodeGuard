# Student 13 - Recursive Approach

"""
Recursive implementation of FizzBuzz.
Not the most efficient, but demonstrates recursion understanding.
"""

def fizzbuzz_recursive(current=1, end=100):
    """Recursive FizzBuzz implementation."""
    if current > end:
        return

    # Determine what to print
    output = ""
    if current % 3 == 0:
        output += "Fizz"
    if current % 5 == 0:
        output += "Buzz"

    print(output if output else current)

    # Recursive call
    fizzbuzz_recursive(current + 1, end)

if __name__ == "__main__":
    fizzbuzz_recursive()
