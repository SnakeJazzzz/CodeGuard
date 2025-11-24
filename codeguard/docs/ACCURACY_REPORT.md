# CodeGuard Plagiarism Detection - Accuracy Report

**Generated:** 2025-11-24 14:45:36

## Executive Summary

The CodeGuard plagiarism detection system was evaluated against 12 test cases comprising known plagiarism pairs and legitimate code samples. The system achieved the following metrics using the weighted voting ensemble:

- **Precision:** 100.00%
- **Recall:** 100.00%
- **F1 Score:** 100.00%
- **Accuracy:** 100.00%

## Methodology

### Test Dataset Composition

The validation dataset consists of three categories:

1. **Plagiarized Code Pairs:** Near-identical code with minimal changes (whitespace, comments, variable names)
2. **Legitimate Code Pairs:** Different implementations of different algorithms (e.g., bubble sort vs merge sort)
3. **Obfuscated Code Pairs:** Plagiarized code with deliberate obfuscation (renamed variables, reordered functions)

### Detection Pipeline

Each file pair is analyzed through a three-stage detection pipeline:

1. **Token Detector:** Lexical analysis using Jaccard and Cosine similarity on code tokens
2. **AST Detector:** Structural analysis using normalized Abstract Syntax Trees
3. **Hash Detector:** Fingerprinting using Winnowing algorithm for partial match detection

Results are aggregated using a weighted voting system with the following configuration:

| Detector | Threshold | Weight |
|----------|-----------|--------|
| Token    | 0.70      | 1.0x   |
| AST      | 0.80      | 2.0x   |
| Hash     | 0.60      | 1.5x   |

Plagiarism is flagged when weighted votes reach 50% of the total possible weighted votes (2.25 out of 4.5).

## Results

### Overall Performance Metrics

| Detector    | TP | FP | TN | FN | Precision | Recall | F1 Score | Accuracy |
|-------------|----|----|----|----|-----------| -------|----------|----------|
| TOKEN       | 7  | 0  | 5  | 0  |  100.00% | 100.00% |  100.00% |  100.00% |
| AST         | 7  | 0  | 5  | 0  |  100.00% | 100.00% |  100.00% |  100.00% |
| HASH        | 3  | 0  | 5  | 4  |  100.00% | 42.86% |   60.00% |   66.67% |
| Voting System | 7  | 0  | 5  | 0  |  100.00% | 100.00% |  100.00% |  100.00% |

### Detailed Test Case Results

| File Pair | Expected | Token | AST | Hash | Voting | Result |
|-----------|----------|-------|-----|------|--------|--------|
| binary_search_copied vs binary_search_original | Plagiarism | ✓ | ✓ | ✓ | ✓ | **PASS** |
| factorial_copied vs factorial_original | Plagiarism | ✓ | ✓ | ✓ | ✓ | **PASS** |
| prime_checker_original vs prime_checker_reordered | Plagiarism | ✓ | ✓ | ✓ | ✓ | **PASS** |
| quicksort_original vs quicksort_renamed | Plagiarism | ✓ | ✓ | ✗ | ✓ | **PASS** |
| bubble_sort vs factorial_iterative | Legitimate | ✓ | ✓ | ✓ | ✓ | **PASS** |
| factorial_iterative vs factorial_recursive | Legitimate | ✓ | ✓ | ✓ | ✓ | **PASS** |
| factorial_recursive vs hash_table | Legitimate | ✓ | ✓ | ✓ | ✓ | **PASS** |
| hash_table vs linked_list | Legitimate | ✓ | ✓ | ✓ | ✓ | **PASS** |
| linked_list vs merge_sort | Legitimate | ✓ | ✓ | ✓ | ✓ | **PASS** |
| fibonacci_original vs fibonacci_renamed | Plagiarism | ✓ | ✓ | ✗ | ✓ | **PASS** |
| gcd_calculator_original vs gcd_calculator_restructured | Plagiarism | ✓ | ✓ | ✗ | ✓ | **PASS** |
| linear_search_obfuscated vs linear_search_original | Plagiarism | ✓ | ✓ | ✗ | ✓ | **PASS** |

## Analysis

### Detector Performance Comparison

**Token Detector:**
- Achieved 100.00% precision and 100.00% recall
- Strengths: Fast execution, good baseline for exact copies
- Weaknesses: Easily defeated by variable renaming and structural changes

**AST Detector:**
- Achieved 100.00% precision and 100.00% recall
- Strengths: Immune to variable renaming, detects structural similarity effectively
- Weaknesses: Cannot detect if algorithms are fundamentally different

**Hash Detector:**
- Achieved 100.00% precision and 42.86% recall
- Strengths: Detects partial copying and scattered plagiarism
- Weaknesses: May produce false positives on common code patterns

**Voting System:**
- Achieved 100.00% precision and 100.00% recall
- Strengths: Balances individual detector weaknesses, provides robust decision-making
- The 2.0x weight on AST detector reflects its superior reliability for structural plagiarism

## Conclusion

The CodeGuard plagiarism detection system **successfully meets** all target metrics for academic deployment:

- Precision: 100.00% (Target: ≥85%) ✓ ACHIEVED
- Recall: 100.00% (Target: ≥80%) ✓ ACHIEVED
- F1 Score: 100.00% (Target: ≥82%) ✓ ACHIEVED

The system demonstrates high accuracy in distinguishing between plagiarized and legitimate code submissions. The weighted voting ensemble effectively combines the strengths of lexical, structural, and fingerprint-based detection methods.

## Appendix

### Test Dataset Files

**Plagiarized Pairs:**
- binary_search_copied.py vs binary_search_original.py
- factorial_copied.py vs factorial_original.py
- prime_checker_original.py vs prime_checker_reordered.py
- quicksort_original.py vs quicksort_renamed.py
- fibonacci_original.py vs fibonacci_renamed.py
- gcd_calculator_original.py vs gcd_calculator_restructured.py
- linear_search_obfuscated.py vs linear_search_original.py

**Legitimate Pairs:**
- bubble_sort.py vs factorial_iterative.py
- factorial_iterative.py vs factorial_recursive.py
- factorial_recursive.py vs hash_table.py
- hash_table.py vs linked_list.py
- linked_list.py vs merge_sort.py

### Configuration

```json
{
  "token": {
    "threshold": 0.7,
    "weight": 1.0,
    "confidence_weight": 0.3
  },
  "ast": {
    "threshold": 0.8,
    "weight": 2.0,
    "confidence_weight": 0.4
  },
  "hash": {
    "threshold": 0.6,
    "weight": 1.5,
    "confidence_weight": 0.3
  }
}
```
