# Algorithm Documentation

Detailed documentation of the three plagiarism detection algorithms used in CodeGuard.

## Files

### `token-detection.md`
Token-based lexical similarity detection.

**Topics Covered**:
- Tokenization process using Python's tokenize module
- Token normalization and filtering
- Jaccard similarity calculation
- Cosine similarity calculation
- Performance characteristics (5000 lines/second)
- Strengths and weaknesses
- Example code and results

### `ast-detection.md`
Abstract Syntax Tree structural comparison.

**Topics Covered**:
- AST parsing with Python's ast module
- AST normalization (removing identifiers)
- Structural comparison algorithms
- Tree isomorphism detection
- Handling of control flow structures
- Performance characteristics (1000 lines/second)
- Strengths: immune to renaming
- Weaknesses: computational complexity

### `winnowing-algorithm.md`
Hash-based fingerprinting using the Winnowing algorithm.

**Topics Covered**:
- Original Winnowing paper by Schleimer et al. (2003)
- K-gram generation (default k=5)
- Hash function (MD5 truncated to 8 hex digits)
- Winnowing window selection (default w=4)
- Fingerprint comparison using Jaccard similarity
- Detection of partial and scattered copying
- Parameter tuning guidelines
- Performance characteristics (3000 lines/second)

## Algorithm Comparison

| Feature | Token | AST | Hash |
|---------|-------|-----|------|
| **Speed** | 5000 l/s | 1000 l/s | 3000 l/s |
| **Weight** | 1.0x | 2.0x | 1.5x |
| **Threshold** | 0.70 | 0.80 | 0.60 |
| **Best For** | Direct copies | Structural plagiarism | Partial copying |
| **Defeated By** | Renaming | Algorithmic changes | Heavy obfuscation |

## Mathematical Foundations

### Jaccard Similarity

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

### Cosine Similarity

```
cos(θ) = (A · B) / (||A|| × ||B||)
```

### Tree Edit Distance

```
TED(T1, T2) = minimum cost to transform T1 into T2
```

## Implementation Details

Each algorithm file includes:
- Theoretical background
- Implementation pseudocode
- Python code examples
- Parameter explanations
- Tuning recommendations
- Performance analysis
- References to research papers

## References

1. Schleimer, S., Wilkerson, D.S., and Aiken, A. (2003). "Winnowing: Local Algorithms for Document Fingerprinting"
2. Prechelt, L., Malpohl, G., and Philippsen, M. (2002). "Finding Plagiarisms among a Set of Programs with JPlag"
3. Python AST documentation: https://docs.python.org/3/library/ast.html
4. Python tokenize module: https://docs.python.org/3/library/tokenize.html
