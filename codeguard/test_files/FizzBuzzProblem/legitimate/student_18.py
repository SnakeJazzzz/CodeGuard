# Student 18 - Using Divmod Function

"""
Leverages divmod for efficient modulo and division.
Shows understanding of built-in functions.
"""

def fizzbuzz():
    for number in range(1, 101):
        div3, mod3 = divmod(number, 3)
        div5, mod5 = divmod(number, 5)

        fizz = mod3 == 0
        buzz = mod5 == 0

        if fizz and buzz:
            print("FizzBuzz")
        elif fizz:
            print("Fizz")
        elif buzz:
            print("Buzz")
        else:
            print(number)

if __name__ == "__main__":
    fizzbuzz()
