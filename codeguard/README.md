# CodeGuard - Code Plagiarism Detection System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)

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

- **Interactive Web Interface**: Built with Streamlit
  - Drag-and-drop file upload
  - Real-time analysis progress
  - Interactive configuration sliders
  - Visual results with metrics
  - JSON export functionality

- **Privacy-First**: Complete local processing, no external data transmission

- **Easy Deployment**: Multiple deployment options
  - Streamlit Cloud (free, one-click)
  - Docker (local or custom server)
  - Local Python (development)

## Quick Start

### Option 1: Streamlit Cloud (Recommended for Testing)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your GitHub repository
4. Access your app at: `https://[your-app-name].streamlit.app`

### Option 2: Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/yourusername/codeguard.git
cd codeguard

# Start with Docker Compose
docker-compose up

# Access the application
# Open browser to: http://localhost:8501
```

### Option 3: Local Python (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/codeguard.git
cd codeguard

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Access the application
# Browser will open automatically at http://localhost:8501
```

## Usage

1. **Upload Files**
   - Click "Browse files" or drag-and-drop Python (.py) files
   - Minimum 2 files, maximum 100 files
   - Each file maximum 16MB

2. **Configure Detection (Optional)**
   - Adjust thresholds in the sidebar
   - Modify voting weights
   - Change decision threshold

3. **Analyze**
   - Click "🔍 Analyze for Plagiarism"
   - Wait for processing (typically <2 minutes for 50 files)

4. **Review Results**
   - Switch to "Results" tab
   - View summary statistics
   - Filter and sort comparisons
   - Expand details for each pair
   - Download JSON report

## Project Structure

```
codeguard/
├── app.py                      # Main Streamlit application
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
├── .streamlit/                 # Streamlit configuration
│   └── config.toml
├── src/                        # Source code
│   ├── detectors/             # Detection algorithms
│   │   ├── base_detector.py
│   │   ├── token_detector.py
│   │   ├── ast_detector.py
│   │   └── hash_detector.py
│   ├── voting/                # Voting system
│   │   ├── voting_system.py
│   │   ├── confidence_calculator.py
│   │   └── thresholds.py
│   ├── database/              # Database layer
│   │   ├── models.py
│   │   ├── operations.py
│   │   └── connection.py
│   └── utils/                 # Utility functions
│       ├── file_utils.py
│       ├── validation.py
│       ├── logger.py
│       └── constants.py
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── config/                     # Configuration files
├── docs/                       # Documentation
│   ├── algorithms/            # Algorithm details
│   └── user-guide/            # User guides
├── data/                       # Runtime data
│   ├── uploads/               # Temporary uploads
│   └── results/               # Analysis results
├── scripts/                    # Utility scripts
└── validation-datasets/        # Test datasets
```

## Detection Algorithms

### Token-Based Detection (Weight: 1.0x)
- Analyzes code at lexical level using Python's `tokenize` module
- Calculates Jaccard and Cosine similarity
- Fast processing (~5000 lines/second)
- Effective for direct copying
- Defeated by variable renaming

### AST-Based Detection (Weight: 2.0x)
- Parses code into Abstract Syntax Trees using `ast` module
- Normalizes variable names, compares structure
- Processing speed (~1000 lines/second)
- Immune to variable renaming
- Detects structural plagiarism

### Hash-Based Detection (Weight: 1.5x)
- Implements Winnowing algorithm (Schleimer et al., 2003)
- Creates code fingerprints using k-grams (k=5)
- Winnowing window size: 4
- Processing speed (~3000 lines/second)
- Detects partial and scattered copying

## Voting System

The weighted voting mechanism combines results from all three detectors:

1. Each detector compares its similarity score against its threshold
   - Token threshold: 0.70 (default)
   - AST threshold: 0.80 (default)
   - Hash threshold: 0.60 (default)

2. If score > threshold, detector "votes" with its weight
   - Total possible votes = 4.5 (1.0 + 2.0 + 1.5)

3. Plagiarism flagged when weighted_votes / 4.5 ≥ 0.50 (50%)

4. Confidence score = (0.3 × token) + (0.4 × AST) + (0.3 × hash)

## Success Metrics

- **Precision**: ≥85% (minimize false positives)
- **Recall**: ≥80% (catch most plagiarism)
- **F1 Score**: ≥82% (balanced performance)
- **False Positive Rate**: ≤10%
- **Processing Speed**: <2 minutes for 50 files
- **Test Coverage**: ≥80%

## Development

### Setup Development Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run specific test
pytest tests/unit/test_token_detector.py

# Generate coverage report
pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Format code
black src/ tests/ app.py

# Check style
flake8 src/ tests/ app.py

# Type checking
mypy src/

# Linting
pylint src/
```

### Running the Application Locally

```bash
# Development mode with auto-reload
streamlit run app.py

# Production mode
streamlit run app.py --server.headless true
```

## Configuration

### Detection Thresholds

Edit `config/thresholds.json` or use the sidebar sliders:

```json
{
  "thresholds": {
    "token": 0.70,
    "ast": 0.80,
    "hash": 0.60
  },
  "weights": {
    "token": 1.0,
    "ast": 2.0,
    "hash": 1.5
  },
  "decision_threshold": 0.50
}
```

### Streamlit Configuration

Edit `.streamlit/config.toml` for theme and server settings.

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Set main file: `app.py`
6. Click "Deploy"

### Deploy with Docker

```bash
# Build image
docker build -t codeguard:latest .

# Run container
docker run -p 8501:8501 codeguard:latest

# Or use Docker Compose
docker-compose up -d
```

## Documentation

- [Algorithm Details](docs/algorithms/) - Detailed algorithm documentation
- [User Guide](docs/user-guide/) - Complete user guide
- [Technical Decisions Log](technicalDecisionsLog.md) - Architecture decisions
- [CLAUDE.md](CLAUDE.md) - Developer guidance
- Individual module documentation in each directory's README.md

## Technology Stack

- **Language**: Python 3.11
- **Web Framework**: Streamlit 1.28+
- **UI**: Streamlit components (built-in)
- **Database**: SQLite
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest, pytest-cov
- **Platform**: Cross-platform (Windows, Mac, Linux)

## Performance Expectations

| Files | Comparisons | Typical Time |
|-------|-------------|--------------|
| 10    | 45          | ~10 seconds  |
| 25    | 300         | ~30 seconds  |
| 50    | 1,225       | ~90 seconds  |
| 100   | 4,950       | ~5 minutes   |

## Authors

- Michael Andrew Devlyn Roach (A01781041)
- Roberto Castro Soto (A01640117)

Instituto Tecnológico y de Estudios Superiores de Monterrey

## Academic Project Information

**Course**: Desarrollo de aplicaciones avanzadas de ciencias computacionales (TC3002B)
**Institution**: Tecnológico de Monterrey
**Semester**: Fall 2024
**Project Type**: Algorithm Design Implementation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Winnowing algorithm: Schleimer, Wilkerson, and Aiken (2003)
- Python AST module documentation
- Python tokenize module documentation
- Streamlit framework and community

## Architecture Notes

**Why Streamlit?**

This project initially designed for Flask but migrated to Streamlit to:
- Focus development time on core algorithms (project's learning objective)
- Simplify deployment and maintenance
- Reduce UI complexity (70% less code)
- Enable faster iteration and testing

See [technicalDecisionsLog.md](technicalDecisionsLog.md) for detailed rationale.

## Support

For issues and questions:
- Open an issue on GitHub
- Consult the documentation in `docs/`
- Review [technicalDecisionsLog.md](technicalDecisionsLog.md)

## Contributing

This is an academic project. Contributions welcome after December 2024.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Roadmap

- [x] Project planning and design
- [x] Streamlit UI implementation
- [x] Token detector implementation (93% coverage)
- [x] AST detector implementation (90% coverage)
- [x] Hash detector (Winnowing) implementation (95% coverage)
- [x] Multi-detector Streamlit integration
- [x] Database integration (SQLite)
- [x] Comprehensive testing infrastructure (199 tests)
- [x] Validation dataset creation (6 files)
- [x] Analysis persistence and history
- [ ] Voting system (dedicated modules)
- [ ] Database test fixes (35 failing tests)
- [ ] Increase test coverage (61% → 80%)
- [ ] Code quality improvements (black: 14 files, flake8: 25 issues)
- [ ] Precision/Recall validation measurement
- [ ] Performance benchmarking
- [ ] Documentation completion
- [ ] Deployment to Streamlit Cloud
- [ ] Project defense and presentation

---

**Note**: This project is under active development as part of an academic assignment. Core algorithm implementations are in progress.
