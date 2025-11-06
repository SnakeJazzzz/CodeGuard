# Test Suite

Comprehensive test suite for the CodeGuard plagiarism detection system using pytest.

## Overview

The test suite is organized into two main categories:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows

**Coverage Target**: ≥80% code coverage

## Directory Structure

```
tests/
├── unit/              # Unit tests for individual modules
│   ├── test_token_detector.py
│   ├── test_ast_detector.py
│   ├── test_hash_detector.py
│   ├── test_voting_system.py
│   ├── test_confidence_calculator.py
│   ├── test_database_operations.py
│   ├── test_file_utils.py
│   ├── test_validation.py
│   └── ...
├── integration/       # Integration tests for workflows
│   ├── test_analysis_workflow.py
│   ├── test_api_endpoints.py
│   ├── test_batch_processing.py
│   └── ...
├── fixtures/          # Test fixtures and sample data
│   ├── sample_code/
│   ├── plagiarized_pairs/
│   └── test_configs/
└── conftest.py        # Shared pytest fixtures
```

## Running Tests

### All Tests
```bash
# Run all tests
pytest tests/

# With coverage report
pytest tests/ --cov=src --cov-report=html

# With verbose output
pytest tests/ -v

# Parallel execution
pytest tests/ -n auto
```

### Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific module
pytest tests/unit/test_token_detector.py

# Specific test
pytest tests/unit/test_token_detector.py::test_identical_code
```

### Coverage Analysis
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Fail if coverage below threshold
pytest tests/ --cov=src --cov-fail-under=80
```

## Test Organization

### Naming Conventions

- **Test Files**: `test_<module_name>.py`
- **Test Functions**: `test_<functionality>_<scenario>`
- **Test Classes**: `Test<ComponentName>`

Examples:
```python
# tests/unit/test_token_detector.py
def test_identical_code_high_similarity():
    """Test that identical code produces ~1.0 similarity."""

def test_different_code_low_similarity():
    """Test that different code produces ~0.0 similarity."""

class TestTokenDetector:
    def test_variable_renaming(self):
        """Test token detector with renamed variables."""
```

### Test Structure

Each test follows the Arrange-Act-Assert pattern:

```python
def test_voting_with_unanimous_agreement():
    # Arrange
    voter = VotingSystem()
    token_sim = 0.85
    ast_sim = 0.92
    hash_sim = 0.78

    # Act
    result = voter.vote(token_sim, ast_sim, hash_sim)

    # Assert
    assert result['is_plagiarized'] is True
    assert result['confidence_score'] > 0.80
    assert result['weighted_votes'] > 2.25
```

## Common Fixtures

Defined in `conftest.py`:

```python
@pytest.fixture
def sample_code_identical():
    """Provide identical code samples."""

@pytest.fixture
def sample_code_different():
    """Provide completely different code samples."""

@pytest.fixture
def sample_code_renamed():
    """Provide code with renamed variables."""

@pytest.fixture
def temp_upload_dir(tmp_path):
    """Provide temporary upload directory."""

@pytest.fixture
def test_db():
    """Provide in-memory test database."""

@pytest.fixture
def flask_client():
    """Provide Flask test client."""
```

## Test Categories

### Detector Tests (Unit)
Test individual detection algorithms:
- Identical code (expect ~1.0 similarity)
- Completely different code (expect ~0.0 similarity)
- Variable renaming (AST should detect, token shouldn't)
- Partial copying (hash should detect)
- Syntax errors (graceful handling)
- Performance benchmarks

### Voting System Tests (Unit)
Test voting logic:
- Unanimous agreement scenarios
- Split decisions
- Edge cases (all zeros, all ones)
- Threshold boundary conditions
- Custom configuration

### Database Tests (Unit)
Test database operations:
- Create/read/update/delete operations
- Transaction handling
- Constraint enforcement
- Query performance

### Web Layer Tests (Integration)
Test HTTP endpoints:
- File upload validation
- Batch processing workflow
- Results retrieval
- Error handling
- JSON response format

### End-to-End Tests (Integration)
Test complete workflows:
- Upload → Analyze → Results
- Multiple file pairs
- Error recovery
- Performance under load

## Test Data

### Sample Code Files

Located in `tests/fixtures/sample_code/`:
- `identical_*.py` - Identical code pairs
- `different_*.py` - Completely different code
- `renamed_*.py` - Variable renamed versions
- `partial_*.py` - Partial copy scenarios
- `obfuscated_*.py` - Obfuscated versions

### Validation Datasets

Located in `validation-datasets/`:
- `plagiarized/` - Known plagiarized pairs
- `legitimate/` - Legitimate similar code
- `obfuscated/` - Obfuscation attempts

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Performance Testing

### Benchmark Tests

```python
import pytest

@pytest.mark.benchmark
def test_token_detector_performance(benchmark):
    detector = TokenDetector()
    result = benchmark(detector.compare, source1, source2)
    assert result >= 0.0
```

Run benchmarks:
```bash
pytest tests/ -m benchmark --benchmark-only
```

## Testing Best Practices

1. **Isolation**: Each test should be independent
2. **Repeatability**: Tests should produce consistent results
3. **Fast Execution**: Unit tests should run in milliseconds
4. **Clear Assertions**: Use descriptive assertion messages
5. **Mock External Dependencies**: Use pytest-mock for external services
6. **Test Edge Cases**: Include boundary conditions and error cases
7. **Documentation**: Add docstrings explaining test purpose

## Mocking

Using `pytest-mock` for external dependencies:

```python
def test_file_upload_error(mocker, flask_client):
    # Mock file save to simulate failure
    mocker.patch('src.web.file_handler.save_file',
                 side_effect=IOError("Disk full"))

    response = flask_client.post('/upload', data={...})
    assert response.status_code == 500
```

## Code Coverage Goals

Target coverage by module:
- Detectors: ≥90%
- Voting System: ≥95%
- Database Operations: ≥85%
- Web Layer: ≥80%
- Utilities: ≥90%

## Reporting

### Coverage Report Format
```
---------- coverage: platform darwin, python 3.11.5 -----------
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
src/detectors/token_detector.py       120      8    93%   45-47, 89
src/detectors/ast_detector.py         156     12    92%   67-71, 134
src/voting/voting_system.py            89      3    97%   112-114
-----------------------------------------------------------------
TOTAL                                 1234     89    93%
```

## Dependencies

```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-benchmark>=4.0.0
pytest-xdist>=3.3.0  # Parallel execution
```
