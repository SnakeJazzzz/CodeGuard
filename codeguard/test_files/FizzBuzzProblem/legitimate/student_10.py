# Student 10 - Dictionary Lookup Approach

"""
Data-driven solution using dictionaries.
Demonstrates separation of logic from data.
"""

def fizzbuzz():
    # Pre-compute all special cases
    special_values = {}

    for i in range(1, 101):
        if i % 15 == 0:
            special_values[i] = "FizzBuzz"
        elif i % 3 == 0:
            special_values[i] = "Fizz"
        elif i % 5 == 0:
            special_values[i] = "Buzz"

    # Print using dictionary lookup
    for i in range(1, 101):
        print(special_values.get(i, i))

if __name__ == "__main__":
    fizzbuzz()
