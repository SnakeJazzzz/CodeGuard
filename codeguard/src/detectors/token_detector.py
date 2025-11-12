"""
Token-based Plagiarism Detector for Python Code.

This module implements lexical similarity detection using token-based analysis.
It tokenizes Python source code and compares files using Jaccard and Cosine
similarity metrics.

Mathematical foundations:
    - Jaccard Similarity: J(A,B) = |A ∩ B| / |A ∪ B|
    - Cosine Similarity: cos(θ) = (A·B) / (||A|| × ||B||)

Author: CodeGuard Team
"""

import io
import tokenize
import keyword
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union
import math


class TokenDetector:
    """
    Token-based similarity detector for Python code plagiarism detection.

    This detector tokenizes Python source code using the built-in tokenize module,
    filters semantic tokens, and computes similarity using both Jaccard and Cosine
    metrics for robust comparison.

    Attributes:
        threshold (float): Similarity threshold for plagiarism detection (0.0 to 1.0).
                          Default is 0.7 (70% similarity).

    Example:
        >>> detector = TokenDetector(threshold=0.7)
        >>> result = detector.analyze('file1.py', 'file2.py')
        >>> print(f"Similarity: {result['similarity_score']:.2%}")
        >>> print(f"Is plagiarism: {result['is_plagiarism']}")
    """

    # Token types that carry semantic meaning (exclude formatting/whitespace)
    SEMANTIC_TOKEN_TYPES = {
        tokenize.NAME,       # Identifiers (variable names, function names, keywords)
        tokenize.NUMBER,     # Numeric literals
        tokenize.STRING,     # String literals
        tokenize.OP,         # Operators (+, -, *, /, etc.)
    }

    def __init__(self, threshold: float = 0.7):
        """
        Initialize the TokenDetector with a similarity threshold.

        Args:
            threshold (float): Similarity threshold for plagiarism detection.
                             Must be between 0.0 and 1.0. Default is 0.7.

        Raises:
            ValueError: If threshold is not between 0.0 and 1.0.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

        self.threshold = threshold

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
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")

    def _tokenize_code(self, source_code: str) -> List[str]:
        """
        Tokenize Python source code into semantic tokens.

        This method uses Python's built-in tokenize module to extract tokens,
        filtering out comments, whitespace, and other non-semantic elements.
        Only tokens that carry semantic meaning are retained.

        Args:
            source_code: Python source code as a string.

        Returns:
            List[str]: List of semantic token strings.

        Note:
            - Syntax errors are handled gracefully by returning an empty list
            - Comments and docstrings are filtered out
            - Whitespace and formatting tokens are ignored
            - Token values are normalized to lowercase for case-insensitive comparison
        """
        tokens = []

        try:
            # Convert source code string to bytes for tokenizer
            source_bytes = source_code.encode('utf-8')
            readline = io.BytesIO(source_bytes).readline

            # Tokenize the source code
            token_generator = tokenize.tokenize(readline)

            for token in token_generator:
                token_type = token.type
                token_string = token.string

                # Filter for semantic tokens only
                if token_type in self.SEMANTIC_TOKEN_TYPES:
                    # Normalize token to lowercase for case-insensitive comparison
                    normalized_token = token_string.lower()
                    tokens.append(normalized_token)

        except tokenize.TokenError as e:
            # Handle incomplete or malformed Python code
            # Return tokens collected so far
            pass
        except Exception as e:
            # Handle other tokenization errors gracefully
            # Return empty list for completely invalid code
            pass

        return tokens

    def _calculate_jaccard_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate Jaccard similarity between two token sequences.

        Jaccard similarity measures the overlap between two sets:
            J(A,B) = |A ∩ B| / |A ∪ B|

        This metric is effective for detecting copy-paste plagiarism where
        the same unique tokens appear in both files.

        Args:
            tokens1: List of tokens from the first file.
            tokens2: List of tokens from the second file.

        Returns:
            float: Jaccard similarity score between 0.0 and 1.0.
                  Returns 0.0 if both token lists are empty.
        """
        # Convert token lists to sets for set operations
        set1 = set(tokens1)
        set2 = set(tokens2)

        # Handle edge case: both sets are empty
        if len(set1) == 0 and len(set2) == 0:
            return 0.0

        # Calculate intersection and union
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        # Handle edge case: union is empty (shouldn't happen, but be safe)
        if len(union) == 0:
            return 0.0

        # Calculate Jaccard similarity
        jaccard_similarity = len(intersection) / len(union)

        return jaccard_similarity

    def _calculate_cosine_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate Cosine similarity between two token sequences.

        Cosine similarity measures the cosine of the angle between two
        frequency vectors:
            cos(θ) = (A·B) / (||A|| × ||B||)

        This metric accounts for token frequency and is effective for
        detecting plagiarism where code patterns are repeated.

        Args:
            tokens1: List of tokens from the first file.
            tokens2: List of tokens from the second file.

        Returns:
            float: Cosine similarity score between 0.0 and 1.0.
                  Returns 0.0 if either token list is empty.
        """
        # Handle edge cases: empty token lists
        if len(tokens1) == 0 or len(tokens2) == 0:
            return 0.0

        # Create frequency vectors using Counter
        freq1 = Counter(tokens1)
        freq2 = Counter(tokens2)

        # Get all unique tokens from both files
        all_tokens = set(freq1.keys()).union(set(freq2.keys()))

        # Calculate dot product
        dot_product = sum(freq1.get(token, 0) * freq2.get(token, 0)
                         for token in all_tokens)

        # Calculate magnitudes (L2 norm)
        magnitude1 = math.sqrt(sum(count ** 2 for count in freq1.values()))
        magnitude2 = math.sqrt(sum(count ** 2 for count in freq2.values()))

        # Handle edge case: zero magnitude
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        # Calculate cosine similarity
        cosine_similarity = dot_product / (magnitude1 * magnitude2)

        return cosine_similarity

    def analyze(self, file1_path: Union[str, Path], file2_path: Union[str, Path]) -> Dict:
        """
        Analyze two Python files for similarity and potential plagiarism.

        This method reads both files, tokenizes them, and computes similarity
        using both Jaccard and Cosine metrics. The final similarity score is
        the average of both metrics.

        Args:
            file1_path: Path to the first Python file.
            file2_path: Path to the second Python file.

        Returns:
            Dict: A dictionary containing:
                - similarity_score (float): Combined similarity score (0.0 to 1.0)
                - is_plagiarism (bool): True if similarity >= threshold
                - threshold (float): The threshold used for detection
                - jaccard_similarity (float): Jaccard similarity score
                - cosine_similarity (float): Cosine similarity score
                - details (dict): Additional statistics:
                    - file1_tokens (int): Number of tokens in file 1
                    - file2_tokens (int): Number of tokens in file 2
                    - common_tokens (int): Number of unique common tokens
                    - file1_path (str): Path to file 1
                    - file2_path (str): Path to file 2

        Raises:
            FileNotFoundError: If either file does not exist.
            IOError: If either file cannot be read.

        Example:
            >>> detector = TokenDetector(threshold=0.7)
            >>> result = detector.analyze('student1.py', 'student2.py')
            >>> if result['is_plagiarism']:
            ...     print(f"Plagiarism detected! Score: {result['similarity_score']:.2%}")
        """
        # Read both files
        source1 = self._read_file(file1_path)
        source2 = self._read_file(file2_path)

        # Tokenize both files
        tokens1 = self._tokenize_code(source1)
        tokens2 = self._tokenize_code(source2)

        # Calculate both similarity metrics
        jaccard_sim = self._calculate_jaccard_similarity(tokens1, tokens2)
        cosine_sim = self._calculate_cosine_similarity(tokens1, tokens2)

        # Calculate combined similarity score (average of both metrics)
        # This provides a balanced measure that combines set overlap (Jaccard)
        # with frequency-based similarity (Cosine)
        similarity_score = (jaccard_sim + cosine_sim) / 2.0

        # Determine if this is plagiarism based on threshold
        is_plagiarism = similarity_score >= self.threshold

        # Calculate common tokens for detailed statistics
        common_tokens = set(tokens1).intersection(set(tokens2))

        # Prepare detailed result dictionary
        result = {
            'similarity_score': similarity_score,
            'is_plagiarism': is_plagiarism,
            'threshold': self.threshold,
            'jaccard_similarity': jaccard_sim,
            'cosine_similarity': cosine_sim,
            'details': {
                'file1_tokens': len(tokens1),
                'file2_tokens': len(tokens2),
                'common_tokens': len(common_tokens),
                'file1_path': str(file1_path),
                'file2_path': str(file2_path),
            }
        }

        return result

    def compare(self, source1: str, source2: str) -> float:
        """
        Compare two Python source code strings directly.

        This is a convenience method for comparing source code strings
        without reading from files. It's useful for testing or when
        source code is already loaded in memory.

        Args:
            source1: First Python source code string.
            source2: Second Python source code string.

        Returns:
            float: Combined similarity score between 0.0 and 1.0.

        Example:
            >>> detector = TokenDetector()
            >>> code1 = "def add(a, b):\\n    return a + b"
            >>> code2 = "def sum(x, y):\\n    return x + y"
            >>> similarity = detector.compare(code1, code2)
            >>> print(f"Similarity: {similarity:.2%}")
        """
        # Tokenize both source strings
        tokens1 = self._tokenize_code(source1)
        tokens2 = self._tokenize_code(source2)

        # Calculate both similarity metrics
        jaccard_sim = self._calculate_jaccard_similarity(tokens1, tokens2)
        cosine_sim = self._calculate_cosine_similarity(tokens1, tokens2)

        # Return average similarity
        return (jaccard_sim + cosine_sim) / 2.0
