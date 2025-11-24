"""
Sequential Search Module

Implementation of sequential search with various helper functions.

Author: Student N
Date: 2024-11-12
"""


def find_element(data_list, search_value):
    """
    Find element in list using sequential approach.

    Args:
        data_list (list): Collection to search
        search_value: Item to locate

    Returns:
        int: Position of item if found, -1 if not found
    """
    # Loop through indices
    for pos in range(len(data_list)):
        # Compare current item with search value
        if data_list[pos] == search_value:
            return pos

    # Item not in list
    return -1


def find_all_positions(data_list, search_value):
    """
    Locate all positions where value appears.

    Args:
        data_list (list): Collection to search
        search_value: Item to locate

    Returns:
        list: All positions where item appears
    """
    positions = []

    for pos in range(len(data_list)):
        if data_list[pos] == search_value:
            positions.append(pos)

    return positions


def tally_matches(data_list, search_value):
    """
    Tally occurrences of value in list.

    Args:
        data_list (list): Collection to examine
        search_value: Item to tally

    Returns:
        int: Total occurrences
    """
    tally = 0

    for item in data_list:
        if item == search_value:
            tally += 1

    return tally


if __name__ == "__main__":
    # Demonstration
    numbers = [5, 3, 7, 1, 9, 3, 2, 8, 3]

    print("Array:", numbers)
    print("Search for 7:", find_element(numbers, 7))
    print("Search for 10:", find_element(numbers, 10))

    print("\nAll occurrences of 3:", find_all_positions(numbers, 3))
    print("Count of 3:", tally_matches(numbers, 3))
