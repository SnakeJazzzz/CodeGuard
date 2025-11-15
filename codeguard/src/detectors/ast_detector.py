"""
AST-based Plagiarism Detector for Python Code.

This module implements structural similarity detection using Abstract Syntax Tree (AST)
analysis. It normalizes code to remove variable/function names and compares the
underlying structure, making it highly effective against simple obfuscation techniques
like variable renaming.

Mathematical foundations:
    - Tree similarity based on node-by-node structural comparison
    - Normalization removes identifier information while preserving control flow
    - Similarity score = (matching_nodes × 2) / (total_nodes1 + total_nodes2)

Key advantages:
    - Detects plagiarism with renamed variables (>80% accuracy target)
    - Immune to simple obfuscation (spacing, comments, identifier renaming)
    - Focuses on algorithmic structure rather than surface features

Author: CodeGuard Team
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Union, Any, Optional


class ASTDetector:
    """
    AST-based structural similarity detector for Python code plagiarism detection.

    This detector parses Python source code into Abstract Syntax Trees (ASTs),
    normalizes them by removing variable and function names, and compares the
    resulting structural patterns. This approach is particularly effective at
    detecting plagiarism where students have renamed variables or functions but
    kept the same algorithmic structure.

    The detector uses a node-by-node comparison strategy that accounts for:
    - Control flow structures (if/for/while/try/with)
    - Expression complexity and nesting
    - Function and class definitions
    - Operator usage patterns

    Attributes:
        threshold (float): Similarity threshold for plagiarism detection (0.0 to 1.0).
                          Default is 0.8 (80% structural similarity).

    Example:
        >>> detector = ASTDetector(threshold=0.8)
        >>> result = detector.analyze('file1.py', 'file2.py')
        >>> print(f"Similarity: {result['similarity_score']:.2%}")
        >>> print(f"Detector: {result['detector']}")
    """

    # AST node types that represent control flow structures
    # These are key indicators of algorithmic structure
    CONTROL_FLOW_NODES = {
        ast.If, ast.For, ast.While, ast.With, ast.Try,
        ast.ExceptHandler, ast.Match, ast.AsyncFor, ast.AsyncWith
    }

    # AST node types that represent function/class definitions
    DEFINITION_NODES = {
        ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef
    }

    # AST node types for operators and operations
    OPERATOR_NODES = {
        ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
        ast.AugAssign, ast.AnnAssign
    }

    def __init__(self, threshold: float = 0.8):
        """
        Initialize the ASTDetector with a similarity threshold.

        Args:
            threshold (float): Similarity threshold for plagiarism detection.
                             Must be between 0.0 and 1.0. Default is 0.8.
                             Higher thresholds (0.85-0.95) reduce false positives.
                             Lower thresholds (0.70-0.75) increase sensitivity.

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

    def _parse_ast(self, source_code: str) -> Optional[ast.AST]:
        """
        Parse Python source code into an Abstract Syntax Tree.

        Args:
            source_code: Python source code as a string.

        Returns:
            Optional[ast.AST]: The parsed AST, or None if parsing fails.

        Note:
            Syntax errors are handled gracefully by returning None.
            This allows the detector to return 0.0 similarity for unparseable code.
            Empty source code is also treated as unparseable.
        """
        # Handle empty or whitespace-only source code
        if not source_code or not source_code.strip():
            return None

        try:
            return ast.parse(source_code)
        except SyntaxError:
            # Handle syntax errors - return None to indicate unparseable code
            return None
        except Exception:
            # Handle other parsing errors gracefully
            return None

    def _normalize_ast(self, tree: ast.AST) -> ast.AST:
        """
        Normalize an AST by removing variable and function names.

        This normalization process removes all identifier information while
        preserving the structural skeleton of the code. This makes the comparison
        immune to simple obfuscation techniques like variable renaming.

        Normalization steps:
        1. Replace all variable names with generic placeholder 'var'
        2. Replace all function names with generic placeholder 'func'
        3. Replace all string literals with empty string ''
        4. Replace all numeric constants with 0
        5. Keep control flow structures intact
        6. Keep operator types intact

        Args:
            tree: The AST to normalize.

        Returns:
            ast.AST: A normalized copy of the AST with identifiers removed.

        Example:
            Original: def calc(x, y): return x + y
            Normalized: def func(var, var): return var + var
        """
        class NormalizingTransformer(ast.NodeTransformer):
            """
            AST transformer that removes identifier information.

            This transformer visits each node in the AST and replaces
            identifying information with generic placeholders.
            """

            def visit_Name(self, node):
                """Replace variable names with generic 'var'."""
                # Preserve the node type but replace the identifier
                node.id = 'var'
                return node

            def visit_arg(self, node):
                """Replace function argument names with generic 'var'."""
                node.arg = 'var'
                # Remove type annotations for normalization
                node.annotation = None
                return node

            def visit_FunctionDef(self, node):
                """Replace function names but keep structure."""
                node.name = 'func'
                # Remove decorators for normalization
                node.decorator_list = []
                # Remove return type annotation
                node.returns = None
                # Continue normalizing the function body
                self.generic_visit(node)
                return node

            def visit_AsyncFunctionDef(self, node):
                """Replace async function names but keep structure."""
                node.name = 'func'
                node.decorator_list = []
                node.returns = None
                self.generic_visit(node)
                return node

            def visit_ClassDef(self, node):
                """Replace class names but keep structure."""
                node.name = 'Class'
                node.decorator_list = []
                # Keep inheritance structure but normalize base names
                self.generic_visit(node)
                return node

            def visit_Constant(self, node):
                """Replace constant values with generic placeholders."""
                # Preserve the type of constant but normalize the value
                if isinstance(node.value, str):
                    node.value = ''
                elif isinstance(node.value, (int, float, complex)):
                    node.value = 0
                elif isinstance(node.value, bool):
                    node.value = True
                elif node.value is None:
                    pass  # Keep None as is
                return node

            def visit_Attribute(self, node):
                """Replace attribute names with generic 'attr'."""
                node.attr = 'attr'
                self.generic_visit(node)
                return node

        # Create a deep copy and normalize it
        import copy
        normalized_tree = copy.deepcopy(tree)
        transformer = NormalizingTransformer()
        normalized_tree = transformer.visit(normalized_tree)

        return normalized_tree

    def _extract_structure_signature(self, tree: ast.AST) -> List[str]:
        """
        Extract a structural signature from an AST.

        This creates a sequence of node type identifiers that represents
        the structural pattern of the code. The signature captures:
        - Node types in depth-first traversal order
        - Control flow patterns
        - Expression nesting
        - Operator types (to distinguish different operations)

        Args:
            tree: The AST to extract signature from.

        Returns:
            List[str]: A list of node type names representing the structure,
                      including operator details for better discrimination.

        Example:
            For code: "if x > 0: return x"
            Signature: ['Module', 'If', 'Compare', 'Name', 'Gt', 'Constant',
                       'Return', 'Name']
        """
        signature = []

        def traverse(node):
            """Depth-first traversal to collect node types with operator details."""
            if node is None:
                return

            # Add the node type to signature
            node_type = node.__class__.__name__
            signature.append(node_type)

            # For operators, also add the specific operator type
            # This helps distinguish between different operations
            if isinstance(node, ast.BinOp):
                signature.append(node.op.__class__.__name__)
            elif isinstance(node, ast.UnaryOp):
                signature.append(node.op.__class__.__name__)
            elif isinstance(node, ast.BoolOp):
                signature.append(node.op.__class__.__name__)
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    signature.append(op.__class__.__name__)
            elif isinstance(node, ast.AugAssign):
                signature.append(node.op.__class__.__name__)

            # Recursively traverse child nodes
            for child in ast.iter_child_nodes(node):
                traverse(child)

        traverse(tree)
        return signature

    def _count_node_types(self, tree: ast.AST) -> Dict[str, int]:
        """
        Count occurrences of each node type in the AST.

        This provides a frequency-based structural fingerprint that can
        be used to quickly assess similarity before detailed comparison.

        Args:
            tree: The AST to analyze.

        Returns:
            Dict[str, int]: Mapping of node type names to their counts.

        Example:
            {'FunctionDef': 2, 'If': 3, 'For': 1, 'Return': 2, ...}
        """
        counts = {}

        def traverse(node):
            """Count each node type."""
            if node is None:
                return

            node_type = node.__class__.__name__
            counts[node_type] = counts.get(node_type, 0) + 1

            for child in ast.iter_child_nodes(node):
                traverse(child)

        traverse(tree)
        return counts

    def _calculate_structure_similarity(self, sig1: List[str], sig2: List[str]) -> float:
        """
        Calculate similarity between two structural signatures.

        Uses both Longest Common Subsequence (LCS) for structural matching
        and Jaccard similarity for overall node type overlap. This provides
        a balanced measure that rewards both sequence similarity and node diversity.

        Args:
            sig1: First structure signature.
            sig2: Second structure signature.

        Returns:
            float: Similarity score between 0.0 and 1.0.

        Algorithm:
            - LCS similarity = (2 × LCS_length) / (len(sig1) + len(sig2))
            - Jaccard similarity = |set1 ∩ set2| / |set1 ∪ set2|
            - Combined = 0.7 × LCS + 0.3 × Jaccard

        This formula ensures:
        - Identical structures score 1.0
        - Different algorithms with different node types score lower
        - Sequence order matters (70% weight on LCS)
        """
        if len(sig1) == 0 and len(sig2) == 0:
            return 0.0

        if len(sig1) == 0 or len(sig2) == 0:
            return 0.0

        # Calculate Longest Common Subsequence length using dynamic programming
        lcs_length = self._lcs_length(sig1, sig2)

        # Calculate LCS-based similarity
        total_length = len(sig1) + len(sig2)
        lcs_similarity = (2.0 * lcs_length) / total_length

        # Calculate Jaccard similarity on node type sets
        set1 = set(sig1)
        set2 = set(sig2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        jaccard_similarity = intersection / union if union > 0 else 0.0

        # Combine both metrics
        # LCS captures sequence order (main structure)
        # Jaccard captures node diversity (penalizes different operations)
        combined = 0.7 * lcs_similarity + 0.3 * jaccard_similarity

        return combined

    def _lcs_length(self, seq1: List[str], seq2: List[str]) -> int:
        """
        Calculate the length of the Longest Common Subsequence.

        This is a classic dynamic programming algorithm used to find the
        longest sequence of elements that appear in both sequences in the
        same relative order (but not necessarily consecutively).

        Args:
            seq1: First sequence.
            seq2: Second sequence.

        Returns:
            int: Length of the longest common subsequence.

        Time Complexity: O(m × n) where m, n are sequence lengths
        Space Complexity: O(m × n)

        Note:
            For performance on large files, this could be optimized to O(n)
            space by keeping only two rows of the DP table.
        """
        m, n = len(seq1), len(seq2)

        # Create DP table - dp[i][j] stores LCS length of seq1[0:i] and seq2[0:j]
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Fill the DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    # Characters match - extend LCS
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    # Characters don't match - take max from previous states
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    def _compare_trees(self, tree1: ast.AST, tree2: ast.AST) -> float:
        """
        Compare two ASTs and return a similarity score.

        This method combines multiple similarity metrics for robust comparison:
        1. Structural signature similarity (sequence-based with operator details)
        2. Node type frequency similarity (bag-of-nodes)
        3. Tree size ratio (to penalize very different-sized programs)

        Args:
            tree1: First AST to compare.
            tree2: Second AST to compare.

        Returns:
            float: Similarity score between 0.0 and 1.0.

        Algorithm:
            - Extract structural signatures from both trees
            - Calculate sequence-based similarity using LCS
            - Calculate frequency-based similarity
            - Apply size penalty for significantly different tree sizes
            - Combine with weighted average
        """
        # Extract structural signatures
        sig1 = self._extract_structure_signature(tree1)
        sig2 = self._extract_structure_signature(tree2)

        # Calculate primary similarity metric (structural sequence similarity)
        structural_similarity = self._calculate_structure_similarity(sig1, sig2)

        # Calculate node type frequency similarity as secondary metric
        counts1 = self._count_node_types(tree1)
        counts2 = self._count_node_types(tree2)
        frequency_similarity = self._calculate_frequency_similarity(counts1, counts2)

        # Calculate size ratio penalty
        # If trees are very different sizes, penalize the similarity
        len1, len2 = len(sig1), len(sig2)
        if len1 == 0 or len2 == 0:
            size_ratio = 0.0
        else:
            size_ratio = min(len1, len2) / max(len1, len2)

        # Apply size penalty: if size difference is >20%, reduce similarity
        if size_ratio < 0.8:
            size_penalty = size_ratio
        else:
            size_penalty = 1.0

        # Combine metrics with weights
        # Structural similarity: 60%
        # Frequency similarity: 30%
        # Size consideration: 10% (penalizes mismatched sizes)
        combined_similarity = (
            0.6 * structural_similarity +
            0.3 * frequency_similarity +
            0.1 * size_penalty
        )

        return combined_similarity

    def _calculate_frequency_similarity(self, counts1: Dict[str, int],
                                       counts2: Dict[str, int]) -> float:
        """
        Calculate similarity based on node type frequencies.

        Uses cosine similarity on node type frequency vectors.
        This provides a complementary metric to structural sequence similarity.

        Args:
            counts1: Node type counts from first tree.
            counts2: Node type counts from second tree.

        Returns:
            float: Frequency-based similarity score between 0.0 and 1.0.
        """
        if len(counts1) == 0 and len(counts2) == 0:
            return 0.0

        if len(counts1) == 0 or len(counts2) == 0:
            return 0.0

        # Get all unique node types
        all_types = set(counts1.keys()).union(set(counts2.keys()))

        # Calculate dot product and magnitudes for cosine similarity
        dot_product = 0.0
        magnitude1 = 0.0
        magnitude2 = 0.0

        for node_type in all_types:
            count1 = counts1.get(node_type, 0)
            count2 = counts2.get(node_type, 0)

            dot_product += count1 * count2
            magnitude1 += count1 ** 2
            magnitude2 += count2 ** 2

        # Calculate cosine similarity
        magnitude1 = magnitude1 ** 0.5
        magnitude2 = magnitude2 ** 0.5

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        cosine_sim = dot_product / (magnitude1 * magnitude2)

        return cosine_sim

    def analyze(self, file1_path: Union[str, Path], file2_path: Union[str, Path]) -> Dict:
        """
        Analyze two Python files for structural similarity and potential plagiarism.

        This method:
        1. Reads both files
        2. Parses them into ASTs
        3. Normalizes the ASTs to remove identifier information
        4. Compares the normalized structures
        5. Returns detailed similarity analysis

        Args:
            file1_path: Path to the first Python file.
            file2_path: Path to the second Python file.

        Returns:
            Dict: A dictionary containing:
                - similarity_score (float): Structural similarity score (0.0 to 1.0)
                - file1 (str): Path to file 1
                - file2 (str): Path to file 2
                - file1_nodes (int): Number of AST nodes in file 1
                - file2_nodes (int): Number of AST nodes in file 2
                - common_structures (int): Approximate number of matching structures
                - detector (str): Always 'ast'

        Raises:
            FileNotFoundError: If either file does not exist.
            IOError: If either file cannot be read.

        Example:
            >>> detector = ASTDetector(threshold=0.8)
            >>> result = detector.analyze('student1.py', 'student2.py')
            >>> if result['similarity_score'] >= 0.8:
            ...     print(f"High structural similarity: {result['similarity_score']:.2%}")
        """
        # Read both files
        source1 = self._read_file(file1_path)
        source2 = self._read_file(file2_path)

        # Parse into ASTs
        tree1 = self._parse_ast(source1)
        tree2 = self._parse_ast(source2)

        # Handle parsing failures
        if tree1 is None or tree2 is None:
            # If either file has syntax errors, return zero similarity
            return {
                'similarity_score': 0.0,
                'file1': str(file1_path),
                'file2': str(file2_path),
                'file1_nodes': 0,
                'file2_nodes': 0,
                'common_structures': 0,
                'detector': 'ast'
            }

        # Normalize ASTs to remove identifier information
        normalized1 = self._normalize_ast(tree1)
        normalized2 = self._normalize_ast(tree2)

        # Compare normalized ASTs
        similarity_score = self._compare_trees(normalized1, normalized2)

        # Extract structural signatures for statistics
        sig1 = self._extract_structure_signature(tree1)
        sig2 = self._extract_structure_signature(tree2)

        # Calculate common structures (approximation using LCS)
        common_structures = self._lcs_length(sig1, sig2)

        # Prepare detailed result
        result = {
            'similarity_score': similarity_score,
            'file1': str(file1_path),
            'file2': str(file2_path),
            'file1_nodes': len(sig1),
            'file2_nodes': len(sig2),
            'common_structures': common_structures,
            'detector': 'ast'
        }

        return result

    def compare(self, source1: str, source2: str) -> float:
        """
        Compare two Python source code strings directly for structural similarity.

        This is a convenience method for comparing source code strings
        without reading from files. It's useful for testing or when
        source code is already loaded in memory.

        Args:
            source1: First Python source code string.
            source2: Second Python source code string.

        Returns:
            float: Structural similarity score between 0.0 and 1.0.
                  Returns 0.0 if either source has syntax errors.

        Example:
            >>> detector = ASTDetector()
            >>> code1 = "def add(a, b):\\n    return a + b"
            >>> code2 = "def sum(x, y):\\n    return x + y"
            >>> similarity = detector.compare(code1, code2)
            >>> print(f"Structural similarity: {similarity:.2%}")
        """
        # Parse both source strings
        tree1 = self._parse_ast(source1)
        tree2 = self._parse_ast(source2)

        # Handle parsing failures
        if tree1 is None or tree2 is None:
            return 0.0

        # Normalize ASTs
        normalized1 = self._normalize_ast(tree1)
        normalized2 = self._normalize_ast(tree2)

        # Compare and return similarity
        return self._compare_trees(normalized1, normalized2)
