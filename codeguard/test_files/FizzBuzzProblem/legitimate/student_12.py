# Student 12 - Object-Oriented Programming

"""
OOP solution with FizzBuzz class.
Demonstrates encapsulation and class design.
"""

class FizzBuzzGame:
    """A FizzBuzz game implementation."""

    def __init__(self, start=1, end=100):
        """Initialize the game with a range."""
        self.start = start
        self.end = end

    def evaluate(self, number):
        """Evaluate a single number according to FizzBuzz rules."""
        result = ""
        if number % 3 == 0:
            result += "Fizz"
        if number % 5 == 0:
            result += "Buzz"
        return result if result else str(number)

    def play(self):
        """Play the game and print results."""
        for num in range(self.start, self.end + 1):
            print(self.evaluate(num))

if __name__ == "__main__":
    game = FizzBuzzGame()
    game.play()
