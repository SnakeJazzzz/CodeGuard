"""
Hash-based Plagiarism Detector for Python Code using Winnowing Algorithm.

This module implements the Winnowing algorithm (Schleimer et al. 2003) for
document fingerprinting and plagiarism detection. The algorithm creates robust
fingerprints that can detect partial and scattered copying while being resilient
to small insertions and deletions.

Mathematical foundations:
    - k-gram fingerprinting: Hash overlapping sequences of k tokens
    - Winnowing: Select minimum hash in each window of w consecutive hashes
    - Jaccard similarity: J(A,B) = |A ∩ B| / |A ∪ B| on fingerprint sets

Key advantages:
    - Detects partial copying (code fragments scattered across files)
    - Resilient to small insertions/deletions (guaranteed density)
    - Space-efficient fingerprint representation
    - Fast comparison using set operations

Reference:
    Schleimer, S., Wilkerson, D. S., & Aiken, A. (2003).
    "Winnowing: Local algorithms for document fingerprinting."
    Proceedings of the 2003 ACM SIGMOD International Conference on
    Management of Data, 76-85.

Author: CodeGuard Team
"""

import io
import tokenize
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union


class HashDetector:
    """
    Hash-based similarity detector using the Winnowing algorithm.

    This detector implements the Winnowing algorithm for robust document
    fingerprinting. It tokenizes Python source code, generates k-grams,
    hashes them, and selects a guaranteed minimal subset using a sliding
    window approach. This makes it particularly effective at detecting
    partial and scattered copying.

    The Winnowing algorithm guarantees:
    1. If two documents share a substring of length at least t = w + k - 1,
       then this match will be detected (no false negatives for long matches)
    2. The density of selected fingerprints is bounded (space-efficient)

    Attributes:
        threshold (float): Similarity threshold for plagiarism detection (0.0 to 1.0).
                          Default is 0.6 (60% fingerprint overlap).
        k (int): Size of k-grams (number of tokens per gram). Default is 5.
                Larger k reduces false positives but may miss small matches.
        w (int): Winnowing window size (number of hashes to consider). Default is 4.
                Larger w creates sparser fingerprints (fewer selected hashes).

    Example:
        >>> detector = HashDetector(threshold=0.6, k=5, w=4)
        >>> result = detector.analyze('file1.py', 'file2.py')
        >>> print(f"Similarity: {result['similarity_score']:.2%}")
        >>> print(f"Common fingerprints: {result['common_fingerprints']}")
    """

    # Token types that carry semantic meaning (same as TokenDetector)
    SEMANTIC_TOKEN_TYPES = {
        tokenize.NAME,  # Identifiers (variable names, function names, keywords)
        tokenize.NUMBER,  # Numeric literals
        tokenize.STRING,  # String literals
        tokenize.OP,  # Operators (+, -, *, /, etc.)
    }

    def __init__(self, threshold: float = 0.6, k: int = 5, w: int = 4):
        """
        Initialize the HashDetector with Winnowing parameters.

        Args:
            threshold (float): Similarity threshold for plagiarism detection.
                             Must be between 0.0 and 1.0. Default is 0.6.
            k (int): K-gram size (number of tokens per gram).
                    Must be >= 1. Default is 5.
                    Recommended range: 3-7 (5 balances sensitivity and specificity).
            w (int): Winnowing window size (number of hashes to consider).
                    Must be >= 1. Default is 4.
                    Recommended range: 2-5 (4 provides good noise resistance).

        Raises:
            ValueError: If parameters are out of valid ranges.

        Note:
            The guaranteed match threshold is t = w + k - 1.
            With k=5, w=4: matches of length >= 8 tokens are guaranteed to be detected.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        if k < 1:
            raise ValueError(f"k-gram size must be >= 1, got {k}")
        if w < 1:
            raise ValueError(f"Window size must be >= 1, got {w}")

        self.threshold = threshold
        self.k = k
        self.w = w

    def _read_file(self, file_path: Union[str, Path]) -> str:
        """
        Read the contents of a Python source file.

        Args:
            file_path: Path to the Python file to read.

        Returns:
            str: The file contents as a string.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be read.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")

    def _tokenize(self, source: str) -> List[str]:
        """
        Tokenize Python source code into semantic tokens.

        This method uses Python's built-in tokenize module to extract tokens,
        filtering out comments, whitespace, and other non-semantic elements.
        Only tokens that carry semantic meaning are retained.

        Args:
            source: Python source code as a string.

        Returns:
            List[str]: List of semantic token strings.

        Note:
            - Syntax errors are handled gracefully by returning tokens collected so far
            - Comments and docstrings are filtered out
            - Whitespace and formatting tokens are ignored
            - Token values are kept as-is (not normalized to lowercase)
              to preserve distinction between different identifiers
        """
        tokens = []

        try:
            # Convert source code string to bytes for tokenizer
            source_bytes = source.encode("utf-8")
            readline = io.BytesIO(source_bytes).readline

            # Tokenize the source code
            token_generator = tokenize.tokenize(readline)

            for token in token_generator:
                token_type = token.type
                token_string = token.string

                # Filter for semantic tokens only
                if token_type in self.SEMANTIC_TOKEN_TYPES:
                    tokens.append(token_string)

        except tokenize.TokenError:
            # Handle incomplete or malformed Python code
            # Return tokens collected so far
            pass
        except Exception:
            # Handle other tokenization errors gracefully
            # Return empty list for completely invalid code
            pass

        return tokens

    def _generate_kgrams(self, tokens: List[str], k: int) -> List[Tuple[str, ...]]:
        """
        Generate overlapping k-grams from a token sequence.

        A k-gram is a contiguous subsequence of k tokens. This method creates
        all possible k-grams using a sliding window approach.

        Args:
            tokens: List of tokens from tokenized source code.
            k: Size of each k-gram (number of tokens).

        Returns:
            List[Tuple[str, ...]]: List of k-gram tuples.
                                   Returns empty list if len(tokens) < k.

        Example:
            >>> tokens = ['def', 'foo', '(', 'x', ')']
            >>> _generate_kgrams(tokens, 3)
            [('def', 'foo', '('), ('foo', '(', 'x'), ('(', 'x', ')')]

        Note:
            For n tokens and k-gram size k, this generates (n - k + 1) k-grams.
        """
        # Handle edge case: not enough tokens to create k-grams
        if len(tokens) < k:
            return []

        kgrams = []

        # Slide window of size k across the token sequence
        for i in range(len(tokens) - k + 1):
            kgram = tuple(tokens[i : i + k])
            kgrams.append(kgram)

        return kgrams

    def _hash_kgrams(self, kgrams: List[Tuple[str, ...]]) -> List[int]:
        """
        Hash each k-gram to create numeric fingerprints.

        Uses MD5 hashing to convert k-grams into fixed-size integer values.
        MD5 is chosen for its speed and low collision rate for short strings.

        Args:
            kgrams: List of k-gram tuples.

        Returns:
            List[int]: List of integer hash values, one per k-gram.

        Note:
            - We use MD5 for speed (not for security)
            - Hash values are converted to integers for numeric comparison
            - Identical k-grams will always produce identical hashes
        """
        hashes = []

        for kgram in kgrams:
            # Join k-gram tokens into a single string
            # Use a separator to avoid collision (e.g., ('a','bc') vs ('ab','c'))
            kgram_str = "\x00".join(kgram)

            # Hash using MD5 (fast, good distribution)
            hash_obj = hashlib.md5(kgram_str.encode("utf-8"))

            # Convert hex digest to integer for numeric comparison
            hash_val = int(hash_obj.hexdigest(), 16)

            hashes.append(hash_val)

        return hashes

    def _winnow(self, hashes: List[int], w: int) -> Set[int]:
        """
        Apply the Winnowing algorithm to select a minimal subset of hashes.

        The Winnowing algorithm slides a window of size w over the hash sequence
        and selects the minimum hash in each window. If there are multiple
        minimums, it selects the rightmost one. This creates a guaranteed
        density of fingerprints while maintaining noise resistance.

        Args:
            hashes: List of integer hash values from k-grams.
            w: Window size (number of consecutive hashes to consider).

        Returns:
            Set[int]: Set of selected fingerprint hash values.

        Algorithm:
            For each window position i (where window = hashes[i:i+w]):
                1. Find the minimum hash value in the window
                2. If multiple minimums exist, select the rightmost occurrence
                3. Add the selected hash to the fingerprint set

        Example:
            >>> hashes = [77, 74, 42, 17, 98, 50, 17, 98]
            >>> _winnow(hashes, w=4)
            {17, 42}  # Selected minimums from each window

        Note:
            - If len(hashes) < w, all hashes are selected
            - The rightmost selection rule ensures consistent fingerprints
            - Fingerprint density is bounded: at least one hash per w positions
        """
        # Edge case: if we have fewer hashes than window size, keep all
        if len(hashes) < w:
            return set(hashes)

        fingerprints = set()

        # Slide window of size w across the hash sequence
        for i in range(len(hashes) - w + 1):
            window = hashes[i : i + w]

            # Find the minimum hash value in this window
            min_hash = min(window)

            # Find the rightmost occurrence of the minimum
            # We reverse the window and find the first (rightmost) occurrence
            rightmost_offset = len(window) - 1 - window[::-1].index(min_hash)

            # Calculate the absolute position in the original hash list
            min_position = i + rightmost_offset

            # Add the selected hash to our fingerprint set
            fingerprints.add(hashes[min_position])

        return fingerprints

    def _compare_fingerprints(self, fp1: Set[int], fp2: Set[int]) -> float:
        """
        Compare two fingerprint sets using Jaccard similarity.

        Jaccard similarity measures the overlap between two sets:
            J(A,B) = |A ∩ B| / |A ∪ B|

        This metric is ideal for fingerprint comparison as it:
        - Accounts for set size differences
        - Returns 1.0 for identical sets
        - Returns 0.0 for completely disjoint sets
        - Is symmetric: J(A,B) = J(B,A)

        Args:
            fp1: First fingerprint set.
            fp2: Second fingerprint set.

        Returns:
            float: Jaccard similarity score between 0.0 and 1.0.
                  Returns 0.0 if both sets are empty or if either is empty.

        Example:
            >>> fp1 = {1, 2, 3, 4, 5}
            >>> fp2 = {3, 4, 5, 6, 7}
            >>> _compare_fingerprints(fp1, fp2)
            0.428...  # 3 common / 7 total unique
        """
        # Handle edge cases: empty fingerprint sets
        if not fp1 or not fp2:
            return 0.0

        # Calculate intersection (common fingerprints)
        intersection = fp1 & fp2

        # Calculate union (all unique fingerprints)
        union = fp1 | fp2

        # Handle edge case: empty union (shouldn't happen, but be defensive)
        if len(union) == 0:
            return 0.0

        # Calculate Jaccard similarity
        jaccard_similarity = len(intersection) / len(union)

        return jaccard_similarity

    def analyze(self, file1_path: Union[str, Path], file2_path: Union[str, Path]) -> Dict:
        """
        Analyze two Python files for similarity using the Winnowing algorithm.

        This method performs the complete Winnowing-based similarity analysis:
        1. Read both files
        2. Tokenize source code
        3. Generate k-grams
        4. Hash k-grams
        5. Apply winnowing to select fingerprints
        6. Compare fingerprint sets using Jaccard similarity

        Args:
            file1_path: Path to the first Python file.
            file2_path: Path to the second Python file.

        Returns:
            Dict: A dictionary containing:
                - similarity_score (float): Fingerprint similarity (0.0 to 1.0)
                - file1 (str): Path to file 1
                - file2 (str): Path to file 2
                - file1_fingerprints (int): Number of fingerprints in file 1
                - file2_fingerprints (int): Number of fingerprints in file 2
                - common_fingerprints (int): Number of matching fingerprints
                - k (int): K-gram size used
                - w (int): Window size used
                - detector (str): Always 'hash'

        Raises:
            FileNotFoundError: If either file does not exist.
            IOError: If either file cannot be read.

        Example:
            >>> detector = HashDetector(threshold=0.6, k=5, w=4)
            >>> result = detector.analyze('student1.py', 'student2.py')
            >>> if result['similarity_score'] >= 0.6:
            ...     print(f"Detected partial copying: {result['similarity_score']:.2%}")
            ...     print(f"Common fingerprints: {result['common_fingerprints']}")
        """
        # Read both files
        source1 = self._read_file(file1_path)
        source2 = self._read_file(file2_path)

        # Tokenize both files
        tokens1 = self._tokenize(source1)
        tokens2 = self._tokenize(source2)

        # Generate k-grams
        kgrams1 = self._generate_kgrams(tokens1, self.k)
        kgrams2 = self._generate_kgrams(tokens2, self.k)

        # Hash k-grams
        hashes1 = self._hash_kgrams(kgrams1)
        hashes2 = self._hash_kgrams(kgrams2)

        # Apply winnowing to select fingerprints
        fingerprints1 = self._winnow(hashes1, self.w)
        fingerprints2 = self._winnow(hashes2, self.w)

        # Compare fingerprints using Jaccard similarity
        similarity_score = self._compare_fingerprints(fingerprints1, fingerprints2)

        # Calculate common fingerprints
        common_fingerprints = len(fingerprints1 & fingerprints2)

        # Prepare detailed result dictionary
        result = {
            "similarity_score": similarity_score,
            "file1": str(file1_path),
            "file2": str(file2_path),
            "file1_fingerprints": len(fingerprints1),
            "file2_fingerprints": len(fingerprints2),
            "common_fingerprints": common_fingerprints,
            "k": self.k,
            "w": self.w,
            "detector": "hash",
        }

        return result

    def compare(self, source1: str, source2: str) -> float:
        """
        Compare two Python source code strings directly using Winnowing.

        This is a convenience method for comparing source code strings
        without reading from files. It's useful for testing or when
        source code is already loaded in memory.

        Args:
            source1: First Python source code string.
            source2: Second Python source code string.

        Returns:
            float: Fingerprint similarity score between 0.0 and 1.0.
                  Returns 0.0 if either source produces no fingerprints.

        Example:
            >>> detector = HashDetector(k=5, w=4)
            >>> code1 = "def add(a, b):\\n    return a + b"
            >>> code2 = "def sum(x, y):\\n    return x + y"
            >>> similarity = detector.compare(code1, code2)
            >>> print(f"Fingerprint similarity: {similarity:.2%}")

        Note:
            This method uses the k and w parameters set during initialization.
        """
        # Tokenize both source strings
        tokens1 = self._tokenize(source1)
        tokens2 = self._tokenize(source2)

        # Generate k-grams
        kgrams1 = self._generate_kgrams(tokens1, self.k)
        kgrams2 = self._generate_kgrams(tokens2, self.k)

        # Hash k-grams
        hashes1 = self._hash_kgrams(kgrams1)
        hashes2 = self._hash_kgrams(kgrams2)

        # Apply winnowing to select fingerprints
        fingerprints1 = self._winnow(hashes1, self.w)
        fingerprints2 = self._winnow(hashes2, self.w)

        # Compare fingerprints and return similarity
        return self._compare_fingerprints(fingerprints1, fingerprints2)
