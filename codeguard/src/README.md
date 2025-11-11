# Source Code Directory

This directory contains the core implementation of the CodeGuard plagiarism detection system.

## Organization

### `detectors/`
Detection algorithms implementing three complementary approaches:
- `base_detector.py` - Abstract base class for all detectors
- `token_detector.py` - Lexical token-based similarity detection
- `ast_detector.py` - Abstract Syntax Tree structural comparison
- `hash_detector.py` - Winnowing hash-based fingerprinting

### `voting/`
Multi-method voting system for result aggregation:
- `voting_system.py` - Weighted voting mechanism
- `confidence_calculator.py` - Confidence score computation
- `thresholds.py` - Configurable threshold management

### `database/`
Database layer for persistent storage:
- `models.py` - SQLAlchemy model definitions
- `schema.sql` - Database schema definitions
- `operations.py` - CRUD operations and queries
- `connection.py` - Database connection management

### `utils/`
Shared utility functions and helpers:
- `file_utils.py` - File I/O operations and path handling
- `validation.py` - Input validation functions
- `logger.py` - Logging configuration and utilities
- `constants.py` - Application-wide constants

## Architecture

```
┌─────────────────────────────────────┐
│    Streamlit UI Layer (app.py)     │
│  File Upload → Configuration        │
│  Progress → Results Display         │
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
│      Database Layer (Optional)      │
│  Persists results and configuration │
└─────────────────────────────────────┘
```

## Framework-Independent Design

The detection algorithms, voting system, database layer, and utilities are **completely independent** of the UI framework. This allows:

- Easy integration with any web framework (Streamlit, Flask, FastAPI, etc.)
- Command-line interface development
- API service deployment
- Testing without UI dependencies

### Example: Using Detectors Independently

```python
# Import detectors (framework-independent)
from detectors.token_detector import TokenDetector
from detectors.ast_detector import ASTDetector
from detectors.hash_detector import HashDetector
from voting.voting_system import VotingSystem

# Read source files
with open('submission1.py', 'r') as f:
    source1 = f.read()
with open('submission2.py', 'r') as f:
    source2 = f.read()

# Run detectors
token_detector = TokenDetector()
ast_detector = ASTDetector()
hash_detector = HashDetector()

token_sim = token_detector.compare(source1, source2)
ast_sim = ast_detector.compare(source1, source2)
hash_sim = hash_detector.compare(source1, source2)

# Aggregate via voting
voter = VotingSystem()
result = voter.vote(token_sim, ast_sim, hash_sim)

print(f"Plagiarized: {result['is_plagiarized']}")
print(f"Confidence: {result['confidence_score']:.2%}")
```

## Integration with Streamlit

The Streamlit app (`../app.py`) imports and uses these modules:

```python
# In app.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from detectors.token_detector import TokenDetector
from detectors.ast_detector import ASTDetector
from detectors.hash_detector import HashDetector
from voting.voting_system import VotingSystem
from utils.constants import *
```

## Code Standards

- **Python Version**: 3.11+
- **Style Guide**: PEP 8
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all modules, classes, and functions
- **Testing**: Minimum 80% code coverage

## Development Workflow

1. Implement functionality in appropriate module
2. Write unit tests in `../tests/unit/`
3. Add integration tests if multiple components interact
4. Update documentation in relevant README files
5. Ensure all tests pass and coverage meets requirements
6. Test integration with Streamlit UI

## Testing

All source modules should have corresponding test files:

```
src/detectors/token_detector.py  →  tests/unit/test_token_detector.py
src/voting/voting_system.py      →  tests/unit/test_voting_system.py
```

Run tests from project root:
```bash
pytest tests/ --cov=src
```

## Module Dependencies

```
detectors/
  └─ Uses: utils/constants.py, utils/logger.py

voting/
  └─ Uses: utils/constants.py, utils/logger.py

database/
  └─ Uses: utils/constants.py, utils/logger.py

utils/
  └─ No dependencies (base layer)
```

## Performance Targets

| Component | Target | Measurement |
|-----------|--------|-------------|
| Token Detector | 5000 lines/sec | Time to process file pairs |
| AST Detector | 1000 lines/sec | Time to process file pairs |
| Hash Detector | 3000 lines/sec | Time to process file pairs |
| Voting System | <1ms per vote | Time to aggregate results |

## Notes

- This directory structure is framework-agnostic
- Can be used with Flask, FastAPI, Django, or any other framework
- Streamlit chosen for this project for simplicity and speed
- See `../technicalDecisionsLog.md` for architecture decisions
