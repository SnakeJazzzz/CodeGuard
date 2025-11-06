# CodeGuard - Code Plagiarism Detection System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

## Overview

CodeGuard is an intelligent code plagiarism detection system designed to help educators maintain academic integrity in programming courses. Using a multi-method approach combining token-based, AST-based, and hash-based detection techniques with a weighted voting system, CodeGuard achieves approximately 85-90% accuracy in identifying code plagiarism while minimizing false positives.

## Key Features

- **Multi-Method Detection**: Three complementary algorithms working together
  - Token-Based: Lexical similarity analysis (Jaccard & Cosine)
  - AST-Based: Structural comparison via Abstract Syntax Trees
  - Hash-Based: Winnowing algorithm for partial copy detection

- **Weighted Voting System**: Intelligent aggregation with configurable thresholds
  - AST detection: 2.0x weight (most reliable)
  - Hash detection: 1.5x weight (partial copies)
  - Token detection: 1.0x weight (baseline)

- **Privacy-First**: Complete local processing, no external data transmission

- **Easy Deployment**: Single-command Docker deployment across platforms

- **User-Friendly**: Web interface with drag-and-drop upload and real-time progress

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM, 10GB disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/codeguard.git
cd codeguard

# Start CodeGuard
docker-compose up
```

Access the web interface at `http://localhost:5000`

### Basic Usage

1. Open your browser to `http://localhost:5000`
2. Drag and drop Python files (minimum 2 files)
3. Click "Analyze for Plagiarism"
4. Review results with confidence scores
5. Download JSON report for records

## Project Structure

```
codeguard/
├── src/                    # Source code
│   ├── detectors/         # Detection algorithms
│   ├── web/               # Flask web application
│   ├── database/          # Database layer
│   ├── voting/            # Voting system
│   └── utils/             # Utility functions
├── tests/                 # Test suite (pytest)
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── config/                # Configuration files
├── docker/                # Docker configuration
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── algorithms/        # Algorithm details
│   └── user-guide/        # User guide
├── data/                  # Runtime data
│   ├── uploads/           # Temporary uploads
│   └── results/           # Analysis results
├── static/                # Web assets
├── templates/             # Jinja2 templates
├── scripts/               # Utility scripts
└── validation-datasets/   # Test datasets
```

## Success Metrics

- **Precision**: ≥85%
- **Recall**: ≥80%
- **F1 Score**: ≥82%
- **False Positive Rate**: ≤10%
- **Processing Speed**: <2 minutes for 50 files
- **Test Coverage**: ≥80%

## Development

### Setup Development Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/ --cov=src --cov-report=html
```

### Running Tests

```bash
# All tests
./scripts/run_tests.sh

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Coverage report
pytest --cov=src --cov-report=term-missing
```

## Documentation

- [Installation Guide](docs/user-guide/installation.md)
- [Quick Start Guide](docs/user-guide/quick-start.md)
- [API Documentation](docs/api/endpoints.md)
- [Algorithm Details](docs/algorithms/)
- [Troubleshooting](docs/user-guide/troubleshooting.md)

## Technology Stack

- **Language**: Python 3.11
- **Web Framework**: Flask 3.0
- **Database**: SQLite
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest, pytest-cov
- **Platform**: Cross-platform (Windows, Mac, Linux)

## Authors

- Michael Andrew Devlyn Roach (A01781041)
- Roberto Castro Soto (A01640117)

Instituto Tecnológico y de Estudios Superiores de Monterrey

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Winnowing algorithm: Schleimer, Wilkerson, and Aiken (2003)
- Python AST module documentation
- Flask and Docker communities

## Support

For issues and questions:
- Open an issue on GitHub
- Consult the [troubleshooting guide](docs/user-guide/troubleshooting.md)
- Review [API documentation](docs/api/endpoints.md)
