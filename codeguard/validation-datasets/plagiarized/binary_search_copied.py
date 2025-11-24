"""
Binary Search Implementation - Original Submission

This module implements a binary search algorithm for finding elements
in sorted lists. Student submission for Algorithm Analysis course.

Author: Student D
Date: 2024-11-01
"""


def binary_search(arr, target):
    """
    Perform binary search on a sorted array.

    Args:
        arr (list): Sorted list of comparable elements
        target: Element to search for

    Returns:
        int: Index of target if found, -1 otherwise
    """
    left = 0
    right = len(arr) - 1

    while left <= right:
        # Calculate middle index
        mid = (left + right) // 2

        # Check if target is at middle
        if arr[mid] == target:
            return mid

        # Target is in right half
        elif arr[mid] < target:
            left = mid + 1

        # Target is in left half
        else:
            right = mid - 1

    # Not found
    return -1


def test_binary_search():
    """Test cases for binary search implementation."""
    test_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    # Test finding existing elements
    assert binary_search(test_array, 7) == 3
    assert binary_search(test_array, 1) == 0
    assert binary_search(test_array, 19) == 9

    # Test non-existing elements
    assert binary_search(test_array, 4) == -1
    assert binary_search(test_array, 20) == -1

    print("All binary search tests passed!")


if __name__ == "__main__":
    test_binary_search()

    # Demonstration
    numbers = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    search_for = 12
    result = binary_search(numbers, search_for)

    if result != -1:
        print(f"Found {search_for} at index {result}")
    else:
        print(f"{search_for} not found in list")
