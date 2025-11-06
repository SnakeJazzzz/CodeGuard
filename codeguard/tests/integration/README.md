# Integration Tests

Integration tests verify that multiple components work together correctly to achieve complete workflows.

## Test Files

### `test_analysis_workflow.py`
Tests the complete analysis workflow from file upload to results.

**Test Scenarios**:

```python
def test_complete_analysis_workflow():
    """
    Test full workflow:
    1. Upload multiple Python files
    2. Process through all three detectors
    3. Aggregate via voting system
    4. Store results in database
    5. Retrieve and verify results
    """

def test_batch_processing_multiple_pairs():
    """
    Test batch processing with N files:
    - Should generate N*(N-1)/2 comparisons
    - All pairs processed successfully
    - Results stored correctly
    """

def test_error_recovery_partial_batch():
    """
    Test error handling:
    - One file has syntax error
    - Other files still processed
    - Error logged but workflow continues
    """

def test_concurrent_analysis_jobs():
    """
    Test multiple simultaneous jobs:
    - Jobs don't interfere with each other
    - Results isolated per job
    - Database transactions handled correctly
    """

def test_end_to_end_plagiarism_detection():
    """
    Test with known plagiarized pair:
    - Upload original and copied files
    - Verify plagiarism detected
    - Confidence score appropriate
    """

def test_end_to_end_legitimate_similarity():
    """
    Test with legitimate similar code:
    - Upload different solutions to same problem
    - Verify no false positive
    - Similarity scores reasonable
    """
```

### `test_api_endpoints.py`
Tests Flask web application endpoints and HTTP interactions.

**Test Scenarios**:

```python
def test_home_page_loads(flask_client):
    """Test GET / returns 200 with upload form."""

def test_upload_valid_files(flask_client):
    """
    Test POST /upload with valid Python files:
    - Returns 302 redirect or 200 success
    - Job ID generated
    - Files saved to upload directory
    """

def test_upload_invalid_extension(flask_client):
    """
    Test POST /upload with .txt file:
    - Returns 400 Bad Request
    - Error message indicates invalid extension
    """

def test_upload_too_few_files(flask_client):
    """
    Test POST /upload with single file:
    - Returns 400 Bad Request
    - Error message indicates minimum 2 files
    """

def test_upload_file_too_large(flask_client):
    """
    Test POST /upload with 20MB file:
    - Returns 413 Request Entity Too Large
    """

def test_upload_syntax_error(flask_client):
    """
    Test POST /upload with invalid Python:
    - Returns 400 Bad Request
    - Error message indicates syntax error
    """

def test_results_page_valid_job(flask_client):
    """
    Test GET /results/<job_id> with valid job:
    - Returns 200 OK
    - Displays comparison results
    - Shows similarity scores
    """

def test_results_page_invalid_job(flask_client):
    """
    Test GET /results/<invalid_job_id>:
    - Returns 404 Not Found
    """

def test_download_report_json(flask_client):
    """
    Test GET /download/<job_id>:
    - Returns JSON file
    - Content-Type: application/json
    - Contains all comparison results
    """

def test_health_check_endpoint(flask_client):
    """
    Test GET /health:
    - Returns 200 OK
    - Response indicates system healthy
    """
```

### `test_batch_processing.py`
Tests batch file processing and pairwise comparison generation.

**Test Scenarios**:

```python
def test_pairwise_combination_generation():
    """
    Test with N=5 files:
    - Should generate 10 pairs
    - No duplicate pairs
    - No self-comparisons
    """

def test_batch_processing_order_independence():
    """
    Test that file order doesn't affect results:
    - Process [A, B, C]
    - Process [C, B, A]
    - Results should be identical
    """

def test_batch_processing_performance():
    """
    Test with 50 files (1225 pairs):
    - Completes within 2 minutes
    - Memory usage reasonable
    - Progress tracking works
    """

def test_large_batch_handling():
    """
    Test with 100 files (4950 pairs):
    - System handles load
    - Results accurate
    - Database can store all results
    """
```

### `test_database_integration.py`
Tests database integration with application components.

**Test Scenarios**:

```python
def test_job_lifecycle():
    """
    Test complete job lifecycle:
    1. Create job (status='pending')
    2. Update to 'processing'
    3. Save results
    4. Update to 'completed'
    5. Query results
    """

def test_transaction_rollback_on_error():
    """
    Test transaction handling:
    - Start transaction
    - Insert multiple results
    - Simulate error
    - Verify rollback (no partial data)
    """

def test_concurrent_database_writes():
    """
    Test multiple simultaneous database operations:
    - Multiple jobs writing concurrently
    - No race conditions
    - Data consistency maintained
    """

def test_query_performance():
    """
    Test query performance with large dataset:
    - 1000 jobs with 100 results each
    - Queries complete in reasonable time
    - Indexes effective
    """
```

### `test_detector_integration.py`
Tests integration between multiple detection algorithms.

**Test Scenarios**:

```python
def test_all_detectors_agree_high_similarity():
    """
    Test with identical code:
    - Token detector: ~1.0
    - AST detector: ~1.0
    - Hash detector: ~1.0
    - Voting: plagiarism detected
    """

def test_ast_alone_detects_structural_plagiarism():
    """
    Test with renamed variables:
    - Token detector: low (~0.3)
    - AST detector: high (~0.9)
    - Hash detector: moderate (~0.6)
    - Voting: plagiarism detected (AST weight decisive)
    """

def test_hash_detects_partial_copying():
    """
    Test with scattered copying:
    - Token detector: low
    - AST detector: moderate
    - Hash detector: high
    - Voting: depends on configuration
    """

def test_no_detector_finds_similarity():
    """
    Test with completely different code:
    - All detectors: ~0.0
    - Voting: no plagiarism
    """
```

### `test_configuration_integration.py`
Tests configuration management across components.

**Test Scenarios**:

```python
def test_threshold_changes_affect_voting():
    """
    Test configuration propagation:
    - Change AST threshold
    - Verify voting system uses new threshold
    - Results change appropriately
    """

def test_custom_configuration_file():
    """
    Test loading custom config:
    - Load thresholds.json
    - All components use custom values
    - Configuration persists
    """

def test_runtime_configuration_update():
    """
    Test updating config during runtime:
    - Change threshold via API
    - New analyses use updated config
    - Old results unchanged
    """
```

## Running Integration Tests

```bash
# All integration tests
pytest tests/integration/

# Specific test file
pytest tests/integration/test_analysis_workflow.py

# Specific scenario
pytest tests/integration/test_api_endpoints.py::test_upload_valid_files

# With verbose output
pytest tests/integration/ -v

# With coverage
pytest tests/integration/ --cov=src
```

## Test Setup

Integration tests use more complex fixtures:

```python
# conftest.py for integration tests

@pytest.fixture
def flask_client():
    """Provide Flask test client."""
    from src.web.app import create_app
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_database(tmp_path):
    """Provide temporary test database."""
    db_path = tmp_path / "test.db"
    # Initialize schema
    # Yield connection
    # Cleanup after test

@pytest.fixture
def sample_file_batch(tmp_path):
    """Provide multiple test Python files."""
    files = []
    for i in range(5):
        file_path = tmp_path / f"file_{i}.py"
        file_path.write_text(f"def func_{i}(): pass")
        files.append(file_path)
    return files

@pytest.fixture
def plagiarized_pair(tmp_path):
    """Provide known plagiarized pair."""
    original = tmp_path / "original.py"
    copied = tmp_path / "copied.py"
    # Create files with known plagiarism
    return original, copied
```

## Test Data

Integration tests use realistic test data from:
- `tests/fixtures/sample_code/` - Sample Python files
- `validation-datasets/` - Validation dataset pairs

## Performance Benchmarks

```python
import time

def test_analysis_performance_benchmark():
    """
    Performance requirements:
    - 50 files in <2 minutes
    - Memory usage <2GB
    """
    start_time = time.time()

    # Run analysis on 50 files
    result = run_batch_analysis(files)

    duration = time.time() - start_time
    assert duration < 120, f"Analysis took {duration}s (max: 120s)"
```

## Error Handling Tests

```python
def test_network_timeout_handling():
    """Test graceful handling of timeouts."""

def test_disk_full_error_recovery():
    """Test behavior when disk space exhausted."""

def test_memory_limit_handling():
    """Test behavior under memory pressure."""
```

## End-to-End Scenarios

```python
def test_instructor_workflow():
    """
    Simulate typical instructor usage:
    1. Start application
    2. Upload student submissions
    3. Wait for analysis
    4. Review results
    5. Download report
    6. Close application
    """
```

## Coverage Goals

Target: ≥80% for integration tests

Focus on:
- Component interactions
- Data flow through system
- Error propagation and recovery
- Configuration management
- Performance under realistic load

## Continuous Integration

Integration tests run in CI/CD:

```yaml
# .github/workflows/test.yml
- name: Run Integration Tests
  run: |
    pytest tests/integration/ \
      --cov=src \
      --cov-report=xml \
      --maxfail=3 \
      --timeout=300
```
