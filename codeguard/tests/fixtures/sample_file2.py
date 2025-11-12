"""Sample Python file 2 - Similar to file 1 with variable renaming."""


def binary_search(array, value):
    """Binary search with renamed variables."""
    start = 0
    end = len(array) - 1

    while start <= end:
        middle = (start + end) // 2

        if array[middle] == value:
            return middle
        elif array[middle] < value:
            start = middle + 1
        else:
            end = middle - 1

    return -1


def linear_search(data, item):
    """Linear search with renamed variables."""
    for index in range(len(data)):
        if data[index] == item:
            return index
    return -1


if __name__ == "__main__":
    values = [1, 3, 5, 7, 9, 11, 13, 15]
    found = binary_search(values, 7)
    print(f"Found at index: {found}")
