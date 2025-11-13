"""
Database Connection Management Module

This module provides thread-safe SQLite database connection management
for the CodeGuard plagiarism detection system.

Features:
- Automatic database initialization from schema.sql
- Thread-safe connection pooling
- Context manager support for safe transactions
- Database backup functionality
- Foreign key constraint enforcement

Database Location: data/codeguard.db (relative to project root)
Schema Location: src/database/schema.sql

Example Usage:
    # Initialize database
    init_db()

    # Use context manager for safe transactions
    with get_session() as conn:
        cursor = conn.execute("SELECT * FROM analysis_jobs")
        jobs = cursor.fetchall()

    # Create backup
    backup_database("backups/codeguard_backup.db")
"""

import sqlite3
import shutil
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Generator
from datetime import datetime

# Configure module logger
logger = logging.getLogger(__name__)

# =============================================================================
# Module-Level Constants
# =============================================================================

# Get project root directory (3 levels up from this file)
# This file is at: src/database/connection.py
# Project root is at: ../../..
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Database file location: {project_root}/data/codeguard.db
DB_PATH: Path = PROJECT_ROOT / "data" / "codeguard.db"

# Schema file location: {project_root}/src/database/schema.sql
SCHEMA_PATH: Path = PROJECT_ROOT / "src" / "database" / "schema.sql"

# Default backup directory
BACKUP_DIR: Path = PROJECT_ROOT / "data" / "backups"

# Connection timeout in seconds
CONNECTION_TIMEOUT: int = 30

# =============================================================================
# Database Initialization
# =============================================================================

def init_db() -> None:
    """
    Initialize database schema from schema.sql file.

    This function:
    1. Creates the data/ directory if it doesn't exist
    2. Reads the SQL schema from schema.sql
    3. Executes the schema to create all tables and indexes
    4. Enables foreign key constraints
    5. Commits the changes

    The function is idempotent - it can be safely called multiple times.
    Tables are created with IF NOT EXISTS, so existing tables won't be modified.

    Raises:
        FileNotFoundError: If schema.sql cannot be found
        sqlite3.Error: If database initialization fails
        IOError: If schema.sql cannot be read

    Example:
        >>> init_db()
        >>> # Database is now ready to use
    """
    try:
        # Create data directory if it doesn't exist
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory ensured at: {DB_PATH.parent}")

        # Verify schema file exists
        if not SCHEMA_PATH.exists():
            error_msg = f"Schema file not found: {SCHEMA_PATH}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Read schema SQL
        logger.info(f"Reading schema from: {SCHEMA_PATH}")
        schema_sql = SCHEMA_PATH.read_text(encoding='utf-8')

        # Create database connection
        logger.info(f"Initializing database at: {DB_PATH}")
        conn = sqlite3.connect(
            str(DB_PATH),
            timeout=CONNECTION_TIMEOUT,
            check_same_thread=False
        )

        try:
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")

            # Execute schema SQL
            conn.executescript(schema_sql)
            conn.commit()

            # Verify tables were created
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Database initialized successfully. Tables created: {', '.join(tables)}")

        finally:
            conn.close()

    except FileNotFoundError as e:
        logger.error(f"Schema file not found: {e}")
        raise
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    except IOError as e:
        logger.error(f"Failed to read schema file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        raise

# =============================================================================
# Connection Management
# =============================================================================

def get_db_connection() -> sqlite3.Connection:
    """
    Get a database connection with proper configuration.

    This function:
    1. Checks if database exists; if not, initializes it
    2. Creates a connection to the SQLite database
    3. Enables foreign key constraints
    4. Sets row factory to sqlite3.Row for dict-like access
    5. Configures connection for thread-safe operation

    The connection should be closed by the caller when done, or use
    get_session() context manager for automatic resource management.

    Returns:
        sqlite3.Connection: Configured database connection

    Raises:
        sqlite3.Error: If connection cannot be established
        FileNotFoundError: If schema file is missing during initialization

    Example:
        >>> conn = get_db_connection()
        >>> try:
        ...     cursor = conn.execute("SELECT * FROM analysis_jobs")
        ...     jobs = cursor.fetchall()
        ... finally:
        ...     conn.close()
    """
    try:
        # Initialize database if it doesn't exist
        if not DB_PATH.exists():
            logger.info("Database not found. Initializing...")
            init_db()

        # Create connection
        conn = sqlite3.connect(
            str(DB_PATH),
            timeout=CONNECTION_TIMEOUT,
            check_same_thread=False  # Allow connection to be used across threads
        )

        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        # Set row factory for dict-like access
        # This allows accessing columns by name: row['column_name']
        conn.row_factory = sqlite3.Row

        logger.debug(f"Database connection established: {DB_PATH}")
        return conn

    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting database connection: {e}")
        raise

@contextmanager
def get_session() -> Generator[sqlite3.Connection, None, None]:
    """
    Get database session as a context manager for safe transaction handling.

    This context manager:
    1. Acquires a database connection
    2. Yields the connection for use
    3. Commits changes on successful completion
    4. Rolls back changes if an exception occurs
    5. Always closes the connection when done

    This is the recommended way to interact with the database as it
    ensures proper resource cleanup and transaction management.

    Yields:
        sqlite3.Connection: Database connection for the session

    Raises:
        sqlite3.Error: If database operations fail

    Example:
        >>> with get_session() as conn:
        ...     conn.execute(
        ...         "INSERT INTO analysis_jobs (id, status, file_count, pair_count) "
        ...         "VALUES (?, ?, ?, ?)",
        ...         ('job-123', 'pending', 10, 45)
        ...     )
        >>> # Changes are automatically committed

        >>> # On error, changes are rolled back
        >>> try:
        ...     with get_session() as conn:
        ...         conn.execute("INVALID SQL")
        ... except sqlite3.Error:
        ...     pass  # Changes were automatically rolled back
    """
    conn = None
    try:
        # Acquire connection
        conn = get_db_connection()
        logger.debug("Database session started")

        # Yield connection to caller
        yield conn

        # Commit on successful completion
        conn.commit()
        logger.debug("Database session committed")

    except sqlite3.Error as e:
        # Rollback on database errors
        if conn:
            conn.rollback()
            logger.warning(f"Database session rolled back due to error: {e}")
        raise
    except Exception as e:
        # Rollback on any other errors
        if conn:
            conn.rollback()
            logger.warning(f"Database session rolled back due to unexpected error: {e}")
        raise
    finally:
        # Always close connection
        if conn:
            conn.close()
            logger.debug("Database session closed")

# =============================================================================
# Connection Cleanup
# =============================================================================

def close_connection(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Close a database connection safely.

    This function handles closing database connections with proper error
    handling. It gracefully handles None values and already-closed connections.

    Args:
        conn: Database connection to close. If None, this function does nothing.

    Example:
        >>> conn = get_db_connection()
        >>> # ... use connection ...
        >>> close_connection(conn)

        >>> # Safe to call with None
        >>> close_connection(None)  # Does nothing
    """
    if conn is None:
        logger.debug("close_connection called with None, skipping")
        return

    try:
        conn.close()
        logger.debug("Database connection closed successfully")
    except sqlite3.Error as e:
        logger.warning(f"Error closing database connection: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error closing database connection: {e}")

# =============================================================================
# Database Backup
# =============================================================================

def backup_database(backup_path: Optional[str] = None) -> str:
    """
    Create a backup of the database file.

    This function:
    1. Creates the backup directory if it doesn't exist
    2. Generates a timestamped filename if path not provided
    3. Copies the database file to the backup location
    4. Verifies the backup was created successfully
    5. Returns the absolute path to the backup file

    Args:
        backup_path: Path for the backup file. If None, creates a timestamped
                    backup in data/backups/codeguard_YYYYMMDD_HHMMSS.db

    Returns:
        str: Absolute path to the created backup file

    Raises:
        FileNotFoundError: If the source database doesn't exist
        IOError: If backup creation fails
        PermissionError: If insufficient permissions for backup location

    Example:
        >>> # Create backup with custom path
        >>> backup_path = backup_database("backups/my_backup.db")
        >>> print(f"Backup created at: {backup_path}")

        >>> # Create timestamped backup in default location
        >>> backup_path = backup_database()
        >>> # Creates: data/backups/codeguard_20251112_143022.db
    """
    try:
        # Check if database exists
        if not DB_PATH.exists():
            error_msg = f"Cannot backup non-existent database: {DB_PATH}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Determine backup path
        if backup_path is None:
            # Create timestamped backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"codeguard_{timestamp}.db"
            backup_path_obj = BACKUP_DIR / backup_filename
        else:
            backup_path_obj = Path(backup_path)
            # Make absolute if relative path provided
            if not backup_path_obj.is_absolute():
                backup_path_obj = PROJECT_ROOT / backup_path_obj

        # Create backup directory if it doesn't exist
        backup_path_obj.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup directory ensured at: {backup_path_obj.parent}")

        # Copy database file
        logger.info(f"Creating backup: {DB_PATH} -> {backup_path_obj}")
        shutil.copy2(str(DB_PATH), str(backup_path_obj))

        # Verify backup was created and has non-zero size
        if not backup_path_obj.exists():
            error_msg = f"Backup file was not created: {backup_path_obj}"
            logger.error(error_msg)
            raise IOError(error_msg)

        backup_size = backup_path_obj.stat().st_size
        original_size = DB_PATH.stat().st_size

        if backup_size == 0:
            error_msg = f"Backup file is empty: {backup_path_obj}"
            logger.error(error_msg)
            raise IOError(error_msg)

        if backup_size != original_size:
            logger.warning(
                f"Backup size ({backup_size} bytes) differs from original "
                f"({original_size} bytes)"
            )

        logger.info(
            f"Backup created successfully: {backup_path_obj} ({backup_size} bytes)"
        )

        return str(backup_path_obj.resolve())

    except FileNotFoundError as e:
        logger.error(f"Source database not found: {e}")
        raise
    except PermissionError as e:
        logger.error(f"Permission denied creating backup: {e}")
        raise
    except IOError as e:
        logger.error(f"Failed to create backup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating backup: {e}")
        raise

# =============================================================================
# Database Information
# =============================================================================

def get_database_info() -> dict:
    """
    Get information about the database.

    Returns:
        dict: Database information including:
            - path: Absolute path to database file
            - exists: Whether database file exists
            - size_bytes: Size of database file in bytes (if exists)
            - tables: List of table names (if exists)
            - indexes: List of index names (if exists)

    Example:
        >>> info = get_database_info()
        >>> print(f"Database: {info['path']}")
        >>> print(f"Size: {info['size_bytes']} bytes")
        >>> print(f"Tables: {', '.join(info['tables'])}")
    """
    info = {
        'path': str(DB_PATH.resolve()),
        'exists': DB_PATH.exists(),
        'size_bytes': None,
        'tables': [],
        'indexes': []
    }

    if DB_PATH.exists():
        info['size_bytes'] = DB_PATH.stat().st_size

        try:
            with get_session() as conn:
                # Get table names
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "ORDER BY name"
                )
                info['tables'] = [row['name'] for row in cursor.fetchall()]

                # Get index names
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' "
                    "ORDER BY name"
                )
                info['indexes'] = [row['name'] for row in cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"Failed to get database info: {e}")

    return info

# =============================================================================
# Module Initialization
# =============================================================================

# Log module constants on import (for debugging)
logger.debug(f"Database module initialized")
logger.debug(f"PROJECT_ROOT: {PROJECT_ROOT}")
logger.debug(f"DB_PATH: {DB_PATH}")
logger.debug(f"SCHEMA_PATH: {SCHEMA_PATH}")
