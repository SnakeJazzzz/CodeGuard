"""
Database CRUD Operations Module

This module provides comprehensive Create, Read, Update, Delete operations
for the CodeGuard plagiarism detection system database. All functions use
the connection module for thread-safe database access.

Features:
    - Job management (create, update, query, cleanup)
    - Comparison results storage (single and batch operations)
    - Configuration management (get/set key-value pairs)
    - Transaction support for atomic operations
    - Comprehensive error handling and validation
    - Logging for audit trails

Functions:
    Job Management:
        - create_analysis_job: Create new analysis job
        - update_job_status: Update job processing status
        - update_job_results_path: Update results file path
        - get_job_summary: Get job statistics and summary
        - get_recent_jobs: Retrieve recent analysis jobs
        - cleanup_old_jobs: Delete jobs older than threshold
        - job_exists: Check if job exists

    Comparison Results:
        - save_comparison_result: Save single comparison result
        - save_batch_results: Save multiple results atomically
        - get_job_results: Retrieve all results for a job
        - get_plagiarism_count: Count plagiarized pairs

    Configuration:
        - get_configuration: Retrieve configuration value
        - set_configuration: Store/update configuration value
        - get_all_configuration: Retrieve all configuration values

Example:
    >>> from database.operations import create_analysis_job, save_batch_results
    >>> from database.connection import init_db
    >>>
    >>> # Initialize database
    >>> init_db()
    >>>
    >>> # Create a new job
    >>> job = create_analysis_job(job_id='job_20251112_143022', file_count=10)
    >>>
    >>> # Save comparison results
    >>> results = [
    ...     {
    ...         'file1_name': 'student1.py',
    ...         'file2_name': 'student2.py',
    ...         'token_similarity': 0.85,
    ...         'ast_similarity': 0.92,
    ...         'hash_similarity': 0.78,
    ...         'is_plagiarized': True,
    ...         'confidence_score': 0.87
    ...     }
    ... ]
    >>> save_batch_results(job['id'], results)
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .connection import get_session
from .models import row_to_analysis_job, row_to_comparison_result, VALID_STATUSES

# Configure module logger
logger = logging.getLogger(__name__)

# =============================================================================
# Custom Exceptions
# =============================================================================


class JobNotFoundError(ValueError):
    """Raised when a job ID is not found in the database."""

    pass


class InvalidStatusError(ValueError):
    """Raised when an invalid status value is provided."""

    pass


class InvalidResultDataError(ValueError):
    """Raised when comparison result data is invalid."""

    pass


class DatabaseOperationError(Exception):
    """Raised when a database operation fails."""

    pass


# =============================================================================
# Job Management Functions
# =============================================================================


def create_analysis_job(job_id: str, file_count: int) -> Dict[str, Any]:
    """
    Create a new analysis job record.

    This function initializes a new plagiarism analysis job in the database.
    It calculates the number of pairwise comparisons based on the file count
    and sets the initial status to 'pending'.

    Args:
        job_id: Unique job identifier (typically timestamp-based)
        file_count: Number of files being analyzed

    Returns:
        Dictionary with job details including:
        - id: Job identifier
        - created_at: Creation timestamp
        - status: Job status (always 'pending')
        - file_count: Number of files
        - pair_count: Number of comparisons (N*(N-1)/2)
        - results_path: Path to results (initially None)

    Raises:
        ValueError: If job_id already exists or file_count is invalid
        DatabaseOperationError: If database operation fails

    Example:
        >>> job = create_analysis_job('job_20251112_143022', file_count=10)
        >>> print(f"Created job with {job['pair_count']} pairs to compare")
        Created job with 45 pairs to compare
    """
    logger.info(f"Creating analysis job: {job_id} with {file_count} files")

    # Validate file_count
    if file_count < 0:
        error_msg = f"file_count must be non-negative, got {file_count}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Calculate pair_count: N*(N-1)/2
    if file_count < 2:
        pair_count = 0
    else:
        pair_count = (file_count * (file_count - 1)) // 2

    try:
        with get_session() as conn:
            # Check if job_id already exists
            cursor = conn.execute("SELECT id FROM analysis_jobs WHERE id = ?", (job_id,))
            if cursor.fetchone() is not None:
                error_msg = f"Job with id '{job_id}' already exists"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Insert new job
            conn.execute(
                """
                INSERT INTO analysis_jobs (id, status, file_count, pair_count, results_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_id, "pending", file_count, pair_count, None),
            )

            # Retrieve the inserted job
            cursor = conn.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()

            if row is None:
                raise DatabaseOperationError("Failed to retrieve newly created job")

            job = row_to_analysis_job(row)
            logger.info(
                f"Successfully created job {job_id}: {file_count} files, " f"{pair_count} pairs"
            )

            return job.to_dict()

    except ValueError:
        raise  # Re-raise validation errors as-is
    except sqlite3.IntegrityError as e:
        error_msg = f"Integrity constraint violation creating job {job_id}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except sqlite3.Error as e:
        error_msg = f"Database error creating job {job_id}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error creating job {job_id}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def update_job_status(job_id: str, status: str) -> None:
    """
    Update the processing status of an analysis job.

    Args:
        job_id: Job identifier
        status: New status value ('pending', 'running', 'completed', 'failed')
               Note: 'processing' is accepted as an alias for 'running'

    Raises:
        JobNotFoundError: If job_id is not found
        InvalidStatusError: If status is not a valid value
        DatabaseOperationError: If database operation fails

    Example:
        >>> update_job_status('job_20251112_143022', 'processing')
        >>> # Job status is now 'processing'
        >>>
        >>> update_job_status('job_20251112_143022', 'completed')
        >>> # Job status is now 'completed'
    """
    logger.info(f"Updating job {job_id} status to '{status}'")

    # Handle status aliases
    from .models import STATUS_ALIASES

    normalized_status = STATUS_ALIASES.get(status, status)

    # Validate status
    if normalized_status not in VALID_STATUSES:
        error_msg = f"Invalid status '{status}'. " f"Must be one of: {', '.join(VALID_STATUSES)}"
        logger.error(error_msg)
        raise InvalidStatusError(error_msg)

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Update status (use normalized status)
            cursor = conn.execute(
                "UPDATE analysis_jobs SET status = ? WHERE id = ?", (normalized_status, job_id)
            )

            if cursor.rowcount == 0:
                error_msg = f"Failed to update status for job {job_id}"
                logger.error(error_msg)
                raise DatabaseOperationError(error_msg)

            logger.info(f"Successfully updated job {job_id} status to '{status}'")

    except (JobNotFoundError, InvalidStatusError):
        raise  # Re-raise custom exceptions as-is
    except sqlite3.Error as e:
        error_msg = f"Database error updating job {job_id} status: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error updating job {job_id} status: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def update_job_results_path(job_id: str, results_path: str) -> None:
    """
    Update the results file path for an analysis job.

    Args:
        job_id: Job identifier
        results_path: Path to the JSON results file

    Raises:
        JobNotFoundError: If job_id is not found
        DatabaseOperationError: If database operation fails

    Example:
        >>> update_job_results_path(
        ...     'job_20251112_143022',
        ...     'data/results/analysis_job_20251112_143022.json'
        ... )
    """
    logger.info(f"Updating job {job_id} results path to '{results_path}'")

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Update results_path
            cursor = conn.execute(
                "UPDATE analysis_jobs SET results_path = ? WHERE id = ?", (results_path, job_id)
            )

            if cursor.rowcount == 0:
                error_msg = f"Failed to update results path for job {job_id}"
                logger.error(error_msg)
                raise DatabaseOperationError(error_msg)

            logger.info(f"Successfully updated job {job_id} results path")

    except JobNotFoundError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error updating job {job_id} results path: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error updating job {job_id} results path: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def get_job_summary(job_id: str) -> Dict[str, Any]:
    """
    Get comprehensive job statistics and summary.

    This function retrieves job details along with aggregated statistics
    from the comparison results.

    Args:
        job_id: Job identifier

    Returns:
        Dictionary containing:
        - Job details (id, status, file_count, pair_count, created_at, results_path)
        - total_comparisons: Number of comparison results
        - plagiarized_count: Number of pairs flagged as plagiarized
        - clean_count: Number of pairs not flagged
        - average_confidence: Mean confidence score across all results
        - completion_percentage: Percent of expected pairs completed

    Raises:
        JobNotFoundError: If job_id is not found
        DatabaseOperationError: If database operation fails

    Example:
        >>> summary = get_job_summary('job_20251112_143022')
        >>> print(f"Plagiarism rate: {summary['plagiarized_count']}/{summary['total_comparisons']}")
        Plagiarism rate: 3/45
    """
    logger.debug(f"Getting summary for job {job_id}")

    try:
        with get_session() as conn:
            # Get job details
            cursor = conn.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,))
            job_row = cursor.fetchone()

            if job_row is None:
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            job = row_to_analysis_job(job_row)

            # Get comparison statistics
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_comparisons,
                    SUM(CASE WHEN is_plagiarized = 1 THEN 1 ELSE 0 END) as plagiarized_count,
                    AVG(confidence_score) as average_confidence
                FROM comparison_results
                WHERE job_id = ?
                """,
                (job_id,),
            )
            stats_row = cursor.fetchone()

            total_comparisons = stats_row["total_comparisons"] or 0
            plagiarized_count = stats_row["plagiarized_count"] or 0
            average_confidence = stats_row["average_confidence"] or 0.0
            clean_count = total_comparisons - plagiarized_count

            # Calculate completion percentage
            if job.pair_count > 0:
                completion_percentage = (total_comparisons / job.pair_count) * 100
            else:
                completion_percentage = 100.0 if total_comparisons == 0 else 0.0

            summary = {
                # Job details
                "id": job.id,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "status": job.status,
                "file_count": job.file_count,
                "pair_count": job.pair_count,
                "results_path": job.results_path,
                # Statistics
                "total_comparisons": total_comparisons,
                "plagiarized_count": plagiarized_count,
                "clean_count": clean_count,
                "average_confidence": round(average_confidence, 4),
                "completion_percentage": round(completion_percentage, 2),
            }

            logger.debug(
                f"Job {job_id} summary: {total_comparisons} comparisons, "
                f"{plagiarized_count} plagiarized, {completion_percentage:.1f}% complete"
            )

            return summary

    except JobNotFoundError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error getting job {job_id} summary: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error getting job {job_id} summary: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def get_recent_jobs(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve recent analysis jobs.

    Args:
        limit: Maximum number of jobs to return (default 10)

    Returns:
        List of job dictionaries, sorted by created_at DESC (most recent first)

    Raises:
        ValueError: If limit is negative
        DatabaseOperationError: If database operation fails

    Example:
        >>> recent = get_recent_jobs(limit=5)
        >>> for job in recent:
        ...     print(f"{job['id']}: {job['status']}")
        job_20251112_143022: completed
        job_20251112_120000: processing
        ...
    """
    logger.debug(f"Getting {limit} recent jobs")

    if limit < 0:
        error_msg = f"limit must be non-negative, got {limit}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        with get_session() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM analysis_jobs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )

            jobs = []
            for row in cursor.fetchall():
                job = row_to_analysis_job(row)
                jobs.append(job.to_dict())

            logger.debug(f"Retrieved {len(jobs)} recent jobs")
            return jobs

    except ValueError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error getting recent jobs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error getting recent jobs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def cleanup_old_jobs(days: int = 30) -> int:
    """
    Delete analysis jobs older than the specified number of days.

    This function removes old jobs and their associated comparison results
    due to the CASCADE DELETE foreign key constraint.

    Args:
        days: Age threshold in days (default 30)

    Returns:
        Number of jobs deleted

    Raises:
        ValueError: If days is negative
        DatabaseOperationError: If database operation fails

    Note:
        This operation cascades to comparison_results table, removing all
        associated results for deleted jobs.

    Example:
        >>> deleted = cleanup_old_jobs(days=30)
        >>> print(f"Cleaned up {deleted} jobs older than 30 days")
        Cleaned up 5 jobs older than 30 days
    """
    logger.info(f"Cleaning up jobs older than {days} days")

    if days < 0:
        error_msg = f"days must be non-negative, got {days}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        with get_session() as conn:
            # Calculate cutoff datetime
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            # Delete old jobs (cascade deletes comparison_results)
            cursor = conn.execute("DELETE FROM analysis_jobs WHERE created_at < ?", (cutoff_str,))

            deleted_count = cursor.rowcount
            logger.info(
                f"Successfully deleted {deleted_count} jobs older than {days} days "
                f"(cutoff: {cutoff_str})"
            )

            return deleted_count

    except ValueError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error cleaning up old jobs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error cleaning up old jobs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def job_exists(job_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
    """
    Check if a job exists in the database.

    Args:
        job_id: Job identifier to check
        conn: Existing database connection (optional, creates new if None)

    Returns:
        True if job exists, False otherwise

    Example:
        >>> if job_exists('job_20251112_143022'):
        ...     print("Job found!")
        Job found!
    """
    logger.debug(f"Checking if job exists: {job_id}")

    try:
        if conn is not None:
            # Use provided connection
            cursor = conn.execute("SELECT 1 FROM analysis_jobs WHERE id = ?", (job_id,))
            exists = cursor.fetchone() is not None
        else:
            # Create new connection
            with get_session() as conn:
                cursor = conn.execute("SELECT 1 FROM analysis_jobs WHERE id = ?", (job_id,))
                exists = cursor.fetchone() is not None

        logger.debug(f"Job {job_id} exists: {exists}")
        return exists

    except sqlite3.Error as e:
        logger.error(f"Database error checking job existence: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking job existence: {e}")
        return False


# =============================================================================
# Comparison Results Functions
# =============================================================================


def save_comparison_result(job_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a single comparison result to the database.

    Args:
        job_id: Job identifier
        result: Dictionary with keys:
            - file1_name: str (required)
            - file2_name: str (required)
            - token_similarity: float (required, 0.0-1.0)
            - ast_similarity: float (required, 0.0-1.0)
            - hash_similarity: float (required, 0.0-1.0)
            - is_plagiarized: bool (required)
            - confidence_score: float (required, 0.0-1.0)

    Returns:
        Dictionary with inserted result including auto-generated id

    Raises:
        JobNotFoundError: If job_id is not found
        InvalidResultDataError: If result data is invalid or missing fields
        DatabaseOperationError: If database operation fails

    Example:
        >>> result = {
        ...     'file1_name': 'student1.py',
        ...     'file2_name': 'student2.py',
        ...     'token_similarity': 0.85,
        ...     'ast_similarity': 0.92,
        ...     'hash_similarity': 0.78,
        ...     'is_plagiarized': True,
        ...     'confidence_score': 0.87
        ... }
        >>> saved = save_comparison_result('job_20251112_143022', result)
        >>> print(f"Saved result with ID: {saved['id']}")
    """
    logger.debug(
        f"Saving comparison result for job {job_id}: "
        f"{result.get('file1_name')} vs {result.get('file2_name')}"
    )

    # Validate result data
    _validate_result_data(result)

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Insert result
            cursor = conn.execute(
                """
                INSERT INTO comparison_results (
                    job_id, file1_name, file2_name,
                    token_similarity, ast_similarity, hash_similarity,
                    is_plagiarized, confidence_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    result["file1_name"],
                    result["file2_name"],
                    result["token_similarity"],
                    result["ast_similarity"],
                    result["hash_similarity"],
                    1 if result["is_plagiarized"] else 0,
                    result["confidence_score"],
                ),
            )

            # Get the inserted result with its ID
            result_id = cursor.lastrowid
            cursor = conn.execute("SELECT * FROM comparison_results WHERE id = ?", (result_id,))
            row = cursor.fetchone()

            if row is None:
                raise DatabaseOperationError("Failed to retrieve newly inserted result")

            comparison_result = row_to_comparison_result(row)
            logger.debug(f"Successfully saved comparison result with ID {result_id}")

            return comparison_result.to_dict()

    except (JobNotFoundError, InvalidResultDataError):
        raise
    except sqlite3.IntegrityError as e:
        error_msg = f"Integrity constraint violation saving result: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except sqlite3.Error as e:
        error_msg = f"Database error saving comparison result: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error saving comparison result: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def save_batch_results(job_id: str, results: List[Dict[str, Any]]) -> None:
    """
    Save multiple comparison results atomically.

    This function uses a transaction to ensure all results are saved or none.
    If any result is invalid or the operation fails, no results are saved.

    Args:
        job_id: Job identifier
        results: List of result dictionaries (same format as save_comparison_result)

    Raises:
        JobNotFoundError: If job_id is not found
        InvalidResultDataError: If any result data is invalid
        DatabaseOperationError: If transaction fails (all or nothing)

    Example:
        >>> results = [
        ...     {
        ...         'file1_name': 'student1.py',
        ...         'file2_name': 'student2.py',
        ...         'token_similarity': 0.85,
        ...         'ast_similarity': 0.92,
        ...         'hash_similarity': 0.78,
        ...         'is_plagiarized': True,
        ...         'confidence_score': 0.87
        ...     },
        ...     # ... more results
        ... ]
        >>> save_batch_results('job_20251112_143022', results)
    """
    logger.info(f"Saving batch of {len(results)} results for job {job_id}")

    # Validate all results first (fail fast before database operations)
    for i, result in enumerate(results):
        try:
            _validate_result_data(result)
        except InvalidResultDataError as e:
            error_msg = f"Invalid result at index {i}: {e}"
            logger.error(error_msg)
            raise InvalidResultDataError(error_msg) from e

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Insert all results in single transaction
            for result in results:
                conn.execute(
                    """
                    INSERT INTO comparison_results (
                        job_id, file1_name, file2_name,
                        token_similarity, ast_similarity, hash_similarity,
                        is_plagiarized, confidence_score
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        result["file1_name"],
                        result["file2_name"],
                        result["token_similarity"],
                        result["ast_similarity"],
                        result["hash_similarity"],
                        1 if result["is_plagiarized"] else 0,
                        result["confidence_score"],
                    ),
                )

            logger.info(f"Successfully saved batch of {len(results)} results for job {job_id}")

    except (JobNotFoundError, InvalidResultDataError):
        raise
    except sqlite3.IntegrityError as e:
        error_msg = f"Integrity constraint violation in batch save: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except sqlite3.Error as e:
        error_msg = f"Database error saving batch results: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error saving batch results: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def get_job_results(job_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all comparison results for a job.

    Args:
        job_id: Job identifier

    Returns:
        List of comparison result dictionaries, ordered by created_at

    Raises:
        JobNotFoundError: If job_id is not found
        DatabaseOperationError: If database operation fails

    Example:
        >>> results = get_job_results('job_20251112_143022')
        >>> plagiarized = [r for r in results if r['is_plagiarized']]
        >>> print(f"Found {len(plagiarized)} plagiarized pairs")
    """
    logger.debug(f"Getting results for job {job_id}")

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Get all results for job
            cursor = conn.execute(
                """
                SELECT * FROM comparison_results
                WHERE job_id = ?
                ORDER BY created_at
                """,
                (job_id,),
            )

            results = []
            for row in cursor.fetchall():
                result = row_to_comparison_result(row)
                results.append(result.to_dict())

            logger.debug(f"Retrieved {len(results)} results for job {job_id}")
            return results

    except JobNotFoundError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error getting job results: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error getting job results: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def get_plagiarism_count(job_id: str) -> int:
    """
    Count the number of plagiarized pairs in a job.

    Args:
        job_id: Job identifier

    Returns:
        Number of pairs flagged as plagiarized

    Raises:
        JobNotFoundError: If job_id is not found
        DatabaseOperationError: If database operation fails

    Example:
        >>> count = get_plagiarism_count('job_20251112_143022')
        >>> print(f"Found {count} plagiarized pairs")
        Found 3 plagiarized pairs
    """
    logger.debug(f"Counting plagiarized pairs for job {job_id}")

    try:
        with get_session() as conn:
            # Verify job exists
            if not job_exists(job_id, conn):
                error_msg = f"Job not found: {job_id}"
                logger.error(error_msg)
                raise JobNotFoundError(error_msg)

            # Count plagiarized results
            cursor = conn.execute(
                """
                SELECT COUNT(*) as count
                FROM comparison_results
                WHERE job_id = ? AND is_plagiarized = 1
                """,
                (job_id,),
            )

            row = cursor.fetchone()
            count = row["count"] if row else 0

            logger.debug(f"Job {job_id} has {count} plagiarized pairs")
            return count

    except JobNotFoundError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Database error counting plagiarized pairs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error counting plagiarized pairs: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


# =============================================================================
# Configuration Functions
# =============================================================================


def get_configuration(key: str) -> Optional[str]:
    """
    Retrieve a configuration value by key.

    Args:
        key: Configuration key

    Returns:
        Configuration value as string, or None if not found

    Raises:
        DatabaseOperationError: If database operation fails

    Example:
        >>> threshold = get_configuration('similarity_threshold')
        >>> if threshold:
        ...     print(f"Threshold: {threshold}")
        Threshold: 0.80
    """
    logger.debug(f"Getting configuration for key: {key}")

    try:
        with get_session() as conn:
            cursor = conn.execute("SELECT value FROM configuration WHERE key = ?", (key,))

            row = cursor.fetchone()
            value = row["value"] if row else None

            logger.debug(f"Configuration {key}: {value}")
            return value

    except sqlite3.Error as e:
        error_msg = f"Database error getting configuration {key}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error getting configuration {key}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def set_configuration(key: str, value: str) -> None:
    """
    Store or update a configuration value.

    This function uses INSERT OR REPLACE to handle both new and existing keys.
    The updated_at timestamp is automatically set to the current time.

    Args:
        key: Configuration key
        value: Configuration value (will be stored as string)

    Raises:
        DatabaseOperationError: If database operation fails

    Note:
        For complex values (dicts, lists), JSON serialize before passing.

    Example:
        >>> set_configuration('similarity_threshold', '0.85')
        >>> # Threshold updated to 0.85
        >>>
        >>> import json
        >>> set_configuration('detector_weights', json.dumps({'token': 1.0, 'ast': 2.0}))
    """
    logger.info(f"Setting configuration {key} = {value}")

    try:
        with get_session() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO configuration (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (key, value),
            )

            logger.info(f"Successfully set configuration {key}")

    except sqlite3.Error as e:
        error_msg = f"Database error setting configuration {key}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error setting configuration {key}: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


def get_all_configuration() -> Dict[str, str]:
    """
    Retrieve all configuration key-value pairs.

    Returns:
        Dictionary mapping configuration keys to values

    Raises:
        DatabaseOperationError: If database operation fails

    Example:
        >>> config = get_all_configuration()
        >>> for key, value in config.items():
        ...     print(f"{key}: {value}")
        similarity_threshold: 0.80
        confidence_threshold: 0.75
        max_file_size_mb: 16
    """
    logger.debug("Getting all configuration values")

    try:
        with get_session() as conn:
            cursor = conn.execute("SELECT key, value FROM configuration")

            config = {}
            for row in cursor.fetchall():
                config[row["key"]] = row["value"]

            logger.debug(f"Retrieved {len(config)} configuration values")
            return config

    except sqlite3.Error as e:
        error_msg = f"Database error getting all configuration: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error getting all configuration: {e}"
        logger.error(error_msg)
        raise DatabaseOperationError(error_msg) from e


# =============================================================================
# Helper Functions
# =============================================================================


def _validate_result_data(result: Dict[str, Any]) -> None:
    """
    Validate comparison result data.

    Args:
        result: Result dictionary to validate

    Raises:
        InvalidResultDataError: If result data is invalid or missing fields

    Note:
        This is an internal helper function for result validation.
    """
    # Required fields
    required_fields = {
        "file1_name": str,
        "file2_name": str,
        "token_similarity": (int, float),
        "ast_similarity": (int, float),
        "hash_similarity": (int, float),
        "is_plagiarized": bool,
        "confidence_score": (int, float),
    }

    # Check for missing fields
    missing = [field for field in required_fields if field not in result]
    if missing:
        raise InvalidResultDataError(f"Missing required fields: {', '.join(missing)}")

    # Check field types
    for field, expected_type in required_fields.items():
        value = result[field]
        if not isinstance(value, expected_type):
            raise InvalidResultDataError(
                f"Field '{field}' must be {expected_type}, got {type(value)}"
            )

    # Validate similarity scores are in range [0.0, 1.0]
    similarity_fields = [
        "token_similarity",
        "ast_similarity",
        "hash_similarity",
        "confidence_score",
    ]
    for field in similarity_fields:
        value = result[field]
        if not 0.0 <= value <= 1.0:
            raise InvalidResultDataError(
                f"Field '{field}' must be between 0.0 and 1.0, got {value}"
            )

    # Validate file names are not empty
    if not result["file1_name"].strip():
        raise InvalidResultDataError("file1_name cannot be empty")
    if not result["file2_name"].strip():
        raise InvalidResultDataError("file2_name cannot be empty")


# =============================================================================
# Module Initialization
# =============================================================================

logger.debug("Database operations module initialized")
