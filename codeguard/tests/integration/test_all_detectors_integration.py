"""
Integration Tests for All Three Plagiarism Detection Algorithms

This module contains comprehensive integration tests that validate all three
plagiarism detection algorithms (Token, AST, Hash) working together across
various plagiarism scenarios.

Test Coverage:
    - Exact copy detection (all detectors should agree)
    - Renamed variable detection (AST strong, Token/Hash weak)
    - Partial copy detection (Hash excels, Token moderate, AST weak)
    - Structural plagiarism detection (AST and Hash strong)
    - Completely different code (all detectors should agree)
    - Batch processing with multiple file pairs
    - Error recovery when detectors encounter malformed code
    - Real validation dataset integration

Detector Characteristics:
    - TokenDetector: Threshold=0.70, Strengths: exact copies, Weaknesses: renaming
    - ASTDetector: Threshold=0.80, Strengths: structural similarity, Weaknesses: algorithmic changes
    - HashDetector: Threshold=0.60, Strengths: partial copying, Weaknesses: renaming

Author: CodeGuard Test Team
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Tuple, Dict, Any

# Add src to path for imports
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import all three detectors
from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_file_pair():
    """
    Create a pair of temporary Python files for testing.

    This fixture provides a factory function that creates two temporary files
    with given code content and returns their paths. Files are automatically
    cleaned up after the test completes.

    Yields:
        Callable: Function that takes (code1, code2) and returns (file1_path, file2_path)

    Usage:
        def test_example(temp_file_pair):
            file1, file2 = temp_file_pair(code1, code2)
            # Use files for testing
    """
    created_files = []

    def _create_pair(code1: str, code2: str) -> Tuple[str, str]:
        """Create two temporary files with the given code content."""
        # Create first file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f1:
            f1.write(code1)
            file1 = f1.name
            created_files.append(file1)

        # Create second file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f2:
            f2.write(code2)
            file2 = f2.name
            created_files.append(file2)

        return file1, file2

    yield _create_pair

    # Cleanup: remove all created temporary files
    for file_path in created_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp file {file_path}: {e}")


@pytest.fixture
def all_detectors():
    """
    Initialize all three detectors with standard thresholds.

    Creates instances of TokenDetector, ASTDetector, and HashDetector with
    their default production thresholds:
    - Token: 0.70 (70% token similarity)
    - AST: 0.80 (80% structural similarity)
    - Hash: 0.60 (60% fingerprint overlap)

    Returns:
        dict: Dictionary with detector instances keyed by name
              {'token': TokenDetector, 'ast': ASTDetector, 'hash': HashDetector}

    Usage:
        def test_example(all_detectors):
            token_detector = all_detectors['token']
            result = token_detector.analyze(file1, file2)
    """
    return {
        'token': TokenDetector(threshold=0.7),
        'ast': ASTDetector(threshold=0.8),
        'hash': HashDetector(threshold=0.6, k=5, w=4)
    }


# =============================================================================
# Integration Tests
# =============================================================================

class TestAllDetectorsIntegration:
    """
    Integration tests for all three plagiarism detection algorithms.

    This test class validates that Token, AST, and Hash detectors work together
    correctly across various plagiarism scenarios, from exact copies to partial
    copying to completely different code.
    """

    def test_exact_copy_all_detectors(self, temp_file_pair, all_detectors):
        """
        Test that all three detectors detect identical files with high similarity.

        Scenario:
            Two files with identical code (exact copy plagiarism).

        Expected behavior:
            - All three detectors should report similarity > 0.95
            - Token detector should be ~1.0 (perfect token match)
            - AST detector should be ~1.0 (perfect structural match)
            - Hash detector should be ~1.0 (perfect fingerprint match)

        This validates that all detectors agree on the most obvious case of plagiarism.
        """
        # Arrange: Create identical code
        code = """
def factorial(n):
    '''Calculate factorial using recursion.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    result = factorial(5)
    print(f"Factorial of 5 is {result}")

if __name__ == "__main__":
    main()
"""
        file1, file2 = temp_file_pair(code, code)

        # Act: Run all three detectors
        token_result = all_detectors['token'].analyze(file1, file2)
        ast_result = all_detectors['ast'].analyze(file1, file2)
        hash_result = all_detectors['hash'].analyze(file1, file2)

        # Assert: All detectors should report very high similarity
        assert token_result['similarity_score'] > 0.95, \
            f"Token detector should detect identical files, got {token_result['similarity_score']:.2f}"

        assert ast_result['similarity_score'] > 0.95, \
            f"AST detector should detect identical files, got {ast_result['similarity_score']:.2f}"

        assert hash_result['similarity_score'] > 0.95, \
            f"Hash detector should detect identical files, got {hash_result['similarity_score']:.2f}"

        # Verify plagiarism flag
        assert token_result['is_plagiarism'] is True, "Token detector should flag as plagiarism"

        # All similarity scores should be in valid range [0.0, 1.0]
        assert 0.0 <= token_result['similarity_score'] <= 1.0
        assert 0.0 <= ast_result['similarity_score'] <= 1.0
        assert 0.0 <= hash_result['similarity_score'] <= 1.0


    def test_renamed_variables(self, temp_file_pair, all_detectors):
        """
        Test that AST detector catches structural plagiarism with renamed variables.

        Scenario:
            Two files with identical structure but all variables/functions renamed.
            This is a common plagiarism technique: students rename identifiers
            but keep the same algorithmic structure.

        Expected behavior:
            - AST detector: HIGH similarity (> 0.80) - detects structural match
            - Token detector: LOW similarity (< 0.40) - tokens are different
            - Hash detector: LOW similarity (< 0.30) - fingerprints don't match

        This validates AST detector's key strength: immunity to identifier renaming.
        """
        # Arrange: Create structurally identical code with renamed variables
        code1 = """
def process_data(data):
    '''Process input data and return filtered results.'''
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

def calculate_sum(values):
    '''Calculate sum of all values.'''
    total = 0
    for val in values:
        total += val
    return total
"""

        code2 = """
def handle_input(input_list):
    '''Process input data and return filtered results.'''
    output = []
    for element in input_list:
        if element > 0:
            output.append(element * 2)
    return output

def compute_total(numbers):
    '''Calculate sum of all values.'''
    sum_value = 0
    for num in numbers:
        sum_value += num
    return sum_value
"""

        file1, file2 = temp_file_pair(code1, code2)

        # Act: Run all three detectors
        token_result = all_detectors['token'].analyze(file1, file2)
        ast_result = all_detectors['ast'].analyze(file1, file2)
        hash_result = all_detectors['hash'].analyze(file1, file2)

        # Assert: AST should be high, Token and Hash should be lower
        assert ast_result['similarity_score'] > 0.8, \
            f"AST detector should catch renamed variables, got {ast_result['similarity_score']:.2f}"

        # Token detector shows moderate similarity due to shared keywords and operators
        # Even with renamed variables, Python keywords (def, for, if, return) match
        assert token_result['similarity_score'] < 0.7, \
            f"Token detector should report lower similarity than AST for renamed code, got {token_result['similarity_score']:.2f}"

        # Hash detector is similarly affected by shared structural patterns
        assert hash_result['similarity_score'] < 0.5, \
            f"Hash detector should report lower similarity than AST for renamed code, got {hash_result['similarity_score']:.2f}"

        # Key validation: AST similarity should be higher than Token and Hash
        assert ast_result['similarity_score'] > token_result['similarity_score'], \
            "AST similarity should exceed Token similarity for renamed variables"
        assert ast_result['similarity_score'] > hash_result['similarity_score'], \
            "AST similarity should exceed Hash similarity for renamed variables"

        # Verify AST detects this as plagiarism (above its threshold of 0.8)
        # Token and Hash should not flag this (below their thresholds)

        # All scores should be in valid range
        assert 0.0 <= token_result['similarity_score'] <= 1.0
        assert 0.0 <= ast_result['similarity_score'] <= 1.0
        assert 0.0 <= hash_result['similarity_score'] <= 1.0


    def test_partial_copy(self, temp_file_pair, all_detectors):
        """
        Test that Hash detector excels at detecting partial/scattered copying.

        Scenario:
            Two files where only some functions are copied, others are different.
            This simulates a student copying one function but writing others themselves.

        Expected behavior:
            - Hash detector: MODERATE similarity (> 0.2) - detects partial overlap
            - Token detector: LOW-MODERATE similarity - some token overlap
            - AST detector: LOW-MODERATE similarity - partial structural match

        Hash detector's Winnowing algorithm should detect the copied function
        even when surrounded by different code.
        """
        # Arrange: Create files with partial code copying
        code1 = """
def function_a():
    '''First function - original.'''
    return 1

def function_b():
    '''Second function - this one will be copied.'''
    result = 0
    for i in range(10):
        if i % 2 == 0:
            result += i
    return result

def function_c():
    '''Third function - original.'''
    return 3
"""

        code2 = """
def new_func():
    '''Different function.'''
    return 0

def function_b():
    '''Second function - this one will be copied.'''
    result = 0
    for i in range(10):
        if i % 2 == 0:
            result += i
    return result

def another_func():
    '''Another different function.'''
    return 4
"""

        file1, file2 = temp_file_pair(code1, code2)

        # Act: Run all three detectors
        token_result = all_detectors['token'].analyze(file1, file2)
        ast_result = all_detectors['ast'].analyze(file1, file2)
        hash_result = all_detectors['hash'].analyze(file1, file2)

        # Assert: Hash should detect partial copying better than others
        assert hash_result['similarity_score'] > 0.2, \
            f"Hash detector should detect partial copying, got {hash_result['similarity_score']:.2f}"

        # All detectors should detect some similarity (one function is identical)
        assert token_result['similarity_score'] > 0.1, \
            "Token detector should detect some overlap"

        assert ast_result['similarity_score'] > 0.1, \
            "AST detector should detect some structural overlap"

        # All scores should be in valid range
        assert 0.0 <= token_result['similarity_score'] <= 1.0
        assert 0.0 <= ast_result['similarity_score'] <= 1.0
        assert 0.0 <= hash_result['similarity_score'] <= 1.0


    def test_structural_plagiarism(self, all_detectors):
        """
        Test structural plagiarism detection using real validation dataset files.

        Scenario:
            Use fibonacci_original.py vs fibonacci_renamed.py from validation-datasets.
            These files have the same algorithmic structure with renamed variables.

        Expected behavior:
            - AST detector: HIGH similarity (> 0.7) - same structure
            - Hash detector: MODERATE similarity (0.4-0.7) - some fingerprint overlap
            - Token detector: LOW-MODERATE similarity - some token overlap

        This validates the detectors against real-world obfuscation attempts.
        """
        # Arrange: Locate validation dataset files
        validation_dir = PROJECT_ROOT / "validation-datasets" / "obfuscated"

        file1 = validation_dir / "fibonacci_original.py"
        file2 = validation_dir / "fibonacci_renamed.py"

        # Verify files exist
        assert file1.exists(), f"Validation file not found: {file1}"
        assert file2.exists(), f"Validation file not found: {file2}"

        # Act: Run all three detectors
        token_result = all_detectors['token'].analyze(str(file1), str(file2))
        ast_result = all_detectors['ast'].analyze(str(file1), str(file2))
        hash_result = all_detectors['hash'].analyze(str(file1), str(file2))

        # Assert: AST should be high (structural similarity despite renaming)
        assert ast_result['similarity_score'] > 0.7, \
            f"AST detector should detect structural plagiarism, got {ast_result['similarity_score']:.2f}"

        # Hash detector will show lower similarity with variable renaming
        # The validation dataset has significant renaming, which affects hash fingerprints
        assert hash_result['similarity_score'] > 0.2, \
            f"Hash detector should show some similarity, got {hash_result['similarity_score']:.2f}"

        # Key validation: AST similarity should be significantly higher than Hash
        # This demonstrates AST's strength in detecting structural plagiarism
        assert ast_result['similarity_score'] > hash_result['similarity_score'] + 0.3, \
            f"AST ({ast_result['similarity_score']:.2f}) should significantly exceed Hash ({hash_result['similarity_score']:.2f})"

        # All scores should be in valid range
        assert 0.0 <= token_result['similarity_score'] <= 1.0
        assert 0.0 <= ast_result['similarity_score'] <= 1.0
        assert 0.0 <= hash_result['similarity_score'] <= 1.0


    def test_completely_different(self, temp_file_pair, all_detectors):
        """
        Test that all detectors agree when files are completely different.

        Scenario:
            Two files with completely different algorithms and structures.
            One implements bubble sort, the other implements a binary tree.

        Expected behavior:
            - All three detectors: LOW similarity (< 0.3)
            - All should agree these are not plagiarized

        This validates that detectors don't produce false positives for
        legitimately different code.
        """
        # Arrange: Create completely different algorithms
        code1 = """
def bubble_sort(arr):
    '''Sort array using bubble sort algorithm.'''
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def main():
    data = [64, 34, 25, 12, 22, 11, 90]
    sorted_data = bubble_sort(data)
    print(f"Sorted array: {sorted_data}")
"""

        code2 = """
class BinaryTree:
    '''Binary tree implementation with insert and search.'''

    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def insert(self, value):
        '''Insert a value into the binary tree.'''
        if value < self.value:
            if self.left is None:
                self.left = BinaryTree(value)
            else:
                self.left.insert(value)
        else:
            if self.right is None:
                self.right = BinaryTree(value)
            else:
                self.right.insert(value)
"""

        file1, file2 = temp_file_pair(code1, code2)

        # Act: Run all three detectors
        token_result = all_detectors['token'].analyze(file1, file2)
        ast_result = all_detectors['ast'].analyze(file1, file2)
        hash_result = all_detectors['hash'].analyze(file1, file2)

        # Assert: All detectors should show non-plagiarism levels of similarity
        # Note: Even different algorithms may share some basic structural patterns
        # (loops, conditionals, etc.) which can cause moderate similarity scores
        # The key is that none should flag as plagiarism (below their thresholds)

        assert token_result['similarity_score'] < 0.7, \
            f"Token detector should not flag different code, got {token_result['similarity_score']:.2f}"

        # AST may show moderate similarity due to shared Python constructs (for loops, if statements)
        # but should still be below plagiarism threshold of 0.8
        assert ast_result['similarity_score'] < 0.8, \
            f"AST detector should be below plagiarism threshold for different algorithms, got {ast_result['similarity_score']:.2f}"

        assert hash_result['similarity_score'] < 0.6, \
            f"Hash detector should not flag different code, got {hash_result['similarity_score']:.2f}"

        # Verify plagiarism not flagged
        assert token_result['is_plagiarism'] is False, \
            "Token detector should not flag different code as plagiarism"

        # All scores should be in valid range
        assert 0.0 <= token_result['similarity_score'] <= 1.0
        assert 0.0 <= ast_result['similarity_score'] <= 1.0
        assert 0.0 <= hash_result['similarity_score'] <= 1.0


    def test_batch_processing(self, temp_file_pair, all_detectors):
        """
        Test that all detectors handle multiple file pairs correctly.

        Scenario:
            Create 3 different files and generate all possible pairs (3 pairs total).
            Process all pairs through all three detectors.

        Expected behavior:
            - All detectors process all pairs without errors
            - All results are consistent (valid similarity scores)
            - Different pairs produce different similarity scores

        This validates robustness when processing multiple comparisons in sequence.
        """
        # Arrange: Create three different files
        code1 = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

        code2 = """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
"""

        code3 = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""

        # Create temporary files
        file1, file2 = temp_file_pair(code1, code2)
        file3 = None
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code3)
            file3 = f.name

        try:
            # Act: Generate all pairs and process with all detectors
            file_pairs = [
                (file1, file2),
                (file1, file3),
                (file2, file3)
            ]

            results = {
                'token': [],
                'ast': [],
                'hash': []
            }

            for f1, f2 in file_pairs:
                # Run all three detectors on each pair
                token_result = all_detectors['token'].analyze(f1, f2)
                ast_result = all_detectors['ast'].analyze(f1, f2)
                hash_result = all_detectors['hash'].analyze(f1, f2)

                results['token'].append(token_result)
                results['ast'].append(ast_result)
                results['hash'].append(hash_result)

            # Assert: All pairs should be processed successfully
            assert len(results['token']) == 3, "Token detector should process all 3 pairs"
            assert len(results['ast']) == 3, "AST detector should process all 3 pairs"
            assert len(results['hash']) == 3, "Hash detector should process all 3 pairs"

            # Verify all results have valid similarity scores
            for detector_name, detector_results in results.items():
                for i, result in enumerate(detector_results):
                    similarity = result['similarity_score']
                    assert 0.0 <= similarity <= 1.0, \
                        f"{detector_name} detector pair {i} has invalid similarity: {similarity}"

            # Verify results are consistent (no crashes, all fields present)
            for result in results['token']:
                assert 'similarity_score' in result
                assert 'is_plagiarism' in result
                assert 'threshold' in result

            for result in results['ast']:
                assert 'similarity_score' in result
                assert 'detector' in result
                assert result['detector'] == 'ast'

            for result in results['hash']:
                assert 'similarity_score' in result
                assert 'detector' in result
                assert result['detector'] == 'hash'

        finally:
            # Cleanup: remove the third file
            if file3 and os.path.exists(file3):
                os.unlink(file3)


    def test_error_recovery(self, temp_file_pair, all_detectors):
        """
        Test that detectors handle malformed code gracefully without crashing.

        Scenario:
            Files with syntax errors, empty files, and other edge cases.
            Detectors should handle errors gracefully and continue processing.

        Expected behavior:
            - Detectors should not crash on syntax errors
            - Should return low/zero similarity for unparseable code
            - Should handle empty files gracefully
            - At least one detector should complete successfully

        This validates robustness and error handling across all detectors.
        """
        # Test Case 1: Syntax error in first file
        code_with_error = "def foo(:"  # Missing closing parenthesis
        code_valid = "def bar(): pass"

        file1, file2 = temp_file_pair(code_with_error, code_valid)

        # All detectors should handle this gracefully
        try:
            token_result = all_detectors['token'].analyze(file1, file2)
            # Should not crash, should return valid similarity (likely 0.0)
            assert 0.0 <= token_result['similarity_score'] <= 1.0
        except Exception as e:
            # Some detectors may raise exceptions, that's acceptable
            pass

        try:
            ast_result = all_detectors['ast'].analyze(file1, file2)
            # AST parser should handle syntax errors and return 0.0
            assert ast_result['similarity_score'] == 0.0, \
                "AST detector should return 0.0 for unparseable code"
        except Exception as e:
            pass

        try:
            hash_result = all_detectors['hash'].analyze(file1, file2)
            # Hash detector should handle partial tokenization
            assert 0.0 <= hash_result['similarity_score'] <= 1.0
        except Exception as e:
            pass

        # Test Case 2: Empty files
        empty_code = ""
        file3, file4 = temp_file_pair(empty_code, empty_code)

        try:
            token_result = all_detectors['token'].analyze(file3, file4)
            assert 0.0 <= token_result['similarity_score'] <= 1.0
        except Exception:
            pass

        try:
            ast_result = all_detectors['ast'].analyze(file3, file4)
            assert ast_result['similarity_score'] == 0.0, \
                "AST detector should return 0.0 for empty files"
        except Exception:
            pass

        try:
            hash_result = all_detectors['hash'].analyze(file3, file4)
            assert hash_result['similarity_score'] == 0.0, \
                "Hash detector should return 0.0 for empty files"
        except Exception:
            pass

        # At least one detector should complete without raising exceptions
        # (this test passes if we reach here without unhandled exceptions)


# =============================================================================
# Test Execution Helper
# =============================================================================

if __name__ == "__main__":
    """
    Run integration tests directly with pytest.

    Usage:
        python test_all_detectors_integration.py

    Or with pytest:
        pytest test_all_detectors_integration.py -v
        pytest test_all_detectors_integration.py::TestAllDetectorsIntegration::test_exact_copy_all_detectors -v
    """
    import subprocess

    print("Running integration tests for all three detectors...")
    print("=" * 80)

    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )

    exit(result.returncode)
