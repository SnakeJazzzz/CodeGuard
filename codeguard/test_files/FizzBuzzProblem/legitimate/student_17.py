# Student 17 - Chained Ternary Operators

"""
Compact solution using nested ternary operators.
One-liner approach with complex conditionals.
"""

def fizzbuzz():
    for n in range(1, 101):
        print(
            "FizzBuzz" if n % 15 == 0 else
            "Fizz" if n % 3 == 0 else
            "Buzz" if n % 5 == 0 else
            n
        )

if __name__ == "__main__":
    fizzbuzz()
