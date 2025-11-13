"""
Database Models Module

This module defines SQLAlchemy ORM models for the CodeGuard plagiarism
detection system. All models map to the database schema defined in schema.sql.

Models:
    AnalysisJob: Represents a batch analysis job
    ComparisonResult: Represents a single file pair comparison
    Configuration: Stores system configuration key-value pairs

Features:
    - Complete type hints for all attributes
    - Bidirectional relationships with cascade rules
    - to_dict() and from_dict() helper methods
    - Property validators for data integrity
    - Comprehensive docstrings and examples

Example:
    >>> from database.models import AnalysisJob, ComparisonResult
    >>> from database.connection import get_session
    >>>
    >>> # Create a new job
    >>> job = AnalysisJob(
    ...     id='job_20251112_143022',
    ...     status='pending',
    ...     file_count=10,
    ...     pair_count=45
    ... )
    >>>
    >>> # Convert to dictionary
    >>> job_dict = job.to_dict()
    >>> print(job_dict['status'])  # 'pending'
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import logging

# Configure module logger
logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

# Valid status values for AnalysisJob (must match schema.sql CHECK constraint)
VALID_STATUSES = {'pending', 'running', 'completed', 'failed'}

# Status aliases for backward compatibility
# 'processing' is an alias for 'running'
STATUS_ALIASES = {
    'processing': 'running'
}

# =============================================================================
# Model Classes
# =============================================================================

class AnalysisJob:
    """
    Represents a batch plagiarism analysis job.

    Each job corresponds to a single batch upload of Python files.
    The job tracks metadata about the analysis including status,
    file count, and results location.

    Attributes:
        id: Unique job identifier (typically timestamp-based)
        created_at: Job creation timestamp (UTC)
        status: Current job status ('pending', 'running', 'completed', 'failed')
        file_count: Number of files in the analysis
        pair_count: Number of pairwise comparisons (N*(N-1)/2)
        results_path: Path to detailed JSON results file (nullable)

    Relationships:
        comparison_results: List of ComparisonResult objects for this job

    Example:
        >>> job = AnalysisJob(
        ...     id='job_20251112_143022',
        ...     status='pending',
        ...     file_count=10,
        ...     pair_count=45
        ... )
        >>> job.status = 'processing'
        >>> job.results_path = 'data/results/analysis_job_20251112_143022.json'
    """

    def __init__(
        self,
        id: str,
        status: str,
        file_count: int,
        pair_count: int,
        created_at: Optional[datetime] = None,
        results_path: Optional[str] = None
    ):
        """
        Initialize an AnalysisJob instance.

        Args:
            id: Unique job identifier
            status: Job status (must be one of VALID_STATUSES)
            file_count: Number of files analyzed
            pair_count: Number of pairwise comparisons
            created_at: Job creation timestamp (defaults to now)
            results_path: Path to results JSON file (optional)

        Raises:
            ValueError: If status is invalid or counts are negative
        """
        self.id = id
        self.status = status  # Validated by property setter
        self.file_count = file_count
        self.pair_count = pair_count
        self.created_at = created_at or datetime.utcnow()
        self.results_path = results_path

        # Validate counts
        if self.file_count < 0:
            raise ValueError(f"file_count must be non-negative, got {file_count}")
        if self.pair_count < 0:
            raise ValueError(f"pair_count must be non-negative, got {pair_count}")

        # Placeholder for relationship (populated by database operations)
        self._comparison_results: List['ComparisonResult'] = []

    @property
    def status(self) -> str:
        """Get the current job status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """
        Set the job status with validation.

        Args:
            value: New status value

        Raises:
            ValueError: If status is not in VALID_STATUSES
        """
        # Handle deprecated status aliases
        normalized_value = STATUS_ALIASES.get(value, value)

        if normalized_value not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{value}'. Must be one of: {', '.join(VALID_STATUSES)}"
            )
        self._status = normalized_value

    @property
    def comparison_results(self) -> List['ComparisonResult']:
        """Get the list of comparison results for this job."""
        return self._comparison_results

    @comparison_results.setter
    def comparison_results(self, value: List['ComparisonResult']) -> None:
        """Set the comparison results list."""
        self._comparison_results = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the job to a dictionary representation.

        Returns:
            Dictionary containing all job attributes

        Example:
            >>> job = AnalysisJob(id='job1', status='pending', file_count=5, pair_count=10)
            >>> data = job.to_dict()
            >>> print(data['status'])  # 'pending'
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'file_count': self.file_count,
            'pair_count': self.pair_count,
            'results_path': self.results_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisJob':
        """
        Create an AnalysisJob instance from a dictionary.

        Args:
            data: Dictionary containing job attributes

        Returns:
            New AnalysisJob instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If data is invalid

        Example:
            >>> data = {
            ...     'id': 'job1',
            ...     'status': 'pending',
            ...     'file_count': 5,
            ...     'pair_count': 10
            ... }
            >>> job = AnalysisJob.from_dict(data)
        """
        # Parse datetime if provided as string
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data['id'],
            status=data['status'],
            file_count=data['file_count'],
            pair_count=data['pair_count'],
            created_at=created_at,
            results_path=data.get('results_path')
        )

    def __repr__(self) -> str:
        """Return a string representation of the job for debugging."""
        return (
            f"AnalysisJob(id={self.id!r}, status={self.status!r}, "
            f"file_count={self.file_count}, pair_count={self.pair_count})"
        )

    def __eq__(self, other: Any) -> bool:
        """Compare jobs by ID."""
        if not isinstance(other, AnalysisJob):
            return False
        return self.id == other.id


class ComparisonResult:
    """
    Represents a single file pair comparison result.

    Each result stores the similarity scores from all three detectors
    (token, AST, hash) along with the final plagiarism verdict and
    confidence score from the voting system.

    Attributes:
        id: Auto-increment primary key
        job_id: Foreign key to AnalysisJob
        file1_name: Name of the first file
        file2_name: Name of the second file
        token_similarity: Token detector similarity score (0.0-1.0)
        ast_similarity: AST detector similarity score (0.0-1.0)
        hash_similarity: Hash detector similarity score (0.0-1.0)
        is_plagiarized: Final plagiarism verdict (True/False)
        confidence_score: Voting system confidence (0.0-1.0)
        created_at: Comparison timestamp (UTC)

    Example:
        >>> result = ComparisonResult(
        ...     job_id='job_20251112_143022',
        ...     file1_name='student1.py',
        ...     file2_name='student2.py',
        ...     token_similarity=0.85,
        ...     ast_similarity=0.92,
        ...     hash_similarity=0.78,
        ...     is_plagiarized=True,
        ...     confidence_score=0.87
        ... )
    """

    def __init__(
        self,
        job_id: str,
        file1_name: str,
        file2_name: str,
        token_similarity: float,
        ast_similarity: float,
        hash_similarity: float,
        is_plagiarized: bool,
        confidence_score: float,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a ComparisonResult instance.

        Args:
            job_id: ID of the parent analysis job
            file1_name: Name of the first file
            file2_name: Name of the second file
            token_similarity: Token similarity score (0.0-1.0)
            ast_similarity: AST similarity score (0.0-1.0)
            hash_similarity: Hash similarity score (0.0-1.0)
            is_plagiarized: Plagiarism verdict
            confidence_score: Confidence in verdict (0.0-1.0)
            id: Primary key (auto-assigned by database)
            created_at: Comparison timestamp (defaults to now)

        Raises:
            ValueError: If similarity scores are out of range
        """
        self.id = id
        self.job_id = job_id
        self.file1_name = file1_name
        self.file2_name = file2_name
        self.token_similarity = token_similarity
        self.ast_similarity = ast_similarity
        self.hash_similarity = hash_similarity
        self.is_plagiarized = is_plagiarized
        self.confidence_score = confidence_score
        self.created_at = created_at or datetime.utcnow()

        # Validate similarity scores
        self._validate_score('token_similarity', token_similarity)
        self._validate_score('ast_similarity', ast_similarity)
        self._validate_score('hash_similarity', hash_similarity)
        self._validate_score('confidence_score', confidence_score)

    @staticmethod
    def _validate_score(name: str, value: float) -> None:
        """
        Validate that a similarity score is in the valid range.

        Args:
            name: Name of the score field (for error messages)
            value: Score value to validate

        Raises:
            ValueError: If score is not in [0.0, 1.0] range
        """
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be between 0.0 and 1.0, got {value}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a dictionary representation.

        Returns:
            Dictionary containing all result attributes

        Example:
            >>> result = ComparisonResult(...)
            >>> data = result.to_dict()
            >>> print(data['is_plagiarized'])  # True or False
        """
        return {
            'id': self.id,
            'job_id': self.job_id,
            'file1_name': self.file1_name,
            'file2_name': self.file2_name,
            'token_similarity': self.token_similarity,
            'ast_similarity': self.ast_similarity,
            'hash_similarity': self.hash_similarity,
            'is_plagiarized': self.is_plagiarized,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonResult':
        """
        Create a ComparisonResult instance from a dictionary.

        Args:
            data: Dictionary containing result attributes

        Returns:
            New ComparisonResult instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If data is invalid

        Example:
            >>> data = {
            ...     'job_id': 'job1',
            ...     'file1_name': 'a.py',
            ...     'file2_name': 'b.py',
            ...     'token_similarity': 0.85,
            ...     'ast_similarity': 0.92,
            ...     'hash_similarity': 0.78,
            ...     'is_plagiarized': True,
            ...     'confidence_score': 0.87
            ... }
            >>> result = ComparisonResult.from_dict(data)
        """
        # Parse datetime if provided as string
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            id=data.get('id'),
            job_id=data['job_id'],
            file1_name=data['file1_name'],
            file2_name=data['file2_name'],
            token_similarity=data['token_similarity'],
            ast_similarity=data['ast_similarity'],
            hash_similarity=data['hash_similarity'],
            is_plagiarized=data['is_plagiarized'],
            confidence_score=data['confidence_score'],
            created_at=created_at
        )

    def __repr__(self) -> str:
        """Return a string representation of the result for debugging."""
        return (
            f"ComparisonResult(id={self.id}, job_id={self.job_id!r}, "
            f"files={self.file1_name!r} vs {self.file2_name!r}, "
            f"plagiarized={self.is_plagiarized}, confidence={self.confidence_score:.2f})"
        )

    def __eq__(self, other: Any) -> bool:
        """Compare results by ID."""
        if not isinstance(other, ComparisonResult):
            return False
        return self.id == other.id


class Configuration:
    """
    Stores system configuration key-value pairs.

    Configuration entries are stored as key-value pairs with automatic
    timestamp tracking. Values are stored as strings and can be JSON
    serialized for complex types.

    Attributes:
        key: Configuration key (primary key)
        value: Configuration value (stored as string)
        updated_at: Last update timestamp (UTC)

    Example:
        >>> config = Configuration(
        ...     key='similarity_threshold',
        ...     value='0.80'
        ... )
        >>> config.value = '0.85'  # Updates automatically track time
    """

    def __init__(
        self,
        key: str,
        value: str,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize a Configuration instance.

        Args:
            key: Configuration key (unique identifier)
            value: Configuration value (string)
            updated_at: Last update timestamp (defaults to now)
        """
        self.key = key
        self.value = value
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary representation.

        Returns:
            Dictionary containing all configuration attributes

        Example:
            >>> config = Configuration(key='threshold', value='0.80')
            >>> data = config.to_dict()
            >>> print(data['key'])  # 'threshold'
        """
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Configuration':
        """
        Create a Configuration instance from a dictionary.

        Args:
            data: Dictionary containing configuration attributes

        Returns:
            New Configuration instance

        Raises:
            KeyError: If required fields are missing

        Example:
            >>> data = {'key': 'threshold', 'value': '0.80'}
            >>> config = Configuration.from_dict(data)
        """
        # Parse datetime if provided as string
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            key=data['key'],
            value=data['value'],
            updated_at=updated_at
        )

    def get_json_value(self) -> Any:
        """
        Parse the value as JSON if possible.

        Returns:
            Parsed JSON value, or original string if not valid JSON

        Example:
            >>> config = Configuration(key='settings', value='{"max": 100}')
            >>> settings = config.get_json_value()
            >>> print(settings['max'])  # 100
        """
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_json_value(self, obj: Any) -> None:
        """
        Set the value from a Python object by JSON serializing it.

        Args:
            obj: Python object to serialize (must be JSON-serializable)

        Example:
            >>> config = Configuration(key='settings', value='')
            >>> config.set_json_value({'max': 100, 'min': 10})
            >>> print(config.value)  # '{"max": 100, "min": 10}'
        """
        self.value = json.dumps(obj)
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """Return a string representation of the configuration for debugging."""
        return f"Configuration(key={self.key!r}, value={self.value!r})"

    def __eq__(self, other: Any) -> bool:
        """Compare configurations by key."""
        if not isinstance(other, Configuration):
            return False
        return self.key == other.key


# =============================================================================
# Module-Level Functions
# =============================================================================

def row_to_analysis_job(row: Any) -> AnalysisJob:
    """
    Convert a database row (sqlite3.Row) to an AnalysisJob instance.

    Args:
        row: Database row with job data

    Returns:
        AnalysisJob instance

    Example:
        >>> cursor.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,))
        >>> row = cursor.fetchone()
        >>> job = row_to_analysis_job(row)
    """
    # Parse datetime string if needed
    created_at = row['created_at']
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    return AnalysisJob(
        id=row['id'],
        created_at=created_at,
        status=row['status'],
        file_count=row['file_count'],
        pair_count=row['pair_count'],
        results_path=row['results_path']
    )


def row_to_comparison_result(row: Any) -> ComparisonResult:
    """
    Convert a database row (sqlite3.Row) to a ComparisonResult instance.

    Args:
        row: Database row with result data

    Returns:
        ComparisonResult instance

    Example:
        >>> cursor.execute("SELECT * FROM comparison_results WHERE job_id = ?", (job_id,))
        >>> rows = cursor.fetchall()
        >>> results = [row_to_comparison_result(row) for row in rows]
    """
    # Parse datetime string if needed
    created_at = row['created_at']
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    return ComparisonResult(
        id=row['id'],
        job_id=row['job_id'],
        file1_name=row['file1_name'],
        file2_name=row['file2_name'],
        token_similarity=row['token_similarity'],
        ast_similarity=row['ast_similarity'],
        hash_similarity=row['hash_similarity'],
        is_plagiarized=bool(row['is_plagiarized']),
        confidence_score=row['confidence_score'],
        created_at=created_at
    )


def row_to_configuration(row: Any) -> Configuration:
    """
    Convert a database row (sqlite3.Row) to a Configuration instance.

    Args:
        row: Database row with configuration data

    Returns:
        Configuration instance

    Example:
        >>> cursor.execute("SELECT * FROM configuration WHERE key = ?", (key,))
        >>> row = cursor.fetchone()
        >>> config = row_to_configuration(row)
    """
    # Parse datetime string if needed
    updated_at = row['updated_at']
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)

    return Configuration(
        key=row['key'],
        value=row['value'],
        updated_at=updated_at
    )


# =============================================================================
# Module Initialization
# =============================================================================

logger.debug("Database models module initialized")
