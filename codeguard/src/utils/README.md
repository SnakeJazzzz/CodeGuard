# Utility Functions

This directory contains shared utility functions and helper modules used throughout the CodeGuard application.

## Files

### `file_utils.py`
File I/O operations and path handling utilities.

**Functions**:

```python
def read_python_file(filepath: str, encoding: str = 'utf-8') -> str:
    """
    Read Python source file with automatic encoding detection.
    Falls back to latin-1 if UTF-8 fails.
    """

def write_json_report(data: Dict, filepath: str) -> None:
    """Write analysis results to JSON file with pretty formatting."""

def get_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of file for integrity checking."""

def ensure_directory(directory: str) -> None:
    """Create directory if it doesn't exist."""

def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""

def count_lines(filepath: str) -> int:
    """Count number of lines in file."""

def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filename."""

def generate_unique_filename(base: str, extension: str = '.py') -> str:
    """Generate unique filename with timestamp suffix."""

def list_python_files(directory: str) -> List[str]:
    """List all .py files in directory recursively."""
```

### `validation.py`
Input validation functions for files and parameters.

**Functions**:

```python
def validate_python_syntax(source_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python syntax using ast.parse().

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """

def validate_file_extension(filename: str, allowed: Set[str]) -> bool:
    """Check if file has allowed extension."""

def validate_file_size(filepath: str, max_bytes: int) -> bool:
    """Check if file size is within limit."""

def validate_job_id(job_id: str) -> bool:
    """Validate job ID format (YYYYMMDD_HHMMSS)."""

def validate_similarity_score(score: float) -> bool:
    """Validate similarity score is in range [0.0, 1.0]."""

def validate_threshold(threshold: float) -> bool:
    """Validate threshold is in range [0.0, 1.0]."""

def validate_upload_batch(files: List[FileStorage]) -> Tuple[bool, List[str]]:
    """
    Validate batch of uploaded files.

    Returns:
        (is_valid: bool, error_messages: List[str])
    """
```

### `logger.py`
Logging configuration and utilities.

**Functions**:

```python
def setup_logger(
    name: str = 'codeguard',
    level: str = 'INFO',
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure logger with console and optional file output.

    Formats:
        Console: [%(levelname)s] %(message)s
        File: %(asctime)s - %(name)s - %(levelname)s - %(message)s
    """

def get_logger(name: str = 'codeguard') -> logging.Logger:
    """Get configured logger instance."""

def log_analysis_start(job_id: str, file_count: int) -> None:
    """Log analysis job start."""

def log_analysis_complete(
    job_id: str,
    duration: float,
    plagiarism_count: int
) -> None:
    """Log analysis job completion."""

def log_error(error: Exception, context: Dict = None) -> None:
    """Log error with context information."""

def log_performance(
    operation: str,
    duration: float,
    details: Dict = None
) -> None:
    """Log performance metrics."""
```

**Log Levels**:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors requiring immediate attention

### `constants.py`
Application-wide constants and configuration values.

**Constants**:

```python
# File Settings
MAX_FILE_SIZE_BYTES = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'.py'}
MAX_FILES_PER_UPLOAD = 100
MIN_FILES_PER_UPLOAD = 2

# Processing Settings
DEFAULT_ENCODING = 'utf-8'
FALLBACK_ENCODINGS = ['latin-1', 'cp1252', 'iso-8859-1']
MAX_LINE_LENGTH = 10000

# Detection Thresholds (defaults)
TOKEN_THRESHOLD = 0.70
AST_THRESHOLD = 0.80
HASH_THRESHOLD = 0.60

# Voting Weights
TOKEN_WEIGHT = 1.0
AST_WEIGHT = 2.0
HASH_WEIGHT = 1.5
DECISION_THRESHOLD = 0.50

# Confidence Weights
CONFIDENCE_TOKEN_WEIGHT = 0.3
CONFIDENCE_AST_WEIGHT = 0.4
CONFIDENCE_HASH_WEIGHT = 0.3

# Winnowing Parameters
KGRAM_SIZE = 5
WINNOWING_WINDOW = 4

# Directory Paths
UPLOAD_DIR = '/app/data/uploads'
RESULTS_DIR = '/app/data/results'
DATABASE_PATH = '/app/data/codeguard.db'
CONFIG_DIR = '/app/config'

# Job ID Format
JOB_ID_FORMAT = '%Y%m%d_%H%M%S'

# Cleanup Settings
UPLOAD_RETENTION_HOURS = 24
JOB_RETENTION_DAYS = 30

# Performance Targets
TOKEN_DETECTOR_SPEED = 5000  # lines/second
AST_DETECTOR_SPEED = 1000    # lines/second
HASH_DETECTOR_SPEED = 3000   # lines/second

# HTTP Settings
HTTP_TIMEOUT = 120  # seconds
MAX_CONTENT_LENGTH = MAX_FILE_SIZE_BYTES

# Response Messages
MSG_UPLOAD_SUCCESS = "Files uploaded successfully"
MSG_ANALYSIS_COMPLETE = "Analysis completed"
MSG_INVALID_FILE = "Invalid file format"
MSG_FILE_TOO_LARGE = "File size exceeds maximum"
MSG_TOO_FEW_FILES = "Minimum 2 files required"

# Error Codes
ERR_INVALID_SYNTAX = "INVALID_SYNTAX"
ERR_FILE_NOT_FOUND = "FILE_NOT_FOUND"
ERR_PERMISSION_DENIED = "PERMISSION_DENIED"
ERR_PROCESSING_FAILED = "PROCESSING_FAILED"
```

## Usage Examples

### File Operations

```python
from utils.file_utils import read_python_file, write_json_report

# Read Python file with automatic encoding detection
source_code = read_python_file('student_submission.py')

# Write analysis results
results = {
    'job_id': '20251105_143022',
    'results': [...]
}
write_json_report(results, '/app/data/results/analysis.json')
```

### Validation

```python
from utils.validation import (
    validate_python_syntax,
    validate_file_extension,
    validate_upload_batch
)

# Validate syntax
is_valid, error_msg = validate_python_syntax(source_code)
if not is_valid:
    print(f"Syntax error: {error_msg}")

# Validate extension
if not validate_file_extension('test.py', {'.py'}):
    print("Invalid file type")

# Validate batch upload
is_valid, errors = validate_upload_batch(uploaded_files)
for error in errors:
    print(error)
```

### Logging

```python
from utils.logger import setup_logger, log_analysis_start, log_error

# Setup logger
logger = setup_logger(
    name='codeguard',
    level='INFO',
    log_file='/app/logs/codeguard.log'
)

# Log analysis
log_analysis_start('20251105_143022', file_count=10)

try:
    # Process files
    pass
except Exception as e:
    log_error(e, context={'job_id': '20251105_143022'})
```

### Using Constants

```python
from utils.constants import (
    MAX_FILE_SIZE_BYTES,
    ALLOWED_EXTENSIONS,
    TOKEN_THRESHOLD,
    UPLOAD_DIR
)

# Check file size
if file_size > MAX_FILE_SIZE_BYTES:
    raise ValueError("File too large")

# Use thresholds
if similarity > TOKEN_THRESHOLD:
    print("Similar files detected")

# Use paths
upload_path = os.path.join(UPLOAD_DIR, filename)
```

## Design Principles

1. **Single Responsibility**: Each utility module has a focused purpose
2. **Reusability**: Functions designed for use across multiple modules
3. **Error Handling**: Graceful degradation with informative errors
4. **Type Safety**: Type hints for all function signatures
5. **Documentation**: Comprehensive docstrings with examples

## Testing

```bash
# Test all utilities
pytest tests/unit/test_utils.py

# Test specific module
pytest tests/unit/test_file_utils.py
pytest tests/unit/test_validation.py
pytest tests/unit/test_logger.py
```

## Dependencies

- `os`, `sys` - File system operations
- `pathlib` - Path handling
- `json` - JSON serialization
- `hashlib` - File hashing
- `logging` - Logging framework
- `ast` - Python syntax validation
- `typing` - Type hints
