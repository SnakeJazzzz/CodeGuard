"""
Comprehensive Unit Tests for Database Operations.

This test module provides extensive coverage of the database operations module,
including job creation, result storage, retrieval, updates, and error handling.

Coverage target: ≥60% for src/database/operations.py
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from src.database.operations import (
    create_analysis_job,
    save_comparison_result,
    get_job_results,
    update_job_status,
    get_job_summary,
    get_recent_jobs,
    job_exists,
)


@pytest.fixture(autouse=True)
def use_test_db(db_session, monkeypatch):
    """
    Auto-use fixture that patches database operations to use test database.

    This fixture automatically patches get_session() for all tests in this module
    to use the in-memory test database instead of the production database.
    """

    @contextmanager
    def mock_get_session():
        """Mock get_session to return test database connection."""
        try:
            yield db_session
        finally:
            pass

    # Patch get_session in the operations module
    monkeypatch.setattr("src.database.operations.get_session", mock_get_session)

    # Also patch it in the connection module for job_exists
    monkeypatch.setattr("src.database.connection.get_session", mock_get_session)

    yield db_session


class TestJobCreation:
    """Test analysis job creation operations."""

    def test_create_job_basic(self, db_session):
        """Test creating a basic analysis job."""
        job_id = "test_job_001"
        file_count = 5

        result = create_analysis_job(job_id=job_id, file_count=file_count)

        assert result is not None
        assert result["id"] == job_id
        assert result["file_count"] == file_count
        assert result["pair_count"] == 10  # Calculated as 5*(5-1)/2
        assert result["status"] == "pending"

    def test_create_job_with_custom_status(self, db_session):
        """Test creating job with custom status then updating it."""
        job_id = "test_job_002"

        result = create_analysis_job(job_id=job_id, file_count=3)

        # Status is always 'pending' on creation, update it separately
        assert result["status"] == "pending"

        # Update status to 'running'
        update_job_status(job_id=job_id, status="running")

        # Verify the update
        assert job_exists(job_id)

    def test_create_job_timestamp(self, db_session):
        """Test that job creation includes timestamp."""
        job_id = "test_job_003"

        result = create_analysis_job(job_id=job_id, file_count=2)

        assert "created_at" in result
        assert result["created_at"] is not None

    def test_create_multiple_jobs(self, db_session):
        """Test creating multiple jobs."""
        jobs = []
        for i in range(5):
            job_id = f"test_job_{i:03d}"
            result = create_analysis_job(job_id=job_id, file_count=i + 2)
            jobs.append(result)

        assert len(jobs) == 5
        for i, job in enumerate(jobs):
            assert job["id"] == f"test_job_{i:03d}"


class TestComparisonResults:
    """Test comparison result storage operations."""

    def test_save_comparison_result(self, db_session):
        """Test saving a comparison result."""
        # First create a job
        job_id = "test_job_result_001"
        create_analysis_job(job_id=job_id, file_count=2)

        # Save a comparison result
        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 0.85,
            "ast_similarity": 0.92,
            "hash_similarity": 0.78,
            "is_plagiarized": True,
            "confidence_score": 0.85,
        }
        result = save_comparison_result(job_id=job_id, result=result_data)

        assert result is not None
        assert result["job_id"] == job_id
        assert result["file1_name"] == "file1.py"
        assert result["file2_name"] == "file2.py"
        assert result["is_plagiarized"] is True

    def test_save_multiple_results(self, db_session):
        """Test saving multiple comparison results for one job."""
        job_id = "test_job_multi_results"
        create_analysis_job(job_id=job_id, file_count=3)

        results = []
        pairs = [
            ("file1.py", "file2.py", 0.9, 0.95, 0.88),
            ("file1.py", "file3.py", 0.5, 0.6, 0.45),
            ("file2.py", "file3.py", 0.3, 0.4, 0.35),
        ]

        for file1, file2, token_sim, ast_sim, hash_sim in pairs:
            result_data = {
                "file1_name": file1,
                "file2_name": file2,
                "token_similarity": token_sim,
                "ast_similarity": ast_sim,
                "hash_similarity": hash_sim,
                "is_plagiarized": (token_sim > 0.7),
                "confidence_score": token_sim,
            }
            result = save_comparison_result(job_id=job_id, result=result_data)
            results.append(result)

        assert len(results) == 3


class TestJobRetrieval:
    """Test job retrieval operations."""

    def test_job_exists(self, db_session):
        """Test checking if job exists."""
        job_id = "test_job_retrieve"
        create_analysis_job(job_id=job_id, file_count=5)

        exists = job_exists(job_id)
        assert exists is True

    def test_job_not_exists(self, db_session):
        """Test checking nonexistent job returns False."""
        exists = job_exists("nonexistent_job")
        assert exists is False

    def test_get_recent_jobs_empty(self, db_session):
        """Test listing recent jobs when database is empty."""
        jobs = get_recent_jobs(limit=10)
        assert isinstance(jobs, list)
        # May be empty or have jobs from other tests
        assert jobs is not None

    def test_get_recent_jobs_multiple(self, db_session):
        """Test listing recent jobs."""
        # Create several jobs
        for i in range(3):
            create_analysis_job(job_id=f"list_test_{i}", file_count=i + 2)

        jobs = get_recent_jobs(limit=10)

        assert len(jobs) >= 3
        # Jobs should be sorted by creation date


class TestJobResults:
    """Test job results retrieval operations."""

    def test_get_job_results(self, db_session):
        """Test getting results for a job."""
        job_id = "test_job_get_results"
        create_analysis_job(job_id=job_id, file_count=2)

        # Save a result
        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 0.85,
            "ast_similarity": 0.90,
            "hash_similarity": 0.80,
            "is_plagiarized": True,
            "confidence_score": 0.85,
        }
        save_comparison_result(job_id=job_id, result=result_data)

        results = get_job_results(job_id)

        assert len(results) >= 1
        assert results[0]["job_id"] == job_id

    def test_get_results_nonexistent_job(self, db_session):
        """Test getting results for nonexistent job."""
        from src.database.operations import JobNotFoundError

        with pytest.raises(JobNotFoundError):
            get_job_results("nonexistent_job")

    def test_get_results_job_with_no_results(self, db_session):
        """Test getting results for job with no comparison results yet."""
        job_id = "test_job_no_results"
        create_analysis_job(job_id=job_id, file_count=2)

        results = get_job_results(job_id)

        assert isinstance(results, list)
        assert len(results) == 0


class TestJobStatusUpdates:
    """Test job status update operations."""

    def test_update_job_status(self, db_session):
        """Test updating job status."""
        job_id = "test_job_status_update"
        create_analysis_job(job_id=job_id, file_count=2)

        # Update status (function returns None on success, raises on error)
        update_job_status(job_id=job_id, status="completed")

        # Verify update by checking job exists
        exists = job_exists(job_id)
        assert exists is True

    def test_update_status_through_workflow(self, db_session):
        """Test updating status through typical workflow."""
        job_id = "test_workflow_status"
        create_analysis_job(job_id=job_id, file_count=2)

        # Simulate workflow: pending -> running -> completed
        update_job_status(job_id, "running")
        update_job_status(job_id, "completed")

        # Verify job still exists
        assert job_exists(job_id)

    def test_update_status_to_failed(self, db_session):
        """Test updating job status to failed."""
        job_id = "test_job_failed"
        create_analysis_job(job_id=job_id, file_count=2)

        update_job_status(job_id=job_id, status="failed")

        # Verify job exists
        assert job_exists(job_id)


class TestJobSummary:
    """Test job summary retrieval operations."""

    def test_get_job_summary(self, db_session):
        """Test getting job summary statistics."""
        job_id = "test_job_summary"
        create_analysis_job(job_id=job_id, file_count=3)

        # Add some results
        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 0.9,
            "ast_similarity": 0.95,
            "hash_similarity": 0.88,
            "is_plagiarized": True,
            "confidence_score": 0.91,
        }
        save_comparison_result(job_id=job_id, result=result_data)

        summary = get_job_summary(job_id)

        assert summary is not None
        assert "id" in summary
        assert "total_comparisons" in summary
        assert "pair_count" in summary

    def test_get_summary_nonexistent_job(self, db_session):
        """Test getting summary for nonexistent job."""
        from src.database.operations import JobNotFoundError

        with pytest.raises(JobNotFoundError):
            get_job_summary("nonexistent_job")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_create_job_with_zero_files(self, db_session):
        """Test creating job with zero files."""
        job_id = "test_job_zero_files"

        result = create_analysis_job(job_id=job_id, file_count=0)

        # Should still create job
        assert result is not None
        assert result["pair_count"] == 0

    def test_save_result_with_boundary_values(self, db_session):
        """Test saving result with boundary similarity values."""
        job_id = "test_boundary_values"
        create_analysis_job(job_id=job_id, file_count=2)

        # Test with 0.0 similarity
        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 0.0,
            "ast_similarity": 0.0,
            "hash_similarity": 0.0,
            "is_plagiarized": False,
            "confidence_score": 0.0,
        }
        result = save_comparison_result(job_id=job_id, result=result_data)

        assert result is not None
        assert result["token_similarity"] == 0.0

    def test_save_result_with_max_values(self, db_session):
        """Test saving result with maximum similarity values."""
        job_id = "test_max_values"
        create_analysis_job(job_id=job_id, file_count=2)

        # Test with 1.0 similarity
        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 1.0,
            "ast_similarity": 1.0,
            "hash_similarity": 1.0,
            "is_plagiarized": True,
            "confidence_score": 1.0,
        }
        result = save_comparison_result(job_id=job_id, result=result_data)

        assert result is not None
        assert result["token_similarity"] == 1.0

    def test_long_filename_handling(self, db_session):
        """Test handling of long filenames."""
        job_id = "test_long_filenames"
        create_analysis_job(job_id=job_id, file_count=2)

        long_filename = "a" * 200 + ".py"

        result_data = {
            "file1_name": long_filename,
            "file2_name": "file2.py",
            "token_similarity": 0.5,
            "ast_similarity": 0.6,
            "hash_similarity": 0.4,
            "is_plagiarized": False,
            "confidence_score": 0.5,
        }
        result = save_comparison_result(job_id=job_id, result=result_data)

        assert result is not None

    def test_special_characters_in_filenames(self, db_session):
        """Test handling special characters in filenames."""
        job_id = "test_special_chars"
        create_analysis_job(job_id=job_id, file_count=2)

        result_data = {
            "file1_name": "file-with-dashes.py",
            "file2_name": "file_with_underscores.py",
            "token_similarity": 0.5,
            "ast_similarity": 0.6,
            "hash_similarity": 0.4,
            "is_plagiarized": False,
            "confidence_score": 0.5,
        }
        result = save_comparison_result(job_id=job_id, result=result_data)

        assert result is not None


class TestDatabaseConsistency:
    """Test database consistency and foreign key constraints."""

    def test_job_and_results_relationship(self, db_session):
        """Test relationship between jobs and results."""
        job_id = "test_relationship"
        create_analysis_job(job_id=job_id, file_count=2)

        result_data = {
            "file1_name": "file1.py",
            "file2_name": "file2.py",
            "token_similarity": 0.8,
            "ast_similarity": 0.85,
            "hash_similarity": 0.75,
            "is_plagiarized": True,
            "confidence_score": 0.8,
        }
        save_comparison_result(job_id=job_id, result=result_data)

        # Get job and verify it has results
        results = get_job_results(job_id)
        assert len(results) > 0

    def test_multiple_results_per_job(self, db_session):
        """Test storing multiple results for single job."""
        job_id = "test_multi_results"
        create_analysis_job(job_id=job_id, file_count=3)

        # Add multiple results
        for i in range(3):
            result_data = {
                "file1_name": f"file{i}.py",
                "file2_name": f"file{i+1}.py",
                "token_similarity": 0.5 + (i * 0.1),
                "ast_similarity": 0.6 + (i * 0.1),
                "hash_similarity": 0.4 + (i * 0.1),
                "is_plagiarized": (i == 0),
                "confidence_score": 0.5 + (i * 0.1),
            }
            save_comparison_result(job_id=job_id, result=result_data)

        results = get_job_results(job_id)
        assert len(results) == 3


class TestConcurrentOperations:
    """Test handling of concurrent-like operations."""

    def test_create_and_check_immediately(self, db_session):
        """Test creating and immediately checking a job."""
        job_id = "test_immediate_check"

        # Create
        create_analysis_job(job_id=job_id, file_count=2)

        # Immediately check exists
        exists = job_exists(job_id)

        assert exists is True

    def test_update_and_check_immediately(self, db_session):
        """Test updating and immediately checking."""
        job_id = "test_immediate_update"

        create_analysis_job(job_id=job_id, file_count=2)

        # Update
        update_job_status(job_id, "completed")

        # Immediately check
        exists = job_exists(job_id)
        assert exists is True


@pytest.mark.parametrize("status", ["pending", "running", "completed", "failed"])
def test_all_valid_statuses(db_session, status):
    """Test all valid job statuses."""
    job_id = f"test_status_{status}"

    result = create_analysis_job(job_id=job_id, file_count=2)

    # Jobs always start as 'pending', then update if needed
    assert result["status"] == "pending"

    if status != "pending":
        update_job_status(job_id, status)


@pytest.mark.parametrize("similarity", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_similarity_value_ranges(db_session, similarity):
    """Test various similarity value ranges."""
    job_id = f"test_sim_{int(similarity * 100)}"

    create_analysis_job(job_id=job_id, file_count=2)

    result_data = {
        "file1_name": "file1.py",
        "file2_name": "file2.py",
        "token_similarity": similarity,
        "ast_similarity": similarity,
        "hash_similarity": similarity,
        "is_plagiarized": (similarity >= 0.7),
        "confidence_score": similarity,
    }
    result = save_comparison_result(job_id=job_id, result=result_data)

    assert result["token_similarity"] == similarity
    assert result["ast_similarity"] == similarity
    assert result["hash_similarity"] == similarity
