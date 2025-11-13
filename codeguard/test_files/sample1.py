"""
Sample Python file 1 for testing CodeGuard
"""

def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if len(numbers) == 0:
        return 0
    return calculate_sum(numbers) / len(numbers)

if __name__ == "__main__":
    data = [1, 2, 3, 4, 5]
    print(f"Sum: {calculate_sum(data)}")
    print(f"Average: {calculate_average(data)}")
