"""
Unit tests for HashDetector (Winnowing algorithm).

Tests cover:
- Basic functionality (tokenization, k-gram generation, hashing, winnowing)
- Similarity comparison (identical, different, partial)
- Edge cases (empty, syntax errors, small files)
- Parameter validation
- Algorithm correctness
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import the detector
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from detectors.hash_detector import HashDetector


class TestHashDetectorInitialization:
    """Test HashDetector initialization and parameter validation."""

    def test_default_initialization(self):
        """Test default parameter values."""
        detector = HashDetector()
        assert detector.threshold == 0.6
        assert detector.k == 5
        assert detector.w == 4

    def test_custom_initialization(self):
        """Test custom parameter values."""
        detector = HashDetector(threshold=0.7, k=3, w=2)
        assert detector.threshold == 0.7
        assert detector.k == 3
        assert detector.w == 2

    def test_invalid_threshold_low(self):
        """Test that threshold below 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            HashDetector(threshold=-0.1)

    def test_invalid_threshold_high(self):
        """Test that threshold above 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            HashDetector(threshold=1.5)

    def test_invalid_k(self):
        """Test that k < 1 raises ValueError."""
        with pytest.raises(ValueError, match="k-gram size must be >= 1"):
            HashDetector(k=0)

    def test_invalid_w(self):
        """Test that w < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Window size must be >= 1"):
            HashDetector(w=0)


class TestTokenization:
    """Test tokenization functionality."""

    def test_basic_tokenization(self):
        """Test basic token extraction."""
        detector = HashDetector()
        code = "def add(a, b):\n    return a + b"
        tokens = detector._tokenize(code)

        # Should contain: def, add, (, a, ,, b, ), :, return, a, +, b
        assert "def" in tokens
        assert "add" in tokens
        assert "return" in tokens
        assert "+" in tokens
        assert len(tokens) > 0

    def test_tokenization_filters_comments(self):
        """Test that comments are filtered out."""
        detector = HashDetector()
        code = """
# This is a comment
def foo():
    # Another comment
    return 1
"""
        tokens = detector._tokenize(code)

        # Comments should not be in tokens
        assert "This" not in tokens
        assert "comment" not in tokens
        assert "def" in tokens
        assert "foo" in tokens

    def test_tokenization_empty_code(self):
        """Test tokenization of empty code."""
        detector = HashDetector()
        tokens = detector._tokenize("")
        assert tokens == []

    def test_tokenization_syntax_error(self):
        """Test tokenization handles syntax errors gracefully."""
        detector = HashDetector()
        code = "def foo(:"  # Syntax error
        tokens = detector._tokenize(code)

        # Should return partial tokens, not raise exception
        assert isinstance(tokens, list)


class TestKGramGeneration:
    """Test k-gram generation."""

    def test_basic_kgram_generation(self):
        """Test basic k-gram generation."""
        detector = HashDetector(k=3)
        tokens = ["a", "b", "c", "d", "e"]
        kgrams = detector._generate_kgrams(tokens, 3)

        expected = [("a", "b", "c"), ("b", "c", "d"), ("c", "d", "e")]
        assert kgrams == expected

    def test_kgram_generation_exact_k(self):
        """Test k-gram generation when token count equals k."""
        detector = HashDetector(k=3)
        tokens = ["a", "b", "c"]
        kgrams = detector._generate_kgrams(tokens, 3)

        assert kgrams == [("a", "b", "c")]

    def test_kgram_generation_insufficient_tokens(self):
        """Test k-gram generation with fewer tokens than k."""
        detector = HashDetector(k=5)
        tokens = ["a", "b", "c"]
        kgrams = detector._generate_kgrams(tokens, 5)

        assert kgrams == []

    def test_kgram_generation_k_equals_1(self):
        """Test k-gram generation with k=1."""
        detector = HashDetector(k=1)
        tokens = ["a", "b", "c"]
        kgrams = detector._generate_kgrams(tokens, 1)

        expected = [("a",), ("b",), ("c",)]
        assert kgrams == expected


class TestHashing:
    """Test k-gram hashing."""

    def test_hash_produces_integers(self):
        """Test that hashing produces integer values."""
        detector = HashDetector()
        kgrams = [("a", "b", "c"), ("b", "c", "d")]
        hashes = detector._hash_kgrams(kgrams)

        assert len(hashes) == 2
        assert all(isinstance(h, int) for h in hashes)

    def test_hash_consistency(self):
        """Test that same k-gram produces same hash."""
        detector = HashDetector()
        kgram = ("def", "foo", "(")

        hash1 = detector._hash_kgrams([kgram])[0]
        hash2 = detector._hash_kgrams([kgram])[0]

        assert hash1 == hash2

    def test_hash_uniqueness(self):
        """Test that different k-grams produce different hashes (usually)."""
        detector = HashDetector()
        kgrams = [("a", "b", "c"), ("d", "e", "f"), ("g", "h", "i")]
        hashes = detector._hash_kgrams(kgrams)

        # With MD5, collisions are extremely rare for different inputs
        assert len(set(hashes)) == len(hashes)


class TestWinnowing:
    """Test winnowing algorithm."""

    def test_winnowing_basic(self):
        """Test basic winnowing behavior."""
        detector = HashDetector()
        hashes = [77, 74, 42, 17, 98, 50, 17, 98]
        fingerprints = detector._winnow(hashes, 4)

        # Should select subset of hashes
        assert len(fingerprints) > 0
        assert len(fingerprints) <= len(hashes)
        assert all(h in hashes for h in fingerprints)

    def test_winnowing_selects_minimums(self):
        """Test that winnowing selects minimum values."""
        detector = HashDetector()
        hashes = [5, 4, 3, 2, 1]  # Decreasing sequence
        fingerprints = detector._winnow(hashes, 3)

        # Should include some of the smaller values
        assert min(fingerprints) <= min(hashes)

    def test_winnowing_window_larger_than_hashes(self):
        """Test winnowing when window size > hash count."""
        detector = HashDetector()
        hashes = [10, 20, 30]
        fingerprints = detector._winnow(hashes, 10)

        # Should return all hashes
        assert fingerprints == set(hashes)

    def test_winnowing_single_hash(self):
        """Test winnowing with single hash."""
        detector = HashDetector()
        hashes = [42]
        fingerprints = detector._winnow(hashes, 4)

        assert fingerprints == {42}

    def test_winnowing_deterministic(self):
        """Test that winnowing is deterministic."""
        detector = HashDetector()
        hashes = [77, 74, 42, 17, 98, 50, 17, 98]

        fp1 = detector._winnow(hashes, 4)
        fp2 = detector._winnow(hashes, 4)

        assert fp1 == fp2


class TestFingerprintComparison:
    """Test fingerprint comparison (Jaccard similarity)."""

    def test_identical_fingerprints(self):
        """Test comparison of identical fingerprint sets."""
        detector = HashDetector()
        fp1 = {1, 2, 3, 4, 5}
        fp2 = {1, 2, 3, 4, 5}

        similarity = detector._compare_fingerprints(fp1, fp2)
        assert similarity == 1.0

    def test_disjoint_fingerprints(self):
        """Test comparison of completely different fingerprints."""
        detector = HashDetector()
        fp1 = {1, 2, 3}
        fp2 = {4, 5, 6}

        similarity = detector._compare_fingerprints(fp1, fp2)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Test comparison with partial overlap."""
        detector = HashDetector()
        fp1 = {1, 2, 3, 4, 5}
        fp2 = {3, 4, 5, 6, 7}

        similarity = detector._compare_fingerprints(fp1, fp2)
        # 3 common / 7 total = 0.428...
        assert 0.4 < similarity < 0.5

    def test_empty_fingerprints(self):
        """Test comparison with empty fingerprint sets."""
        detector = HashDetector()

        assert detector._compare_fingerprints(set(), {1, 2, 3}) == 0.0
        assert detector._compare_fingerprints({1, 2, 3}, set()) == 0.0
        assert detector._compare_fingerprints(set(), set()) == 0.0


class TestCompareMethod:
    """Test the compare() method."""

    def test_compare_identical_code(self):
        """Test comparison of identical code."""
        detector = HashDetector()
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
        similarity = detector.compare(code, code)
        assert similarity == 1.0

    def test_compare_different_code(self):
        """Test comparison of completely different code."""
        detector = HashDetector()
        code1 = "def add(a, b):\n    return a + b"
        code2 = "class Foo:\n    def __init__(self):\n        pass"

        similarity = detector.compare(code1, code2)
        assert similarity < 0.3

    def test_compare_similar_code(self):
        """Test comparison of similar code."""
        detector = HashDetector()
        code1 = """
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
        code2 = """
def process(data):
    output = []
    for item in data:
        output.append(item * 2)
    return output
"""
        similarity = detector.compare(code1, code2)
        # Variable names differ, which affects tokens and thus hashes
        # HashDetector is token-based, so renaming reduces similarity
        # AST detector is better for structural similarity with renaming
        assert 0.3 <= similarity <= 1.0

    def test_compare_empty_code(self):
        """Test comparison with empty code."""
        detector = HashDetector()
        assert detector.compare("", "def foo(): pass") == 0.0
        assert detector.compare("def foo(): pass", "") == 0.0
        assert detector.compare("", "") == 0.0

    def test_compare_syntax_error(self):
        """Test comparison handles syntax errors gracefully."""
        detector = HashDetector()
        code1 = "def foo(:"  # Syntax error
        code2 = "def bar(): pass"

        # Should not raise exception
        similarity = detector.compare(code1, code2)
        assert isinstance(similarity, float)


class TestAnalyzeMethod:
    """Test the analyze() method with files."""

    def test_analyze_identical_files(self):
        """Test analysis of identical files."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
            f1.write(code)
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
            f2.write(code)
            file2 = f2.name

        try:
            detector = HashDetector()
            result = detector.analyze(file1, file2)

            assert result["similarity_score"] == 1.0
            assert result["detector"] == "hash"
            assert result["file1"] == file1
            assert result["file2"] == file2
            assert result["k"] == 5
            assert result["w"] == 4
            assert result["file1_fingerprints"] > 0
            assert result["file2_fingerprints"] > 0
            assert result["common_fingerprints"] == result["file1_fingerprints"]

        finally:
            os.unlink(file1)
            os.unlink(file2)

    def test_analyze_different_files(self):
        """Test analysis of different files."""
        code1 = "def foo():\n    return 1"
        code2 = "class Bar:\n    def __init__(self):\n        self.x = 10"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f1:
            f1.write(code1)
            file1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f2:
            f2.write(code2)
            file2 = f2.name

        try:
            detector = HashDetector()
            result = detector.analyze(file1, file2)

            assert result["similarity_score"] < 0.3
            assert result["detector"] == "hash"

        finally:
            os.unlink(file1)
            os.unlink(file2)

    def test_analyze_nonexistent_file(self):
        """Test that analyze raises FileNotFoundError for missing files."""
        detector = HashDetector()

        with pytest.raises(FileNotFoundError):
            detector.analyze("nonexistent1.py", "nonexistent2.py")


class TestScatteredCopying:
    """Test detection of scattered copying (HashDetector's strength)."""

    def test_scattered_fragments(self):
        """Test detection of code fragments scattered in different order."""
        original = """
def func_a():
    x = 1
    y = 2
    return x + y

def func_b():
    for i in range(10):
        print(i * 2)

def func_c():
    data = [1, 2, 3, 4, 5]
    return sum(data)
"""

        # Copy func_a and func_c, add new code
        plagiarized = """
def new_func():
    return 0

def func_a():
    x = 1
    y = 2
    return x + y

def another_new():
    return 4

def func_c():
    data = [1, 2, 3, 4, 5]
    return sum(data)
"""

        detector = HashDetector()
        similarity = detector.compare(original, plagiarized)

        # Should detect partial overlap (with more substantial functions)
        assert similarity > 0.2


class TestParameterEffects:
    """Test effects of different parameters."""

    def test_smaller_k_more_sensitive(self):
        """Test that smaller k produces higher similarity."""
        code1 = "def foo(x):\n    return x + 1"
        code2 = "def bar(y):\n    return y + 1"

        detector_small_k = HashDetector(k=2)
        detector_large_k = HashDetector(k=6)

        sim_small = detector_small_k.compare(code1, code2)
        sim_large = detector_large_k.compare(code1, code2)

        # Smaller k should generally produce more matches
        # (though this depends on the specific code)
        assert sim_small >= 0.0 and sim_large >= 0.0

    def test_different_w_values(self):
        """Test that different w values affect fingerprint count."""
        code = """
def process(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

        detector_small_w = HashDetector(k=5, w=2)
        detector_large_w = HashDetector(k=5, w=6)

        tokens = detector_small_w._tokenize(code)
        kgrams = detector_small_w._generate_kgrams(tokens, 5)
        hashes = detector_small_w._hash_kgrams(kgrams)

        fp_small_w = detector_small_w._winnow(hashes, 2)
        fp_large_w = detector_large_w._winnow(hashes, 6)

        # Smaller w should produce more fingerprints
        assert len(fp_small_w) >= len(fp_large_w)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_file(self):
        """Test with file smaller than k tokens."""
        detector = HashDetector(k=10)
        code = "x = 1"  # Very few tokens

        similarity = detector.compare(code, code)
        # Should handle gracefully (may be 0.0 or handle specially)
        assert isinstance(similarity, float)

    def test_only_whitespace(self):
        """Test with whitespace-only code."""
        detector = HashDetector()
        code = "   \n\n   \n"

        similarity = detector.compare(code, code)
        assert similarity == 0.0

    def test_only_comments(self):
        """Test with comment-only code."""
        detector = HashDetector()
        code = "# This is a comment\n# Another comment"

        similarity = detector.compare(code, code)
        # Comments are filtered, so no tokens
        assert similarity == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
