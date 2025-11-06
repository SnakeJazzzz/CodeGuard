# Validation Datasets

Test datasets for validating detection algorithm accuracy.

## Purpose

These datasets provide known plagiarism cases and legitimate code pairs for:
- Algorithm validation and tuning
- Accuracy measurement (precision, recall, F1 score)
- Performance benchmarking
- Regression testing

## Directory Structure

```
validation-datasets/
├── plagiarized/     # Known plagiarism pairs
├── legitimate/      # Legitimate similar code
└── obfuscated/      # Obfuscation attempts
```

## Subdirectories

### `plagiarized/`
Known plagiarized code pairs (true positives).

**Contains**:
- Identical copies
- Variable renaming
- Structural modifications
- Whitespace/formatting changes
- Comment additions/removals

**Expected Result**: System should detect plagiarism (is_plagiarized=True)

**File Naming**:
- `original_*.py` - Original submission
- `copied_*.py` - Plagiarized version

### `legitimate/`
Legitimate code that may appear similar (true negatives).

**Contains**:
- Different solutions to same problem
- Common patterns (e.g., factorial implementations)
- Standard algorithms (sorting, searching)
- Similar structure but different logic

**Expected Result**: System should NOT detect plagiarism (is_plagiarized=False)

**File Naming**:
- Descriptive names indicating the problem/algorithm
- `factorial_v1.py`, `factorial_v2.py`, etc.

### `obfuscated/`
Intentionally obfuscated plagiarism attempts.

**Contains**:
- Heavy variable renaming
- Code restructuring
- Added dead code
- Statement reordering
- Control flow changes (if→while, etc.)

**Purpose**: Test system resilience against sophisticated obfuscation

**Expected Result**: May or may not detect (depends on obfuscation level)

## Dataset Composition

Recommended dataset sizes for validation:

| Category | Pairs | Purpose |
|----------|-------|---------|
| Plagiarized | 100 | Measure recall (true positive rate) |
| Legitimate | 100 | Measure precision (avoid false positives) |
| Obfuscated | 50 | Test robustness |

## Generating Datasets

Use the provided script to generate test data:

```bash
python scripts/generate_test_data.py
```

Or manually create files based on real student submissions (anonymized).

## Example Dataset Structure

```
plagiarized/
├── factorial_original.py      # Original
├── factorial_copied.py        # Exact copy
├── fibonacci_original.py      # Original
├── fibonacci_renamed.py       # Variables renamed
├── quicksort_original.py      # Original
└── quicksort_reformatted.py   # Reformatted only

legitimate/
├── factorial_recursive.py     # Recursive implementation
├── factorial_iterative.py     # Iterative implementation
├── bubble_sort.py             # Bubble sort
├── selection_sort.py          # Selection sort
├── linear_search.py           # Linear search
└── binary_search.py           # Binary search

obfuscated/
├── factorial_original.py      # Original
├── factorial_obfuscated.py    # Heavily obfuscated
├── fibonacci_original.py      # Original
└── fibonacci_obfuscated.py    # Heavily obfuscated
```

## Validation Metrics

### Running Validation

```python
from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem

def validate_dataset(pairs, expected_plagiarized):
    """
    Validate detection accuracy on dataset.

    Args:
        pairs: List of (file1, file2) tuples
        expected_plagiarized: List of booleans

    Returns:
        Dict with precision, recall, F1 scores
    """
    voter = VotingSystem()
    detectors = {
        'token': TokenDetector(),
        'ast': ASTDetector(),
        'hash': HashDetector()
    }

    results = []
    for (file1, file2), expected in zip(pairs, expected_plagiarized):
        # Read files
        with open(file1) as f1, open(file2) as f2:
            code1, code2 = f1.read(), f2.read()

        # Run detectors
        scores = {
            name: detector.compare(code1, code2)
            for name, detector in detectors.items()
        }

        # Vote
        result = voter.vote(
            scores['token'],
            scores['ast'],
            scores['hash']
        )

        results.append({
            'predicted': result['is_plagiarized'],
            'expected': expected,
            'confidence': result['confidence_score']
        })

    # Calculate metrics
    tp = sum(1 for r in results if r['predicted'] and r['expected'])
    fp = sum(1 for r in results if r['predicted'] and not r['expected'])
    tn = sum(1 for r in results if not r['predicted'] and not r['expected'])
    fn = sum(1 for r in results if not r['predicted'] and r['expected'])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': tp,
        'false_positives': fp,
        'true_negatives': tn,
        'false_negatives': fn
    }
```

### Success Criteria

Target metrics:
- **Precision**: ≥85% (minimize false positives)
- **Recall**: ≥80% (catch most plagiarism)
- **F1 Score**: ≥82% (balanced performance)
- **False Positive Rate**: ≤10%

## Dataset Maintenance

### Adding New Cases

1. Obtain real-world examples (with permission)
2. Anonymize student information
3. Document the plagiarism technique
4. Add to appropriate directory
5. Update ground truth labels
6. Re-run validation

### Quality Guidelines

- **Realistic**: Based on actual student submissions
- **Diverse**: Cover various plagiarism techniques
- **Balanced**: Equal positive and negative cases
- **Documented**: Clear labels and expected outcomes
- **Clean**: Valid Python syntax
- **Anonymized**: No identifying information

## Ground Truth Labels

Create `ground_truth.json` documenting expected results:

```json
{
  "plagiarized": [
    {
      "file1": "factorial_original.py",
      "file2": "factorial_copied.py",
      "type": "exact_copy",
      "expected_confidence": ">0.95"
    },
    {
      "file1": "fibonacci_original.py",
      "file2": "fibonacci_renamed.py",
      "type": "variable_renaming",
      "expected_confidence": ">0.85"
    }
  ],
  "legitimate": [
    {
      "file1": "factorial_recursive.py",
      "file2": "factorial_iterative.py",
      "type": "different_approaches",
      "expected_confidence": "<0.50"
    }
  ]
}
```

## Continuous Validation

Run validation tests regularly:

```bash
# Include in test suite
pytest tests/integration/test_validation_datasets.py

# Or run standalone
python scripts/validate_accuracy.py
```

## Contributing Datasets

When contributing new validation cases:
1. Ensure cases are anonymized
2. Provide clear expected outcomes
3. Document plagiarism technique
4. Add to appropriate directory
5. Update ground truth file
6. Run validation to verify
