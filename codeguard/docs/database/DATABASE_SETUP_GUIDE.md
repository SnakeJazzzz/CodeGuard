# CodeGuard Database Setup Guide

## Overview

This guide documents the completed database schema and connection management implementation for CodeGuard's plagiarism detection system.

## Files Created

### 1. Schema Definition
**File**: `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/src/database/schema.sql`

The schema file defines:
- **3 core tables**: analysis_jobs, comparison_results, configuration
- **4 performance indexes**: idx_job_id, idx_created_at, idx_plagiarized, idx_job_plagiarized
- **CHECK constraints**: For data validation (valid status values, score ranges)
- **FOREIGN KEY constraints**: For referential integrity
- **Default configuration values**: System parameters

### 2. Connection Management
**File**: `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/src/database/connection.py`

Provides thread-safe database operations with:
- Automatic schema initialization
- Context manager support for safe transactions
- Database backup functionality
- Comprehensive error handling
- Dict-like row access (sqlite3.Row factory)

## Database Schema

### Table: analysis_jobs
Stores metadata about each plagiarism analysis job.

```sql
CREATE TABLE analysis_jobs (
    id TEXT PRIMARY KEY,                    -- UUID for job identification
    created_at TIMESTAMP,                   -- Job creation time (UTC)
    status TEXT NOT NULL,                   -- 'pending', 'running', 'completed', 'failed'
    file_count INTEGER NOT NULL,            -- Total number of files analyzed
    pair_count INTEGER NOT NULL,            -- Total number of comparisons
    results_path TEXT                       -- Path to detailed results JSON
);
```

**Constraints**:
- Valid status values: 'pending', 'running', 'completed', 'failed'
- File count >= 0
- Pair count >= 0

### Table: comparison_results
Stores individual file pair comparison results.

```sql
CREATE TABLE comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Auto-incrementing ID
    job_id TEXT NOT NULL,                   -- Foreign key to analysis_jobs
    file1_name TEXT NOT NULL,               -- First file name
    file2_name TEXT NOT NULL,               -- Second file name
    token_similarity REAL NOT NULL,         -- Token similarity (0.0-1.0)
    ast_similarity REAL NOT NULL,           -- AST similarity (0.0-1.0)
    hash_similarity REAL NOT NULL,          -- Hash similarity (0.0-1.0)
    is_plagiarized BOOLEAN NOT NULL,        -- Final verdict (0 or 1)
    confidence_score REAL NOT NULL,         -- Confidence (0.0-1.0)
    created_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES analysis_jobs(id) ON DELETE CASCADE
);
```

**Constraints**:
- All similarity scores between 0.0 and 1.0
- Confidence score between 0.0 and 1.0
- Cascade delete when parent job is deleted

### Table: configuration
Stores system configuration key-value pairs.

```sql
CREATE TABLE configuration (
    key TEXT PRIMARY KEY,                   -- Configuration key
    value TEXT NOT NULL,                    -- Configuration value
    updated_at TIMESTAMP
);
```

## Connection Management API

### Initialize Database

```python
from src.database.connection import init_db

# Initialize database (idempotent - safe to call multiple times)
init_db()
```

### Get Database Connection

```python
from src.database.connection import get_db_connection, close_connection

# Get connection
conn = get_db_connection()
try:
    cursor = conn.execute("SELECT * FROM analysis_jobs")
    jobs = cursor.fetchall()
finally:
    close_connection(conn)
```

### Use Context Manager (Recommended)

```python
from src.database.connection import get_session

# Automatic commit on success, rollback on error
with get_session() as conn:
    conn.execute(
        "INSERT INTO analysis_jobs (id, status, file_count, pair_count) "
        "VALUES (?, ?, ?, ?)",
        ('job-001', 'pending', 10, 45)
    )
    # Automatically committed
```

### Create Database Backup

```python
from src.database.connection import backup_database

# Create timestamped backup in default location
backup_path = backup_database()
print(f"Backup created: {backup_path}")

# Create backup with custom path
backup_path = backup_database("backups/my_backup.db")
```

### Get Database Information

```python
from src.database.connection import get_database_info

info = get_database_info()
print(f"Database: {info['path']}")
print(f"Size: {info['size_bytes']} bytes")
print(f"Tables: {info['tables']}")
print(f"Indexes: {info['indexes']}")
```

## Database Location

- **Database file**: `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/data/codeguard.db`
- **Backups directory**: `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/data/backups/`

## Default Configuration Values

The database is pre-populated with the following configuration:

| Key | Value | Description |
|-----|-------|-------------|
| similarity_threshold | 0.80 | Threshold for plagiarism detection (80%) |
| confidence_threshold | 0.75 | Minimum confidence for positive match (75%) |
| max_file_size_mb | 16 | Maximum file size in megabytes |
| database_version | 1.0 | Schema version for migrations |

## Performance Indexes

The following indexes are created for query optimization:

1. **idx_job_id**: Fast lookup of comparison results by job_id
2. **idx_created_at**: Fast chronological queries on analysis_jobs
3. **idx_plagiarized**: Fast filtering of flagged comparisons
4. **idx_job_plagiarized**: Composite index for job-specific plagiarism queries

## Features

### Thread Safety
- Connections configured with `check_same_thread=False`
- Each operation gets its own connection
- Context managers ensure proper resource cleanup

### Foreign Key Enforcement
- Foreign key constraints are enabled by default
- Cascade delete ensures referential integrity
- Invalid references are caught at insert time

### Row Factory
- All connections use `sqlite3.Row` factory
- Allows dict-like access to columns: `row['column_name']`
- Column names accessible via `row.keys()`

### Error Handling
- All database errors are caught and logged
- Transactions automatically rollback on errors
- Descriptive error messages for debugging

### Backup System
- Create backups on demand
- Timestamped backups for version control
- Verification of backup integrity

## Testing

A comprehensive test suite is provided in `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/test_database_setup.py`

Run tests:
```bash
cd /Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard
python3 test_database_setup.py
```

### Test Coverage

The test suite verifies:
1. ✓ Schema file exists and is valid
2. ✓ Database initialization creates file
3. ✓ All tables and indexes are created
4. ✓ Table structures match schema
5. ✓ Foreign key constraints work
6. ✓ Session context manager commits/rollbacks
7. ✓ Row factory provides dict-like access
8. ✓ Default configuration values are inserted
9. ✓ Backup creation and verification
10. ✓ Database information retrieval

**All 10 tests passed successfully!**

## Usage Examples

### Example 1: Create a New Analysis Job

```python
from src.database.connection import get_session
import uuid

job_id = str(uuid.uuid4())

with get_session() as conn:
    conn.execute(
        "INSERT INTO analysis_jobs (id, status, file_count, pair_count) "
        "VALUES (?, ?, ?, ?)",
        (job_id, 'pending', 5, 10)
    )

print(f"Created job: {job_id}")
```

### Example 2: Store Comparison Results

```python
from src.database.connection import get_session

with get_session() as conn:
    conn.execute(
        "INSERT INTO comparison_results "
        "(job_id, file1_name, file2_name, token_similarity, ast_similarity, "
        "hash_similarity, is_plagiarized, confidence_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (job_id, 'file1.py', 'file2.py', 0.85, 0.82, 0.90, 1, 0.89)
    )
```

### Example 3: Query Results

```python
from src.database.connection import get_session

with get_session() as conn:
    # Get all plagiarized comparisons for a job
    cursor = conn.execute(
        "SELECT file1_name, file2_name, confidence_score "
        "FROM comparison_results "
        "WHERE job_id = ? AND is_plagiarized = 1 "
        "ORDER BY confidence_score DESC",
        (job_id,)
    )

    for row in cursor.fetchall():
        print(f"{row['file1_name']} <-> {row['file2_name']}: "
              f"{row['confidence_score']:.2%} confidence")
```

### Example 4: Update Job Status

```python
from src.database.connection import get_session

with get_session() as conn:
    conn.execute(
        "UPDATE analysis_jobs SET status = ?, results_path = ? WHERE id = ?",
        ('completed', 'data/results/job-123.json', job_id)
    )
```

### Example 5: Get Configuration

```python
from src.database.connection import get_session

with get_session() as conn:
    cursor = conn.execute(
        "SELECT value FROM configuration WHERE key = ?",
        ('similarity_threshold',)
    )
    threshold = float(cursor.fetchone()['value'])
    print(f"Similarity threshold: {threshold}")
```

## Best Practices

1. **Always use context managers** (`get_session()`) for automatic transaction management
2. **Use parameterized queries** to prevent SQL injection
3. **Create backups** before major operations or schema changes
4. **Monitor database size** using `get_database_info()`
5. **Check foreign key constraints** are enabled before bulk operations
6. **Use indexes** for frequently queried columns

## Next Steps

The database layer is now ready for use. Recommended next steps:

1. **Create CRUD operations** in `src/database/operations.py`
2. **Add migration system** for schema versioning
3. **Implement query helpers** for common operations
4. **Add database connection pooling** for high-concurrency scenarios
5. **Create data access layer** to abstract raw SQL from business logic

## Troubleshooting

### Database File Not Found
```python
from src.database.connection import init_db
init_db()  # Creates database if missing
```

### Foreign Key Constraint Failed
- Ensure parent record exists before inserting child records
- Check that job_id in comparison_results matches an existing analysis_jobs.id

### Connection Issues
- Check file permissions on data/ directory
- Verify database file is not locked by another process
- Ensure sufficient disk space for database operations

## Support

For issues or questions about the database layer, refer to:
- `/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/src/database/README.md`
- Source code in `src/database/connection.py` (comprehensive docstrings)
- Test suite in `test_database_setup.py` (usage examples)
