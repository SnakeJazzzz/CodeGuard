# Student 16 - Tuple Unpacking with Divmod

"""
Creative use of tuple unpacking and enumeration.
Shows advanced Python features.
"""

def fizzbuzz():
    numbers = list(range(1, 101))

    for idx, n in enumerate(numbers, start=1):
        quotient_3, remainder_3 = divmod(idx, 3)
        quotient_5, remainder_5 = divmod(idx, 5)

        result = ""
        result += "Fizz" if remainder_3 == 0 else ""
        result += "Buzz" if remainder_5 == 0 else ""

        print(result or idx)

if __name__ == "__main__":
    fizzbuzz()
