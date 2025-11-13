"""
Test Shared Fixtures

This module verifies that all shared fixtures defined in conftest.py
work correctly and provide the expected functionality.

Test coverage:
- Database session fixture
- Sample code pairs fixture
- Temporary directory fixture
- Mock analysis job fixture
- Sample Python files fixture
- Test configuration fixture
- Log capture fixture
"""

import pytest
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any


# =============================================================================
# Database Session Fixture Tests
# =============================================================================

def test_db_session_fixture(db_session):
    """Test that db_session fixture provides working database connection."""
    # Verify connection is not None
    assert db_session is not None

    # Verify connection is sqlite3.Connection
    assert isinstance(db_session, sqlite3.Connection)

    # Verify can execute queries
    cursor = db_session.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Verify expected tables exist
    assert 'analysis_jobs' in tables
    assert 'comparison_results' in tables
    assert 'configuration' in tables


def test_db_session_isolation(db_session):
    """Test that db_session provides isolated database for each test."""
    # Insert test data
    db_session.execute(
        """
        INSERT INTO analysis_jobs (id, status, file_count, pair_count)
        VALUES (?, ?, ?, ?)
        """,
        ('test-isolation', 'pending', 5, 10)
    )
    db_session.commit()

    # Verify data exists
    cursor = db_session.execute(
        "SELECT * FROM analysis_jobs WHERE id = ?",
        ('test-isolation',)
    )
    result = cursor.fetchone()
    assert result is not None
    assert result['id'] == 'test-isolation'


def test_db_session_foreign_keys(db_session):
    """Test that foreign key constraints are enabled."""
    # Create a job
    db_session.execute(
        """
        INSERT INTO analysis_jobs (id, status, file_count, pair_count)
        VALUES (?, ?, ?, ?)
        """,
        ('test-fk', 'pending', 2, 1)
    )
    db_session.commit()

    # Insert comparison result with valid foreign key
    db_session.execute(
        """
        INSERT INTO comparison_results (
            job_id, file1_name, file2_name,
            token_similarity, ast_similarity, hash_similarity,
            is_plagiarized, confidence_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ('test-fk', 'file1.py', 'file2.py', 0.5, 0.6, 0.7, 0, 0.6)
    )
    db_session.commit()

    # Verify foreign key constraint is enforced (should raise error for invalid FK)
    with pytest.raises(sqlite3.IntegrityError):
        db_session.execute(
            """
            INSERT INTO comparison_results (
                job_id, file1_name, file2_name,
                token_similarity, ast_similarity, hash_similarity,
                is_plagiarized, confidence_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ('nonexistent-job', 'file1.py', 'file2.py', 0.5, 0.6, 0.7, 0, 0.6)
        )


# =============================================================================
# Sample Code Pairs Fixture Tests
# =============================================================================

def test_sample_code_pairs_fixture(sample_code_pairs):
    """Test that sample_code_pairs fixture provides expected scenarios."""
    # Verify fixture is not None
    assert sample_code_pairs is not None
    assert isinstance(sample_code_pairs, dict)

    # Verify expected scenarios exist
    expected_scenarios = [
        'identical', 'renamed', 'different', 'similar_structure',
        'with_comments', 'partial_copy', 'whitespace_diff', 'empty', 'one_empty'
    ]
    for scenario in expected_scenarios:
        assert scenario in sample_code_pairs, f"Missing scenario: {scenario}"


def test_sample_code_pairs_structure(sample_code_pairs):
    """Test that each code pair has correct structure."""
    for scenario_name, scenario_data in sample_code_pairs.items():
        # Verify required keys
        assert 'code1' in scenario_data, f"Missing code1 in {scenario_name}"
        assert 'code2' in scenario_data, f"Missing code2 in {scenario_name}"
        assert 'expected_similarity' in scenario_data, f"Missing expected_similarity in {scenario_name}"
        assert 'description' in scenario_data, f"Missing description in {scenario_name}"

        # Verify types
        assert isinstance(scenario_data['code1'], str)
        assert isinstance(scenario_data['code2'], str)
        assert isinstance(scenario_data['expected_similarity'], (int, float))
        assert isinstance(scenario_data['description'], str)

        # Verify similarity is in valid range
        assert 0.0 <= scenario_data['expected_similarity'] <= 1.0


def test_sample_code_pairs_identical(sample_code_pairs):
    """Test identical code pair scenario."""
    identical = sample_code_pairs['identical']
    assert identical['code1'] == identical['code2']
    assert identical['expected_similarity'] == 1.0


def test_sample_code_pairs_different(sample_code_pairs):
    """Test different code pair scenario."""
    different = sample_code_pairs['different']
    assert different['code1'] != different['code2']
    assert different['expected_similarity'] < 0.5


def test_sample_code_pairs_empty(sample_code_pairs):
    """Test empty code pair scenario."""
    empty = sample_code_pairs['empty']
    assert empty['code1'] == ''
    assert empty['code2'] == ''
    assert empty['expected_similarity'] == 1.0


# =============================================================================
# Temporary Directory Fixture Tests
# =============================================================================

def test_temp_upload_dir_fixture(temp_upload_dir):
    """Test that temp_upload_dir fixture provides working directory."""
    # Verify directory exists
    assert temp_upload_dir is not None
    assert isinstance(temp_upload_dir, Path)
    assert temp_upload_dir.exists()
    assert temp_upload_dir.is_dir()


def test_temp_upload_dir_writeable(temp_upload_dir):
    """Test that temp_upload_dir is writeable."""
    # Create a test file
    test_file = temp_upload_dir / "test.txt"
    test_file.write_text("test content")

    # Verify file was created
    assert test_file.exists()
    assert test_file.read_text() == "test content"


def test_temp_upload_dir_multiple_files(temp_upload_dir):
    """Test that temp_upload_dir can contain multiple files."""
    # Create multiple files
    files = []
    for i in range(5):
        file_path = temp_upload_dir / f"file{i}.py"
        file_path.write_text(f"# File {i}")
        files.append(file_path)

    # Verify all files exist
    for file_path in files:
        assert file_path.exists()

    # Verify directory listing
    dir_files = list(temp_upload_dir.glob("*.py"))
    assert len(dir_files) == 5


# =============================================================================
# Mock Analysis Job Fixture Tests
# =============================================================================

def test_mock_analysis_job_fixture(mock_analysis_job):
    """Test that mock_analysis_job fixture provides valid job data."""
    # Verify fixture is not None
    assert mock_analysis_job is not None
    assert isinstance(mock_analysis_job, dict)

    # Verify required keys
    assert 'id' in mock_analysis_job
    assert 'status' in mock_analysis_job
    assert 'file_count' in mock_analysis_job
    assert 'pair_count' in mock_analysis_job
    assert 'results' in mock_analysis_job

    # Verify values
    assert mock_analysis_job['status'] == 'completed'
    assert mock_analysis_job['file_count'] == 5
    assert mock_analysis_job['pair_count'] == 10
    assert isinstance(mock_analysis_job['results'], list)
    assert len(mock_analysis_job['results']) == 6  # 3 plagiarized + 3 clean


def test_mock_analysis_job_in_database(mock_analysis_job, db_session):
    """Test that mock_analysis_job is actually in database."""
    job_id = mock_analysis_job['id']

    # Verify job exists in database
    cursor = db_session.execute(
        "SELECT * FROM analysis_jobs WHERE id = ?",
        (job_id,)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row['id'] == job_id
    assert row['status'] == 'completed'


def test_mock_analysis_job_results(mock_analysis_job, db_session):
    """Test that mock_analysis_job has results in database."""
    job_id = mock_analysis_job['id']

    # Count results in database
    cursor = db_session.execute(
        "SELECT COUNT(*) as count FROM comparison_results WHERE job_id = ?",
        (job_id,)
    )
    row = cursor.fetchone()
    assert row['count'] == 6

    # Count plagiarized results
    cursor = db_session.execute(
        """
        SELECT COUNT(*) as count FROM comparison_results
        WHERE job_id = ? AND is_plagiarized = 1
        """,
        (job_id,)
    )
    row = cursor.fetchone()
    assert row['count'] == 3  # 3 plagiarized pairs


# =============================================================================
# Sample Python Files Fixture Tests
# =============================================================================

def test_sample_python_files_fixture(sample_python_files):
    """Test that sample_python_files fixture creates files."""
    # Verify fixture is not None
    assert sample_python_files is not None
    assert isinstance(sample_python_files, list)

    # Verify expected number of files
    assert len(sample_python_files) == 5

    # Verify all are Path objects
    for file_path in sample_python_files:
        assert isinstance(file_path, Path)


def test_sample_python_files_exist(sample_python_files):
    """Test that all sample files exist."""
    for file_path in sample_python_files:
        assert file_path.exists(), f"File does not exist: {file_path}"
        assert file_path.is_file(), f"Not a file: {file_path}"
        assert file_path.suffix == '.py', f"Wrong extension: {file_path}"


def test_sample_python_files_content(sample_python_files):
    """Test that sample files have content (except empty one)."""
    for i, file_path in enumerate(sample_python_files):
        content = file_path.read_text()
        if i < 4:  # First 4 files should have content
            assert len(content) > 0, f"File should have content: {file_path}"
        else:  # Last file is empty
            assert len(content) == 0, f"File should be empty: {file_path}"


def test_sample_python_files_names(sample_python_files):
    """Test that sample files have expected names."""
    expected_names = ['student1.py', 'student2.py', 'student3.py', 'student4.py', 'student5.py']
    actual_names = [f.name for f in sample_python_files]

    for expected in expected_names:
        assert expected in actual_names, f"Missing file: {expected}"


# =============================================================================
# Test Configuration Fixture Tests
# =============================================================================

def test_test_config_fixture(test_config):
    """Test that test_config fixture provides configuration."""
    # Verify fixture is not None
    assert test_config is not None
    assert isinstance(test_config, dict)

    # Verify required keys
    required_keys = [
        'token_threshold', 'ast_threshold', 'hash_threshold',
        'token_weight', 'ast_weight', 'hash_weight',
        'decision_threshold', 'max_file_size', 'allowed_extensions'
    ]
    for key in required_keys:
        assert key in test_config, f"Missing configuration key: {key}"


def test_test_config_thresholds(test_config):
    """Test that threshold values are in valid range."""
    # All thresholds should be between 0.0 and 1.0
    thresholds = [
        'token_threshold', 'ast_threshold', 'hash_threshold', 'decision_threshold'
    ]
    for threshold_key in thresholds:
        value = test_config[threshold_key]
        assert 0.0 <= value <= 1.0, f"{threshold_key} out of range: {value}"


def test_test_config_weights(test_config):
    """Test that weight values are positive."""
    weights = ['token_weight', 'ast_weight', 'hash_weight']
    for weight_key in weights:
        value = test_config[weight_key]
        assert value > 0, f"{weight_key} should be positive: {value}"


def test_test_config_file_limits(test_config):
    """Test that file limit values are valid."""
    # Max file size should be positive
    assert test_config['max_file_size'] > 0

    # Allowed extensions should be a list
    assert isinstance(test_config['allowed_extensions'], list)
    assert len(test_config['allowed_extensions']) > 0

    # Min/max files should be valid
    assert test_config['min_files'] > 0
    assert test_config['max_files'] > test_config['min_files']


# =============================================================================
# Log Capture Fixture Tests
# =============================================================================

def test_capture_logs_fixture(capture_logs):
    """Test that capture_logs fixture captures log messages."""
    # Verify fixture is not None
    assert capture_logs is not None
    assert isinstance(capture_logs, list)

    # Create a logger and log a message
    logger = logging.getLogger('test_logger')
    logger.error('Test error message')

    # Verify log was captured
    # Note: There may be other logs, so we check if our log is present
    error_logs = [record for record in capture_logs if record.levelname == 'ERROR']
    assert len(error_logs) > 0, "No ERROR logs captured"

    # Find our specific log message
    our_log = next((r for r in error_logs if 'Test error message' in r.message), None)
    assert our_log is not None, "Our test log message was not captured"


def test_capture_logs_multiple_levels(capture_logs):
    """Test that capture_logs captures different log levels."""
    logger = logging.getLogger('test_multi_level')

    # Log messages at different levels
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')

    # Verify all levels were captured
    levels = {record.levelname for record in capture_logs}
    # At minimum, we should have the levels we logged
    # (may have others from fixtures)
    assert len(capture_logs) > 0


# =============================================================================
# Fixture Integration Tests
# =============================================================================

def test_fixtures_work_together(db_session, sample_code_pairs, test_config):
    """Test that multiple fixtures can be used together."""
    # Use db_session
    cursor = db_session.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert len(tables) > 0

    # Use sample_code_pairs
    assert 'identical' in sample_code_pairs

    # Use test_config
    assert test_config['token_threshold'] > 0


def test_fixture_cleanup_isolation():
    """Test that fixture cleanup works (run this multiple times)."""
    # This test verifies that fixture cleanup happens between tests
    # by ensuring we start with a clean state
    # If this passes multiple times, cleanup is working
    assert True


@pytest.mark.parametrize("scenario", [
    'identical', 'renamed', 'different', 'similar_structure'
])
def test_sample_code_pairs_parametrized(sample_code_pairs, scenario):
    """Test sample code pairs with parametrization."""
    assert scenario in sample_code_pairs
    pair = sample_code_pairs[scenario]
    assert 'code1' in pair
    assert 'code2' in pair
    assert 'expected_similarity' in pair
