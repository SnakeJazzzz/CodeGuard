# Student 4 - Advanced Implementation

def check_fizzbuzz(n):
    if n % 3 == 0 and n % 5 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return n

def main():
    for i in range(1, 101):
        result = check_fizzbuzz(i)
        print(result)

if __name__ == "__main__":
    main()
