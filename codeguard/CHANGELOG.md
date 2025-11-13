# Changelog

All notable changes to the CodeGuard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### To Be Implemented
- AST Detector (structural plagiarism detection)
- Hash Detector (Winnowing algorithm)
- Voting System (weighted aggregation of detectors)
- Configuration management UI
- Code quality improvements (formatting, linting)
- Test coverage increase (47% → 80%)

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

**Component Completion**
- Detection Algorithms: 33% (1/3 detectors)
- Database Layer: 100%
- Web Interface: 100%
- Testing Infrastructure: 100%
- Documentation: 60%
- Overall Project: 52%

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
