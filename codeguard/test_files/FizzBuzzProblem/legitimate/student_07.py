# Student 7 - List Comprehension

"""
Functional programming approach using list comprehension.
Demonstrates understanding of Python's functional features.
"""

def get_fizzbuzz_value(n):
    """Returns the FizzBuzz value for a given number."""
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)

def fizzbuzz():
    results = [get_fizzbuzz_value(i) for i in range(1, 101)]
    for result in results:
        print(result)

if __name__ == "__main__":
    fizzbuzz()
