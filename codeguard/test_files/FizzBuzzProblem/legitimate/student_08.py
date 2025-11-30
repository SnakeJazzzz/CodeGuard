# Student 8 - Generator Function

"""
Memory-efficient solution using generator with yield.
Good for processing large sequences without storing all values.
"""

def fizzbuzz_generator(start=1, end=100):
    """Generator that yields FizzBuzz values."""
    for num in range(start, end + 1):
        if num % 15 == 0:
            yield "FizzBuzz"
        elif num % 3 == 0:
            yield "Fizz"
        elif num % 5 == 0:
            yield "Buzz"
        else:
            yield num

def main():
    for value in fizzbuzz_generator():
        print(value)

if __name__ == "__main__":
    main()
