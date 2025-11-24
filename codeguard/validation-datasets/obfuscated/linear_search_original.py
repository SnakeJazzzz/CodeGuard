"""
Linear Search Implementation

Simple search algorithm that checks every element in a sequence
until the target is found or the sequence ends.

Author: Student M
Date: 2024-11-11
"""


def linear_search(array, target):
    """
    Perform linear search on an array.

    Iterates through each element sequentially until target is found.

    Args:
        array (list): List to search through
        target: Element to find

    Returns:
        int: Index of target if found, -1 otherwise
    """
    # Iterate through each index
    for index in range(len(array)):
        # Check if current element matches target
        if array[index] == target:
            return index

    # Target not found
    return -1


def linear_search_all(array, target):
    """
    Find all occurrences of target in array.

    Args:
        array (list): List to search through
        target: Element to find

    Returns:
        list: List of indices where target appears
    """
    indices = []

    for index in range(len(array)):
        if array[index] == target:
            indices.append(index)

    return indices


def count_occurrences(array, target):
    """
    Count how many times target appears in array.

    Args:
        array (list): List to search
        target: Element to count

    Returns:
        int: Number of occurrences
    """
    count = 0

    for element in array:
        if element == target:
            count += 1

    return count


if __name__ == "__main__":
    # Test linear search
    test_array = [5, 3, 7, 1, 9, 3, 2, 8, 3]

    print("Array:", test_array)
    print("Search for 7:", linear_search(test_array, 7))
    print("Search for 10:", linear_search(test_array, 10))

    print("\nAll occurrences of 3:", linear_search_all(test_array, 3))
    print("Count of 3:", count_occurrences(test_array, 3))
