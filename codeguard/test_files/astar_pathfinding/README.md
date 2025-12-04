# A* Pathfinding Algorithm - Test Files Summary

## Overview
This directory contains 20 realistic student submissions for the A* Pathfinding Algorithm assignment, including both legitimate and plagiarised submissions.

## Directory Structure

```
/test_files/astar_pathfinding/
├── legitimate/          (17 files)
│   ├── student_1.py    - Original OOP implementation (will be copied by students 3 & 4)
│   ├── student_2.py    - Original functional implementation (will be copied by student 5)
│   ├── student_6.py    - Beginner: Simple procedural approach
│   ├── student_7.py    - Advanced: Diagonal movement with Chebyshev distance
│   ├── student_8.py    - Intermediate: Dictionary-based grid
│   ├── student_9.py    - Intermediate: Interactive with multiple heuristics
│   ├── student_10.py   - Beginner: Minimal implementation
│   ├── student_11.py   - Advanced: Named tuples and type hints
│   ├── student_12.py   - Intermediate: Custom heap implementation
│   ├── student_13.py   - Beginner: Basic lists only
│   ├── student_14.py   - Advanced: Bidirectional A* search
│   ├── student_15.py   - Advanced: Weighted heuristic with path smoothing
│   ├── student_16.py   - Intermediate: Recursive A* approach
│   ├── student_17.py   - Advanced: Multiple heuristics comparison
│   ├── student_18.py   - Intermediate: Custom Position and Grid classes
│   ├── student_19.py   - Beginner: Verbose helper functions
│   └── student_20.py   - Advanced: Jump Point Search optimization
│
└── plagiarised/         (3 files)
    ├── student_3.py    - Exact copy of student_1.py with added comments
    ├── student_4.py    - student_1.py with all identifiers renamed
    └── student_5.py    - Frankenstein mix of student_1.py and student_2.py (50% renamed)

```

## File Characteristics

### Legitimate Files (17 total)

#### Beginner Level (4 students)
- **student_6.py**: Simple procedural, basic variables, minimal error handling
- **student_10.py**: Minimal implementation, verbose code
- **student_13.py**: Uses only lists and basic operations
- **student_19.py**: Helper functions, very explicit logic

#### Intermediate Level (6 students)
- **student_8.py**: Dictionary-based grid representation
- **student_9.py**: Interactive version with multiple heuristic options
- **student_12.py**: Custom MinHeap implementation
- **student_16.py**: Recursive A* approach (experimental)
- **student_18.py**: Custom Position and GridWorld classes

#### Advanced Level (7 students)
- **student_1.py**: Professional OOP with heapq (ORIGINAL - copied by 3 & 4)
- **student_2.py**: Functional approach with PriorityQueue (ORIGINAL - copied by 5)
- **student_7.py**: Diagonal movement, dataclasses, Chebyshev distance
- **student_11.py**: Type hints, named tuples, professional structure
- **student_14.py**: Bidirectional A* search optimization
- **student_15.py**: Weighted heuristic with path smoothing
- **student_17.py**: Multiple heuristics with performance metrics
- **student_20.py**: Jump Point Search (highly optimized A*)

### Plagiarised Files (3 total)

#### student_3.py (Plagiarised from student_1.py)
- **Type**: Direct copy with added comments
- **Changes**: Only added comments throughout to appear unique
- **Detection**: Should show 95%+ similarity to student_1.py

#### student_4.py (Plagiarised from student_1.py)
- **Type**: Renamed identifiers
- **Changes**: 
  - Node → Cell
  - AStarPathfinder → PathFinder
  - grid → map
  - position → loc
  - parent → prev
  - All variable names changed
- **Detection**: Same logic structure, should show structural similarity

#### student_5.py (Plagiarised from student_1.py + student_2.py)
- **Type**: Frankenstein/patchwork plagiarism
- **Changes**:
  - Combines OOP approach from student_1.py
  - Uses euclidean_distance function from student_2.py
  - Uses get_valid_neighbors from student_2.py
  - Mixed class (PathNode) with functional helpers
  - ~50% identifiers renamed
- **Detection**: Should show similarity to both originals

## Key Diversity Features

### Programming Paradigms
- Object-oriented (students 1, 4, 7, 11, 14, 18)
- Functional (student 2)
- Procedural (students 6, 10, 13, 19)
- Hybrid (students 5, 9, 15, 16, 17)

### Data Structures
- heapq (students 1, 3, 4, 5, 7)
- PriorityQueue (students 2, 11)
- Custom MinHeap (student 12)
- Lists only (students 6, 10, 13, 19)
- Sets and dictionaries (student 8)
- Named tuples (student 11)
- Dataclasses (student 7)

### Heuristics Used
- Manhattan distance (students 1, 3, 4, 6, 8, 9, 10, 13, 18, 19)
- Euclidean distance (students 2, 5, 15)
- Chebyshev distance (students 7, 17)
- Octile distance (students 17, 20)
- Multiple/selectable (students 9, 17)

### Grid Sizes
- Small (5x5 to 8x8): students 6, 10, 12, 16, 18, 19
- Medium (10x10 to 12x12): students 1, 2, 3, 4, 5, 8, 9, 11, 13, 14, 17, 20
- Large (15x15): students 7, 9, 15

### Special Features
- Diagonal movement (students 7, 20)
- Bidirectional search (student 14)
- Path smoothing (student 15)
- Jump Point Search (student 20)
- Recursive approach (student 16)
- Performance metrics (student 17)
- Weighted heuristics (student 15)
- Custom heap (student 12)

## Testing Instructions

All files can be run independently:

```bash
# Test legitimate submission
python3 legitimate/student_1.py

# Test plagiarised submission
python3 plagiarised/student_3.py

# Run all tests
for file in legitimate/*.py plagiarised/*.py; do
    echo "Testing $file..."
    python3 "$file"
done
```

## Plagiarism Detection Expected Results

When running plagiarism detection tools on these files:

1. **student_3.py vs student_1.py**: Should show ~95-100% code similarity
2. **student_4.py vs student_1.py**: Should show high structural similarity despite renamed identifiers
3. **student_5.py vs student_1.py + student_2.py**: Should show moderate similarity to both sources
4. **All other pairs**: Should show low similarity (normal variance)

## Assignment Compliance

All implementations include:
- ✅ Open list (nodes to explore)
- ✅ Closed list (explored nodes)
- ✅ g score (cost from start)
- ✅ h score (heuristic estimate)
- ✅ f score (f = g + h)
- ✅ Path reconstruction
- ✅ Grid representation with obstacles
- ✅ Heuristic function
- ✅ Visual output (S, G, #, ., *)

All solutions are functionally correct and find optimal or near-optimal paths.

---
Generated for CodeGuard plagiarism detection testing
