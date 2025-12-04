# CodeGuard Performance Benchmark Report

**Generated:** 2025-12-03 20:05:47

**Benchmark Configuration:** 3 runs per problem with warmup

## Executive Summary

This report presents performance benchmarking results for CodeGuard's plagiarism detection system across 4 test problems comprising 80 files (8,591 total lines of code, 760 pairwise comparisons).

**Key Findings:**

- **Total processing time:** 193.72 seconds for all 4 problems
- **Fastest problem:** FizzBuzzProblem at 1.5488s per 1000 LOC
- **Slowest problem:** astar_pathfinding at 36.2545s per 1000 LOC
- **Average throughput:** 201.6 lines/second
- **Peak memory usage:** 20.11 MB

## Performance Metrics

| Problem | Files | Lines | Comparisons | Total Time (s) | Time/Comp (s) | Time/1000 LOC (s) | Lines/Sec | Memory (MB) | Preset |
|---------|-------|-------|-------------|----------------|---------------|-------------------|-----------|-------------|--------|
| FizzBuzzProblem | 20 | 490 | 190 | 0.76 | 0.0040 | 1.5488 | 645.7 | 0.72 | simple |
| RockPaperScissors | 20 | 2,534 | 190 | 27.85 | 0.1466 | 10.9888 | 91.0 | 5.89 | standard |
| astar_pathfinding | 20 | 2,643 | 190 | 95.82 | 0.5043 | 36.2545 | 27.6 | 20.11 | standard |
| inventory_ice_cream_shop | 20 | 2,924 | 190 | 69.29 | 0.3647 | 23.6981 | 42.2 | 15.91 | standard |

## Detailed Analysis

### Processing Speed by Problem Size

The benchmark results show clear trends in processing speed relative to code volume:

**FizzBuzzProblem** (490 lines, avg 24 lines/file):
- Total time: 0.76s (range: 0.76s - 0.76s)
- Normalized: 1.5488s per 1000 LOC
- Throughput: 645.7 lines/second
- Preset used: simple

**RockPaperScissors** (2534 lines, avg 127 lines/file):
- Total time: 27.85s (range: 27.36s - 28.20s)
- Normalized: 10.9888s per 1000 LOC
- Throughput: 91.0 lines/second
- Preset used: standard

**astar_pathfinding** (2643 lines, avg 132 lines/file):
- Total time: 95.82s (range: 95.72s - 95.98s)
- Normalized: 36.2545s per 1000 LOC
- Throughput: 27.6 lines/second
- Preset used: standard

**inventory_ice_cream_shop** (2924 lines, avg 146 lines/file):
- Total time: 69.29s (range: 69.23s - 69.38s)
- Normalized: 23.6981s per 1000 LOC
- Throughput: 42.2 lines/second
- Preset used: standard

### Fastest vs Slowest Problem

**Fastest:** FizzBuzzProblem processed at 645.7 lines/sec

**Slowest:** astar_pathfinding processed at 27.6 lines/sec

**Performance ratio:** 23.41x (slowest vs fastest)

### Bottleneck Analysis

Based on the CodeGuard architecture (Token, AST, Hash detectors with VotingSystem):

**Expected detector performance (from CLAUDE.md):**
- Token Detector: Target 5000 lines/second
- AST Detector: Target 1000 lines/second (most expensive)
- Hash Detector: Target 3000 lines/second

**Observed average throughput:** 201.6 lines/second

**Analysis:**
- The observed throughput suggests the **AST detector is the primary bottleneck**, as expected from the architecture documentation.
- AST parsing and structural comparison are computationally expensive operations.
- The Token and Hash detectors are likely running significantly faster.
- Voting system overhead is minimal (simple weighted aggregation).

### Memory Usage

**Peak memory usage:** 20.11 MB (astar_pathfinding)
**Minimum memory usage:** 0.72 MB (FizzBuzzProblem)

Memory usage is well within acceptable limits for a classroom tool. The system handles all test problems comfortably with less than 100 MB peak memory.

### Line Count Impact on Processing Speed

The relationship between code volume and processing time:

| Problem | Total Lines | Time/1000 LOC (s) | Efficiency Ratio |
|---------|-------------|-------------------|------------------|
| FizzBuzzProblem | 490 | 1.5488 | 1.00x |
| RockPaperScissors | 2,534 | 10.9888 | 0.14x |
| astar_pathfinding | 2,643 | 36.2545 | 0.04x |
| inventory_ice_cream_shop | 2,924 | 23.6981 | 0.07x |

**Observations:**
- Processing time scales roughly linearly with code volume (as expected for O(n²) pairwise comparisons)
- Smaller files may benefit from better cache locality
- Larger files may incur additional AST parsing overhead

## Optimization Recommendations

### High Priority

1. **Optimize AST Detector:**
   - Cache parsed AST trees to avoid re-parsing the same file
   - Consider parallel AST comparison for independent file pairs
   - Profile AST normalization and tree traversal for optimization opportunities

2. **Implement Result Caching:**
   - Cache pairwise comparison results to avoid redundant computation
   - Use file content hash as cache key
   - Potential speedup: 2-10x for repeated analyses

3. **Parallelize Detector Execution:**
   - Run Token, AST, and Hash detectors in parallel using threading or multiprocessing
   - Current implementation runs detectors sequentially
   - Estimated speedup: 1.5-2x (limited by AST detector as bottleneck)

### Medium Priority

4. **Batch Processing Optimization:**
   - Process file pairs in batches with multiprocessing pool
   - Distribute work across CPU cores
   - Potential speedup: 2-4x on multi-core systems

5. **Early Termination Strategy:**
   - If Token detector shows very low similarity (<0.3), skip expensive AST analysis
   - Implement adaptive thresholding based on initial results
   - Reduces unnecessary computation on clearly non-plagiarized pairs

### Low Priority

6. **Memory Optimization:**
   - Current memory usage is acceptable (<100 MB peak)
   - Consider streaming large files instead of loading all into memory
   - Implement garbage collection hints after batch processing

## Overall Assessment: Classroom Suitability

**Current Performance:**
- 20-file assignment: ~48.4 seconds average
- 50-file assignment: ~302.7 seconds (estimated)
- 100-file assignment: ~20.2 minutes (estimated)

**Verdict:** ✅ **ACCEPTABLE for classroom use**

**Justification:**
- Processing times are reasonable for typical classroom assignments (20-50 files)
- Sub-minute analysis for small assignments (FizzBuzz: ~0.8s)
- 1-2 minute analysis for medium assignments (RPS, A*: ~64.3s average)
- Memory footprint is minimal (<100 MB)
- System is stable and handles all test cases successfully

**Recommendations for Production Deployment:**
- Implement AST caching for 2-3x speedup on repeated analyses
- Add progress indicators for assignments with >30 files
- Consider async processing with job queue for large batches (100+ files)
- Set timeout limits (e.g., 10 minutes) for very large assignments

## Appendix: Raw Data

Detailed CSV files with individual run results are available in:
- `docs/performance_data/`

**Files generated:**
- `FizzBuzzProblem_benchmark.csv`
- `RockPaperScissors_benchmark.csv`
- `astar_pathfinding_benchmark.csv`
- `inventory_ice_cream_shop_benchmark.csv`

---

*This report was automatically generated by scripts/performance_benchmark.py*
