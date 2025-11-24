"""
Merge Sort Implementation

Divide-and-conquer sorting algorithm that divides array into halves,
sorts them recursively, and then merges them back together.

Author: Student J
Date: 2024-11-08
"""


def merge(left, right):
    """
    Merge two sorted arrays into one sorted array.

    Args:
        left (list): First sorted array
        right (list): Second sorted array

    Returns:
        list: Merged sorted array
    """
    result = []
    i = j = 0

    # Compare elements from left and right arrays
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Add remaining elements from left array
    result.extend(left[i:])

    # Add remaining elements from right array
    result.extend(right[j:])

    return result


def merge_sort(arr):
    """
    Sort an array using merge sort algorithm.

    Merge sort divides the array in half, recursively sorts each half,
    then merges them. Time complexity: O(n log n)

    Args:
        arr (list): Array to sort

    Returns:
        list: Sorted array
    """
    # Base case: array with 0 or 1 element is already sorted
    if len(arr) <= 1:
        return arr

    # Divide array into two halves
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # Recursively sort both halves
    sorted_left = merge_sort(left_half)
    sorted_right = merge_sort(right_half)

    # Merge the sorted halves
    return merge(sorted_left, sorted_right)


def merge_sort_with_stats(arr):
    """
    Merge sort that returns both result and comparison count.

    Args:
        arr (list): Array to sort

    Returns:
        tuple: (sorted_array, comparison_count)
    """
    comparisons = [0]  # Use list to allow modification in nested function

    def merge_count(left, right):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            comparisons[0] += 1
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def sort_helper(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = sort_helper(arr[:mid])
        right = sort_helper(arr[mid:])
        return merge_count(left, right)

    sorted_arr = sort_helper(arr)
    return sorted_arr, comparisons[0]


if __name__ == "__main__":
    # Test merge sort
    test_array = [38, 27, 43, 3, 9, 82, 10]

    print("Original array:", test_array)
    sorted_array = merge_sort(test_array)
    print("Sorted array:", sorted_array)

    # Test with statistics
    sorted_with_stats, comp_count = merge_sort_with_stats(test_array)
    print(f"Sorted with {comp_count} comparisons:", sorted_with_stats)

    # Test edge cases
    print("\nEdge cases:")
    print("Empty:", merge_sort([]))
    print("Single:", merge_sort([7]))
    print("Two elements:", merge_sort([5, 2]))
