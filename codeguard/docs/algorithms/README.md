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

## Voting System

CodeGuard uses a weighted voting system to combine results from three complementary detectors.

### Voting Mechanism

Each detector votes independently based on its similarity score:
- If similarity >= threshold, detector votes with its assigned weight
- Total possible votes: 4.5 (sum of all weights)
- Decision threshold: 2.25 (50% of total possible votes)
- Plagiarism flagged when weighted_votes >= 2.25

### Detector Weights

**AST Detector: 2.0x** (Highest)
- Most reliable detector
- Immune to variable renaming
- Detects structural similarity
- Threshold: 0.80 (strictest)

**Hash Detector: 1.5x** (Medium)
- Detects partial and scattered copying
- Uses Winnowing algorithm
- Good for obfuscated code
- Threshold: 0.60 (moderate)

**Token Detector: 1.0x** (Baseline)
- Fast, simple comparison
- Easily defeated by renaming
- Good for exact copies
- Threshold: 0.70 (moderate)

### Confidence Scoring

Separate from voting, confidence represents overall similarity:

```
confidence = (0.3 × token_sim) + (0.4 × ast_sim) + (0.3 × hash_sim)
```

**Confidence Levels:**
- Very High: >= 0.90
- High: 0.75 - 0.89
- Medium: 0.50 - 0.74
- Low: 0.25 - 0.49
- Very Low: < 0.25

### Algorithm Comparison Table (Updated)

| Detector | Threshold | Weight | Defeats | Defeated By | Speed | Complexity |
|----------|-----------|--------|---------|-------------|-------|------------|
| Token    | 0.70      | 1.0x   | Exact copies | Variable renaming | Very Fast | O(n) |
| AST      | 0.80      | 2.0x   | Renaming, restructuring | Algorithm changes | Fast | O(n) |
| Hash     | 0.60      | 1.5x   | Partial copying | Heavy obfuscation | Fast | O(n) |

### Performance Characteristics

**Voting Overhead:**
- Time complexity: O(1) per file pair
- Space complexity: O(1)
- Adds approximately 1ms per comparison

**Scalability:**
- Linear with number of detectors
- Parallelizable across file pairs
- No performance degradation at scale

## References

1. Schleimer, S., Wilkerson, D.S., and Aiken, A. (2003). "Winnowing: Local Algorithms for Document Fingerprinting". *Proceedings of the 2003 ACM SIGMOD International Conference on Management of Data*, 76-85.
2. Prechelt, L., Malpohl, G., and Philippsen, M. (2002). "Finding Plagiarisms among a Set of Programs with JPlag"
3. Gitchell, D., & Tran, N. (1999). "Sim: A utility for detecting similarity in computer programs". *ACM SIGCSE Bulletin*, 31(1), 266-270.
4. Wise, M. J. (1996). "YAP3: Improved detection of similarities in computer program and other texts". *ACM SIGCSE Bulletin*, 28(1), 130-134.
5. Python AST documentation: https://docs.python.org/3/library/ast.html
6. Python tokenize module: https://docs.python.org/3/library/tokenize.html
