# Detection Algorithms

This directory contains the three complementary plagiarism detection algorithms that form the core of CodeGuard's analysis engine.

## Files

### `base_detector.py`
Abstract base class defining the detector interface. All detection algorithms inherit from this class.

**Key Components**:
- `BaseDetector` abstract class
- `compare(source1: str, source2: str) -> float` method signature
- Common preprocessing utilities
- Error handling framework

### `token_detector.py`
Lexical token-based similarity detection.

**Algorithm**:
- Tokenizes Python source code using the `tokenize` module
- Normalizes tokens (removes identifiers, keeps structure)
- Calculates Jaccard and Cosine similarity on token sequences

**Strengths**:
- Fast processing (~5000 lines/second)
- Effective for direct copying
- Simple implementation

**Weaknesses**:
- Defeated by variable renaming
- Sensitive to code formatting

**Configuration**:
- Threshold: 0.70 (default)
- Weight in voting: 1.0x

### `ast_detector.py`
Abstract Syntax Tree structural comparison.

**Algorithm**:
- Parses code into AST using Python's `ast` module
- Normalizes AST (removes variable names, keeps structure)
- Compares tree structure using tree edit distance or isomorphism

**Strengths**:
- Detects structural plagiarism
- Immune to variable renaming
- Captures algorithmic similarity

**Weaknesses**:
- Slower processing (~1000 lines/second)
- May produce false positives for simple patterns
- Computationally intensive

**Configuration**:
- Threshold: 0.80 (default)
- Weight in voting: 2.0x (highest weight - most reliable)

### `hash_detector.py`
Winnowing algorithm for hash-based fingerprinting.

**Algorithm**:
- Creates k-grams from token sequences (k=5 default)
- Hashes k-grams using MD5 (truncated to 8 hex digits)
- Selects representative fingerprints using winnowing window (w=4)
- Compares fingerprint sets using Jaccard similarity

**Strengths**:
- Detects partial copying
- Identifies scattered plagiarism (patchwork)
- Moderate processing speed (~3000 lines/second)

**Weaknesses**:
- Requires parameter tuning (k-gram size, window size)
- May miss heavily obfuscated code

**Configuration**:
- Threshold: 0.60 (default)
- Weight in voting: 1.5x
- k-gram size: 5 tokens
- Winnowing window: 4 k-grams

## Usage Example

```python
from detectors.token_detector import TokenDetector
from detectors.ast_detector import ASTDetector
from detectors.hash_detector import HashDetector

# Read source files
with open('submission1.py', 'r') as f:
    source1 = f.read()
with open('submission2.py', 'r') as f:
    source2 = f.read()

# Run all three detectors
token_detector = TokenDetector()
ast_detector = ASTDetector()
hash_detector = HashDetector()

token_similarity = token_detector.compare(source1, source2)
ast_similarity = ast_detector.compare(source1, source2)
hash_similarity = hash_detector.compare(source1, source2)

print(f"Token similarity: {token_similarity:.2%}")
print(f"AST similarity: {ast_similarity:.2%}")
print(f"Hash similarity: {hash_similarity:.2%}")
```

## Detection Strategy

The three methods complement each other:

1. **Token Detection**: Quick initial screening
   - Fast execution
   - Catches obvious copying
   - Low false negatives for direct copies

2. **AST Detection**: Deep structural analysis
   - Most reliable for plagiarism determination
   - Highest weight in voting system
   - Catches sophisticated attempts

3. **Hash Detection**: Partial copy identification
   - Finds scattered copying
   - Detects patchwork plagiarism
   - Balances speed and accuracy

## Implementation Requirements

Each detector must:
- Inherit from `BaseDetector`
- Implement `compare(source1: str, source2: str) -> float`
- Return similarity score in range [0.0, 1.0]
- Handle syntax errors gracefully
- Log processing time and errors
- Support configuration via constructor parameters

## Testing

Unit tests for each detector:
- `tests/unit/test_token_detector.py`
- `tests/unit/test_ast_detector.py`
- `tests/unit/test_hash_detector.py`

Test cases include:
- Identical code (expect ~1.0 similarity)
- Completely different code (expect ~0.0 similarity)
- Variable renaming (expect high AST, low token)
- Partial copying (expect high hash similarity)
- Syntax errors (expect graceful handling)

## Performance Targets

| Detector | Speed Target | Typical Use Case |
|----------|-------------|------------------|
| Token    | 5000 lines/sec | Initial screening |
| AST      | 1000 lines/sec | Primary detection |
| Hash     | 3000 lines/sec | Partial copy detection |

## References

- Python `tokenize` module: https://docs.python.org/3/library/tokenize.html
- Python `ast` module: https://docs.python.org/3/library/ast.html
- Winnowing algorithm: Schleimer et al. (2003)
