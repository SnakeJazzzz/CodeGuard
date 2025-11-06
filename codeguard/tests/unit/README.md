# Unit Tests

Unit tests for individual components in isolation. Each module in `src/` should have corresponding unit tests.

## Test Files

### Detection Algorithms

#### `test_token_detector.py`
Tests for token-based similarity detection.

**Test Cases**:
- `test_identical_code_returns_high_similarity` - Identical code → ~1.0
- `test_completely_different_code_returns_low_similarity` - Different code → ~0.0
- `test_variable_renaming_reduces_similarity` - Renamed vars → lower score
- `test_whitespace_differences_ignored` - Formatting ignored
- `test_comment_differences_ignored` - Comments ignored
- `test_empty_files_handled_gracefully` - Edge case: empty files
- `test_syntax_error_raises_exception` - Invalid syntax → error
- `test_performance_benchmark` - Processing speed target

#### `test_ast_detector.py`
Tests for AST-based structural comparison.

**Test Cases**:
- `test_identical_structure_high_similarity` - Same structure → ~1.0
- `test_different_structure_low_similarity` - Different logic → ~0.0
- `test_variable_renaming_no_effect` - Renamed vars → still high similarity
- `test_reordered_statements_detected` - Statement order changes
- `test_control_flow_equivalence` - Equivalent if/else → for/while
- `test_nested_structures_compared` - Nested loops/conditionals
- `test_function_definitions_normalized` - Function names normalized
- `test_ast_normalization_correctness` - Normalization preserves structure

#### `test_hash_detector.py`
Tests for winnowing hash-based fingerprinting.

**Test Cases**:
- `test_identical_code_high_similarity` - Identical → ~1.0
- `test_partial_copy_detected` - Partial copy → moderate similarity
- `test_scattered_copying_detected` - Multiple small copies
- `test_kgram_generation` - K-gram creation correctness
- `test_winnowing_window_selection` - Fingerprint selection
- `test_hash_collision_handling` - Duplicate hashes
- `test_configurable_kgram_size` - Custom k-gram parameter
- `test_configurable_window_size` - Custom window parameter

### Voting System

#### `test_voting_system.py`
Tests for weighted voting mechanism.

**Test Cases**:
- `test_unanimous_high_votes_plagiarism` - All detectors agree → plagiarism
- `test_unanimous_low_votes_no_plagiarism` - All detectors disagree → no plagiarism
- `test_ast_only_detection_borderline` - Only AST detects → edge case
- `test_majority_detection_plagiarism` - 2/3 detectors → plagiarism
- `test_weighted_votes_calculation` - Vote weights correct
- `test_decision_threshold_boundary` - Exactly 50% threshold
- `test_custom_configuration` - Custom thresholds/weights
- `test_vote_transparency` - Returns detailed breakdown

#### `test_confidence_calculator.py`
Tests for confidence score calculation.

**Test Cases**:
- `test_confidence_calculation_formula` - Correct weighted average
- `test_confidence_clamped_to_one` - Max value is 1.0
- `test_confidence_level_categorization` - Correct level assignment
- `test_detector_agreement_analysis` - Agreement metrics
- `test_high_variance_flagged` - Large differences between detectors
- `test_custom_confidence_weights` - Custom weight configuration

#### `test_thresholds.py`
Tests for threshold management.

**Test Cases**:
- `test_default_thresholds_loaded` - Defaults correct
- `test_set_valid_threshold` - Valid threshold accepted
- `test_invalid_threshold_rejected` - Out of range rejected
- `test_save_and_load_config` - Persistence works
- `test_threshold_validation` - All thresholds valid
- `test_weight_management` - Get/set weights

### Database Layer

#### `test_database_operations.py`
Tests for database CRUD operations.

**Test Cases**:
- `test_create_analysis_job` - Job creation
- `test_save_comparison_result` - Result storage
- `test_save_batch_results_atomic` - Transaction atomicity
- `test_get_job_results` - Result retrieval
- `test_get_job_summary_statistics` - Summary calculations
- `test_update_job_status` - Status updates
- `test_get_plagiarism_count` - Count calculations
- `test_cleanup_old_jobs` - Cleanup functionality
- `test_foreign_key_constraints` - Referential integrity

#### `test_database_models.py`
Tests for SQLAlchemy models.

**Test Cases**:
- `test_analysis_job_model_creation` - Model instantiation
- `test_comparison_result_model_creation` - Model fields
- `test_model_relationships` - Foreign key relationships
- `test_model_validation` - Field constraints
- `test_timestamp_defaults` - Auto-timestamp fields

### Utility Functions

#### `test_file_utils.py`
Tests for file operations.

**Test Cases**:
- `test_read_python_file_utf8` - UTF-8 reading
- `test_read_python_file_fallback_encoding` - Encoding detection
- `test_write_json_report` - JSON writing
- `test_file_hash_calculation` - SHA-256 hashing
- `test_ensure_directory_creates_dir` - Directory creation
- `test_count_lines_accuracy` - Line counting
- `test_sanitize_filename` - Filename cleaning
- `test_generate_unique_filename` - Unique name generation

#### `test_validation.py`
Tests for input validation.

**Test Cases**:
- `test_validate_python_syntax_valid` - Valid syntax passes
- `test_validate_python_syntax_invalid` - Invalid syntax fails
- `test_validate_file_extension_allowed` - Allowed extensions
- `test_validate_file_extension_rejected` - Rejected extensions
- `test_validate_file_size_within_limit` - Size checks
- `test_validate_job_id_format` - ID format validation
- `test_validate_similarity_score_range` - Score range [0,1]
- `test_validate_upload_batch` - Batch validation

#### `test_logger.py`
Tests for logging utilities.

**Test Cases**:
- `test_logger_setup` - Logger configuration
- `test_console_handler_added` - Console output
- `test_file_handler_added` - File output
- `test_log_levels_respected` - Level filtering
- `test_log_format_correct` - Message formatting
- `test_log_analysis_events` - Specialized logging functions

## Running Unit Tests

```bash
# All unit tests
pytest tests/unit/

# Specific module
pytest tests/unit/test_token_detector.py

# Specific test
pytest tests/unit/test_token_detector.py::test_identical_code_returns_high_similarity

# With coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# Fast fail (stop on first failure)
pytest tests/unit/ -x

# Verbose output
pytest tests/unit/ -v
```

## Test Fixtures

Common fixtures used across unit tests (from `conftest.py`):

```python
@pytest.fixture
def sample_python_code():
    return '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

@pytest.fixture
def sample_python_code_renamed():
    return '''
def compute_factorial(num):
    if num <= 1:
        return 1
    return num * compute_factorial(num - 1)
'''

@pytest.fixture
def temp_test_dir(tmp_path):
    return tmp_path / "test_files"
```

## Naming Convention

```
test_<component>_<functionality>_<scenario>

Examples:
- test_token_detector_identical_code
- test_voting_system_unanimous_agreement
- test_database_save_batch_atomic_transaction
```

## Assertion Patterns

### Similarity Scores
```python
assert 0.95 <= similarity <= 1.0  # Nearly identical
assert 0.0 <= similarity <= 0.05  # Nearly different
```

### Exceptions
```python
with pytest.raises(ValueError, match="Invalid syntax"):
    detector.compare(invalid_code, valid_code)
```

### Approximate Equality
```python
import pytest
assert similarity == pytest.approx(0.85, abs=0.01)
```

## Mock Examples

```python
def test_file_read_error(mocker):
    mocker.patch('builtins.open', side_effect=IOError("File not found"))

    with pytest.raises(IOError):
        read_python_file('nonexistent.py')
```

## Performance Testing

```python
import pytest

@pytest.mark.benchmark
def test_token_detector_speed(benchmark):
    detector = TokenDetector()
    result = benchmark(detector.compare, long_code, long_code)
    # Should process 5000+ lines/second
```

## Coverage Goals

Target: ≥90% for unit tests

Focus on:
- All public methods
- Edge cases and error handling
- Boundary conditions
- Configuration variations
