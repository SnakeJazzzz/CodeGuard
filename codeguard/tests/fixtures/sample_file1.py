"""Sample Python file 1 for testing TokenDetector."""


def binary_search(arr, target):
    """Binary search implementation."""
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def linear_search(arr, target):
    """Linear search implementation."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1


if __name__ == "__main__":
    numbers = [1, 3, 5, 7, 9, 11, 13, 15]
    result = binary_search(numbers, 7)
    print(f"Found at index: {result}")
