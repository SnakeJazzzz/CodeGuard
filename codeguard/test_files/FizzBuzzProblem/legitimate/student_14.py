# Student 14 - String Concatenation

"""
Build output string incrementally using concatenation.
Different logical flow from standard solutions.
"""

def fizzbuzz():
    for val in range(1, 101):
        message = ""

        # Check divisibility by 3
        if val % 3 == 0:
            message = message + "Fizz"

        # Check divisibility by 5
        if val % 5 == 0:
            message = message + "Buzz"

        # If no special case, use the number
        if not message:
            message = str(val)

        print(message)

if __name__ == "__main__":
    fizzbuzz()
