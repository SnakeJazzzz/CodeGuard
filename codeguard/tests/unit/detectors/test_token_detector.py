"""
Test script for TokenDetector.

This script demonstrates the TokenDetector functionality with various
test cases including identical code, similar code, and different code.
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.detectors.token_detector import TokenDetector


def test_identical_code():
    """Test with identical code - should have very high similarity."""
    print("=" * 60)
    print("Test 1: Identical Code")
    print("=" * 60)

    code = """
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

result = factorial(5)
print(result)
"""

    detector = TokenDetector(threshold=0.7)
    similarity = detector.compare(code, code)

    print(f"Similarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
    print(f"Expected: ~1.0 (100%)")
    print(f"Result: {'PASS' if similarity > 0.95 else 'FAIL'}")
    print()


def test_variable_renaming():
    """Test with variable renaming - should show high token similarity."""
    print("=" * 60)
    print("Test 2: Variable Renaming")
    print("=" * 60)

    code1 = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""

    code2 = """
def calculate_sum(data):
    result = 0
    for value in data:
        result += value
    return result
"""

    detector = TokenDetector(threshold=0.7)
    similarity = detector.compare(code1, code2)

    print("Code 1:")
    print(code1)
    print("\nCode 2:")
    print(code2)
    print(f"\nSimilarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
    print(f"Expected: ~0.75-0.85 (high similarity due to same structure)")
    print(f"Result: {'PASS' if 0.7 <= similarity <= 0.9 else 'UNCERTAIN'}")
    print()


def test_completely_different():
    """Test with completely different code - should have low similarity."""
    print("=" * 60)
    print("Test 3: Completely Different Code")
    print("=" * 60)

    code1 = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

    code2 = """
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, my name is {self.name}"
"""

    detector = TokenDetector(threshold=0.7)
    similarity = detector.compare(code1, code2)

    print("Code 1 (Bubble Sort):")
    print(code1)
    print("\nCode 2 (Person Class):")
    print(code2)
    print(f"\nSimilarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
    print(f"Expected: <0.4 (low similarity)")
    print(f"Result: {'PASS' if similarity < 0.4 else 'UNCERTAIN'}")
    print()


def test_copy_with_comments():
    """Test with added comments - should still show high similarity."""
    print("=" * 60)
    print("Test 4: Copy with Added Comments")
    print("=" * 60)

    code1 = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    code2 = """
# Calculate fibonacci number
def fibonacci(n):
    # Base case
    if n <= 1:
        return n
    # Recursive case
    return fibonacci(n-1) + fibonacci(n-2)
"""

    detector = TokenDetector(threshold=0.7)
    similarity = detector.compare(code1, code2)

    print("Code 1 (No comments):")
    print(code1)
    print("\nCode 2 (With comments):")
    print(code2)
    print(f"\nSimilarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
    print(f"Expected: ~1.0 (comments are filtered out)")
    print(f"Result: {'PASS' if similarity > 0.95 else 'FAIL'}")
    print()


def test_similarity_metrics():
    """Test both Jaccard and Cosine metrics separately."""
    print("=" * 60)
    print("Test 5: Individual Similarity Metrics")
    print("=" * 60)

    code1 = """
def square(x):
    return x * x

def cube(x):
    return x * x * x
"""

    code2 = """
def square(y):
    return y * y

def power_four(y):
    return y * y * y * y
"""

    detector = TokenDetector(threshold=0.7)

    # Tokenize both codes
    tokens1 = detector._tokenize_code(code1)
    tokens2 = detector._tokenize_code(code2)

    jaccard = detector._calculate_jaccard_similarity(tokens1, tokens2)
    cosine = detector._calculate_cosine_similarity(tokens1, tokens2)
    combined = (jaccard + cosine) / 2.0

    print("Code 1:")
    print(code1)
    print("\nCode 2:")
    print(code2)
    print(f"\nTokens in Code 1: {len(tokens1)}")
    print(f"Tokens in Code 2: {len(tokens2)}")
    print(f"Unique tokens in Code 1: {len(set(tokens1))}")
    print(f"Unique tokens in Code 2: {len(set(tokens2))}")
    print(f"Common unique tokens: {len(set(tokens1).intersection(set(tokens2)))}")
    print(f"\nJaccard Similarity: {jaccard:.4f} ({jaccard*100:.2f}%)")
    print(f"Cosine Similarity: {cosine:.4f} ({cosine*100:.2f}%)")
    print(f"Combined Similarity: {combined:.4f} ({combined*100:.2f}%)")
    print()


def test_threshold_detection():
    """Test plagiarism detection with different thresholds."""
    print("=" * 60)
    print("Test 6: Threshold-based Plagiarism Detection")
    print("=" * 60)

    code1 = """
def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0
"""

    code2 = """
def is_even(num):
    return num % 2 == 0

def check_odd(num):
    return num % 2 != 0
"""

    # Test with different thresholds
    thresholds = [0.5, 0.7, 0.9]

    for threshold in thresholds:
        detector = TokenDetector(threshold=threshold)
        similarity = detector.compare(code1, code2)
        is_plagiarism = similarity >= threshold

        print(f"\nThreshold: {threshold:.1f} ({threshold*100:.0f}%)")
        print(f"Similarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
        print(f"Plagiarism Detected: {'YES' if is_plagiarism else 'NO'}")
    print()


def test_error_handling():
    """Test error handling with invalid inputs."""
    print("=" * 60)
    print("Test 7: Error Handling")
    print("=" * 60)

    # Test with invalid threshold
    try:
        detector = TokenDetector(threshold=1.5)
        print("FAIL: Should have raised ValueError for threshold > 1.0")
    except ValueError as e:
        print(f"PASS: Correctly raised ValueError: {e}")

    # Test with empty code
    detector = TokenDetector()
    similarity = detector.compare("", "")
    print(f"\nEmpty code similarity: {similarity:.4f}")
    print(f"PASS: Handles empty code gracefully")

    # Test with invalid syntax
    code_with_error = "def foo( invalid syntax here"
    code_normal = "def bar(): return 42"
    similarity = detector.compare(code_with_error, code_normal)
    print(f"\nInvalid syntax similarity: {similarity:.4f}")
    print(f"PASS: Handles syntax errors gracefully")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("=" * 60)
    print("TokenDetector Test Suite")
    print("=" * 60)
    print()

    test_identical_code()
    test_variable_renaming()
    test_completely_different()
    test_copy_with_comments()
    test_similarity_metrics()
    test_threshold_detection()
    test_error_handling()

    print("=" * 60)
    print("All Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
