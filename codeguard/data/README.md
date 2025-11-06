# Data Directory

Runtime data storage for uploads, results, and database.

## Structure

```
data/
├── uploads/          # Temporary uploaded files
├── results/          # Analysis result JSON files
└── codeguard.db      # SQLite database
```

## Subdirectories

### `uploads/`
Temporary storage for uploaded Python files during analysis.

**Characteristics**:
- Files deleted after 24 hours (configurable)
- Original filenames preserved
- .py files only
- Maximum 16MB per file

### `results/`
Persistent storage for JSON analysis reports.

**Characteristics**:
- One JSON file per analysis job
- Filename format: `analysis_<job_id>_<timestamp>.json`
- Retained for 30 days (configurable)
- Human-readable JSON format

## Database

### `codeguard.db`
SQLite database file containing:
- Analysis job metadata
- Comparison results
- System configuration
- Audit logs (optional)

**Location**: `/app/data/codeguard.db` (in container)

**Backup**:
```bash
# Copy database file
cp data/codeguard.db data/backups/codeguard_backup_$(date +%Y%m%d).db
```

## Docker Volume Mounts

When running in Docker, these directories are mounted from the host:

| Host Path | Container Path |
|-----------|---------------|
| `./data/uploads` | `/app/data/uploads` |
| `./data/results` | `/app/data/results` |
| `./data/codeguard.db` | `/app/data/codeguard.db` |

## Permissions

Ensure correct permissions:

```bash
# Set ownership
chown -R $USER:$USER data/

# Set permissions
chmod -R 755 data/
chmod 644 data/codeguard.db
```

## Cleanup

### Manual Cleanup

```bash
# Remove old uploads (>24 hours)
find data/uploads/ -type f -mtime +1 -delete

# Remove old results (>30 days)
find data/results/ -type f -mtime +30 -delete
```

### Automated Cleanup

Cleanup runs automatically on application startup (configurable in `config/config.py`).

## Disk Space Management

Monitor disk usage:

```bash
# Check disk usage
du -sh data/

# By subdirectory
du -sh data/*/

# Files count
find data/ -type f | wc -l
```

## Data Privacy

- All data stored locally
- No external transmission
- Secure file permissions
- Database not accessible outside container
- Temporary files auto-deleted

## Backup Strategy

Recommended backup approach:

1. **Database**: Daily backups
2. **Results**: Weekly backups
3. **Uploads**: No backup needed (temporary)

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backups/codeguard_$DATE.tar.gz data/results/ data/codeguard.db
```

## Recovery

### Database Recovery

```bash
# Stop application
docker-compose down

# Restore backup
cp backups/codeguard_backup.db data/codeguard.db

# Restart application
docker-compose up
```

### Corrupted Database

```bash
# Export data
sqlite3 data/codeguard.db .dump > backup.sql

# Create new database
rm data/codeguard.db
sqlite3 data/codeguard.db < backup.sql
```

## Size Estimates

Typical storage requirements:

- **Upload**: ~1MB per file × 100 files = 100MB
- **Results**: ~10KB per analysis job
- **Database**: ~1MB per 1000 comparisons
- **Total**: ~500MB for active semester

## .gitignore

Data files are excluded from version control:

```gitignore
data/uploads/*
data/results/*
data/*.db
!data/*/README.md
```
