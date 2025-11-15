# HashDetector Implementation

## Overview

The `HashDetector` class implements the **Winnowing algorithm** (Schleimer et al. 2003) for robust code plagiarism detection. This algorithm is particularly effective at detecting partial and scattered copying while being resilient to small insertions and deletions.

## Algorithm Description

### Winnowing Algorithm Steps

1. **Tokenization**: Extract semantic tokens (identifiers, numbers, strings, operators) from Python source code
2. **K-gram Generation**: Create overlapping sequences of k tokens
3. **Hashing**: Hash each k-gram to create numeric fingerprints
4. **Winnowing**: Select a minimal subset of hashes using a sliding window
5. **Comparison**: Compare fingerprint sets using Jaccard similarity

### Mathematical Foundations

**K-grams**: Given a token sequence `[t1, t2, t3, ..., tn]` and k=3:
```
k-grams = [(t1,t2,t3), (t2,t3,t4), (t3,t4,t5), ...]
```

**Hashing**: Each k-gram is hashed using MD5:
```
hash(k-gram) = MD5(join(k-gram))
```

**Winnowing**: For each window of w consecutive hashes:
- Select the minimum hash value
- If multiple minimums exist, select the rightmost occurrence
- This guarantees detection of matches ≥ (w + k - 1) tokens long

**Jaccard Similarity**:
```
J(A,B) = |A ∩ B| / |A ∪ B|
```
Where A and B are the fingerprint sets from two documents.

## Parameters

### Default Configuration
```python
HashDetector(threshold=0.6, k=5, w=4)
```

### Parameter Details

**threshold** (float, default=0.6):
- Similarity threshold for plagiarism detection
- Range: [0.0, 1.0]
- Default 0.6 means 60% fingerprint overlap flags as plagiarism
- Recommended: 0.55-0.65 for balanced detection

**k** (int, default=5):
- K-gram size (number of tokens per gram)
- Range: ≥1, recommended 3-7
- Larger k:
  - ✓ Fewer false positives (more specific matches)
  - ✗ May miss small code fragments
- Smaller k:
  - ✓ Detects smaller matches
  - ✗ More false positives
- Default k=5 balances sensitivity and specificity

**w** (int, default=4):
- Winnowing window size
- Range: ≥1, recommended 2-5
- Larger w:
  - ✓ Sparser fingerprints (less memory, faster comparison)
  - ✗ May miss some matches
- Smaller w:
  - ✓ Denser fingerprints (more comprehensive)
  - ✗ More memory, slower comparison
- Default w=4 provides good noise resistance

### Guaranteed Match Threshold

With parameters k and w, the algorithm guarantees to detect any match of length:
```
t = w + k - 1 tokens
```

**Example**: With k=5, w=4:
```
t = 4 + 5 - 1 = 8 tokens
```
Any copied sequence ≥ 8 tokens is guaranteed to be detected.

## Usage Examples

### Basic Usage

```python
from detectors.hash_detector import HashDetector

# Create detector with default parameters
detector = HashDetector()

# Compare two files
result = detector.analyze('file1.py', 'file2.py')

print(f"Similarity: {result['similarity_score']:.2%}")
print(f"Common fingerprints: {result['common_fingerprints']}")
print(f"Detection: {'PLAGIARISM' if result['similarity_score'] >= 0.6 else 'OK'}")
```

### Custom Parameters

```python
# High sensitivity (detects smaller matches)
detector_sensitive = HashDetector(threshold=0.5, k=3, w=2)

# High specificity (fewer false positives)
detector_strict = HashDetector(threshold=0.7, k=7, w=5)

# Balanced (default)
detector_balanced = HashDetector(threshold=0.6, k=5, w=4)
```

### Direct String Comparison

```python
detector = HashDetector()

code1 = """
def calculate(x, y):
    return x + y
"""

code2 = """
def compute(a, b):
    return a + b
"""

similarity = detector.compare(code1, code2)
print(f"Similarity: {similarity:.2%}")
```

## Output Format

### analyze() Method Returns:

```python
{
    'similarity_score': 0.72,           # Jaccard similarity (0.0-1.0)
    'file1': 'path/to/file1.py',        # Path to first file
    'file2': 'path/to/file2.py',        # Path to second file
    'file1_fingerprints': 45,           # Number of fingerprints in file1
    'file2_fingerprints': 47,           # Number of fingerprints in file2
    'common_fingerprints': 32,          # Number of matching fingerprints
    'k': 5,                             # K-gram size used
    'w': 4,                             # Window size used
    'detector': 'hash'                  # Detector identifier
}
```

### compare() Method Returns:

```python
0.72  # Similarity score (float, 0.0-1.0)
```

## Strengths and Limitations

### Strengths

✓ **Detects Partial Copying**: Can identify code fragments scattered across files
✓ **Resilient to Insertions/Deletions**: Small changes don't eliminate detection
✓ **Space-Efficient**: Winnowing creates compact fingerprint representation
✓ **Fast Comparison**: Set operations on fingerprints are very efficient
✓ **Guaranteed Detection**: Matches above threshold length are always detected
✓ **No False Negatives**: For sufficiently long matches (≥ w+k-1 tokens)

### Limitations

✗ **Variable Renaming**: Renaming variables creates different tokens → different hashes
✗ **Reordering**: Changing code order breaks k-gram sequences
✗ **Heavy Obfuscation**: Extensive refactoring can defeat detection
✗ **Small Files**: Fewer than k tokens produce no k-grams
✗ **Syntax Errors**: Unparseable code returns 0.0 similarity

### Comparison with Other Detectors

| Aspect | Token Detector | AST Detector | Hash Detector |
|--------|---------------|--------------|---------------|
| **Speed** | Fast (5000 lines/s) | Slow (1000 lines/s) | Medium (3000 lines/s) |
| **Variable Rename** | ✗ Defeated | ✓ Detects | ✗ Defeated |
| **Partial Copy** | ~ Partial | ✗ Weak | ✓ **Strong** |
| **Reordering** | ~ Partial | ~ Partial | ✗ Defeated |
| **Memory** | Low | Medium | **Very Low** |
| **Best For** | Exact copies | Structural plagiarism | Scattered fragments |

## Performance Characteristics

### Time Complexity

- **Tokenization**: O(n) where n = source code length
- **K-gram Generation**: O(m) where m = number of tokens
- **Hashing**: O(m * k) ≈ O(m) since k is constant
- **Winnowing**: O(m * w) ≈ O(m) since w is constant
- **Comparison**: O(f1 + f2) where f = fingerprint count

**Overall**: O(n + m) ≈ O(n) linear in file size

**Target Performance**: 3000 lines/second

### Space Complexity

- **Tokens**: O(m) where m = number of tokens
- **K-grams**: O(m - k + 1) ≈ O(m)
- **Fingerprints**: O(m / w) - winnowing reduces by factor of w
- **Total**: O(m) linear in token count

**Memory Efficiency**: Winnowing reduces fingerprint count from O(m) to O(m/w)

## Edge Cases and Error Handling

### Empty Files
```python
detector.compare("", "def foo(): pass")
# Returns: 0.0 (no fingerprints to compare)
```

### Syntax Errors
```python
detector.compare("def foo(:", "def bar(): pass")
# Returns: 0.0 (gracefully handles tokenization errors)
```

### Insufficient Tokens
```python
detector.compare("x = 1", "y = 2")  # With k=5
# Returns: 0.0 (fewer than k tokens, no k-grams)
```

### Identical Code
```python
detector.compare(code, code)
# Returns: 1.0 (perfect match)
```

## Integration with CodeGuard

### Voting System Integration

The HashDetector is part of the multi-method detection pipeline:

```
Upload → [Token Detector (1.0x)] ─┐
      → [AST Detector   (2.0x)] ─┼→ Voting System → Decision
      → [Hash Detector  (1.5x)] ─┘
```

**Weight**: 1.5x (medium confidence)
**Threshold**: 0.6 (60% fingerprint overlap)

### Decision Logic

```python
# Each detector votes if similarity > threshold
token_votes = 1.0 if token_similarity > 0.70 else 0.0
ast_votes = 2.0 if ast_similarity > 0.80 else 0.0
hash_votes = 1.5 if hash_similarity > 0.60 else 0.0

total_votes = token_votes + ast_votes + hash_votes
max_votes = 1.0 + 2.0 + 1.5  # = 4.5

# Plagiarism if weighted votes ≥ 50%
is_plagiarism = (total_votes / max_votes) >= 0.50
```

## Testing

### Unit Tests

```bash
# Run HashDetector unit tests
pytest tests/unit/test_hash_detector.py -v

# Run with coverage
pytest tests/unit/test_hash_detector.py --cov=src.detectors.hash_detector

# Run specific test
pytest tests/unit/test_hash_detector.py::test_winnowing_algorithm
```

### Test Scenarios

The detector should handle:
1. ✓ Identical code → ~1.0 similarity
2. ✓ Completely different code → <0.2 similarity
3. ✓ Partial copying (fragments) → 0.3-0.6 similarity
4. ✓ Empty files → 0.0 similarity
5. ✓ Syntax errors → 0.0 similarity (no exception)
6. ✓ Files with < k tokens → 0.0 similarity

### Validation

Use the validation datasets:

```bash
# Test on known plagiarism pairs
python scripts/validate_detector.py hash validation-datasets/plagiarized/

# Test on legitimate code
python scripts/validate_detector.py hash validation-datasets/legitimate/
```

## Tuning Recommendations

### For Academic Settings

**Strict** (reduce false positives):
```python
HashDetector(threshold=0.65, k=6, w=4)
```

**Balanced** (default):
```python
HashDetector(threshold=0.6, k=5, w=4)
```

**Sensitive** (detect more cases):
```python
HashDetector(threshold=0.55, k=4, w=3)
```

### Based on Code Size

**Small files** (< 50 lines):
```python
HashDetector(threshold=0.5, k=3, w=2)  # Smaller k to generate more k-grams
```

**Medium files** (50-200 lines):
```python
HashDetector(threshold=0.6, k=5, w=4)  # Default works well
```

**Large files** (> 200 lines):
```python
HashDetector(threshold=0.65, k=6, w=5)  # Larger w for sparser fingerprints
```

## Algorithm Reference

**Original Paper**:
Schleimer, S., Wilkerson, D. S., & Aiken, A. (2003).
"Winnowing: Local algorithms for document fingerprinting."
*Proceedings of the 2003 ACM SIGMOD International Conference on Management of Data*, 76-85.

**Key Properties**:
1. **Guarantee**: Matches of length ≥ t are always detected
2. **Density**: At least one fingerprint every w positions
3. **Robustness**: Resilient to small edits and insertions

## Implementation Details

### Tokenization Strategy

Uses Python's built-in `tokenize` module:
- Extracts semantic tokens (NAME, NUMBER, STRING, OP)
- Filters out comments, whitespace, formatting
- Handles syntax errors gracefully (returns partial token list)

### Hash Function

Uses MD5 for speed (not security):
- Fast computation
- Good distribution
- Low collision rate for short strings
- 128-bit output converted to integer

### Winnowing Implementation

```python
for i in range(len(hashes) - w + 1):
    window = hashes[i:i+w]
    min_hash = min(window)
    # Select rightmost occurrence of minimum
    rightmost_offset = len(window) - 1 - window[::-1].index(min_hash)
    fingerprints.add(hashes[i + rightmost_offset])
```

**Rightmost Selection**: Ensures consistent fingerprints across documents

## Troubleshooting

### Low Similarity on Similar Code

**Problem**: Similar code shows low similarity score

**Possible Causes**:
1. k too large → Reduce k to 3 or 4
2. Variable renaming → Use ASTDetector instead
3. Code reordering → Token or AST detector may work better

### High Similarity on Different Code

**Problem**: Different code shows high similarity score

**Possible Causes**:
1. k too small → Increase k to 6 or 7
2. Common boilerplate → Filter common patterns
3. Threshold too low → Increase threshold to 0.65-0.70

### Performance Issues

**Problem**: Detection is slow

**Solutions**:
1. Increase w for sparser fingerprints
2. Pre-filter files by size
3. Use parallel processing for multiple comparisons

## Future Enhancements

Potential improvements:
1. **Weighted k-grams**: Give more weight to rare tokens
2. **Local alignment**: Find specific matching regions
3. **Incremental hashing**: Update fingerprints without recomputing
4. **Parallel winnowing**: Process multiple windows concurrently
5. **Adaptive parameters**: Adjust k and w based on file size

## License

Part of the CodeGuard plagiarism detection system.
