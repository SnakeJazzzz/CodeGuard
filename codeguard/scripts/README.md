# CodeGuard Scripts

Utility scripts for testing, validation, and dataset creation.

## Available Scripts

### 1. `compare_mode_effectiveness.py`

**Purpose:** Compare Simple Mode vs Standard Mode effectiveness on validation datasets.

**What it does:**
- Runs both Standard and Simple presets on validation datasets
- Measures True Positives, False Positives, True Negatives, False Negatives
- Calculates Precision, Recall, F1 Score, and Accuracy
- Generates detailed comparison report
- Saves raw results as JSON for further analysis

**Usage:**
```bash
python scripts/compare_mode_effectiveness.py
```

**Output:**
- `docs/MODE_COMPARISON_REPORT.md` - Detailed markdown report
- `docs/mode_comparison_results.json` - Raw results in JSON format

**Requirements:**
- Validation datasets must exist in `validation-datasets/`:
  - `plagiarized/` - Known plagiarism pairs
  - `legitimate/` - Different implementations

**Example Output:**
```
================================================================================
MODE EFFECTIVENESS COMPARISON TEST
================================================================================

Testing validation datasets...
  Standard Mode:
    Precision: 100.00%
    Recall:    100.00%
    F1 Score:  100.00%
    Accuracy:  100.00%

  Simple Mode:
    Precision: 100.00%
    Recall:    100.00%
    F1 Score:  100.00%
    Accuracy:  100.00%

Report saved to: docs/MODE_COMPARISON_REPORT.md
================================================================================
```

---

### 2. `create_specialized_datasets.py`

**Purpose:** Generate example FizzBuzz and Rock-Paper-Scissors datasets for specialized testing.

**What it does:**
- Creates FizzBuzz dataset (<50 lines per file)
  - 7 student implementations
  - 3 plagiarism cases (exact copy, renamed, mosaic)
  - Multiple legitimate different approaches
- Creates Rock-Paper-Scissors dataset (100+ lines per file)
  - 5 student implementations
  - 2 plagiarism cases (exact copy, renamed)
  - Multiple legitimate different architectures

**Usage:**
```bash
python scripts/create_specialized_datasets.py
```

**Output:**
- `validation-datasets/fizzbuzz/` - FizzBuzz examples
- `validation-datasets/rock-paper-scissors/` - RPS examples

**Example Output:**
```
================================================================================
SPECIALIZED DATASET CREATOR
================================================================================

Creating FizzBuzz dataset...
  Created: validation-datasets/fizzbuzz
  Files: 7 students
  Plagiarism pairs: 3 (01-02 exact, 01-03 renamed, 01-04 mosaic)

Creating Rock-Paper-Scissors dataset...
  Created: validation-datasets/rock-paper-scissors
  Files: 5 students
  Plagiarism pairs: 2 (01-02 exact, 01-03 renamed)

DONE!
================================================================================
```

---

## Workflow: Testing Mode Effectiveness

### Step 1: Ensure Validation Datasets Exist

**Option A: Use existing datasets**
```bash
ls validation-datasets/plagiarized/
ls validation-datasets/legitimate/
```

**Option B: Create specialized datasets**
```bash
python scripts/create_specialized_datasets.py
```

### Step 2: Run Comparison Test

```bash
python scripts/compare_mode_effectiveness.py
```

### Step 3: Review Results

**Console Output:**
- High-level metrics for both modes
- Comparison summary

**Detailed Report:**
```bash
cat docs/MODE_COMPARISON_REPORT.md
```

**Raw Data:**
```bash
cat docs/mode_comparison_results.json | jq .
```

---

## Understanding the Results

### Key Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| **Precision** | TP / (TP + FP) | Minimize false accusations |
| **Recall** | TP / (TP + FN) | Catch all plagiarism |
| **F1 Score** | Harmonic mean of precision and recall | Balance both |
| **Accuracy** | (TP + TN) / Total | Overall correctness |

### Interpreting Improvements

**Scenario 1: Simple Mode reduces false positives**
- **Meaning:** Simple Mode is less aggressive, more careful
- **Best for:** Short assignments where false accusations are costly
- **Example:** FizzBuzz (many solutions look similar)

**Scenario 2: Standard Mode maintains higher recall**
- **Meaning:** Standard Mode catches more plagiarism cases
- **Best for:** Complex assignments with varied implementations
- **Example:** Rock-Paper-Scissors (diverse architectures)

**Scenario 3: Equal performance**
- **Meaning:** Both modes work equally well on this dataset
- **Action:** Use Standard Mode (default) unless dataset is constrained

---

## Expected Results by Dataset Type

### FizzBuzz (Constrained Problems)

**Expected:**
- Simple Mode: Fewer false positives, slightly lower recall
- Standard Mode: May flag legitimate similar solutions
- **Winner:** Simple Mode (precision more important)

**Why?**
- Limited solution space
- Many valid solutions look structurally similar
- Hash detector ineffective on <50 line files

### Rock-Paper-Scissors (Realistic Problems)

**Expected:**
- Standard Mode: High precision and recall
- Simple Mode: Similar or slightly lower recall
- **Winner:** Standard Mode (balanced performance)

**Why?**
- Sufficient code volume for all detectors
- Varied implementation approaches
- Hash detector effective on longer files

---

## Troubleshooting

### Error: "Plagiarized dataset not found"

**Solution:**
```bash
python scripts/create_specialized_datasets.py
# OR
# Add files to validation-datasets/plagiarized/
```

### Error: "No plagiarism pairs found"

**Problem:** File naming doesn't match expected patterns.

**Expected naming:**
- `*_original.py` and `*_copied.py`
- `*_original.py` and `*_renamed.py`
- `*_original.py` and `*_reordered.py`

**Solution:**
Rename files to follow the convention or modify the pairing logic in `compare_mode_effectiveness.py`.

### Low scores on both modes

**Possible causes:**
1. **Thresholds too strict:** Adjust in `src/core/config_presets.py`
2. **Detectors not working:** Check detector implementations
3. **Datasets incorrectly labeled:** Review ground truth

---

## Adding Custom Datasets

### 1. Create directory structure

```bash
mkdir -p validation-datasets/my-dataset/plagiarized
mkdir -p validation-datasets/my-dataset/legitimate
```

### 2. Add files

**Plagiarized directory:**
- Name pairs: `problem_original.py` and `problem_copied.py`
- Variants: `_renamed.py`, `_reordered.py`, `_mosaic.py`

**Legitimate directory:**
- Different implementations of the same problem
- Use descriptive names: `bubble_sort.py`, `merge_sort.py`

### 3. Update comparison script

Modify `compare_mode_effectiveness.py` to point to your custom dataset:

```python
plagiarized_dir = validation_dir / "my-dataset" / "plagiarized"
legitimate_dir = validation_dir / "my-dataset" / "legitimate"
```

### 4. Run comparison

```bash
python scripts/compare_mode_effectiveness.py
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Mode Effectiveness Test

on: [push, pull_request]

jobs:
  test-modes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run mode comparison
        run: python scripts/compare_mode_effectiveness.py
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: mode-comparison-report
          path: docs/MODE_COMPARISON_REPORT.md
```

---

## Contributing

When adding new scripts:
1. Follow the naming convention: `action_target.py`
2. Include docstrings with usage examples
3. Add entry to this README
4. Test on existing validation datasets
5. Document expected output format

---

## Future Enhancements

Potential improvements:
- [ ] Add command-line arguments for dataset selection
- [ ] Support for custom thresholds without code changes
- [ ] Visualization of results (charts, graphs)
- [ ] Parallel processing for large datasets
- [ ] Export results to CSV for spreadsheet analysis
- [ ] Integration with pytest for automated testing
