# Student 6 - Nested Conditionals

"""
FizzBuzz with deeply nested if statements.
Different control flow structure than typical solutions.
"""

def fizzbuzz():
    for number in range(1, 101):
        if number % 5 == 0:
            if number % 3 == 0:
                print("FizzBuzz")
            else:
                print("Buzz")
        else:
            if number % 3 == 0:
                print("Fizz")
            else:
                print(number)

if __name__ == "__main__":
    fizzbuzz()
