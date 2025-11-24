"""
Bubble Sort Implementation

Simple comparison-based sorting algorithm that repeatedly steps through
the list, compares adjacent elements and swaps them if they are in wrong order.

Author: Student I
Date: 2024-11-07
"""


def bubble_sort(arr):
    """
    Sort an array using bubble sort algorithm.

    Bubble sort works by repeatedly swapping adjacent elements
    if they are in wrong order. Time complexity: O(n^2)

    Args:
        arr (list): List to sort

    Returns:
        list: Sorted list
    """
    # Make a copy to avoid modifying original
    result = arr.copy()
    n = len(result)

    # Traverse through all array elements
    for i in range(n):
        # Flag to optimize by detecting if array is already sorted
        swapped = False

        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Swap if the element found is greater than the next element
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        # If no swapping occurred, array is sorted
        if not swapped:
            break

    return result


def bubble_sort_descending(arr):
    """
    Sort array in descending order using bubble sort.

    Args:
        arr (list): List to sort

    Returns:
        list: List sorted in descending order
    """
    result = arr.copy()
    n = len(result)

    for i in range(n):
        for j in range(0, n - i - 1):
            # Reverse comparison for descending order
            if result[j] < result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]

    return result


if __name__ == "__main__":
    # Test bubble sort
    test_data = [64, 34, 25, 12, 22, 11, 90]

    print("Original array:", test_data)
    print("Sorted ascending:", bubble_sort(test_data))
    print("Sorted descending:", bubble_sort_descending(test_data))

    # Test edge cases
    print("\nEdge cases:")
    print("Empty:", bubble_sort([]))
    print("Single element:", bubble_sort([42]))
    print("Already sorted:", bubble_sort([1, 2, 3, 4, 5]))
