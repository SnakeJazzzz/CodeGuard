# Results Directory

Persistent storage for JSON analysis reports.

## Purpose

This directory stores the detailed analysis results for each plagiarism detection job in JSON format.

## File Naming Convention

```
analysis_<job_id>_<timestamp>.json
```

Examples:
- `analysis_20251105_143022.json`
- `analysis_20251106_092145.json`

Where:
- `job_id`: YYYYMMDD_HHMMSS format
- `timestamp`: Creation timestamp

## File Structure

Each JSON file contains:

```json
{
  "job_id": "20251105_143022",
  "created_at": "2025-11-05T14:30:22Z",
  "file_count": 10,
  "pair_count": 45,
  "configuration": {
    "thresholds": {...},
    "weights": {...}
  },
  "results": [
    {
      "file1": "student_a.py",
      "file2": "student_b.py",
      "token_similarity": 0.85,
      "ast_similarity": 0.92,
      "hash_similarity": 0.78,
      "is_plagiarized": true,
      "confidence_score": 0.87,
      "weighted_votes": 4.25
    },
    ...
  ],
  "summary": {
    "plagiarized_count": 3,
    "plagiarism_rate": 0.067,
    "avg_confidence": 0.42
  }
}
```

## Retention Policy

- **Default**: 30 days
- **Configurable**: Set in `config/config.py`
- **Manual cleanup**: See commands below

## Usage

### Viewing Results

```bash
# Pretty print JSON
cat data/results/analysis_20251105_143022.json | jq

# Extract summary only
jq '.summary' data/results/analysis_20251105_143022.json

# Find high-confidence matches
jq '.results[] | select(.confidence_score > 0.8)' data/results/*.json
```

### Finding Specific Results

```bash
# Search by file name
grep -r "student_a.py" data/results/

# Find all plagiarism detections
jq '.results[] | select(.is_plagiarized == true)' data/results/*.json
```

## Cleanup

### Manual Cleanup

```bash
# Remove results older than 30 days
find data/results/ -name "*.json" -mtime +30 -delete

# Remove specific job
rm data/results/analysis_20251105_143022.json

# Archive old results
tar -czf archive/results_$(date +%Y%m).tar.gz data/results/*.json
find data/results/ -name "*.json" -mtime +30 -delete
```

### Automated Cleanup

Cleanup runs automatically on application startup (configurable).

## Backup

Recommended to backup results regularly:

```bash
# Daily backup
cp data/results/*.json backups/results_$(date +%Y%m%d)/

# Weekly compressed backup
tar -czf backups/results_$(date +%Y%W).tar.gz data/results/
```

## Storage Estimates

Typical file sizes:
- Small job (10 files, 45 pairs): ~5-10 KB
- Medium job (50 files, 1,225 pairs): ~50-100 KB
- Large job (100 files, 4,950 pairs): ~200-500 KB

Storage requirements:
- 100 analyses: ~5-10 MB
- 1000 analyses: ~50-100 MB

## Integration

Results can be imported into:
- Spreadsheet applications (Excel, Google Sheets)
- Data analysis tools (Python pandas, R)
- Custom reporting systems
- Learning management systems

## API Access

Results accessible via web interface:

```http
GET /results/<job_id>
GET /download/<job_id>
```

## Security

- Files stored with read-only permissions
- No sensitive student information in filenames
- JSON format allows easy sanitization
- Local storage only (no cloud sync)

## Troubleshooting

**Missing results**:
- Check database for job ID
- Verify file wasn't auto-deleted
- Check Docker volume mounts

**Corrupted JSON**:
- Validate with: `jq . file.json`
- Restore from database if available
- Check application logs for errors
