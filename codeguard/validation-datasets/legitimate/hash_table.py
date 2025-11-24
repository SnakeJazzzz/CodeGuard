"""
Hash Table Implementation

Custom hash table (dictionary) implementation using separate chaining
for collision resolution.

Author: Student L
Date: 2024-11-10
"""


class HashTable:
    """
    Hash table with separate chaining for collision resolution.

    Uses Python lists to store multiple items that hash to the same bucket.
    """

    def __init__(self, capacity=10):
        """
        Initialize hash table with given capacity.

        Args:
            capacity (int): Initial number of buckets
        """
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _hash(self, key):
        """
        Compute hash value for a key.

        Args:
            key: Key to hash

        Returns:
            int: Bucket index
        """
        return hash(key) % self.capacity

    def put(self, key, value):
        """
        Insert or update a key-value pair.

        Args:
            key: Key to insert/update
            value: Value to associate with key
        """
        bucket_index = self._hash(key)
        bucket = self.buckets[bucket_index]

        # Check if key already exists and update
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # Key doesn't exist, add new pair
        bucket.append((key, value))
        self.size += 1

        # Check if rehashing is needed
        if self.size / self.capacity > 0.7:
            self._rehash()

    def get(self, key, default=None):
        """
        Retrieve value for a given key.

        Args:
            key: Key to look up
            default: Default value if key not found

        Returns:
            Value associated with key, or default if not found
        """
        bucket_index = self._hash(key)
        bucket = self.buckets[bucket_index]

        for k, v in bucket:
            if k == key:
                return v

        return default

    def remove(self, key):
        """
        Remove a key-value pair.

        Args:
            key: Key to remove

        Returns:
            bool: True if removed, False if key not found
        """
        bucket_index = self._hash(key)
        bucket = self.buckets[bucket_index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True

        return False

    def _rehash(self):
        """Increase capacity and rehash all items."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def keys(self):
        """
        Get all keys in the hash table.

        Returns:
            list: List of all keys
        """
        result = []
        for bucket in self.buckets:
            for key, value in bucket:
                result.append(key)
        return result

    def __len__(self):
        """Return number of items in hash table."""
        return self.size

    def __str__(self):
        """String representation of hash table."""
        items = []
        for bucket in self.buckets:
            for key, value in bucket:
                items.append(f"{key}: {value}")
        return "{" + ", ".join(items) + "}"


if __name__ == "__main__":
    # Test hash table
    ht = HashTable(capacity=5)

    print("Inserting key-value pairs")
    ht.put("name", "Alice")
    ht.put("age", 25)
    ht.put("city", "New York")
    ht.put("country", "USA")

    print("Hash table:", ht)
    print("Size:", len(ht))

    print("\nGetting values:")
    print("name:", ht.get("name"))
    print("age:", ht.get("age"))
    print("missing:", ht.get("missing", "Not found"))

    print("\nRemoving 'city'")
    ht.remove("city")
    print("Hash table:", ht)

    print("\nAll keys:", ht.keys())
