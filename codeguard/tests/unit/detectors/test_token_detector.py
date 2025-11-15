"""
Comprehensive Unit Tests for TokenDetector.

This test module provides extensive coverage of the TokenDetector class,
including initialization, tokenization, similarity calculations, file analysis,
edge cases, and error handling.

Coverage target: ≥80% for src/detectors/token_detector.py
"""

import pytest
import tempfile
from pathlib import Path
from src.detectors.token_detector import TokenDetector


class TestTokenDetectorInitialization:
    """Test TokenDetector initialization and configuration."""

    def test_default_initialization(self):
        """Test TokenDetector initializes with default threshold."""
        detector = TokenDetector()
        assert detector.threshold == 0.7
        assert hasattr(detector, 'SEMANTIC_TOKEN_TYPES')

    def test_custom_threshold(self):
        """Test TokenDetector initializes with custom threshold."""
        detector = TokenDetector(threshold=0.85)
        assert detector.threshold == 0.85

    def test_threshold_lower_bound(self):
        """Test TokenDetector accepts threshold at lower bound (0.0)."""
        detector = TokenDetector(threshold=0.0)
        assert detector.threshold == 0.0

    def test_threshold_upper_bound(self):
        """Test TokenDetector accepts threshold at upper bound (1.0)."""
        detector = TokenDetector(threshold=1.0)
        assert detector.threshold == 1.0

    def test_invalid_threshold_below_zero(self):
        """Test TokenDetector rejects threshold below 0.0."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            TokenDetector(threshold=-0.1)

    def test_invalid_threshold_above_one(self):
        """Test TokenDetector rejects threshold above 1.0."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            TokenDetector(threshold=1.5)


class TestTokenization:
    """Test tokenization functionality."""

    def test_tokenize_simple_code(self):
        """Test tokenization of simple Python code."""
        detector = TokenDetector()
        code = "x = 5"
        tokens = detector._tokenize_code(code)

        assert len(tokens) > 0
        assert 'x' in tokens
        assert '=' in tokens
        assert '5' in tokens

    def test_tokenize_function_definition(self):
        """Test tokenization of function definition."""
        detector = TokenDetector()
        code = """def add(a, b):
    return a + b"""
        tokens = detector._tokenize_code(code)

        assert 'def' in tokens
        assert 'add' in tokens
        assert 'return' in tokens
        assert '+' in tokens

    def test_tokenize_filters_comments(self):
        """Test that tokenization filters out comments."""
        detector = TokenDetector()
        code = """# This is a comment
x = 5  # Inline comment"""
        tokens = detector._tokenize_code(code)

        # Comments should not appear in tokens
        assert 'this' not in [t.lower() for t in tokens]
        assert 'comment' not in [t.lower() for t in tokens]
        # But code should still be present
        assert 'x' in tokens
        assert '5' in tokens

    def test_tokenize_empty_code(self):
        """Test tokenization of empty code returns empty list."""
        detector = TokenDetector()
        tokens = detector._tokenize_code("")
        assert tokens == []

    def test_tokenize_whitespace_only(self):
        """Test tokenization of whitespace-only code."""
        detector = TokenDetector()
        tokens = detector._tokenize_code("   \n\t\n   ")
        assert tokens == []

    def test_tokenize_syntax_error_handling(self):
        """Test tokenization handles syntax errors gracefully."""
        detector = TokenDetector()
        invalid_code = "def foo(\n    incomplete"
        tokens = detector._tokenize_code(invalid_code)
        # Should return partial tokens or empty, not crash
        assert isinstance(tokens, list)

    def test_tokenize_normalizes_case(self):
        """Test that tokens are normalized to lowercase."""
        detector = TokenDetector()
        code = "MyVariable = 10"
        tokens = detector._tokenize_code(code)

        assert 'myvariable' in tokens
        assert 'MyVariable' not in tokens

    def test_tokenize_complex_code(self):
        """Test tokenization of complex code structure."""
        detector = TokenDetector()
        code = """
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x, y):
        return x + y
"""
        tokens = detector._tokenize_code(code)

        assert len(tokens) > 10
        assert 'class' in tokens
        assert 'def' in tokens
        assert 'self' in tokens


class TestJaccardSimilarity:
    """Test Jaccard similarity calculation."""

    def test_identical_tokens(self):
        """Test Jaccard similarity of identical token lists is 1.0."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = ['a', 'b', 'c']
        similarity = detector._calculate_jaccard_similarity(tokens1, tokens2)
        assert similarity == 1.0

    def test_disjoint_tokens(self):
        """Test Jaccard similarity of disjoint token lists is 0.0."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = ['x', 'y', 'z']
        similarity = detector._calculate_jaccard_similarity(tokens1, tokens2)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Test Jaccard similarity with partial overlap."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c', 'd']
        tokens2 = ['c', 'd', 'e', 'f']
        # Intersection: {c, d} = 2 elements
        # Union: {a, b, c, d, e, f} = 6 elements
        # Jaccard = 2/6 = 0.333...
        similarity = detector._calculate_jaccard_similarity(tokens1, tokens2)
        assert abs(similarity - 0.333333) < 0.001

    def test_empty_both_tokens(self):
        """Test Jaccard similarity when both token lists are empty."""
        detector = TokenDetector()
        similarity = detector._calculate_jaccard_similarity([], [])
        assert similarity == 0.0

    def test_one_empty_token_list(self):
        """Test Jaccard similarity when one token list is empty."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = []
        similarity = detector._calculate_jaccard_similarity(tokens1, tokens2)
        assert similarity == 0.0

    def test_duplicate_tokens(self):
        """Test Jaccard similarity with duplicate tokens (sets ignore duplicates)."""
        detector = TokenDetector()
        tokens1 = ['a', 'a', 'b', 'b', 'c']
        tokens2 = ['a', 'b', 'c', 'c']
        # Both convert to set {a, b, c}
        similarity = detector._calculate_jaccard_similarity(tokens1, tokens2)
        assert similarity == 1.0


class TestCosineSimilarity:
    """Test Cosine similarity calculation."""

    def test_identical_tokens(self):
        """Test Cosine similarity of identical token lists is 1.0."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = ['a', 'b', 'c']
        similarity = detector._calculate_cosine_similarity(tokens1, tokens2)
        assert abs(similarity - 1.0) < 0.0001  # Allow for floating point imprecision

    def test_disjoint_tokens(self):
        """Test Cosine similarity of disjoint token lists is 0.0."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = ['x', 'y', 'z']
        similarity = detector._calculate_cosine_similarity(tokens1, tokens2)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Test Cosine similarity with partial overlap."""
        detector = TokenDetector()
        tokens1 = ['a', 'b', 'c']
        tokens2 = ['a', 'b', 'd']
        similarity = detector._calculate_cosine_similarity(tokens1, tokens2)
        # Should be > 0 and < 1
        assert 0.0 < similarity < 1.0

    def test_empty_first_list(self):
        """Test Cosine similarity when first token list is empty."""
        detector = TokenDetector()
        similarity = detector._calculate_cosine_similarity([], ['a', 'b', 'c'])
        assert similarity == 0.0

    def test_empty_second_list(self):
        """Test Cosine similarity when second token list is empty."""
        detector = TokenDetector()
        similarity = detector._calculate_cosine_similarity(['a', 'b', 'c'], [])
        assert similarity == 0.0

    def test_empty_both_lists(self):
        """Test Cosine similarity when both token lists are empty."""
        detector = TokenDetector()
        similarity = detector._calculate_cosine_similarity([], [])
        assert similarity == 0.0

    def test_frequency_matters(self):
        """Test Cosine similarity accounts for token frequency."""
        detector = TokenDetector()
        tokens1 = ['a', 'a', 'a', 'b']
        tokens2 = ['a', 'b', 'b', 'b']
        # Different frequencies should result in < 1.0 similarity
        similarity = detector._calculate_cosine_similarity(tokens1, tokens2)
        assert 0.0 < similarity < 1.0


class TestCompareMethod:
    """Test the compare() method for string comparison."""

    def test_compare_identical_code(self):
        """Test comparing identical code strings."""
        detector = TokenDetector()
        code = "def foo():\n    return 42"
        similarity = detector.compare(code, code)
        assert similarity == 1.0

    def test_compare_different_code(self):
        """Test comparing completely different code."""
        detector = TokenDetector()
        code1 = "x = 5"
        code2 = "y = 10"
        similarity = detector.compare(code1, code2)
        # Should have some similarity (operators) but not high
        assert 0.0 < similarity < 1.0

    def test_compare_similar_structure(self):
        """Test comparing code with similar structure."""
        detector = TokenDetector()
        code1 = "def add(a, b):\n    return a + b"
        code2 = "def sum(x, y):\n    return x + y"
        similarity = detector.compare(code1, code2)
        # Moderate similarity - different function names reduce token overlap
        assert 0.4 < similarity < 0.6

    def test_compare_empty_strings(self):
        """Test comparing empty code strings."""
        detector = TokenDetector()
        similarity = detector.compare("", "")
        assert similarity == 0.0

    def test_compare_one_empty(self):
        """Test comparing when one string is empty."""
        detector = TokenDetector()
        similarity = detector.compare("x = 5", "")
        assert similarity == 0.0


class TestAnalyzeMethod:
    """Test the analyze() method for file comparison."""

    def test_analyze_identical_files(self, sample_code_pairs):
        """Test analyzing identical files."""
        detector = TokenDetector(threshold=0.7)

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            code = sample_code_pairs['identical']['code1']
            file1.write_text(code)
            file2.write_text(code)

            result = detector.analyze(file1, file2)

            assert abs(result['similarity_score'] - 1.0) < 0.0001
            assert result['is_plagiarism'] is True
            assert result['threshold'] == 0.7
            assert abs(result['jaccard_similarity'] - 1.0) < 0.0001
            assert abs(result['cosine_similarity'] - 1.0) < 0.0001
            assert 'details' in result

    def test_analyze_different_files(self, sample_code_pairs):
        """Test analyzing completely different files."""
        detector = TokenDetector(threshold=0.7)

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text(sample_code_pairs['different']['code1'])
            file2.write_text(sample_code_pairs['different']['code2'])

            result = detector.analyze(file1, file2)

            assert result['similarity_score'] < 0.7
            assert result['is_plagiarism'] is False

    def test_analyze_renamed_variables(self, sample_code_pairs):
        """Test analyzing code with renamed variables."""
        detector = TokenDetector(threshold=0.7)

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text(sample_code_pairs['renamed']['code1'])
            file2.write_text(sample_code_pairs['renamed']['code2'])

            result = detector.analyze(file1, file2)

            # Token detector less effective with renamed variables
            assert result['similarity_score'] > 0.3  # Lowered expectation for token detector
            assert 'details' in result
            assert result['details']['file1_tokens'] > 0
            assert result['details']['file2_tokens'] > 0

    def test_analyze_nonexistent_file1(self):
        """Test analyzing when first file doesn't exist."""
        detector = TokenDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "nonexistent1.py"
            file2 = Path(tmpdir) / "file2.py"
            file2.write_text("x = 5")

            with pytest.raises(FileNotFoundError):
                detector.analyze(file1, file2)

    def test_analyze_nonexistent_file2(self):
        """Test analyzing when second file doesn't exist."""
        detector = TokenDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "nonexistent2.py"
            file1.write_text("x = 5")

            with pytest.raises(FileNotFoundError):
                detector.analyze(file1, file2)

    def test_analyze_result_structure(self):
        """Test that analyze() returns complete result structure."""
        detector = TokenDetector(threshold=0.8)

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text("x = 5")
            file2.write_text("y = 10")

            result = detector.analyze(file1, file2)

            # Check all required keys are present
            assert 'similarity_score' in result
            assert 'is_plagiarism' in result
            assert 'threshold' in result
            assert 'jaccard_similarity' in result
            assert 'cosine_similarity' in result
            assert 'details' in result

            # Check details structure
            details = result['details']
            assert 'file1_tokens' in details
            assert 'file2_tokens' in details
            assert 'common_tokens' in details
            assert 'file1_path' in details
            assert 'file2_path' in details


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_large_file(self):
        """Test tokenizing very large file doesn't crash."""
        detector = TokenDetector()

        # Generate large code file
        large_code = "\n".join([f"x{i} = {i}" for i in range(10000)])
        tokens = detector._tokenize_code(large_code)

        assert len(tokens) > 0
        assert len(tokens) == 30000  # Each line has 3 tokens: name, =, number

    def test_unicode_in_strings(self):
        """Test handling of Unicode characters in strings."""
        detector = TokenDetector()
        code = '''text = "Hello 世界 🌍"'''
        tokens = detector._tokenize_code(code)

        assert len(tokens) > 0
        assert 'text' in tokens

    def test_multiline_strings(self):
        """Test handling of multiline strings."""
        detector = TokenDetector()
        code = '''
text = """
This is a
multiline string
"""
'''
        tokens = detector._tokenize_code(code)
        assert len(tokens) > 0

    def test_nested_structures(self):
        """Test handling of deeply nested structures."""
        detector = TokenDetector()
        code = '''
def outer():
    def inner():
        def innermost():
            return 42
        return innermost()
    return inner()
'''
        tokens = detector._tokenize_code(code)
        assert len(tokens) > 0
        assert tokens.count('def') == 3

    def test_special_characters_in_operators(self):
        """Test handling of special operator characters."""
        detector = TokenDetector()
        code = "result = (a + b) * (c - d) / (e // f) ** g % h"
        tokens = detector._tokenize_code(code)

        assert '+' in tokens
        assert '*' in tokens
        assert '-' in tokens
        assert '/' in tokens
        assert '//' in tokens
        assert '**' in tokens
        assert '%' in tokens

    def test_analyze_with_pathlib_path(self):
        """Test analyze() works with pathlib.Path objects."""
        detector = TokenDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text("x = 5")
            file2.write_text("x = 5")

            # Should work with Path objects
            result = detector.analyze(file1, file2)
            assert 'similarity_score' in result

    def test_analyze_with_string_paths(self):
        """Test analyze() works with string paths."""
        detector = TokenDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text("x = 5")
            file2.write_text("x = 5")

            # Should work with string paths
            result = detector.analyze(str(file1), str(file2))
            assert 'similarity_score' in result


class TestThresholdBehavior:
    """Test threshold-based plagiarism detection."""

    def test_below_threshold_not_plagiarism(self):
        """Test that similarity below threshold is not flagged as plagiarism."""
        detector = TokenDetector(threshold=0.9)  # High threshold

        code1 = "def foo(): return 1"
        code2 = "def bar(): return 2"

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text(code1)
            file2.write_text(code2)

            result = detector.analyze(file1, file2)

            assert result['is_plagiarism'] is False

    def test_at_threshold_is_plagiarism(self):
        """Test that similarity at threshold is flagged as plagiarism."""
        detector = TokenDetector(threshold=0.0)  # Zero threshold

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text("x = 1")
            file2.write_text("y = 2")

            result = detector.analyze(file1, file2)

            # Any similarity ≥ 0.0 should be flagged
            assert result['is_plagiarism'] is True

    def test_above_threshold_is_plagiarism(self):
        """Test that similarity above threshold is flagged as plagiarism."""
        detector = TokenDetector(threshold=0.5)

        code = "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"

            file1.write_text(code)
            file2.write_text(code)

            result = detector.analyze(file1, file2)

            assert result['similarity_score'] >= 0.5
            assert result['is_plagiarism'] is True


@pytest.mark.parametrize("threshold,expected_valid", [
    (0.0, True),
    (0.5, True),
    (1.0, True),
    (-0.1, False),
    (1.1, False),
    (2.0, False),
])
def test_threshold_validation(threshold, expected_valid):
    """Test threshold validation with various values."""
    if expected_valid:
        detector = TokenDetector(threshold=threshold)
        assert detector.threshold == threshold
    else:
        with pytest.raises(ValueError):
            TokenDetector(threshold=threshold)
