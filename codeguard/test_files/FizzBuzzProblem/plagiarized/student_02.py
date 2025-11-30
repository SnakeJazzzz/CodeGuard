# Student 2 - Well-Commented Solution

def fizzbuzz():
    """
    FizzBuzz implementation that prints numbers from 1 to 100.
    Numbers divisible by 3 print 'Fizz', by 5 print 'Buzz',
    and by both print 'FizzBuzz'.
    """
    # Iterate through all numbers from 1 to 100
    for index in range(1, 101):
        # Check if the number is divisible by both 3 and 5
        if index % 3 == 0 and index % 5 == 0:
            # Print FizzBuzz for multiples of 15
            print("FizzBuzz")
        # Check if the number is divisible by 3
        elif index % 3 == 0:
            # Print Fizz for multiples of 3
            print("Fizz")
        # Check if the number is divisible by 5
        elif index % 5 == 0:
            # Print Buzz for multiples of 5
            print("Buzz")
        # If none of the above conditions are met
        else:
            # Print the number itself
            print(index)

# Main entry point
if __name__ == "__main__":
    # Execute the fizzbuzz function
    fizzbuzz()
