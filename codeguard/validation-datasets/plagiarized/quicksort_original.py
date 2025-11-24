"""
QuickSort Algorithm Implementation

Implementation of the QuickSort divide-and-conquer sorting algorithm.
Uses the Lomuto partition scheme with last element as pivot.

Author: Student E
Date: 2024-11-03
"""


def partition(array, low, high):
    """
    Partition the array around a pivot element.

    Args:
        array (list): Array to partition
        low (int): Starting index
        high (int): Ending index

    Returns:
        int: Final position of the pivot element
    """
    # Choose the rightmost element as pivot
    pivot = array[high]

    # Pointer for smaller element
    i = low - 1

    # Traverse through all elements
    for j in range(low, high):
        # If current element is smaller than pivot
        if array[j] < pivot:
            # Increment index of smaller element
            i = i + 1
            # Swap elements
            array[i], array[j] = array[j], array[i]

    # Swap the pivot element with element at i+1
    array[i + 1], array[high] = array[high], array[i + 1]

    return i + 1


def quicksort(array, low, high):
    """
    Sort an array using QuickSort algorithm.

    Args:
        array (list): Array to sort
        low (int): Starting index
        high (int): Ending index
    """
    if low < high:
        # Find partition index
        pi = partition(array, low, high)

        # Recursively sort elements before and after partition
        quicksort(array, low, pi - 1)
        quicksort(array, pi + 1, high)


def sort_array(arr):
    """
    Convenience function to sort an array.

    Args:
        arr (list): Array to sort

    Returns:
        list: Sorted array
    """
    # Make a copy to avoid modifying original
    sorted_arr = arr.copy()
    quicksort(sorted_arr, 0, len(sorted_arr) - 1)
    return sorted_arr


if __name__ == "__main__":
    # Test the quicksort implementation
    test_data = [64, 34, 25, 12, 22, 11, 90, 88]

    print("Original array:", test_data)
    sorted_data = sort_array(test_data)
    print("Sorted array:", sorted_data)

    # Additional test cases
    print("\nAdditional tests:")
    print("Empty array:", sort_array([]))
    print("Single element:", sort_array([42]))
    print("Already sorted:", sort_array([1, 2, 3, 4, 5]))
    print("Reverse sorted:", sort_array([5, 4, 3, 2, 1]))
