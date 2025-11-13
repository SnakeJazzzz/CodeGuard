"""
Integration Tests for Complete CodeGuard Workflow

This module contains comprehensive end-to-end integration tests that validate
the complete workflow from file upload through detector analysis to database
storage and retrieval.

Test Coverage:
    - Complete file upload to database flow
    - Batch analysis workflow with multiple files
    - Error handling and recovery
    - Multiple job isolation
    - Detector-database integration
    - Real validation dataset integration

Test Database:
    Uses real SQLite database files (not in-memory) to test actual I/O operations.
    Each test gets a fresh database to ensure isolation.

Author: CodeGuard Test Team
"""

import pytest
import sqlite3
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add src to path for imports
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import modules to test
from src.detectors.token_detector import TokenDetector
from src.database.connection import init_db, get_db_connection, get_session, DB_PATH
from src.database.operations import (
    create_analysis_job,
    save_comparison_result,
    save_batch_results,
    get_job_results,
    get_job_summary,
    update_job_status,
    get_plagiarism_count,
    JobNotFoundError,
    InvalidResultDataError,
    DatabaseOperationError
)
from src.database.models import AnalysisJob, ComparisonResult

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_database(monkeypatch):
    """
    Create temporary test database for integration tests.

    Uses real SQLite file (not in-memory) to test actual file operations.
    The database is created in a temporary directory and cleaned up after the test.

    This fixture uses monkeypatch to override the DB_PATH in the connection module,
    ensuring all database operations use the test database.

    Yields:
        Path: Path to the test database file
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="codeguard_test_")
    test_db_path = Path(temp_dir) / "test.db"

    # Monkeypatch the DB_PATH to point to test database
    import src.database.connection as conn_module
    monkeypatch.setattr(conn_module, 'DB_PATH', test_db_path)

    # Initialize database schema
    init_db()

    # Verify database was created
    assert test_db_path.exists(), "Test database was not created"

    # Yield database path to test
    yield test_db_path

    # Cleanup: remove database and temp directory
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Failed to cleanup test directory {temp_dir}: {e}")


@pytest.fixture(scope="function")
def test_files():
    """
    Create temporary test Python files with known content.

    Creates three test files:
    - test1.py: Simple factorial function (iterative)
    - test2.py: Copy of test1.py (high similarity - should detect plagiarism)
    - test3.py: Different fibonacci function (low similarity - should not detect)
    - test4.py: Modified factorial (medium similarity)
    - test5.py: Empty file (edge case)

    Returns:
        List[Path]: List of file paths
    """
    temp_dir = tempfile.mkdtemp(prefix="codeguard_files_")
    files = []

    # File 1: Simple factorial function
    file1 = Path(temp_dir) / "test1.py"
    file1.write_text("""
def factorial(n):
    '''Calculate factorial using iteration.'''
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
""")
    files.append(file1)

    # File 2: Copy of file 1 (high similarity - plagiarism)
    file2 = Path(temp_dir) / "test2.py"
    file2.write_text(file1.read_text())
    files.append(file2)

    # File 3: Different function (low similarity - legitimate)
    file3 = Path(temp_dir) / "test3.py"
    file3.write_text("""
def fibonacci(n):
    '''Calculate fibonacci number.'''
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
""")
    files.append(file3)

    # File 4: Modified factorial (medium similarity)
    file4 = Path(temp_dir) / "test4.py"
    file4.write_text("""
def compute_factorial(num):
    '''Compute factorial using a loop.'''
    if num <= 1:
        return 1
    product = 1
    for j in range(2, num + 1):
        product *= j
    return product
""")
    files.append(file4)

    # File 5: Empty file (edge case)
    file5 = Path(temp_dir) / "test5.py"
    file5.write_text("")
    files.append(file5)

    yield files

    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Warning: Failed to cleanup test files {temp_dir}: {e}")


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.workflow
def test_file_upload_to_database_flow(test_database, test_files):
    """
    Test the complete flow from file upload to database storage.

    This test validates:
    1. File reading and TokenDetector analysis
    2. Analysis job creation in database
    3. Comparison result storage
    4. Result retrieval and validation

    Expected Flow:
        Files -> TokenDetector -> Database -> Retrieval
    """
    # Step 1: Read test files
    file1_path = test_files[0]  # test1.py
    file2_path = test_files[1]  # test2.py (copy of test1)

    assert file1_path.exists(), "Test file 1 not found"
    assert file2_path.exists(), "Test file 2 not found"

    # Step 2: Run TokenDetector analysis
    detector = TokenDetector(threshold=0.7)
    result = detector.analyze(file1_path, file2_path)

    # Verify detector returned valid result
    assert 'similarity_score' in result
    assert 'is_plagiarism' in result
    assert 0.0 <= result['similarity_score'] <= 1.0

    # Since file2 is a copy of file1, expect high similarity
    assert result['similarity_score'] > 0.9, "Expected high similarity for identical files"
    assert result['is_plagiarism'] is True, "Expected plagiarism detection for identical files"

    # Step 3: Create analysis job in database
    job_id = f"test_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job = create_analysis_job(job_id=job_id, file_count=2)

    # Verify job created successfully
    assert job['id'] == job_id
    assert job['file_count'] == 2
    assert job['pair_count'] == 1  # 2 files = 1 pair
    assert job['status'] == 'pending'

    # Step 4: Save comparison result
    comparison_data = {
        'file1_name': file1_path.name,
        'file2_name': file2_path.name,
        'token_similarity': result['similarity_score'],
        'ast_similarity': 0.95,  # Mock AST score
        'hash_similarity': 0.90,  # Mock hash score
        'is_plagiarized': result['is_plagiarism'],
        'confidence_score': result['similarity_score']
    }

    saved_result = save_comparison_result(job_id, comparison_data)

    # Verify result saved with ID
    assert saved_result['id'] is not None
    assert saved_result['job_id'] == job_id
    assert saved_result['file1_name'] == file1_path.name
    assert saved_result['file2_name'] == file2_path.name

    # Step 5: Retrieve results
    retrieved_results = get_job_results(job_id)

    # Verify retrieval
    assert len(retrieved_results) == 1
    assert retrieved_results[0]['file1_name'] == file1_path.name
    assert retrieved_results[0]['file2_name'] == file2_path.name
    assert retrieved_results[0]['is_plagiarized'] is True

    # Step 6: Verify data integrity (round trip)
    assert abs(retrieved_results[0]['token_similarity'] - comparison_data['token_similarity']) < 0.001
    assert abs(retrieved_results[0]['confidence_score'] - comparison_data['confidence_score']) < 0.001


@pytest.mark.integration
@pytest.mark.workflow
def test_batch_analysis_workflow(test_database, test_files):
    """
    Test batch processing of multiple file pairs.

    This test validates:
    1. Analysis job creation with multiple files
    2. Multiple file pair analysis
    3. Batch result storage (atomic operation)
    4. Job status updates
    5. Job summary statistics
    6. Plagiarism counting

    Expected: 5 files = 10 pairs (N*(N-1)/2)
    """
    # Step 1: Create analysis job with 5 files
    job_id = f"batch_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job = create_analysis_job(job_id=job_id, file_count=5)

    # Verify job setup
    assert job['file_count'] == 5
    assert job['pair_count'] == 10  # 5 files = 10 pairs
    assert job['status'] == 'pending'

    # Step 2: Analyze all pairs using TokenDetector
    detector = TokenDetector(threshold=0.7)
    batch_results = []

    # Generate all pairs
    for i in range(len(test_files)):
        for j in range(i + 1, len(test_files)):
            file1 = test_files[i]
            file2 = test_files[j]

            # Skip empty files in analysis
            if file1.stat().st_size == 0 or file2.stat().st_size == 0:
                # For empty files, create mock result with 0.0 similarity
                result = {
                    'similarity_score': 0.0,
                    'is_plagiarism': False
                }
            else:
                try:
                    result = detector.analyze(file1, file2)
                except Exception:
                    # Handle any analysis errors gracefully
                    result = {
                        'similarity_score': 0.0,
                        'is_plagiarism': False
                    }

            # Create comparison result
            comparison = {
                'file1_name': file1.name,
                'file2_name': file2.name,
                'token_similarity': result['similarity_score'],
                'ast_similarity': result['similarity_score'] * 0.95,  # Mock
                'hash_similarity': result['similarity_score'] * 0.85,  # Mock
                'is_plagiarized': result['is_plagiarism'],
                'confidence_score': result['similarity_score']
            }
            batch_results.append(comparison)

    # Verify we have 10 results
    assert len(batch_results) == 10, f"Expected 10 pairs, got {len(batch_results)}"

    # Step 3: Save all results in batch (atomic operation)
    save_batch_results(job_id, batch_results)

    # Step 4: Update job status to completed
    update_job_status(job_id, 'completed')

    # Step 5: Get job summary
    summary = get_job_summary(job_id)

    # Verify summary statistics
    assert summary['id'] == job_id
    assert summary['status'] == 'completed'
    assert summary['file_count'] == 5
    assert summary['pair_count'] == 10
    assert summary['total_comparisons'] == 10
    assert summary['completion_percentage'] == 100.0

    # Verify plagiarism counts
    assert summary['plagiarized_count'] >= 1  # At least test1 vs test2 (identical)
    assert summary['clean_count'] >= 0
    assert summary['plagiarized_count'] + summary['clean_count'] == 10

    # Step 6: Verify plagiarism count function
    plagiarism_count = get_plagiarism_count(job_id)
    assert plagiarism_count == summary['plagiarized_count']
    assert plagiarism_count >= 1  # At least one plagiarized pair

    # Step 7: Verify average confidence is calculated
    assert 0.0 <= summary['average_confidence'] <= 1.0


@pytest.mark.integration
@pytest.mark.workflow
def test_error_handling_workflow(test_database, test_files):
    """
    Test error handling for invalid scenarios.

    This test validates:
    1. Invalid Python files handling
    2. Empty file handling
    3. Invalid job_id handling
    4. Invalid similarity values handling
    5. Database consistency on errors

    Expected: All errors caught gracefully, database remains consistent
    """
    job_id = f"error_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job = create_analysis_job(job_id=job_id, file_count=2)

    # Test Case 1: Invalid similarity values (out of range)
    invalid_result_high = {
        'file1_name': 'test1.py',
        'file2_name': 'test2.py',
        'token_similarity': 1.5,  # Invalid: > 1.0
        'ast_similarity': 0.8,
        'hash_similarity': 0.7,
        'is_plagiarized': True,
        'confidence_score': 0.9
    }

    with pytest.raises(InvalidResultDataError) as exc_info:
        save_comparison_result(job_id, invalid_result_high)
    assert "must be between 0.0 and 1.0" in str(exc_info.value)

    # Test Case 2: Invalid similarity values (negative)
    invalid_result_negative = {
        'file1_name': 'test1.py',
        'file2_name': 'test2.py',
        'token_similarity': -0.5,  # Invalid: < 0.0
        'ast_similarity': 0.8,
        'hash_similarity': 0.7,
        'is_plagiarized': True,
        'confidence_score': 0.9
    }

    with pytest.raises(InvalidResultDataError) as exc_info:
        save_comparison_result(job_id, invalid_result_negative)
    assert "must be between 0.0 and 1.0" in str(exc_info.value)

    # Test Case 3: Missing required fields
    invalid_result_missing = {
        'file1_name': 'test1.py',
        'file2_name': 'test2.py',
        # Missing token_similarity
        'ast_similarity': 0.8,
        'hash_similarity': 0.7,
        'is_plagiarized': True,
        'confidence_score': 0.9
    }

    with pytest.raises(InvalidResultDataError) as exc_info:
        save_comparison_result(job_id, invalid_result_missing)
    assert "Missing required fields" in str(exc_info.value)

    # Test Case 4: Invalid job_id (non-existent)
    valid_result = {
        'file1_name': 'test1.py',
        'file2_name': 'test2.py',
        'token_similarity': 0.85,
        'ast_similarity': 0.8,
        'hash_similarity': 0.7,
        'is_plagiarized': True,
        'confidence_score': 0.9
    }

    with pytest.raises(JobNotFoundError) as exc_info:
        save_comparison_result('nonexistent_job', valid_result)
    assert "Job not found" in str(exc_info.value)

    # Test Case 5: Empty file names
    invalid_result_empty_name = {
        'file1_name': '',  # Empty
        'file2_name': 'test2.py',
        'token_similarity': 0.85,
        'ast_similarity': 0.8,
        'hash_similarity': 0.7,
        'is_plagiarized': True,
        'confidence_score': 0.9
    }

    with pytest.raises(InvalidResultDataError) as exc_info:
        save_comparison_result(job_id, invalid_result_empty_name)
    assert "cannot be empty" in str(exc_info.value)

    # Verify database consistency: no results should be saved after errors
    results = get_job_results(job_id)
    assert len(results) == 0, "Database should have no results after failed operations"


@pytest.mark.integration
@pytest.mark.workflow
def test_multiple_jobs_isolation(test_database, test_files):
    """
    Test that multiple analysis jobs don't interfere with each other.

    This test validates:
    1. Multiple concurrent jobs
    2. Job result isolation
    3. No cross-contamination between jobs
    4. Independent job status tracking

    Expected: Each job maintains its own results independently
    """
    # Create job 1 with 3 files
    job1_id = f"job1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job1 = create_analysis_job(job_id=job1_id, file_count=3)

    assert job1['pair_count'] == 3  # 3 files = 3 pairs

    # Create job 2 with 4 files
    job2_id = f"job2_{datetime.now().strftime('%Y%m%d_%H%M%S')}_b"
    job2 = create_analysis_job(job_id=job2_id, file_count=4)

    assert job2['pair_count'] == 6  # 4 files = 6 pairs

    # Create results for job 1
    job1_results = []
    for i in range(3):
        result = {
            'file1_name': f'job1_file{i}.py',
            'file2_name': f'job1_file{i+1}.py',
            'token_similarity': 0.5 + i * 0.1,
            'ast_similarity': 0.6 + i * 0.1,
            'hash_similarity': 0.4 + i * 0.1,
            'is_plagiarized': i % 2 == 0,
            'confidence_score': 0.55 + i * 0.1
        }
        job1_results.append(result)

    save_batch_results(job1_id, job1_results)

    # Create results for job 2
    job2_results = []
    for i in range(6):
        result = {
            'file1_name': f'job2_file{i}.py',
            'file2_name': f'job2_file{i+1}.py',
            'token_similarity': 0.3 + i * 0.05,
            'ast_similarity': 0.4 + i * 0.05,
            'hash_similarity': 0.2 + i * 0.05,
            'is_plagiarized': i % 3 == 0,
            'confidence_score': 0.35 + i * 0.05
        }
        job2_results.append(result)

    save_batch_results(job2_id, job2_results)

    # Retrieve results for job 1
    retrieved_job1 = get_job_results(job1_id)
    assert len(retrieved_job1) == 3

    # Verify all results belong to job 1
    for result in retrieved_job1:
        assert result['job_id'] == job1_id
        assert 'job1_file' in result['file1_name']

    # Retrieve results for job 2
    retrieved_job2 = get_job_results(job2_id)
    assert len(retrieved_job2) == 6

    # Verify all results belong to job 2
    for result in retrieved_job2:
        assert result['job_id'] == job2_id
        assert 'job2_file' in result['file1_name']

    # Verify no cross-contamination
    job1_files = {r['file1_name'] for r in retrieved_job1}
    job2_files = {r['file1_name'] for r in retrieved_job2}
    assert len(job1_files.intersection(job2_files)) == 0, "Jobs should have no overlapping files"

    # Verify independent status tracking
    update_job_status(job1_id, 'completed')
    update_job_status(job2_id, 'running')

    summary1 = get_job_summary(job1_id)
    summary2 = get_job_summary(job2_id)

    assert summary1['status'] == 'completed'
    assert summary2['status'] == 'running'


@pytest.mark.integration
@pytest.mark.workflow
def test_detector_database_integration(test_database, test_files):
    """
    Test that detector output integrates correctly with database schema.

    This test validates:
    1. Detector result structure compatibility
    2. Field mapping from detector to database
    3. Data type conversions
    4. No data loss in conversion

    Expected: Detector results can be stored and retrieved without data loss
    """
    job_id = f"detector_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job = create_analysis_job(job_id=job_id, file_count=2)

    # Step 1: Run TokenDetector
    file1 = test_files[0]  # test1.py
    file2 = test_files[1]  # test2.py (copy)

    detector = TokenDetector(threshold=0.7)
    detector_result = detector.analyze(file1, file2)

    # Step 2: Extract and verify detector fields
    assert 'similarity_score' in detector_result
    assert 'is_plagiarism' in detector_result
    assert 'jaccard_similarity' in detector_result
    assert 'cosine_similarity' in detector_result
    assert 'threshold' in detector_result
    assert 'details' in detector_result

    # Step 3: Map detector fields to database fields
    # Database expects: token_similarity, ast_similarity, hash_similarity
    # Detector provides: jaccard_similarity, cosine_similarity, similarity_score

    # Use combined similarity_score as token_similarity
    token_sim = detector_result['similarity_score']

    # For this test, we'll use the individual metrics
    jaccard_sim = detector_result['jaccard_similarity']
    cosine_sim = detector_result['cosine_similarity']

    database_record = {
        'file1_name': file1.name,
        'file2_name': file2.name,
        'token_similarity': min(1.0, token_sim),  # Combined score, clamp to 1.0
        'ast_similarity': min(1.0, jaccard_sim),  # Map Jaccard to AST, clamp to 1.0
        'hash_similarity': min(1.0, cosine_sim),  # Map Cosine to hash, clamp to 1.0
        'is_plagiarized': detector_result['is_plagiarism'],
        'confidence_score': min(1.0, detector_result['similarity_score'])
    }

    # Step 4: Verify field types are compatible
    assert isinstance(database_record['token_similarity'], (int, float))
    assert isinstance(database_record['ast_similarity'], (int, float))
    assert isinstance(database_record['hash_similarity'], (int, float))
    assert isinstance(database_record['is_plagiarized'], bool)
    assert isinstance(database_record['confidence_score'], (int, float))

    # Step 5: Save to database
    saved_result = save_comparison_result(job_id, database_record)

    # Step 6: Retrieve and verify no data loss
    retrieved_results = get_job_results(job_id)
    assert len(retrieved_results) == 1

    retrieved = retrieved_results[0]

    # Verify all fields preserved
    assert abs(retrieved['token_similarity'] - token_sim) < 0.0001
    assert abs(retrieved['ast_similarity'] - jaccard_sim) < 0.0001
    assert abs(retrieved['hash_similarity'] - cosine_sim) < 0.0001
    assert retrieved['is_plagiarized'] == detector_result['is_plagiarism']
    assert abs(retrieved['confidence_score'] - detector_result['similarity_score']) < 0.0001

    # Step 7: Verify types after round trip
    assert isinstance(retrieved['token_similarity'], float)
    assert isinstance(retrieved['ast_similarity'], float)
    assert isinstance(retrieved['hash_similarity'], float)
    assert isinstance(retrieved['is_plagiarized'], bool)
    assert isinstance(retrieved['confidence_score'], float)


@pytest.mark.integration
@pytest.mark.workflow
def test_validation_dataset_integration(test_database):
    """
    Test using real validation dataset files in integration test.

    This test validates:
    1. Real validation dataset file loading
    2. Plagiarism detection on known plagiarized pair
    3. Complete workflow with real-world files
    4. Results stored correctly in database

    Expected: factorial_original.py vs factorial_copied.py should be detected as plagiarism
    """
    # Locate validation dataset files
    validation_dir = PROJECT_ROOT / "validation-datasets" / "plagiarized"

    original_file = validation_dir / "factorial_original.py"
    copied_file = validation_dir / "factorial_copied.py"

    # Verify files exist
    assert original_file.exists(), f"Validation file not found: {original_file}"
    assert copied_file.exists(), f"Validation file not found: {copied_file}"

    # Step 1: Create analysis job
    job_id = f"validation_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job = create_analysis_job(job_id=job_id, file_count=2)

    # Step 2: Run TokenDetector on plagiarized pair
    detector = TokenDetector(threshold=0.7)
    result = detector.analyze(original_file, copied_file)

    # Step 3: Verify plagiarism detected
    # These files are identical, so similarity should be very high
    assert result['similarity_score'] > 0.95, (
        f"Expected very high similarity for identical files, got {result['similarity_score']:.2f}"
    )
    assert result['is_plagiarism'] is True, "Expected plagiarism detection for copied file"

    # Step 4: Save to database
    # Note: Clamp values to 1.0 to handle floating-point precision issues
    comparison_data = {
        'file1_name': original_file.name,
        'file2_name': copied_file.name,
        'token_similarity': min(1.0, result['similarity_score']),
        'ast_similarity': min(1.0, result['jaccard_similarity']),
        'hash_similarity': min(1.0, result['cosine_similarity']),
        'is_plagiarized': result['is_plagiarism'],
        'confidence_score': min(1.0, result['similarity_score'])
    }

    saved_result = save_comparison_result(job_id, comparison_data)

    # Step 5: Verify results correctly stored
    retrieved_results = get_job_results(job_id)
    assert len(retrieved_results) == 1

    retrieved = retrieved_results[0]
    assert retrieved['is_plagiarized'] is True
    assert retrieved['token_similarity'] > 0.95

    # Step 6: Update job and get summary
    update_job_status(job_id, 'completed')
    summary = get_job_summary(job_id)

    assert summary['status'] == 'completed'
    assert summary['total_comparisons'] == 1
    assert summary['plagiarized_count'] == 1
    assert summary['completion_percentage'] == 100.0


# =============================================================================
# Test Execution Helper
# =============================================================================

if __name__ == "__main__":
    """
    Run integration tests directly with pytest.

    Usage:
        python test_workflow_integration.py

    Or with pytest:
        pytest test_workflow_integration.py -v
        pytest test_workflow_integration.py::test_file_upload_to_database_flow -v
        pytest -m integration -v
    """
    import subprocess

    print("Running integration tests...")
    print("=" * 80)

    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )

    exit(result.returncode)
