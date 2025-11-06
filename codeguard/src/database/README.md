# Database Layer

This directory contains the database abstraction layer for persistent storage using SQLite.

## Files

### `models.py`
SQLAlchemy model definitions for database entities.

**Models**:

#### `AnalysisJob`
Represents a batch analysis job.

```python
class AnalysisJob:
    id: str               # Job ID (timestamp-based)
    created_at: datetime  # Job creation time
    status: str           # 'pending', 'processing', 'completed', 'failed'
    file_count: int       # Number of files analyzed
    pair_count: int       # Number of pairs compared
    results_path: str     # Path to JSON results file
```

#### `ComparisonResult`
Represents a single file pair comparison.

```python
class ComparisonResult:
    id: int                    # Auto-increment primary key
    job_id: str               # Foreign key to AnalysisJob
    file1_name: str           # First file name
    file2_name: str           # Second file name
    token_similarity: float   # Token detector score
    ast_similarity: float     # AST detector score
    hash_similarity: float    # Hash detector score
    is_plagiarized: bool      # Voting system decision
    confidence_score: float   # Overall confidence
    created_at: datetime      # Comparison timestamp
```

#### `Configuration`
Stores system configuration and thresholds.

```python
class Configuration:
    key: str      # Configuration key
    value: str    # Configuration value (JSON serialized)
    updated_at: datetime
```

### `schema.sql`
SQL schema definitions for database initialization.

**Tables**:
- `analysis_jobs` - Analysis job metadata
- `comparison_results` - Individual pair comparisons
- `configuration` - System configuration
- `audit_log` - Optional audit trail

**Indexes**:
- `idx_job_id` on `comparison_results(job_id)`
- `idx_created_at` on `analysis_jobs(created_at)`
- `idx_plagiarized` on `comparison_results(is_plagiarized)`

### `operations.py`
CRUD operations and database queries.

**Functions**:

```python
def create_analysis_job(job_id: str, file_count: int) -> AnalysisJob:
    """Create new analysis job record."""

def save_comparison_result(job_id: str, result: Dict) -> ComparisonResult:
    """Save single comparison result."""

def save_batch_results(job_id: str, results: List[Dict]) -> None:
    """Save multiple comparison results atomically."""

def get_job_results(job_id: str) -> List[ComparisonResult]:
    """Retrieve all results for a job."""

def get_job_summary(job_id: str) -> Dict:
    """Get job statistics and summary."""

def update_job_status(job_id: str, status: str) -> None:
    """Update job processing status."""

def get_plagiarism_count(job_id: str) -> int:
    """Count plagiarized pairs in job."""

def get_recent_jobs(limit: int = 10) -> List[AnalysisJob]:
    """Retrieve recent analysis jobs."""

def cleanup_old_jobs(days: int = 30) -> int:
    """Delete jobs older than specified days."""

def get_configuration(key: str) -> Optional[str]:
    """Retrieve configuration value."""

def set_configuration(key: str, value: str) -> None:
    """Store configuration value."""
```

### `connection.py`
Database connection management and session handling.

**Functions**:

```python
def init_db() -> None:
    """Initialize database schema from schema.sql."""

def get_db_connection() -> Connection:
    """Get database connection."""

def get_session() -> Session:
    """Get SQLAlchemy session (context manager)."""

def close_connection() -> None:
    """Close database connection."""

def backup_database(backup_path: str) -> None:
    """Create database backup."""
```

## Database Schema

```sql
-- Analysis Jobs
CREATE TABLE analysis_jobs (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    file_count INTEGER NOT NULL,
    pair_count INTEGER NOT NULL,
    results_path TEXT
);

-- Comparison Results
CREATE TABLE comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    file1_name TEXT NOT NULL,
    file2_name TEXT NOT NULL,
    token_similarity REAL NOT NULL,
    ast_similarity REAL NOT NULL,
    hash_similarity REAL NOT NULL,
    is_plagiarized BOOLEAN NOT NULL,
    confidence_score REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES analysis_jobs(id)
);

-- Configuration
CREATE TABLE configuration (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_job_id ON comparison_results(job_id);
CREATE INDEX idx_created_at ON analysis_jobs(created_at);
CREATE INDEX idx_plagiarized ON comparison_results(is_plagiarized);
```

## Usage Examples

### Creating an Analysis Job

```python
from database.operations import create_analysis_job, save_batch_results
from database.connection import init_db

# Initialize database
init_db()

# Create job
job = create_analysis_job(
    job_id="20251105_143022",
    file_count=10
)

# Save results
results = [
    {
        "file1_name": "student1.py",
        "file2_name": "student2.py",
        "token_similarity": 0.85,
        "ast_similarity": 0.92,
        "hash_similarity": 0.78,
        "is_plagiarized": True,
        "confidence_score": 0.87
    },
    # ... more results
]

save_batch_results(job.id, results)
```

### Querying Results

```python
from database.operations import get_job_results, get_job_summary

# Get all results for a job
results = get_job_results("20251105_143022")

# Get summary statistics
summary = get_job_summary("20251105_143022")
# Returns: {
#   "total_pairs": 45,
#   "plagiarized_count": 3,
#   "plagiarism_rate": 0.067,
#   "avg_confidence": 0.42
# }
```

## Data Persistence

The SQLite database file is stored in the Docker volume:
- Path: `/app/data/codeguard.db`
- Mounted from: `./data/codeguard.db` on host
- Persists across container restarts

## Backup and Maintenance

```python
from database.operations import cleanup_old_jobs
from database.connection import backup_database

# Backup database
backup_database("./backups/codeguard_backup.db")

# Cleanup old jobs
deleted_count = cleanup_old_jobs(days=30)
print(f"Deleted {deleted_count} old jobs")
```

## Transaction Management

All write operations use transactions:

```python
from database.connection import get_session

with get_session() as session:
    # Multiple operations in single transaction
    job = create_analysis_job(...)
    save_batch_results(...)
    session.commit()  # Atomic commit
```

## Testing

```bash
# Test database operations
pytest tests/unit/test_database_operations.py

# Test with in-memory database
pytest tests/unit/test_database_operations.py --db=:memory:
```

## Performance Considerations

- **Batch Inserts**: Use `save_batch_results()` for multiple records
- **Indexes**: Pre-defined on frequently queried columns
- **Connection Pooling**: Managed by SQLAlchemy
- **Query Optimization**: Use joins instead of N+1 queries

## Dependencies

- SQLite 3.35+ (included with Python 3.11)
- SQLAlchemy 2.0+ (optional, for ORM features)
