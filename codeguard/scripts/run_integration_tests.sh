#!/bin/bash

# Integration Test Runner for CodeGuard Bug Fix Validation
# Tasks 11-15: Configuration Presets & Bug Fixes Sprint
#
# This script runs all integration tests for bug fixes and generates
# comprehensive reports including coverage metrics.
#
# Usage:
#   ./scripts/run_integration_tests.sh
#
# Options:
#   -v, --verbose    Show detailed test output
#   -c, --coverage   Generate coverage report
#   -h, --help       Show this help message

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
VERBOSE=0
COVERAGE=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -c|--coverage)
            COVERAGE=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-v|--verbose] [-c|--coverage] [-h|--help]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose    Show detailed test output"
            echo "  -c, --coverage   Generate coverage report"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CodeGuard Integration Test Suite${NC}"
echo -e "${BLUE}Bug Fix Validation (Tasks 11-15)${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}ERROR: pytest is not installed${NC}"
    echo "Please install pytest: pip install pytest pytest-cov"
    exit 1
fi

# Test files to run
TEST_FILES=(
    "tests/integration/test_threshold_application.py"
    "tests/integration/test_reset_defaults.py"
    "tests/integration/test_simple_mode_ui.py"
    "tests/integration/test_simple_mode_voting.py"
    "tests/integration/test_voting_display.py"
    "tests/integration/test_end_to_end_flow.py"
)

# Build pytest command
PYTEST_CMD="pytest"
PYTEST_ARGS=""

if [ $VERBOSE -eq 1 ]; then
    PYTEST_ARGS="$PYTEST_ARGS -v -s"
else
    PYTEST_ARGS="$PYTEST_ARGS -v"
fi

if [ $COVERAGE -eq 1 ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=src/core --cov=src/voting --cov-report=html --cov-report=term-missing"
fi

# Add color output
PYTEST_ARGS="$PYTEST_ARGS --color=yes"

# Add short traceback
PYTEST_ARGS="$PYTEST_ARGS --tb=short"

echo -e "${YELLOW}Running integration tests...${NC}\n"

# Run tests
TEST_RESULT=0
for test_file in "${TEST_FILES[@]}"; do
    if [ -f "$test_file" ]; then
        echo -e "${BLUE}Testing: ${test_file}${NC}"
    else
        echo -e "${RED}WARNING: Test file not found: ${test_file}${NC}"
    fi
done

echo ""

# Execute pytest
if $PYTEST_CMD $PYTEST_ARGS "${TEST_FILES[@]}"; then
    TEST_RESULT=0
else
    TEST_RESULT=$?
fi

echo ""
echo -e "${BLUE}========================================${NC}"

# Print summary
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}Bug fixes validated successfully!${NC}"
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}Please review test output above${NC}"
fi

echo -e "${BLUE}========================================${NC}\n"

# Coverage report
if [ $COVERAGE -eq 1 ]; then
    echo -e "${YELLOW}Coverage report generated:${NC}"
    echo -e "  HTML: ${PROJECT_DIR}/htmlcov/index.html"
    echo -e "  Open with: open htmlcov/index.html\n"
fi

# Test summary
echo -e "${BLUE}Test Summary:${NC}"
echo "  Test Files: ${#TEST_FILES[@]}"
echo "  Coverage: $([ $COVERAGE -eq 1 ] && echo 'Enabled' || echo 'Disabled')"
echo "  Verbose: $([ $VERBOSE -eq 1 ] && echo 'Enabled' || echo 'Disabled')"
echo ""

# Recommendations
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}Next Steps:${NC}"
    echo "  1. Review coverage report (if generated)"
    echo "  2. Update bug fix validation documentation"
    echo "  3. Run full test suite: pytest tests/"
    echo "  4. Deploy to staging environment"
else
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Review failing test output above"
    echo "  2. Check bug fix implementation"
    echo "  3. Run individual test: pytest -v <test_file>"
    echo "  4. Enable verbose mode: ./scripts/run_integration_tests.sh -v"
fi

echo ""

exit $TEST_RESULT
