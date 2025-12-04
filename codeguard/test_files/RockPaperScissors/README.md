# Rock Paper Scissors Game

## Problem Description

Students were asked to create a terminal-based Rock-Paper-Scissors game. The game must include user input handling, computer opponent with random choice generation, win/loss/tie logic, score tracking across multiple rounds, and replay functionality. Realistic classroom assignment size (~80-200 lines).

## Plagiarism Scenario

- **Total submissions:** 20 files (mix of legitimate and plagiarised)
- Multiple students copied and adapted solutions from each other
- Some plagiarised submissions include variable renaming and code reordering
- **Advantage:** Larger file size allows for more implementation diversity compared to FizzBuzz
- Students had freedom in structuring game flow, UI, and feature implementation
- Tests CodeGuard on realistic, medium-complexity classroom assignments

## Expected CodeGuard Detection

- **Perfect detection:** 100% precision, recall, F1 score, and accuracy
- All plagiarised pairs correctly identified across all three detectors
- Zero false positives - all legitimate pairs correctly classified as original
- Token, AST, and Hash detectors all contribute to accurate classification
- Demonstrates production-ready performance on realistic code (≥50 lines)
- Larger file size (~80-200 lines) provides enough context for reliable detection

## Recommended Detection Mode

**Standard Mode** - All three detectors (Token, AST, Hash) active with standard thresholds. Optimal performance on realistic-sized assignments where students have implementation freedom.

## Directory Structure

```
RockPaperScissors/
├── legitimate/        # Original student submissions
└── plagiarized/       # Plagiarised submissions with modifications
```

## Test Purpose

This dataset tests CodeGuard's ability to:
- Achieve perfect detection on realistic classroom assignments
- Handle medium-complexity code (~80-200 lines) with high accuracy
- Detect plagiarism despite variable renaming and code reordering
- Maintain zero false positives on legitimate diverse implementations
- Demonstrate optimal performance when file size allows implementation diversity
- Validate production-ready capability for typical programming assignments
