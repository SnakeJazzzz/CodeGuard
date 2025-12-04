# CodeGuard Test Files

This directory contains comprehensive test datasets for validating CodeGuard's plagiarism detection capabilities across diverse programming problems.

## Overview

**Total Files:** 80 Python files
**Total Lines:** 8,591 lines of code
**Problems:** 4 diverse programming assignments
**Plagiarism Scenarios:** 3 techniques × 4 problems = 12 plagiarized files

All test problems follow a consistent structure with 20 student submissions each (17 legitimate + 3 plagiarized).

---

## Test Problems

### 1. FizzBuzzProblem
**Directory:** `test_files/FizzBuzzProblem/`
**Type:** Simple algorithmic problem
**Files:** 20 (17 legitimate + 3 plagiarized)
**Total Lines:** 490 lines
**Average File Size:** 25 lines
**Complexity:** Low (basic conditionals and loops)

**Problem Description:**
Print numbers 1-100, replacing multiples of 3 with "Fizz", multiples of 5 with "Buzz", and multiples of both with "FizzBuzz".

**Characteristics:**
- Highly constrained problem (limited solution space)
- Tests system behavior on very short files
- Ideal for evaluating SIMPLE mode effectiveness

**Expected Detection:**
- Direct Copy: ✅ Detected
- Identifier Renaming: ✅ Detected
- Frankenstein: ⚠️ Challenging (0% detection in SIMPLE mode)

**Recommended Mode:** SIMPLE (hash disabled to reduce FPs on small files)

**README:** See [`FizzBuzzProblem/README.md`](FizzBuzzProblem/README.md) for detailed scenario

---

### 2. RockPaperScissors
**Directory:** `test_files/RockPaperScissors/`
**Type:** Game implementation
**Files:** 20 (17 legitimate + 3 plagiarized)
**Total Lines:** 2,534 lines
**Average File Size:** 127 lines
**Complexity:** Medium (input validation, game logic, scoring)

**Problem Description:**
Implement Rock-Paper-Scissors game with user input, computer AI, scoring system, and win/loss tracking.

**Characteristics:**
- Realistic classroom assignment size
- Multiple valid implementation approaches
- Tests STANDARD mode on typical code

**Expected Detection:**
- Direct Copy: ✅ Detected
- Identifier Renaming: ⚠️ 1 miss (87.5% detection)
- Frankenstein: ⚠️ Moderate (50% detection)

**Recommended Mode:** STANDARD (all 3 detectors)

**README:** See [`RockPaperScissors/README.md`](RockPaperScissors/README.md) for detailed scenario

---

### 3. astar_pathfinding
**Directory:** `test_files/astar_pathfinding/`
**Type:** Graph search algorithm
**Files:** 20 (17 legitimate + 3 plagiarized)
**Total Lines:** 2,643 lines
**Average File Size:** 132 lines
**Complexity:** High (priority queues, heuristics, path reconstruction)

**Problem Description:**
Implement A* pathfinding algorithm on a 2D grid with obstacles, supporting different heuristics (Manhattan, Euclidean, Chebyshev).

**Characteristics:**
- Algorithm-heavy code (complex AST structures)
- Diverse implementation approaches (different data structures and heuristics)
- Slowest processing time (95.82 seconds for 20 files)

**Expected Detection:**
- Direct Copy: ✅ Detected
- Identifier Renaming: ✅ Detected (100%)
- Frankenstein: ✅ Good (67% detection, highest for this technique)

**Recommended Mode:** STANDARD (all 3 detectors)

**README:** See [`astar_pathfinding/README.md`](astar_pathfinding/README.md) for detailed scenario

---

### 4. inventory_ice_cream_shop
**Directory:** `test_files/inventory_ice_cream_shop/`
**Type:** Inventory management system
**Files:** 20 (17 legitimate + 3 plagiarized)
**Total Lines:** 2,924 lines
**Average File Size:** 146 lines
**Complexity:** Medium-High (OOP, data structures, multiple operations)

**Problem Description:**
Implement ice cream shop inventory management with flavor tracking, sales recording, price management, and revenue calculation.

**Characteristics:**
- Largest file size (146 lines average)
- Mix of OOP and functional paradigms
- Best detection accuracy (66.67% F1 score)

**Expected Detection:**
- Direct Copy: ✅ Detected
- Identifier Renaming: ✅ Detected
- Frankenstein: ✅ Good (67% detection, tied highest)

**Recommended Mode:** STANDARD (all 3 detectors)

**README:** See [`inventory_ice_cream_shop/README.md`](inventory_ice_cream_shop/README.md) for detailed scenario

---

## Plagiarism Scenarios

Each test problem implements the same three plagiarism techniques:

### Technique 1: Direct Copy + Added Comments (student_3.py)
**Description:** Exact copy of `student_1.py` with only cosmetic changes (added comments/docstrings)

**Files:**
- `FizzBuzzProblem/plagiarised/student_3.py`
- `RockPaperScissors/plagiarised/student_3.py`
- `astar_pathfinding/plagiarised/student_3.py`
- `inventory_ice_cream_shop/plagiarised/student_3.py`

**Detection Rate:** 100% (8/8 detected across all problems)
**Average Confidence:** 0.917 (Very High)

**Why it's detected:** Comments are transparent to all three detectors (Token, AST, Hash)

---

### Technique 2: Identifier Renaming (student_4.py)
**Description:** Copy of `student_1.py` with all identifiers systematically renamed (variables, functions, classes)

**Files:**
- `FizzBuzzProblem/plagiarised/student_4.py`
- `RockPaperScissors/plagiarised/student_4.py`
- `astar_pathfinding/plagiarised/student_4.py`
- `inventory_ice_cream_shop/plagiarised/student_4.py`

**Detection Rate:** 87.5% (7/8 detected, 1 miss in RPS/SIMPLE)
**Average Confidence:** 0.813 (High)

**Why it's detected:** AST detector analyzes structure, not variable names. Token detector still catches keywords/operators.

**Known issue:** 1 anomalous miss in RockPaperScissors SIMPLE mode suggests potential voting system edge case.

---

### Technique 3: Frankenstein/Patchwork (student_5.py)
**Description:** Combination of `student_1.py` (50%) and `student_2.py` (50%) with some identifier renaming

**Files:**
- `FizzBuzzProblem/plagiarised/student_5.py`
- `RockPaperScissors/plagiarised/student_5.py`
- `astar_pathfinding/plagiarised/student_5.py`
- `inventory_ice_cream_shop/plagiarised/student_5.py`

**Detection Rate:** 37.5% (6/16 pairs detected - each file compared to both sources)
**Average Confidence:** 0.686 (Medium)

**Why it's challenging:** Partial similarity (50% from each source) produces scores just below detection thresholds, especially AST (0.78-0.79 vs 0.80 threshold).

**File size impact:**
- Small files (<50 lines): 0% detection (FizzBuzz)
- Medium files (50-150 lines): 50% detection (RPS)
- Large files (>150 lines): 67% detection (astar, inventory)

---

## Directory Structure

```
test_files/
├── README.md (this file)
├── FizzBuzzProblem/
│   ├── README.md
│   ├── legitimate/ (17 files: student_1, student_2, student_6-20)
│   └── plagiarised/ (3 files: student_3, student_4, student_5)
├── RockPaperScissors/
│   ├── README.md
│   ├── legitimate/ (17 files)
│   └── plagiarised/ (3 files)
├── astar_pathfinding/
│   ├── README.md
│   ├── legitimate/ (17 files)
│   └── plagiarised/ (3 files)
└── inventory_ice_cream_shop/
    ├── README.md
    ├── legitimate/ (17 files)
    └── plagiarised/ (3 files)
```

---

## How to Use for Testing

### Running Performance Benchmarks

```bash
# Benchmark all 4 problems
python3 scripts/performance_benchmark.py

# Outputs:
# - docs/performance_data/*.csv (raw data)
# - docs/PERFORMANCE_REPORT.md (analysis)
```

### Running Mode Comparison

```bash
# Compare SIMPLE vs STANDARD modes on all problems
python3 scripts/compare_all_modes.py

# Outputs:
# - analysis_results/mode_comparison_detailed.csv (1,520 comparisons)
# - analysis_results/mode_comparison_metrics.csv (summary)
# - docs/MODE_EFFECTIVENESS_ANALYSIS.md (report)
```

### Testing Individual Problems

```python
from pathlib import Path
from src.voting.config_presets import get_standard_config
from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem

# Load configuration
config = get_standard_config()

# Initialize detectors
token_detector = TokenDetector()
ast_detector = ASTDetector()
hash_detector = HashDetector()

# Initialize voting system
voting_system = VotingSystem(config=config)

# Load test files
problem_dir = Path("test_files/RockPaperScissors")
files = list(problem_dir.glob("**/*.py"))

# Run comparison
for i, file1 in enumerate(files):
    for file2 in files[i+1:]:
        with open(file1) as f1, open(file2) as f2:
            code1, code2 = f1.read(), f2.read()

        # Run detectors
        token_score = token_detector.compare(code1, code2)
        ast_score = ast_detector.compare(code1, code2)
        hash_score = hash_detector.compare(code1, code2)

        # Vote
        result = voting_system.vote(token_score, ast_score, hash_score)

        if result['is_plagiarism']:
            print(f"PLAGIARISM DETECTED: {file1.name} vs {file2.name}")
            print(f"  Confidence: {result['confidence']:.3f}")
```

---

## Expected Results Summary

### Overall Detection Rates (STANDARD Mode)

| Technique | Files | Pairs | Detected | Missed | Success Rate | Avg Confidence |
|-----------|-------|-------|----------|--------|--------------|----------------|
| Direct Copy + Comments | 4 | 4 | 4 | 0 | 100% | 0.917 |
| Identifier Renaming | 4 | 4 | 3 | 1 | 75% | 0.813 |
| Frankenstein | 4 | 8 | 3 | 5 | 37.5% | 0.686 |
| **Total** | **12** | **16** | **10** | **6** | **62.5%** | **0.805** |

### Performance by Problem (STANDARD Mode)

| Problem | F1 Score | Precision | Recall | Processing Time |
|---------|----------|-----------|--------|-----------------|
| FizzBuzzProblem | 17.39% | 12.50% | 33.33% | 0.76s |
| RockPaperScissors | 40.00% | 33.33% | 50.00% | 27.85s |
| astar_pathfinding | 53.33% | 36.36% | 100.00% | 95.82s |
| inventory_ice_cream_shop | 66.67% | 60.00% | 75.00% | 69.29s |

---

## Known Limitations

1. **Frankenstein Plagiarism:** Only 37.5% detection rate due to partial similarity falling just below thresholds
2. **Small Files:** FizzBuzz (25 lines/file) produces more false positives in STANDARD mode
3. **Constrained Problems:** When legitimate solutions must be similar (e.g., FizzBuzz), false positives increase

---

## Recommendations

### For Testing New Detectors
1. Test on FizzBuzzProblem first (smallest, fastest)
2. Validate on RockPaperScissors (typical size)
3. Stress-test on astar_pathfinding (slowest, most complex)
4. Confirm on inventory_ice_cream_shop (largest, best accuracy)

### For Validating Threshold Changes
1. Run `scripts/compare_all_modes.py` with new configuration
2. Compare precision/recall trade-offs
3. Check for regression on known plagiarism pairs
4. Verify false positive rate on legitimate pairs

### For Adding New Problems
Follow the established structure:
- 20 total files (17 legitimate + 3 plagiarized)
- student_1.py and student_2.py as plagiarism sources
- student_3.py: Direct copy + comments
- student_4.py: Identifier renaming
- student_5.py: Frankenstein (50% each source)
- Diverse implementations in student_6-20

---

## References

- **Performance Analysis:** [`docs/PERFORMANCE_REPORT.md`](../docs/PERFORMANCE_REPORT.md)
- **Mode Comparison:** [`docs/MODE_EFFECTIVENESS_ANALYSIS.md`](../docs/MODE_EFFECTIVENESS_ANALYSIS.md)
- **Detector Analysis:** [`docs/DETECTOR_ANALYSIS.md`](../docs/DETECTOR_ANALYSIS.md)
- **Plagiarism Patterns:** [`docs/PLAGIARISM_PATTERN_DETECTION.md`](../docs/PLAGIARISM_PATTERN_DETECTION.md)
- **Final Summary:** [`docs/FINAL_PERFORMANCE_SUMMARY.md`](../docs/FINAL_PERFORMANCE_SUMMARY.md)

---

*Test files created during CodeGuard v1.0.0 development (November-December 2025)*
