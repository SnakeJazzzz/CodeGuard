# Upload Directory

Temporary storage for uploaded Python files during analysis.

## Purpose

This directory stores student submission files temporarily during the plagiarism detection analysis process.

## Characteristics

- **Retention**: Files automatically deleted after 24 hours
- **File Types**: Python (.py) files only
- **Size Limit**: 16MB maximum per file
- **Naming**: Original filenames preserved
- **Access**: Container-only (mounted from Docker volume)

## Usage

Files are automatically managed by the application:

1. User uploads files via web interface
2. Files saved to this directory with original names
3. Analysis performed on uploaded files
4. Files automatically cleaned up after 24 hours

## Manual Cleanup

If needed, manually remove old files:

```bash
# Remove all uploaded files
rm -f data/uploads/*.py

# Remove files older than 24 hours
find data/uploads/ -name "*.py" -mtime +1 -delete
```

## Storage Location

- **Host**: `./data/uploads/`
- **Container**: `/app/data/uploads/`

## Security

- Directory not web-accessible
- Files processed within container
- No external network access
- Automatic cleanup prevents data accumulation

## Troubleshooting

**Permission denied errors**:
```bash
chmod 755 data/uploads/
```

**Disk space issues**:
```bash
# Check space
df -h data/uploads/

# Force cleanup
rm -f data/uploads/*.py
```

## Notes

- This directory should remain empty between analyses
- Large files (>16MB) are rejected during upload
- Only .py extension files are accepted
- Files are read-only after upload (no modification)
