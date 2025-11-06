# Utility Scripts

Helper scripts for development, testing, and deployment.

## Files

### `setup_dev_env.sh`
Sets up development environment.

```bash
#!/bin/bash
# setup_dev_env.sh - Setup development environment

set -e  # Exit on error

echo "Setting up CodeGuard development environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Use venv\Scripts\activate on Windows

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov pytest-mock black flake8 mypy

# Install package in editable mode
echo "Installing package..."
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads data/results logs

# Initialize database
echo "Initializing database..."
python -c "from src.database.connection import init_db; init_db()"

# Run tests to verify setup
echo "Running tests..."
pytest tests/ -v

echo "✓ Development environment ready!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  flask run"
```

**Usage**:
```bash
chmod +x scripts/setup_dev_env.sh
./scripts/setup_dev_env.sh
```

### `run_tests.sh`
Runs complete test suite with coverage.

```bash
#!/bin/bash
# run_tests.sh - Run test suite with coverage

set -e

echo "Running CodeGuard test suite..."

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
pytest tests/ \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=80 \
    -v

echo ""
echo "✓ Tests completed!"
echo ""
echo "Coverage report generated:"
echo "  Open htmlcov/index.html in your browser"
echo ""
echo "Coverage summary above shows lines not covered by tests."
```

**Usage**:
```bash
chmod +x scripts/run_tests.sh
./scripts/run_tests.sh
```

### `generate_test_data.py`
Generates synthetic test data for validation.

```python
#!/usr/bin/env python3
"""
generate_test_data.py - Generate test datasets for validation

Creates sample Python files with known plagiarism patterns:
- Identical copies
- Variable renaming
- Structural modifications
- Partial copying
- Completely different code
"""

import os
import random
import string
from pathlib import Path

# Base template code
TEMPLATE_FACTORIAL = '''
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def main():
    result = factorial(5)
    print(f"Factorial: {result}")

if __name__ == "__main__":
    main()
'''

TEMPLATE_FIBONACCI = '''
def fibonacci(n):
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def main():
    result = fibonacci(10)
    print(f"Fibonacci: {result}")

if __name__ == "__main__":
    main()
'''

def create_identical_copy(code, filename, output_dir):
    """Create identical copy."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(code)

def create_renamed_version(code, filename, output_dir):
    """Create version with renamed variables."""
    renamed = code.replace('factorial', 'compute_factorial')
    renamed = renamed.replace('fibonacci', 'compute_fibonacci')
    renamed = renamed.replace('result', 'output')

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(renamed)

def create_reformatted_version(code, filename, output_dir):
    """Create version with different formatting."""
    # Add extra whitespace, change indentation style
    reformatted = code.replace('    ', '  ')  # 4 spaces to 2
    reformatted = '\n\n' + reformatted + '\n\n'  # Extra newlines

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(reformatted)

def generate_different_code(filename, output_dir):
    """Generate completely different code."""
    code = f'''
def bubble_sort(arr):
    """Sort array using bubble sort."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def main():
    numbers = [64, 34, 25, 12, 22, 11, 90]
    sorted_numbers = bubble_sort(numbers)
    print(f"Sorted: {{sorted_numbers}}")

if __name__ == "__main__":
    main()
'''

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(code)

def main():
    """Generate all test datasets."""
    base_dir = 'validation-datasets'

    print("Generating test datasets...")

    # Plagiarized pairs
    print("  Creating plagiarized pairs...")
    create_identical_copy(TEMPLATE_FACTORIAL, 'original_a.py',
                         f'{base_dir}/plagiarized')
    create_identical_copy(TEMPLATE_FACTORIAL, 'copied_a.py',
                         f'{base_dir}/plagiarized')

    create_renamed_version(TEMPLATE_FACTORIAL, 'original_b.py',
                          f'{base_dir}/plagiarized')
    create_renamed_version(TEMPLATE_FACTORIAL, 'renamed_b.py',
                          f'{base_dir}/plagiarized')

    # Legitimate pairs
    print("  Creating legitimate pairs...")
    create_identical_copy(TEMPLATE_FACTORIAL, 'factorial.py',
                         f'{base_dir}/legitimate')
    create_identical_copy(TEMPLATE_FIBONACCI, 'fibonacci.py',
                         f'{base_dir}/legitimate')

    # Obfuscated pairs
    print("  Creating obfuscated pairs...")
    create_reformatted_version(TEMPLATE_FACTORIAL, 'original_c.py',
                              f'{base_dir}/obfuscated')
    create_reformatted_version(TEMPLATE_FACTORIAL, 'reformatted_c.py',
                              f'{base_dir}/obfuscated')

    # Different code
    generate_different_code('bubble_sort.py', f'{base_dir}/legitimate')

    print("✓ Test datasets generated successfully!")
    print(f"  Location: {base_dir}/")

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
chmod +x scripts/generate_test_data.py
python scripts/generate_test_data.py
```

## Additional Useful Scripts

### `lint.sh` - Code linting
```bash
#!/bin/bash
# Run code quality checks

echo "Running flake8..."
flake8 src/ tests/

echo "Running black..."
black --check src/ tests/

echo "Running mypy..."
mypy src/

echo "✓ Linting complete!"
```

### `format.sh` - Code formatting
```bash
#!/bin/bash
# Format code with black

echo "Formatting code..."
black src/ tests/

echo "✓ Code formatted!"
```

### `clean.sh` - Cleanup
```bash
#!/bin/bash
# Clean build artifacts and cache

echo "Cleaning build artifacts..."

rm -rf __pycache__
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov/
rm -rf dist/
rm -rf build/
rm -rf *.egg-info

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "✓ Cleanup complete!"
```

### `backup.sh` - Database backup
```bash
#!/bin/bash
# Backup database and results

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup database
cp data/codeguard.db "$BACKUP_DIR/"

# Backup results
cp -r data/results "$BACKUP_DIR/"

echo "✓ Backup created: $BACKUP_DIR"
```

## Making Scripts Executable

```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## Windows Compatibility

For Windows, create `.bat` equivalents or use WSL/Git Bash.

Example `run_tests.bat`:
```bat
@echo off
call venv\Scripts\activate
pytest tests\ --cov=src --cov-report=html
echo Tests completed!
pause
```
