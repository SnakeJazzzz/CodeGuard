# Source Code Directory

This directory contains the core implementation of the CodeGuard plagiarism detection system.

## Organization

### `detectors/`
Detection algorithms implementing three complementary approaches:
- `base_detector.py` - Abstract base class for all detectors
- `token_detector.py` - Lexical token-based similarity detection
- `ast_detector.py` - Abstract Syntax Tree structural comparison
- `hash_detector.py` - Winnowing hash-based fingerprinting

### `web/`
Flask web application providing the user interface:
- `app.py` - Flask application initialization and configuration
- `routes.py` - HTTP route handlers and request processing
- `forms.py` - Form validation and file upload handling
- `file_handler.py` - File upload management and validation

### `database/`
Database layer for persistent storage:
- `models.py` - SQLAlchemy model definitions
- `schema.sql` - Database schema definitions
- `operations.py` - CRUD operations and queries
- `connection.py` - Database connection management

### `voting/`
Multi-method voting system for result aggregation:
- `voting_system.py` - Weighted voting mechanism
- `confidence_calculator.py` - Confidence score computation
- `thresholds.py` - Configurable threshold management

### `utils/`
Shared utility functions and helpers:
- `file_utils.py` - File I/O operations and path handling
- `validation.py` - Input validation functions
- `logger.py` - Logging configuration and utilities
- `constants.py` - Application-wide constants

## Architecture

```
┌─────────────────────────────────────┐
│         Web Layer (Flask)           │
│  Routes → Forms → File Handler      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Detection Engine               │
│  ┌───────────────────────────────┐  │
│  │  Token Detector  (1.0x)       │  │
│  │  AST Detector    (2.0x)       │  │
│  │  Hash Detector   (1.5x)       │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Voting System                  │
│  Aggregates results with weights    │
│  Calculates confidence scores       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Database Layer                 │
│  Persists results and configuration │
└─────────────────────────────────────┘
```

## Code Standards

- **Python Version**: 3.11+
- **Style Guide**: PEP 8
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all modules, classes, and functions
- **Testing**: Minimum 80% code coverage

## Development Workflow

1. Implement functionality in appropriate module
2. Write unit tests in `tests/unit/`
3. Add integration tests if multiple components interact
4. Update documentation in relevant README files
5. Ensure all tests pass and coverage meets requirements

## Import Structure

```python
# Detectors
from detectors.token_detector import TokenDetector
from detectors.ast_detector import ASTDetector
from detectors.hash_detector import HashDetector

# Voting
from voting.voting_system import VotingSystem

# Database
from database.operations import save_results, load_results

# Utilities
from utils.validation import validate_python_file
from utils.logger import get_logger
```

## Testing

All source modules should have corresponding test files:

```
src/detectors/token_detector.py  →  tests/unit/test_token_detector.py
src/web/routes.py                →  tests/integration/test_api_endpoints.py
```

Run tests from project root:
```bash
pytest tests/ --cov=src
```
