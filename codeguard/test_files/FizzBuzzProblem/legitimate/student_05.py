# Student 5 - String Multiplication Approach

"""
FizzBuzz using string multiplication trick.
Clever use of boolean evaluation to build strings.
"""

def fizzbuzz():
    for n in range(1, 101):
        output = ("Fizz" * (n % 3 == 0)) + ("Buzz" * (n % 5 == 0))
        print(output or n)

if __name__ == "__main__":
    fizzbuzz()
