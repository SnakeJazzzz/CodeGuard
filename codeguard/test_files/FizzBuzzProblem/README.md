# FizzBuzz Problem

## Problem Description

Students were asked to solve the classic FizzBuzz problem: write a program that prints numbers from 1 to 100, but for multiples of 3 print "Fizz", for multiples of 5 print "Buzz", and for multiples of both print "FizzBuzz". This is a constrained problem with limited solution space, resulting in small files (~20-60 lines).

## Plagiarism Scenario

- **Total submissions:** 20 files (mix of legitimate and plagiarised)
- Multiple students copied or adapted solutions with minor variations
- Some students renamed variables or reformatted code from copied sources
- **Challenge:** Constrained problem means even legitimate solutions naturally share structural similarity
- Small file size (~20-60 lines) limits implementation diversity
- Tests CodeGuard's ability to distinguish intentional plagiarism from coincidental similarity
- Higher false positive risk due to limited solution space

## Expected CodeGuard Detection

- **Recommended Mode:** Simple Problems mode (hash detector disabled, stricter AST threshold of 0.85)
- Higher false positive rate compared to larger problems due to constrained solution space
- Simple mode precision: 50-83% (vs 71% in Standard mode with all detectors)
- Successfully detects blatant copying despite small file size
- Some legitimate solutions may show moderate similarity (expected for constrained problems)
- Demonstrates importance of adaptive detection modes for different problem types

## Recommended Detection Mode

**Simple Mode** - Hash detector disabled, stricter thresholds (Token: 0.70, AST: 0.85). Optimized for constrained problems under 50 lines where limited solution space causes higher natural similarity.

## Directory Structure

```
FizzBuzzProblem/
├── legitimate/        # Original student submissions
└── plagiarized/       # Plagiarised submissions with minor modifications
```

## Test Purpose

This dataset tests CodeGuard's ability to:
- Handle small file sizes (<50 lines) with limited solution space
- Distinguish plagiarism from natural similarity in constrained problems
- Adapt detection thresholds for problem-specific characteristics
- Balance precision and recall on simple algorithmic problems
- Demonstrate when hash-based detection may produce false positives
