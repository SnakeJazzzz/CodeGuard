"""
Shared Test Fixtures for CodeGuard Test Suite

This module provides comprehensive shared fixtures for all tests across the
CodeGuard plagiarism detection system. Fixtures are organized by scope and
purpose to optimize test performance and maintainability.

Fixture Categories:
    - Database fixtures: In-memory SQLite sessions
    - Sample data fixtures: Test code pairs and files
    - Temporary directory fixtures: File system test environments
    - Mock data fixtures: Pre-populated test jobs and results
    - Configuration fixtures: Test configuration values
    - Utility fixtures: Log capture and helper functions

Usage:
    Fixtures are automatically available to all test files. Simply add the
    fixture name as a parameter to your test function:

    def test_something(db_session, sample_code_pairs):
        # Use fixtures directly
        assert sample_code_pairs['identical'] is not None
"""

import pytest
import tempfile
import shutil
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Generator, Any
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import init_db, get_db_connection, get_session, DB_PATH, SCHEMA_PATH
from src.database.operations import create_analysis_job, save_comparison_result
from src.database.models import AnalysisJob, ComparisonResult

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def db_session() -> Generator[sqlite3.Connection, None, None]:
    """
    Provide in-memory SQLite database session for tests.

    Scope: function - Fresh database for each test
    Yields: sqlite3.Connection - Database connection
    Cleanup: Closes connection and removes temp files

    This fixture creates a fresh in-memory database for each test,
    ensuring complete test isolation. The database schema is initialized
    from schema.sql and cleaned up after the test completes.

    Usage:
        def test_database_operation(db_session):
            cursor = db_session.execute("SELECT * FROM analysis_jobs")
            assert cursor is not None

    Notes:
        - Uses in-memory database (:memory:) for speed
        - Schema initialized from src/database/schema.sql
        - Foreign key constraints enabled
        - Row factory set for dict-like access
    """
    # Create in-memory database connection
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    try:
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row

        # Read and execute schema
        if SCHEMA_PATH.exists():
            schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
            conn.executescript(schema_sql)
            conn.commit()
        else:
            logger.warning(f"Schema file not found at {SCHEMA_PATH}, creating minimal schema")
            # Minimal fallback schema if file not found
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'running', 'completed', 'failed')),
                    file_count INTEGER NOT NULL,
                    pair_count INTEGER NOT NULL,
                    results_path TEXT
                );

                CREATE TABLE IF NOT EXISTS comparison_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    file1_name TEXT NOT NULL,
                    file2_name TEXT NOT NULL,
                    token_similarity REAL NOT NULL,
                    ast_similarity REAL NOT NULL,
                    hash_similarity REAL NOT NULL,
                    is_plagiarized INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES analysis_jobs (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
            conn.commit()

        logger.debug("In-memory test database initialized")

        # Yield connection to test
        yield conn

    finally:
        # Cleanup: close connection
        conn.close()
        logger.debug("Test database connection closed")


# =============================================================================
# Sample Code Data Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def sample_code_pairs() -> Dict[str, Dict[str, Any]]:
    """
    Provide sample Python code pairs for testing detectors.

    Scope: session - Same data for all tests (immutable)
    Returns: Dict with various code pair scenarios

    Dictionary structure contains test cases for different plagiarism scenarios:
    - identical: Exact copies (100% similarity)
    - renamed: Variable/function names changed (high structural similarity)
    - different: Completely different code (low similarity)
    - similar_structure: Same logic, different variables (high structural)
    - with_comments: Code with/without comments (should ignore comments)
    - partial_copy: Partial plagiarism (moderate similarity)
    - whitespace_diff: Only whitespace differences (should be identical)

    Usage:
        def test_identical_code(sample_code_pairs):
            code1 = sample_code_pairs['identical']['code1']
            code2 = sample_code_pairs['identical']['code2']
            assert code1 == code2

    Returns:
        Dictionary mapping scenario names to code pair dictionaries with:
        - code1: First code string
        - code2: Second code string
        - expected_similarity: Expected similarity score (0.0-1.0)
        - description: Description of the test case
    """
    return {
        "identical": {
            "code1": """def factorial(n):
    '''Calculate factorial of n.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)
""",
            "code2": """def factorial(n):
    '''Calculate factorial of n.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)
""",
            "expected_similarity": 1.0,
            "description": "Exact identical code",
        },
        "renamed": {
            "code1": """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
""",
            "code2": """def compute_total(values):
    result = 0
    for val in values:
        result += val
    return result
""",
            "expected_similarity": 0.8,
            "description": "Same structure, renamed variables and functions",
        },
        "different": {
            "code1": """def add(a, b):
    return a + b
""",
            "code2": """def multiply(x, y):
    result = x
    for _ in range(y - 1):
        result += x
    return result
""",
            "expected_similarity": 0.2,
            "description": "Completely different algorithms",
        },
        "similar_structure": {
            "code1": """for i in range(10):
    print(i)
""",
            "code2": """for j in range(10):
    print(j)
""",
            "expected_similarity": 0.9,
            "description": "Identical structure with variable renaming",
        },
        "with_comments": {
            "code1": """# This is a comment
# Another comment
def foo():
    '''Docstring here'''
    # Inline comment
    pass
""",
            "code2": """def foo():
    '''Docstring here'''
    pass
""",
            "expected_similarity": 1.0,
            "description": "Same code with/without comments",
        },
        "partial_copy": {
            "code1": """def process_data(data):
    cleaned = []
    for item in data:
        if item is not None:
            cleaned.append(item.strip())
    return cleaned

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        f.write('\\n'.join(data))
""",
            "code2": """def process_data(data):
    cleaned = []
    for item in data:
        if item is not None:
            cleaned.append(item.strip())
    return cleaned

def different_function(x):
    return x * 2
""",
            "expected_similarity": 0.5,
            "description": "Partial code copying (one function identical, one different)",
        },
        "whitespace_diff": {
            "code1": """def greet(name):
    return f"Hello, {name}!"
""",
            "code2": """def greet(name):


    return f"Hello, {name}!"
""",
            "expected_similarity": 1.0,
            "description": "Only whitespace differences",
        },
        "empty": {
            "code1": "",
            "code2": "",
            "expected_similarity": 1.0,
            "description": "Both empty strings",
        },
        "one_empty": {
            "code1": "def foo(): pass",
            "code2": "",
            "expected_similarity": 0.0,
            "description": "One empty, one with code",
        },
    }


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def temp_upload_dir() -> Generator[Path, None, None]:
    """
    Provide temporary directory for file upload tests.

    Scope: function - Fresh directory for each test
    Yields: pathlib.Path to temporary directory
    Cleanup: Removes directory and all contents after test

    Creates a temporary directory that is automatically cleaned up after
    the test completes, even if the test fails. Useful for testing file
    operations without affecting the real file system.

    Usage:
        def test_file_upload(temp_upload_dir):
            file_path = temp_upload_dir / "test.py"
            file_path.write_text("print('hello')")
            assert file_path.exists()

    Notes:
        - Directory is created in system temp location
        - Automatically removed after test (including all contents)
        - Safe for parallel test execution (unique per test)
    """
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="codeguard_test_"))

    try:
        logger.debug(f"Created temporary directory: {temp_dir}")
        yield temp_dir

    finally:
        # Cleanup: remove directory and all contents
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.debug(f"Removed temporary directory: {temp_dir}")


# =============================================================================
# Mock Data Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def mock_analysis_job(db_session: sqlite3.Connection) -> Dict[str, Any]:
    """
    Provide pre-populated analysis job for testing.

    Scope: function - Fresh job for each test
    Requires: db_session fixture
    Returns: Dict with job details

    Creates a complete analysis job with multiple comparison results,
    including both plagiarized and clean pairs. This fixture is useful
    for testing job retrieval, statistics, and result processing.

    Job structure:
    - Job ID: 'test-job-{timestamp}'
    - Status: 'completed'
    - File count: 5
    - Pair count: 10
    - Comparison results: 6 pairs (3 plagiarized, 3 clean)

    Usage:
        def test_job_summary(mock_analysis_job, db_session):
            job_id = mock_analysis_job['id']
            cursor = db_session.execute(
                "SELECT * FROM analysis_jobs WHERE id = ?", (job_id,)
            )
            assert cursor.fetchone() is not None

    Returns:
        Dictionary containing:
        - id: Job identifier
        - status: Job status
        - file_count: Number of files
        - pair_count: Number of pairs
        - created_at: Creation timestamp
        - results: List of comparison results
    """
    # Generate unique job ID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    job_id = f"test-job-{timestamp}"

    # Create analysis job in database
    db_session.execute(
        """
        INSERT INTO analysis_jobs (id, status, file_count, pair_count, results_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (job_id, "completed", 5, 10, f"data/results/analysis_{job_id}.json"),
    )
    db_session.commit()

    # Create sample comparison results
    results = [
        # Plagiarized pairs
        {
            "job_id": job_id,
            "file1_name": "student1.py",
            "file2_name": "student2.py",
            "token_similarity": 0.95,
            "ast_similarity": 0.98,
            "hash_similarity": 0.92,
            "is_plagiarized": True,
            "confidence_score": 0.95,
        },
        {
            "job_id": job_id,
            "file1_name": "student1.py",
            "file2_name": "student3.py",
            "token_similarity": 0.88,
            "ast_similarity": 0.91,
            "hash_similarity": 0.85,
            "is_plagiarized": True,
            "confidence_score": 0.88,
        },
        {
            "job_id": job_id,
            "file1_name": "student2.py",
            "file2_name": "student3.py",
            "token_similarity": 0.90,
            "ast_similarity": 0.94,
            "hash_similarity": 0.87,
            "is_plagiarized": True,
            "confidence_score": 0.90,
        },
        # Clean pairs
        {
            "job_id": job_id,
            "file1_name": "student1.py",
            "file2_name": "student4.py",
            "token_similarity": 0.25,
            "ast_similarity": 0.30,
            "hash_similarity": 0.20,
            "is_plagiarized": False,
            "confidence_score": 0.25,
        },
        {
            "job_id": job_id,
            "file1_name": "student1.py",
            "file2_name": "student5.py",
            "token_similarity": 0.15,
            "ast_similarity": 0.18,
            "hash_similarity": 0.12,
            "is_plagiarized": False,
            "confidence_score": 0.15,
        },
        {
            "job_id": job_id,
            "file1_name": "student4.py",
            "file2_name": "student5.py",
            "token_similarity": 0.22,
            "ast_similarity": 0.25,
            "hash_similarity": 0.19,
            "is_plagiarized": False,
            "confidence_score": 0.22,
        },
    ]

    # Insert results into database
    for result in results:
        db_session.execute(
            """
            INSERT INTO comparison_results (
                job_id, file1_name, file2_name,
                token_similarity, ast_similarity, hash_similarity,
                is_plagiarized, confidence_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["job_id"],
                result["file1_name"],
                result["file2_name"],
                result["token_similarity"],
                result["ast_similarity"],
                result["hash_similarity"],
                1 if result["is_plagiarized"] else 0,
                result["confidence_score"],
            ),
        )
    db_session.commit()

    logger.debug(f"Created mock analysis job: {job_id} with {len(results)} results")

    # Return job details
    return {
        "id": job_id,
        "status": "completed",
        "file_count": 5,
        "pair_count": 10,
        "created_at": datetime.utcnow().isoformat(),
        "results_path": f"data/results/analysis_{job_id}.json",
        "results": results,
    }


# =============================================================================
# Sample File Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def sample_python_files(temp_upload_dir: Path) -> List[Path]:
    """
    Create sample Python files in temporary directory.

    Scope: function - Fresh files for each test
    Requires: temp_upload_dir fixture
    Returns: List of Path objects to created files

    Creates realistic Python code files for testing file upload,
    processing, and analysis workflows. Files include various
    complexity levels and plagiarism scenarios.

    Created files:
    - student1.py: Factorial implementation (recursive)
    - student2.py: Factorial copy with renamed variables
    - student3.py: Fibonacci implementation (different algorithm)
    - student4.py: Sorting implementation
    - student5.py: Empty file (edge case)

    Usage:
        def test_file_processing(sample_python_files):
            assert len(sample_python_files) == 5
            for file_path in sample_python_files:
                assert file_path.exists()
                assert file_path.suffix == '.py'

    Returns:
        List of pathlib.Path objects to created .py files
    """
    files = []

    # File 1: Factorial implementation
    file1 = temp_upload_dir / "student1.py"
    file1.write_text(
        """def factorial(n):
    '''Calculate factorial of n using recursion.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    result = factorial(5)
    print(f"Factorial of 5 is {result}")

if __name__ == "__main__":
    main()
"""
    )
    files.append(file1)

    # File 2: Factorial copy with renamed variables (plagiarism)
    file2 = temp_upload_dir / "student2.py"
    file2.write_text(
        """def calc_factorial(num):
    '''Calculate factorial using recursion.'''
    if num <= 1:
        return 1
    return num * calc_factorial(num - 1)

def run():
    answer = calc_factorial(5)
    print(f"Factorial of 5 is {answer}")

if __name__ == "__main__":
    run()
"""
    )
    files.append(file2)

    # File 3: Fibonacci implementation (different)
    file3 = temp_upload_dir / "student3.py"
    file3.write_text(
        """def fibonacci(n):
    '''Calculate nth Fibonacci number.'''
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

def main():
    result = fibonacci(10)
    print(f"Fibonacci(10) = {result}")

if __name__ == "__main__":
    main()
"""
    )
    files.append(file3)

    # File 4: Sorting implementation
    file4 = temp_upload_dir / "student4.py"
    file4.write_text(
        """def bubble_sort(arr):
    '''Sort array using bubble sort.'''
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def main():
    data = [64, 34, 25, 12, 22, 11, 90]
    sorted_data = bubble_sort(data)
    print(f"Sorted: {sorted_data}")

if __name__ == "__main__":
    main()
"""
    )
    files.append(file4)

    # File 5: Empty file (edge case)
    file5 = temp_upload_dir / "student5.py"
    file5.write_text("")
    files.append(file5)

    logger.debug(f"Created {len(files)} sample Python files in {temp_upload_dir}")

    return files


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    Provide test configuration values.

    Scope: session - Same configuration for all tests
    Returns: Dict with test configuration

    Provides standardized configuration values for testing detector
    thresholds, voting weights, file limits, and other system parameters.

    Configuration includes:
    - Detector thresholds (token, AST, hash)
    - Voting system weights
    - Decision threshold
    - File size limits
    - Allowed file extensions
    - Timeout values

    Usage:
        def test_threshold_validation(test_config):
            assert 0.0 <= test_config['token_threshold'] <= 1.0
            assert test_config['max_file_size'] > 0

    Returns:
        Dictionary with configuration values:
        {
            'token_threshold': 0.7,
            'ast_threshold': 0.8,
            'hash_threshold': 0.6,
            'token_weight': 1.0,
            'ast_weight': 2.0,
            'hash_weight': 1.5,
            'decision_threshold': 0.5,
            'max_file_size': 16 * 1024 * 1024,  # 16MB
            'allowed_extensions': ['.py'],
            'min_files': 2,
            'max_files': 100,
            'analysis_timeout': 300  # 5 minutes
        }
    """
    return {
        # Detector thresholds (0.0-1.0)
        "token_threshold": 0.7,
        "ast_threshold": 0.8,
        "hash_threshold": 0.6,
        # Voting weights
        "token_weight": 1.0,
        "ast_weight": 2.0,
        "hash_weight": 1.5,
        # Decision threshold
        "decision_threshold": 0.5,
        # File limits
        "max_file_size": 16 * 1024 * 1024,  # 16MB in bytes
        "allowed_extensions": [".py"],
        "min_files": 2,
        "max_files": 100,
        # Performance limits
        "analysis_timeout": 300,  # 5 minutes in seconds
        # K-gram settings (for hash detector)
        "kgram_size": 5,
        "window_size": 4,
    }


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def capture_logs() -> Generator[List[logging.LogRecord], None, None]:
    """
    Capture log messages during test execution.

    Scope: function - Fresh log capture for each test
    Yields: List that collects log records

    Captures all log messages generated during test execution,
    allowing tests to verify logging behavior and debug output.

    Usage:
        def test_logging(capture_logs):
            logger = logging.getLogger('test')
            logger.error('Test error message')

            # Verify log was captured
            assert len(capture_logs) == 1
            assert capture_logs[0].levelname == 'ERROR'
            assert 'Test error' in capture_logs[0].message

    Notes:
        - Captures all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - Log records are LogRecord objects with attributes:
          - levelname: Log level as string
          - message: Log message
          - name: Logger name
          - created: Timestamp
    """
    # Create custom handler to capture logs
    log_records = []

    class ListHandler(logging.Handler):
        def emit(self, record):
            log_records.append(record)

    # Add handler to root logger
    handler = ListHandler()
    handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        logger.debug("Log capture started")
        yield log_records

    finally:
        # Cleanup: remove handler
        root_logger.removeHandler(handler)
        logger.debug("Log capture stopped")


# =============================================================================
# Session-Level Setup/Teardown
# =============================================================================


def pytest_configure(config):
    """
    Pytest hook called before test collection.

    Performs one-time setup for the entire test session:
    - Configures logging
    - Sets up test environment
    - Registers custom markers
    """
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Test session starting")
    logger.info(f"Working directory: {Path.cwd()}")


def pytest_unconfigure(config):
    """
    Pytest hook called after all tests complete.

    Performs cleanup after the entire test session:
    - Logs test summary
    - Cleans up any remaining resources
    """
    logger.info("Test session completed")
