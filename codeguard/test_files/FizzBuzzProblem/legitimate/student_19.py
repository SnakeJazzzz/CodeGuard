# Student 19 - Iterator Protocol

"""
Custom iterator class implementing __iter__ and __next__.
Advanced OOP with iterator protocol.
"""

class FizzBuzzIterator:
    """Iterator that generates FizzBuzz sequence."""

    def __init__(self, limit=100):
        self.limit = limit
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration

        value = self.current
        self.current += 1

        # Calculate result
        if value % 3 == 0 and value % 5 == 0:
            return "FizzBuzz"
        elif value % 3 == 0:
            return "Fizz"
        elif value % 5 == 0:
            return "Buzz"
        else:
            return value

def main():
    fizzbuzz_iter = FizzBuzzIterator()
    for item in fizzbuzz_iter:
        print(item)

if __name__ == "__main__":
    main()
