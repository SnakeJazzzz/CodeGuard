# User Guide

Complete user guide for instructors and educators using CodeGuard.

## Files

### `installation.md`
Step-by-step installation instructions.

**Contents**:
- System requirements (Docker, hardware)
- Installing Docker on Windows/Mac/Linux
- Downloading CodeGuard
- First-time setup
- Verification steps
- Common installation issues

### `quick-start.md`
Quick start tutorial for first-time users.

**Contents**:
- Starting the application
- Uploading files
- Understanding results
- Downloading reports
- Stopping the application
- Your first analysis walkthrough

### `troubleshooting.md`
Common issues and solutions.

**Contents**:
- Docker issues (port conflicts, permission errors)
- File upload errors (size limits, invalid files)
- Analysis failures (syntax errors, timeouts)
- Performance problems (slow analysis, high memory)
- Database errors (locked database, corruption)
- Web interface issues (connection refused, blank page)

## Quick Reference

### Starting CodeGuard

```bash
cd codeguard
docker-compose up
```

Access at: http://localhost:5000

### Stopping CodeGuard

```bash
docker-compose down
```

## Common Tasks

### Analyzing Student Submissions

1. Collect all .py files in one folder
2. Open http://localhost:5000
3. Drag and drop files or click to upload
4. Wait for analysis to complete
5. Review results by confidence score
6. Download JSON report for records

### Interpreting Results

**Plagiarism Indicators**:
- Red background: Plagiarism detected (confidence ≥50%)
- High confidence (>80%): Strong evidence of plagiarism
- Medium confidence (50-80%): Investigate further
- Low confidence (<50%): Likely original work

**Similarity Scores**:
- **Token**: Lexical similarity (affected by renaming)
- **AST**: Structural similarity (most reliable)
- **Hash**: Partial copy detection (patchwork plagiarism)

### Best Practices

1. **Analyze entire assignment batches**: Upload all submissions together
2. **Review flagged pairs manually**: System assists but doesn't replace judgment
3. **Consider assignment difficulty**: Simple assignments may have natural similarity
4. **Check for allowed collaboration**: Verify against course policies
5. **Keep reports**: Download JSON for documentation

## System Requirements

### Minimum
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 2-core CPU
- 10GB disk space
- Modern web browser

### Recommended
- 8GB RAM
- 4-core CPU
- 20GB disk space
- Chrome, Firefox, or Edge (latest version)

## File Limits

- **File extension**: .py only
- **File size**: 16MB maximum per file
- **Batch size**: 2-100 files
- **Total upload**: ~1GB per batch

## Performance Expectations

| Files | Comparisons | Typical Time |
|-------|-------------|--------------|
| 10 | 45 | ~10 seconds |
| 25 | 300 | ~30 seconds |
| 50 | 1,225 | ~90 seconds |
| 100 | 4,950 | ~5 minutes |

## Getting Help

1. Check [troubleshooting.md](troubleshooting.md)
2. Review [FAQ section](#faq)
3. Check Docker logs: `docker-compose logs`
4. Open GitHub issue with details

## FAQ

**Q: Can I analyze non-Python code?**
A: Currently only Python (.py) files are supported.

**Q: How accurate is the detection?**
A: ~85% precision, ~80% recall based on validation testing.

**Q: Are my files stored anywhere?**
A: All processing is local. Files are temporarily stored only on your machine.

**Q: Can students defeat the detection?**
A: Simple obfuscation (renaming) is detected. Heavy algorithmic changes may not be detected.

**Q: How do I report false positives?**
A: Review the individual detector scores. Consider adjusting thresholds in config.

**Q: Can I run multiple analyses simultaneously?**
A: Yes, each analysis gets a unique job ID and results are isolated.
