"""
Validation Dataset Test Script

This script validates that all sample files in the validation-datasets/ directory
are correctly formatted, executable, and produce expected similarity scores when
compared using the TokenDetector.

It verifies:
1. All files have valid Python syntax
2. All functions execute correctly
3. Plagiarized pairs have high similarity (should detect)
4. Legitimate pairs have low similarity (should NOT detect)
5. Obfuscated pairs have medium-high similarity (AST should catch)

Author: CodeGuard Team
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
codeguard_root = Path(__file__).parent.parent
sys.path.insert(0, str(codeguard_root))

from src.detectors.token_detector import TokenDetector


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text):
    """Print success message in green."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message in red."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def test_syntax(file_path):
    """
    Test if a Python file has valid syntax.

    Args:
        file_path (Path): Path to the Python file

    Returns:
        tuple: (success: bool, error_msg: str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(file_path), 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def execute_file(file_path):
    """
    Execute a Python file and check if it runs without errors.

    Args:
        file_path (Path): Path to the Python file

    Returns:
        tuple: (success: bool, error_msg: str, output: str)
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Create a namespace for execution
        namespace = {}

        # Execute the code
        exec(code, namespace)

        # Try to find and call the main function
        if 'calculate_factorial' in namespace:
            result = namespace['calculate_factorial'](5)
            return True, None, f"calculate_factorial(5) = {result}"
        elif 'factorial' in namespace:
            result = namespace['factorial'](5)
            return True, None, f"factorial(5) = {result}"
        elif 'compute_factorial' in namespace:
            result = namespace['compute_factorial'](5)
            return True, None, f"compute_factorial(5) = {result}"
        elif 'fibonacci' in namespace:
            result = namespace['fibonacci'](10)
            return True, None, f"fibonacci(10) = {result}"
        else:
            return True, None, "No testable function found (but syntax is valid)"

    except Exception as e:
        return False, str(e), None


def count_lines(file_path):
    """Count lines in a file (including blank lines and comments)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())


def get_file_size(file_path):
    """Get file size in bytes."""
    return file_path.stat().st_size


def test_similarity(file1, file2, expected_range, description):
    """
    Test similarity between two files and check if it's in expected range.

    Args:
        file1 (Path): Path to first file
        file2 (Path): Path to second file
        expected_range (tuple): (min, max) expected similarity
        description (str): Description of the comparison

    Returns:
        bool: True if similarity is in expected range
    """
    detector = TokenDetector(threshold=0.7)

    try:
        result = detector.analyze(file1, file2)
        similarity = result['similarity_score']
        jaccard = result['jaccard_similarity']
        cosine = result['cosine_similarity']

        min_expected, max_expected = expected_range
        in_range = min_expected <= similarity <= max_expected

        # Format output
        status = "✓" if in_range else "✗"
        color = Colors.GREEN if in_range else Colors.RED

        print(f"\n{color}{status} {description}{Colors.END}")
        print(f"  File 1: {file1.name}")
        print(f"  File 2: {file2.name}")
        print(f"  Combined Similarity: {similarity:.2%}")
        print(f"  Jaccard Similarity:  {jaccard:.2%}")
        print(f"  Cosine Similarity:   {cosine:.2%}")
        print(f"  Expected Range: {min_expected:.0%} - {max_expected:.0%}")

        if in_range:
            print(f"  {Colors.GREEN}Result: IN EXPECTED RANGE{Colors.END}")
        else:
            print(f"  {Colors.RED}Result: OUT OF RANGE!{Colors.END}")

        return in_range

    except Exception as e:
        print_error(f"Error comparing {file1.name} and {file2.name}: {e}")
        return False


def main():
    """Main test execution."""
    print_header("CodeGuard Validation Dataset Test Suite")

    # Define paths
    validation_dir = Path(__file__).parent
    plagiarized_dir = validation_dir / 'plagiarized'
    legitimate_dir = validation_dir / 'legitimate'
    obfuscated_dir = validation_dir / 'obfuscated'

    all_files = [
        plagiarized_dir / 'factorial_original.py',
        plagiarized_dir / 'factorial_copied.py',
        legitimate_dir / 'factorial_recursive.py',
        legitimate_dir / 'factorial_iterative.py',
        obfuscated_dir / 'fibonacci_original.py',
        obfuscated_dir / 'fibonacci_renamed.py',
    ]

    # Test 1: File Existence
    print_header("Test 1: File Existence Check")
    all_exist = True
    for file_path in all_files:
        if file_path.exists():
            print_success(f"Found: {file_path.relative_to(validation_dir)}")
        else:
            print_error(f"Missing: {file_path.relative_to(validation_dir)}")
            all_exist = False

    if not all_exist:
        print_error("\nSome files are missing! Aborting tests.")
        return 1

    # Test 2: Syntax Validation
    print_header("Test 2: Python Syntax Validation")
    syntax_ok = True
    for file_path in all_files:
        success, error = test_syntax(file_path)
        if success:
            print_success(f"Valid syntax: {file_path.name}")
        else:
            print_error(f"Syntax error in {file_path.name}: {error}")
            syntax_ok = False

    # Test 3: File Metrics
    print_header("Test 3: File Size and Line Count")
    for file_path in all_files:
        lines = count_lines(file_path)
        size = get_file_size(file_path)
        status = "✓" if 15 <= lines <= 100 else "⚠"
        color = Colors.GREEN if 15 <= lines <= 100 else Colors.YELLOW
        print(f"{color}{status} {file_path.name:30} - {lines:3} lines, {size:4} bytes{Colors.END}")

    # Test 4: Code Execution
    print_header("Test 4: Code Execution Test")
    execution_ok = True
    for file_path in all_files:
        success, error, output = execute_file(file_path)
        if success:
            print_success(f"{file_path.name}: {output}")
        else:
            print_error(f"{file_path.name}: Execution failed - {error}")
            execution_ok = False

    # Test 5: Similarity Testing
    print_header("Test 5: Similarity Score Validation")

    similarity_tests = [
        # (file1, file2, (min, max), description)
        (
            plagiarized_dir / 'factorial_original.py',
            plagiarized_dir / 'factorial_copied.py',
            (0.95, 1.00),
            "Plagiarized Pair: Exact Copy (SHOULD DETECT)"
        ),
        (
            legitimate_dir / 'factorial_recursive.py',
            legitimate_dir / 'factorial_iterative.py',
            (0.30, 0.65),
            "Legitimate Pair: Different Approaches (SHOULD NOT DETECT)"
        ),
        (
            obfuscated_dir / 'fibonacci_original.py',
            obfuscated_dir / 'fibonacci_renamed.py',
            (0.60, 0.85),
            "Obfuscated Pair: Variable Renaming (AST SHOULD DETECT)"
        ),
    ]

    similarity_results = []
    for file1, file2, expected_range, description in similarity_tests:
        result = test_similarity(file1, file2, expected_range, description)
        similarity_results.append(result)

    # Test 6: Cross-Category Comparisons
    print_header("Test 6: Cross-Category Validation")

    cross_tests = [
        (
            plagiarized_dir / 'factorial_original.py',
            legitimate_dir / 'factorial_recursive.py',
            (0.30, 0.70),
            "Original vs Recursive (Different approaches, similar problem)"
        ),
        (
            plagiarized_dir / 'factorial_original.py',
            legitimate_dir / 'factorial_iterative.py',
            (0.40, 0.75),
            "Original vs Independent Iterative (Similar approach, different code)"
        ),
    ]

    for file1, file2, expected_range, description in cross_tests:
        test_similarity(file1, file2, expected_range, description)

    # Final Summary
    print_header("Test Summary")

    total_tests = 3  # existence, syntax, similarity
    passed_tests = 0

    if all_exist:
        print_success("File Existence: PASSED")
        passed_tests += 1
    else:
        print_error("File Existence: FAILED")

    if syntax_ok:
        print_success("Syntax Validation: PASSED")
        passed_tests += 1
    else:
        print_error("Syntax Validation: FAILED")

    if execution_ok:
        print_success("Code Execution: PASSED")
    else:
        print_warning("Code Execution: Some files failed")

    if all(similarity_results):
        print_success("Similarity Tests: PASSED")
        passed_tests += 1
    else:
        print_error("Similarity Tests: FAILED (some out of expected range)")

    print(f"\n{Colors.BOLD}Overall: {passed_tests}/{total_tests} test suites passed{Colors.END}")

    if passed_tests == total_tests:
        print_success("\n🎉 All validation tests passed!")
        return 0
    else:
        print_error("\n❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
