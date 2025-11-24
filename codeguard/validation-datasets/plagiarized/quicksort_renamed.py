"""
QuickSort Algorithm - My Implementation

Sorting algorithm using divide and conquer approach.
Uses last element as pivot for partitioning.

Author: Student F
Date: 2024-11-04
"""


def divide_array(data, start, end):
    """
    Partition array around pivot value.

    Args:
        data (list): List to partition
        start (int): First index
        end (int): Last index

    Returns:
        int: Position of pivot after partitioning
    """
    # Select last element as pivot
    pivot_value = data[end]

    # Index for smaller elements
    smaller_idx = start - 1

    # Check all elements
    for current_idx in range(start, end):
        # Compare with pivot
        if data[current_idx] < pivot_value:
            # Move smaller element pointer
            smaller_idx = smaller_idx + 1
            # Exchange elements
            data[smaller_idx], data[current_idx] = data[current_idx], data[smaller_idx]

    # Place pivot in correct position
    data[smaller_idx + 1], data[end] = data[end], data[smaller_idx + 1]

    return smaller_idx + 1


def quick_sort_recursive(data, start, end):
    """
    Recursively sort array using QuickSort.

    Args:
        data (list): List to sort
        start (int): First index
        end (int): Last index
    """
    if start < end:
        # Get partition position
        partition_idx = divide_array(data, start, end)

        # Sort left and right subarrays
        quick_sort_recursive(data, start, partition_idx - 1)
        quick_sort_recursive(data, partition_idx + 1, end)


def perform_sort(input_list):
    """
    Main sorting function.

    Args:
        input_list (list): List to sort

    Returns:
        list: Sorted list
    """
    # Create copy to preserve original
    result_list = input_list.copy()
    quick_sort_recursive(result_list, 0, len(result_list) - 1)
    return result_list


if __name__ == "__main__":
    # Test sorting
    numbers = [64, 34, 25, 12, 22, 11, 90, 88]

    print("Original array:", numbers)
    sorted_numbers = perform_sort(numbers)
    print("Sorted array:", sorted_numbers)

    # More tests
    print("\nAdditional tests:")
    print("Empty array:", perform_sort([]))
    print("Single element:", perform_sort([42]))
    print("Already sorted:", perform_sort([1, 2, 3, 4, 5]))
    print("Reverse sorted:", perform_sort([5, 4, 3, 2, 1]))
