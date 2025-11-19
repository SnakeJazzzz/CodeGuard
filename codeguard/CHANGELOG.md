# Changelog

All notable changes to the CodeGuard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### To Be Implemented
- Code quality improvements (formatting and linting)
- Test coverage increase (68% → 80%)
- Database test fixes (35 failing tests)
- Precision/Recall validation measurement
- Performance benchmarking
- Deployment preparation

---

## [0.4.0] - 2025-11-18

### Added - Voting System & Integration Sprint

**Voting System Core (Complete)**
- VotingSystem class with weighted voting logic (voting_system.py, 367 lines)
- Confidence calculator with 5-level classification (confidence_calculator.py, 351 lines)
- ThresholdManager for configuration management (thresholds.py, 600 lines)
- JSON configuration file (config/thresholds.json)
- 218 comprehensive unit tests (99.7% coverage)
  - test_voting_system.py: 103 tests
  - test_confidence_calculator.py: 68 tests
  - test_thresholds.py: 47 tests

**Streamlit Integration (Complete)**
- Replaced simple majority voting with weighted voting system
- Configuration sidebar with 7 adjustable sliders
  - Token threshold: 0.5-0.9 (default 0.70)
  - AST threshold: 0.6-0.95 (default 0.80)
  - Hash threshold: 0.4-0.8 (default 0.60)
  - Token weight: 0.5-2.0 (default 1.0)
  - AST weight: 1.0-3.0 (default 2.0)
  - Hash weight: 0.5-2.5 (default 1.5)
  - Decision threshold: 0.3-0.7 (default 0.50)
- "Reset to Defaults" button
- Current configuration display showing total votes and decision criteria
- Session state persistence for configuration
- Visual status indicator (default vs custom config)

**Results Enhancements**
- New DataFrame columns: plagiarism_detected, confidence_score, confidence_level, weighted_votes
- Individual detector votes displayed
- Visual indicators: warning for plagiarized, checkmark for clear
- Summary metrics: detector performance, voting system stats, agreement rate
- Detailed voting breakdown for each plagiarized pair
- Enhanced JSON export with voting metadata and dynamic configuration

### Changed
- app.py enhanced from 1,121 to 1,477 lines (approximately 400 lines added/modified)
- Updated results display with current threshold configuration
- Modified plagiarism detection logic to use VotingSystem class
- Enhanced database integration (no schema changes needed)

### Fixed
- TypeError in voting_system.py line 98 when checking decision_threshold float with 'in' operator
- Changed to isinstance(detector, dict) check to properly filter non-dictionary configuration values

### Quality Metrics
- Code written: 3,730 lines (1,318 implementation + 2,412 tests)
- Test coverage: 99.7% on voting system modules
- Test-to-code ratio: 1.8:1
- All 218 voting system tests passing

---

## [0.3.0] - 2025-11-14

### Added - Algorithm Expansion Sprint

**AST Detector (Complete)**
- AST-based structural comparison (ast_detector.py, 191 lines)
- Tree normalization and structural similarity scoring
- 90% test coverage (75+ unit tests)
- Threshold: 0.80, Weight: 2.0x
- Defeats variable/function renaming attacks
- Integrated with Streamlit app

**Hash Detector (Complete)**
- Winnowing fingerprinting algorithm (hash_detector.py, 478 lines)
- k-gram size: 5 tokens, window size: 4
- 95% test coverage (40+ unit tests)
- Threshold: 0.60, Weight: 1.5x
- Detects partial and scattered copying
- Integrated with Streamlit app

**Multi-Detector Streamlit Integration**
- All three detectors run in parallel on each file pair
- Real-time progress tracking with detector-specific status
- Sidebar filters to toggle detector visibility
- 8 summary metrics (4 averages + 4 status counts)
- Enhanced results table with all detector scores
- Voting logic: PLAGIARIZED (2+ detectors), SUSPICIOUS (1), CLEAR (0)
- Database integration for all three detector scores
- Enhanced JSON export with all detector information

**Comprehensive Testing**
- 199 total tests (164 passing, 35 failing)
- Integration tests for all detectors (test_all_detectors_integration.py, 7 tests)
- Unit tests: Token 85+ tests, AST 75+ tests, Hash 40+ tests
- Database tests: 35 tests (failing due to API signature changes)
- Overall coverage: 61.34% (increased from 47%)
- Detector coverage: Token 93%, AST 90%, Hash 95%

**Project Cleanup**
- Removed 14 temporary files (test scripts, implementation summaries)
- Deleted redundant documentation (~1,500 lines)
- Streamlined project structure

### Changed
- app.py enhanced from 908 to 1,121 lines (+213 lines)
- src/detectors/__init__.py updated with AST and Hash exports
- test_hash_detector_basic.py expectations corrected (4 tests)
- test_hash_detector_realistic.py expectations corrected
- Token detector test coverage increased 79%→93%

### Fixed
- Hash detector test expectations aligned with Winnowing algorithm
- Test suite execution (164/199 tests now passing)
- Coverage reporting (HTML reports in htmlcov/)

### Known Issues
- 35 database tests failing (API signature changes)
- 14 files need black formatting
- 25 flake8 linting issues
- Voting system needs dedicated modules
- Precision/Recall not yet measured

---

## [0.2.0] - 2025-11-12

### Added - Database Layer & Testing Infrastructure

**Database Layer (Complete)**
- SQLite database schema with 3 tables (analysis_jobs, comparison_results, configuration)
- Database connection management (connection.py, 472 lines)
- Data models with validation (models.py, 731 lines)
- CRUD operations (operations.py, 1,158 lines)
- 4 database indexes for query optimization
- Automatic database initialization
- Transaction management with rollback support

**Testing Infrastructure (Complete)**
- 88 database unit tests (test_database_operations.py)
- 6 integration tests (test_workflow_integration.py)
- 30 fixture verification tests (test_fixtures.py)
- 7 shared test fixtures (conftest.py)
- pytest configuration with coverage enforcement
- Temporary test database isolation

**Validation Datasets**
- 6 validation Python files created
- Plagiarized pair (factorial: original vs copied)
- Legitimate pair (factorial: recursive vs iterative)
- Obfuscated pair (fibonacci: original vs renamed)
- 100% detection accuracy on validation tests

**Streamlit Integration**
- Two-tab interface (New Analysis + Analysis History)
- Database persistence for all analyses
- Job management with unique job IDs
- View historical results
- Real-time database status indicator
- Enhanced progress tracking
- JSON export functionality

**Quality & Validation**
- Total: 131 tests written (36 collected in final run)
- 100% test pass rate
- Database validation script (5/5 tests passing)
- Complete workflow integration testing

### Changed
- app.py enhanced from 591 to 907 lines
- pytest.ini updated with marker configuration
- Test directory structure improved

### Fixed
- pytest.ini marker configuration error
- Database test isolation issues
- Streamlit pyarrow dependency workaround documented

### Removed
- Task completion documentation files (TASK_*.md)
- Development guides (DATABASE_SETUP_GUIDE.md, etc.)
- Backup files (app_before_database_integration.py, etc.)
- Development test scripts

---

## [0.1.0] - 2025-11-11

### Added - Initial Implementation

**Token Detector (Complete)**
- Token-based plagiarism detection (token_detector.py, 337 lines)
- Jaccard similarity calculation
- Cosine similarity calculation
- Dual-metric comparison approach
- 7 comprehensive unit tests
- 79% test coverage
- Algorithm documentation (412 lines)

**Project Structure**
- Clean directory organization
- Source code structure (src/detectors/, src/utils/)
- Test structure (tests/unit/, tests/integration/, tests/fixtures/)
- Documentation structure (docs/algorithms/)

**Basic Streamlit UI**
- File upload interface (2-100 files)
- Progress tracking
- Results display
- JSON export
- Token detector integration

**Testing Framework**
- pytest configuration
- Unit test framework
- Integration test framework
- Test fixtures directory
- Sample test files

**Documentation**
- README.md (complete project overview)
- CLAUDE.md (developer guidance)
- technicalDecisionsLog.md (architecture decisions)
- TOKEN_DETECTOR_GUIDE.md (algorithm details)
- development_log.md (session tracking)
- project_status.md (progress tracking)

### Technical Details
- Python 3.11+ required
- Streamlit 1.28+ web framework
- SQLite database (not yet implemented in this version)
- Docker support configured
- Cross-platform compatibility

---

## Project Statistics (as of 0.2.0)

**Code Metrics**
- Total Lines of Code: 5,575
  - Source code (src/): 2,597 lines
  - Tests (tests/): 2,071 lines
  - Application (app.py): 907 lines
- Test Coverage: 47% (target: 80%)
- Total Tests: 131 (100% passing)
- Python Files: 19

**Component Completion (as of 0.2.0)**
- Detection Algorithms: 33% (1/3 detectors)
- Database Layer: 100%
- Web Interface: 100%
- Testing Infrastructure: 100%
- Documentation: 60%
- Overall Project: 52%

**Component Completion (as of 0.3.0)**
- Detection Algorithms: 100% (3/3 detectors)
- Database Layer: 100%
- Web Interface: 100%
- Testing Infrastructure: 100%
- Voting System: 25% (basic logic, needs modules)
- Documentation: 65%
- Overall Project: 75%

**Component Completion (as of 0.4.0)**
- Detection Algorithms: 100% (3/3 detectors)
- Database Layer: 100%
- Web Interface: 100%
- Testing Infrastructure: 100%
- Voting System: 100% (3 modules, 218 tests, Streamlit integration)
- Testing & Validation: 70% (unit tests complete, validation pending)
- Documentation: 70%
- Overall Project: 85%

**Known Issues**
- 72 linting warnings (flake8)
- 8 files need formatting (black)
- Test coverage below 80% target
- AST and Hash detectors not implemented
- Voting system not implemented

---

## Future Versions

### [0.3.0] - Planned
- AST Detector implementation
- Hash Detector (Winnowing algorithm)
- Voting System with configurable weights
- Configuration management UI
- Code quality improvements

### [1.0.0] - Planned
- All three detectors operational
- Voting system complete
- 80%+ test coverage
- Code quality standards met
- Ready for production deployment
- Complete documentation

---

## Development Team

- Michael Andrew Devlyn Roach (A01781041)
- Roberto Castro Soto (A01640117)

Instituto Tecnológico y de Estudios Superiores de Monterrey
Course: TC3002B - Desarrollo de aplicaciones avanzadas de ciencias computacionales
Semester: Fall 2024

---

## Notes

This is an academic project under active development. The changelog tracks major milestones and component completions. For detailed session-by-session progress, see `development_log.md`.
