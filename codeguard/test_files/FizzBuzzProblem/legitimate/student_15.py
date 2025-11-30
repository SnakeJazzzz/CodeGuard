# Student 15 - While Loop Implementation

"""
Using while loop instead of for loop.
Different iteration pattern.
"""

def fizzbuzz():
    counter = 1

    while counter <= 100:
        is_fizz = counter % 3 == 0
        is_buzz = counter % 5 == 0

        if is_fizz and is_buzz:
            print("FizzBuzz")
        elif is_fizz:
            print("Fizz")
        elif is_buzz:
            print("Buzz")
        else:
            print(counter)

        counter = counter + 1

if __name__ == "__main__":
    fizzbuzz()
