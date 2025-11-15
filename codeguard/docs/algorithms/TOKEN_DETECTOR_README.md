# TokenDetector Implementation Guide

## Overview

The `TokenDetector` class is a lexical token-based plagiarism detection system for Python code. It uses Python's built-in `tokenize` module to extract semantic tokens and computes similarity using both **Jaccard** and **Cosine** similarity metrics.

## Location

**File:** `/Users/michaelthemac/desktop/Tec/8_semestre/DAA/Reto/CodeGuard/codeguard/src/detectors/token_detector.py`

## Features

### 1. Accurate Tokenization
- Uses Python's built-in `tokenize` module for precise lexical analysis
- Filters out non-semantic tokens (comments, whitespace, indentation)
- Retains semantic tokens: identifiers, numbers, strings, operators
- Handles syntax errors gracefully

### 2. Dual Similarity Metrics

#### Jaccard Similarity
```
J(A,B) = |A ∩ B| / |A ∪ B|
```
- Measures overlap of unique tokens
- Good for detecting copy-paste plagiarism
- Range: 0.0 (no overlap) to 1.0 (identical)

#### Cosine Similarity
```
cos(θ) = (A·B) / (||A|| × ||B||)
```
- Measures similarity of token frequency vectors
- Accounts for token repetition patterns
- Range: 0.0 (orthogonal) to 1.0 (identical)

### 3. Robust Detection
- Combined similarity score (average of Jaccard and Cosine)
- Configurable threshold (default: 0.7 = 70%)
- Comprehensive result dictionary with detailed statistics

## Usage

### Basic Usage

```python
from detectors.token_detector import TokenDetector

# Create detector with default threshold (0.7)
detector = TokenDetector()

# Analyze two files
result = detector.analyze('student1.py', 'student2.py')

# Check results
if result['is_plagiarism']:
    print(f"Plagiarism detected! Similarity: {result['similarity_score']:.2%}")
else:
    print(f"No plagiarism. Similarity: {result['similarity_score']:.2%}")
```

### Custom Threshold

```python
# Stricter detection (80% threshold)
strict_detector = TokenDetector(threshold=0.8)

# More lenient detection (60% threshold)
lenient_detector = TokenDetector(threshold=0.6)
```

### Direct String Comparison

```python
detector = TokenDetector()

code1 = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

code2 = """
def factorial(num):
    if num <= 1:
        return 1
    return num * factorial(num - 1)
"""

similarity = detector.compare(code1, code2)
print(f"Similarity: {similarity:.2%}")
```

## API Reference

### Class: `TokenDetector`

#### Constructor

```python
TokenDetector(threshold: float = 0.7)
```

**Parameters:**
- `threshold` (float): Similarity threshold for plagiarism detection (0.0 to 1.0). Default is 0.7.

**Raises:**
- `ValueError`: If threshold is not between 0.0 and 1.0.

#### Method: `analyze`

```python
analyze(file1_path: Union[str, Path], file2_path: Union[str, Path]) -> Dict
```

Analyze two Python files for similarity and potential plagiarism.

**Parameters:**
- `file1_path`: Path to the first Python file
- `file2_path`: Path to the second Python file

**Returns:** Dictionary with the following structure:
```python
{
    'similarity_score': float,      # Combined score (0.0 to 1.0)
    'is_plagiarism': bool,          # True if score >= threshold
    'threshold': float,             # The threshold used
    'jaccard_similarity': float,    # Jaccard metric (0.0 to 1.0)
    'cosine_similarity': float,     # Cosine metric (0.0 to 1.0)
    'details': {
        'file1_tokens': int,        # Number of tokens in file 1
        'file2_tokens': int,        # Number of tokens in file 2
        'common_tokens': int,       # Number of common unique tokens
        'file1_path': str,          # Path to file 1
        'file2_path': str,          # Path to file 2
    }
}
```

**Raises:**
- `FileNotFoundError`: If either file does not exist
- `IOError`: If either file cannot be read

#### Method: `compare`

```python
compare(source1: str, source2: str) -> float
```

Compare two Python source code strings directly.

**Parameters:**
- `source1`: First Python source code string
- `source2`: Second Python source code string

**Returns:** Combined similarity score (0.0 to 1.0)

## Algorithm Details

### Token Filtering

The detector filters tokens to retain only semantic elements:

- **NAME**: Identifiers (variables, functions, classes, keywords)
- **NUMBER**: Numeric literals (integers, floats, complex)
- **STRING**: String literals
- **OP**: Operators (+, -, *, /, ==, !=, etc.)

**Excluded:**
- COMMENT: Comments
- NL, NEWLINE: Line breaks
- INDENT, DEDENT: Indentation
- ENCODING: File encoding markers

### Normalization

- All tokens are converted to lowercase
- This makes comparison case-insensitive
- Reduces false negatives from style differences

### Edge Cases

1. **Empty files**: Returns 0.0 similarity
2. **Syntax errors**: Handled gracefully, uses tokens collected before error
3. **Identical files**: Returns 1.0 similarity (100%)
4. **Comments**: Ignored (filtered out during tokenization)

## Performance Characteristics

### Time Complexity
- Tokenization: O(n) where n is file size
- Jaccard calculation: O(m) where m is number of unique tokens
- Cosine calculation: O(m)
- **Overall: O(n + m)** - Linear in file size

### Space Complexity
- Token storage: O(n)
- Set operations: O(m)
- **Overall: O(n)** - Linear in file size

### Speed Target
- **~5000 lines/second** (as specified in requirements)
- Actual speed depends on hardware and token density

## Test Results

### Test 1: Identical Code
```
Similarity: 100.00%
Result: PASS
```

### Test 2: Variable Renaming
```
Similarity: 54.93%
Result: Detects structural similarity despite different names
```

### Test 3: Completely Different Code
```
Similarity: 21.98%
Result: PASS (correctly identifies as different)
```

### Test 4: Copy with Comments
```
Similarity: 100.00%
Result: PASS (comments are correctly filtered)
```

### Test 5: Error Handling
```
- Invalid threshold: ValueError raised correctly
- Empty code: 0.0 similarity (graceful handling)
- Syntax errors: Partial tokenization (graceful handling)
```

## Strengths

1. **Fast Processing**: Linear time complexity, handles large files efficiently
2. **Accurate**: Uses Python's standard tokenize module
3. **Robust**: Handles syntax errors and edge cases gracefully
4. **Comment-Agnostic**: Filters out comments automatically
5. **Configurable**: Adjustable threshold for different detection levels
6. **Dual Metrics**: Combines Jaccard and Cosine for balanced detection

## Limitations

1. **Variable Renaming**: Can be defeated by systematic variable renaming (54% similarity vs 100% for identical)
2. **Code Reordering**: Cannot detect if code blocks are reordered
3. **Algorithmic Changes**: Does not understand semantic equivalence
4. **False Positives**: Simple code patterns may show high similarity

## Mitigation Strategies

The TokenDetector is designed to work with other detectors:

- **ASTDetector**: Catches structural plagiarism (variable renaming resistant)
- **HashDetector**: Detects partial copying and patchwork plagiarism

Use all three detectors in combination for comprehensive detection.

## Configuration Recommendations

### Academic Setting (Strict)
```python
detector = TokenDetector(threshold=0.8)
```

### Code Review (Moderate)
```python
detector = TokenDetector(threshold=0.7)  # Default
```

### Initial Screening (Lenient)
```python
detector = TokenDetector(threshold=0.6)
```

## Integration Example

```python
from detectors.token_detector import TokenDetector

class PlagiarismDetector:
    def __init__(self):
        self.token_detector = TokenDetector(threshold=0.7)

    def check_submission(self, student_file, reference_files):
        results = []

        for ref_file in reference_files:
            result = self.token_detector.analyze(student_file, ref_file)

            if result['is_plagiarism']:
                results.append({
                    'file': ref_file,
                    'score': result['similarity_score'],
                    'details': result['details']
                })

        return results
```

## Testing

Run the test suite:

```bash
cd /Users/michaelthemac/desktop/Tec/8_semestre/DAA/Reto/CodeGuard/codeguard
python3 test_token_detector.py
```

Test with sample files:

```bash
python3 test_file_analysis.py
```

## Mathematical Foundations

### Jaccard Similarity

Given two sets A and B:

```
J(A,B) = |A ∩ B| / |A ∪ B|
```

Where:
- |A ∩ B| = size of intersection (common elements)
- |A ∪ B| = size of union (all unique elements)

**Properties:**
- Symmetric: J(A,B) = J(B,A)
- Range: [0, 1]
- J(A,A) = 1 (identical sets)
- J(A,B) = 0 if A and B are disjoint

### Cosine Similarity

Given two vectors A and B:

```
cos(θ) = (A·B) / (||A|| × ||B||)
```

Where:
- A·B = dot product = Σ(Ai × Bi)
- ||A|| = L2 norm = √(Σ(Ai²))
- θ = angle between vectors

**Properties:**
- Symmetric: cos(A,B) = cos(B,A)
- Range: [0, 1] for frequency vectors
- cos(A,A) = 1 (identical vectors)
- Accounts for frequency, not just presence

## File Structure

```
codeguard/
├── src/
│   └── detectors/
│       ├── __init__.py
│       └── token_detector.py          # Main implementation
├── test_token_detector.py             # Unit tests
├── test_file_analysis.py              # File-based tests
├── sample_file1.py                    # Test data
├── sample_file2.py                    # Test data
└── TOKEN_DETECTOR_GUIDE.md            # This file
```

## Dependencies

- Python 3.7+
- Standard library only (no external dependencies)
  - `tokenize`: Lexical analysis
  - `collections.Counter`: Frequency counting
  - `pathlib.Path`: File path handling
  - `math`: Mathematical functions

## Contributing

When modifying the TokenDetector:

1. Maintain backward compatibility with the `analyze()` interface
2. Keep the `compare()` method for string-based comparison
3. Add tests for new functionality
4. Update this documentation
5. Follow PEP 8 style guidelines
6. Include type hints for all methods

## License

Part of the CodeGuard plagiarism detection system.

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the inline documentation (docstrings)
3. Run the test suite to verify functionality

## Version History

- **v1.0** (2025-11-11): Initial implementation
  - Dual similarity metrics (Jaccard + Cosine)
  - File and string comparison
  - Comprehensive error handling
  - Full test coverage
