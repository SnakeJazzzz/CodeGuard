"""
Sample Python file 2 for testing CodeGuard
This file is similar to sample1.py with minor changes
"""

def calculate_sum(values):
    """Calculate the sum of a list of values."""
    result = 0
    for value in values:
        result += value
    return result

def calculate_average(values):
    """Calculate the average of a list of values."""
    if len(values) == 0:
        return 0
    return calculate_sum(values) / len(values)

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5]
    print(f"Sum: {calculate_sum(numbers)}")
    print(f"Average: {calculate_average(numbers)}")
