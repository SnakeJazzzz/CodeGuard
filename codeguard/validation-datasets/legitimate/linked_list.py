"""
Linked List Implementation

A singly linked list data structure with common operations like
insertion, deletion, and search.

Author: Student K
Date: 2024-11-09
"""


class Node:
    """Node class for linked list elements."""

    def __init__(self, data):
        """
        Initialize a node.

        Args:
            data: Value to store in the node
        """
        self.data = data
        self.next = None


class LinkedList:
    """Singly linked list implementation."""

    def __init__(self):
        """Initialize an empty linked list."""
        self.head = None
        self.size = 0

    def append(self, data):
        """
        Add a new node at the end of the list.

        Args:
            data: Value to add to the list
        """
        new_node = Node(data)

        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

        self.size += 1

    def prepend(self, data):
        """
        Add a new node at the beginning of the list.

        Args:
            data: Value to add to the list
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def delete(self, data):
        """
        Remove first occurrence of node with given data.

        Args:
            data: Value to remove from list

        Returns:
            bool: True if deleted, False if not found
        """
        if not self.head:
            return False

        # If head needs to be deleted
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True

        # Search for node to delete
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next

        return False

    def search(self, data):
        """
        Search for a value in the list.

        Args:
            data: Value to search for

        Returns:
            bool: True if found, False otherwise
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def to_list(self):
        """
        Convert linked list to Python list.

        Returns:
            list: Python list containing all elements
        """
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def __len__(self):
        """Return the size of the list."""
        return self.size

    def __str__(self):
        """String representation of the list."""
        return " -> ".join(str(x) for x in self.to_list())


if __name__ == "__main__":
    # Create and test linked list
    ll = LinkedList()

    print("Adding elements: 1, 2, 3")
    ll.append(1)
    ll.append(2)
    ll.append(3)
    print("List:", ll)

    print("\nPrepending 0")
    ll.prepend(0)
    print("List:", ll)

    print("\nSearching for 2:", ll.search(2))
    print("Searching for 5:", ll.search(5))

    print("\nDeleting 2")
    ll.delete(2)
    print("List:", ll)
    print("Size:", len(ll))
