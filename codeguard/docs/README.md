# Documentation

Comprehensive documentation for the CodeGuard plagiarism detection system.

## Structure

### `algorithms/`
Detailed algorithm documentation
- Token-based detection methodology
- AST-based structural comparison
- Winnowing hash-based fingerprinting
- Voting system logic
- Performance characteristics

### `user-guide/`
End-user documentation
- Installation instructions
- Quick start guide
- Usage tutorials
- Troubleshooting tips
- FAQ

## Documentation Types

### 1. Technical Documentation (For Developers)
- Architecture overview in `README.md` files throughout codebase
- Component specifications in `src/` directories
- Database schema in `src/database/`
- Configuration options in `config/`
- Testing guidelines in `tests/README.md`
- [CLAUDE.md](../CLAUDE.md) - Developer guidance for future AI assistance

### 2. Algorithm Documentation (For Researchers)
- Detection method descriptions in `algorithms/`
- Mathematical foundations
- Implementation details
- Parameter tuning
- Performance analysis
- References to academic papers

### 3. User Documentation (For Instructors)
- Installation guide
- Usage instructions
- Interpreting results
- Best practices
- Common scenarios
- Troubleshooting

### 4. Architecture Documentation
- [Technical Decisions Log](../technicalDecisionsLog.md) - Major architecture decisions
- Framework migration rationale
- Design patterns and tradeoffs

## Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](user-guide/installation.md) - Setup instructions
- [Quick Start Tutorial](user-guide/quick-start.md) - First analysis

### Algorithm Details
- [Token Detection](algorithms/token-detection.md) - Lexical analysis
- [AST Detection](algorithms/ast-detection.md) - Structural comparison
- [Winnowing Algorithm](algorithms/winnowing-algorithm.md) - Hash-based fingerprinting

### Architecture & Decisions
- [Technical Decisions Log](../technicalDecisionsLog.md) - Architecture decisions
- [CLAUDE.md](../CLAUDE.md) - Developer guidance

### Troubleshooting
- [Common Issues](user-guide/troubleshooting.md) - Problems and solutions
- [FAQ](user-guide/faq.md) - Frequently asked questions

## Documentation Standards

### Markdown Format
All documentation uses GitHub-flavored Markdown:
- Clear headings hierarchy
- Code blocks with syntax highlighting
- Tables for structured data
- Links for cross-references

### Code Examples
Include runnable code examples:

```python
from detectors.token_detector import TokenDetector

detector = TokenDetector()
similarity = detector.compare(source1, source2)
print(f"Similarity: {similarity:.2%}")
```

### Diagrams
Use ASCII art for diagrams (Streamlit-compatible):

```
┌─────────────────────┐
│  Streamlit UI       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Detection Engine   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Voting System      │
└─────────────────────┘
```

## Contributing to Documentation

### Adding New Documentation

1. Place files in appropriate directory
2. Follow naming convention: lowercase-with-hyphens.md
3. Add entry to relevant README
4. Include examples and diagrams
5. Cross-reference related docs

### Documentation Checklist

- [ ] Clear, descriptive title
- [ ] Introduction paragraph
- [ ] Structured sections with headings
- [ ] Code examples that work
- [ ] Screenshots where helpful (for user guides)
- [ ] Links to related documentation
- [ ] Correct spelling and grammar

### Style Guide

- **Headings**: Use sentence case
- **Code**: Inline `code` or fenced blocks
- **Emphasis**: *Italic* for emphasis, **bold** for strong
- **Lists**: Ordered for steps, unordered for items
- **Links**: Descriptive text, not "click here"

## Version History

Document version history in each file:

```markdown
---
Version: 1.0
Last Updated: 2024-11-11
Author: CodeGuard Team
---
```

## Accessibility

- Use clear, simple language
- Define technical terms on first use
- Include alt text for images
- Structure content logically
- Use descriptive link text

## Feedback

Documentation improvements welcome:
- Open issue on GitHub
- Suggest clarifications
- Report errors or outdated info
- Contribute examples

## Maintenance

Regular documentation updates:
- Review for accuracy when code changes
- Update with new features
- Fix broken links
- Incorporate user feedback
- Keep synchronized with implementation

## Notes on Framework Migration

**Important**: This project migrated from Flask to Streamlit. Some documentation may reference Flask-specific features. Updated documentation reflects current Streamlit implementation.

- Old: Flask routes, templates, static files
- New: Streamlit app.py with interactive components

See [Technical Decisions Log](../technicalDecisionsLog.md) for migration details.

## Documentation TODO

- [ ] Complete algorithm implementation documentation
- [ ] Add user guide with screenshots
- [ ] Create troubleshooting guide with common issues
- [ ] Add FAQ section
- [ ] Document deployment to Streamlit Cloud
- [ ] Add video tutorials (optional)
- [ ] Create API documentation if needed
