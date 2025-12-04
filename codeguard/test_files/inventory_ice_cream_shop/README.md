# Ice Cream Shop Inventory Management System

## Problem Description

Students were asked to create a terminal-based inventory management system for an ice cream shop. The system must include a menu-driven interface with functionality for tracking inventory, recording sales, displaying revenue, and updating prices. Students could choose any programming paradigm (OOP, functional, procedural).

## Plagiarism Scenario

- **Total submissions:** 20 files (17 legitimate, 3 plagiarised)
- **Student 1:** Created original OOP implementation - shared code with students 3 & 4
- **Student 2:** Created original functional implementation - shared code with student 5
- **Student 3:** Exact copy of student_1 with only added comments (comment-based plagiarism)
- **Student 4:** Copied student_1 and renamed ALL identifiers - variables, functions, and classes (identifier renaming)
- **Student 5:** "Frankenstein" approach - combined code from both student_1 and student_2, renamed ~50% of identifiers (hybrid plagiarism)
- **Students 6-20:** All legitimate and diverse implementations using different paradigms (procedural, OOP, functional, minimal)

## Expected CodeGuard Detection

- **student_3.py vs student_1.py:** PLAGIARISED - high similarity across all detectors (comment additions don't hide plagiarism)
- **student_4.py vs student_1.py:** PLAGIARISED - AST and Hash detectors show high similarity, Token detector lower due to renaming
- **student_5.py vs student_1.py:** PLAGIARISED - partial matches detected despite modifications
- **student_5.py vs student_2.py:** PLAGIARISED - partial matches from second source detected
- **All legitimate pairs:** NOT PLAGIARISED - diverse implementations show low similarity scores
- **Overall performance:** High precision and recall due to realistic file size (~100-300 lines)

## Recommended Detection Mode

**Standard Mode** - All three detectors (Token, AST, Hash) active with standard thresholds. Works best for realistic-sized assignments (≥50 lines) where implementation diversity is expected.

## Directory Structure

```
inventory_ice_cream_shop/
├── legitimate/        # 17 original student submissions
└── plagiarised/       # 3 plagiarised submissions (students 3, 4, 5)
```

## Test Purpose

This dataset tests CodeGuard's ability to:
- Detect comment-based plagiarism (added comments to hide copying)
- Detect identifier renaming (systematic variable/function/class renaming)
- Detect hybrid plagiarism (code combined from multiple sources)
- Distinguish legitimate solutions with different paradigms
- Handle realistic classroom assignment sizes
