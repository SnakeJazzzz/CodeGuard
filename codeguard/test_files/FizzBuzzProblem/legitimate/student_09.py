# Student 9 - Functional Style with Map and Lambda

"""
Pure functional programming approach.
Uses map, lambda, and function composition.
"""

def fizzbuzz():
    # Define transformation function
    transform = lambda x: "FizzBuzz" if x % 15 == 0 else \
                         "Fizz" if x % 3 == 0 else \
                         "Buzz" if x % 5 == 0 else x

    # Apply to range and print
    list(map(lambda x: print(x), map(transform, range(1, 101))))

if __name__ == "__main__":
    fizzbuzz()
