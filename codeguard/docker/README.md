# Docker Configuration

This directory contains Docker configuration files for containerizing the CodeGuard application.

## Files

### `Dockerfile`
Multi-stage Docker image definition.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY static/ ./static/
COPY templates/ ./templates/
COPY config/ ./config/

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/results /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src.web.app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
```

### `docker-compose.yml`
Docker Compose configuration for easy deployment.

```yaml
version: '3.8'

services:
  codeguard:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: codeguard
    ports:
      - "5000:5000"
    volumes:
      - ../data/uploads:/app/data/uploads
      - ../data/results:/app/data/results
      - ../data/codeguard.db:/app/data/codeguard.db
      - ../logs:/app/logs
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### `.dockerignore`
Files to exclude from Docker build context.

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
.DS_Store
.git/
.gitignore
*.md
!README.md
.env
*.db
data/uploads/*
data/results/*
!data/uploads/README.md
!data/results/README.md
logs/
Docs/
validation-datasets/
tests/
```

## Building and Running

### Build Image

```bash
# Build from docker directory
cd docker
docker build -t codeguard:latest -f Dockerfile ..

# Or build with docker-compose
docker-compose build
```

### Run Container

```bash
# Using docker-compose (recommended)
docker-compose up

# Run in background
docker-compose up -d

# Using docker directly
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data/uploads:/app/data/uploads \
  -v $(pwd)/data/results:/app/data/results \
  --name codeguard \
  codeguard:latest
```

### Stop Container

```bash
# Using docker-compose
docker-compose down

# Using docker
docker stop codeguard
docker rm codeguard
```

## Volume Mounts

The application uses persistent volumes for data storage:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./data/uploads` | `/app/data/uploads` | Temporary file uploads |
| `./data/results` | `/app/data/results` | Analysis result JSON files |
| `./data/codeguard.db` | `/app/data/codeguard.db` | SQLite database |
| `./logs` | `/app/logs` | Application logs |

## Environment Variables

Configure the application via environment variables:

```yaml
environment:
  - FLASK_ENV=production          # development, production, testing
  - SECRET_KEY=your-secret-key    # Session encryption key
  - LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
  - MAX_CONTENT_LENGTH=16777216   # Max upload size (bytes)
```

## Health Check

The container includes a health check endpoint:

```bash
# Check if container is healthy
docker inspect --format='{{.State.Health.Status}}' codeguard

# View health check logs
docker inspect --format='{{json .State.Health}}' codeguard | jq
```

## Development vs Production

### Development Setup

```yaml
# docker-compose.dev.yml
services:
  codeguard:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    volumes:
      - ../src:/app/src  # Live code reload
      - ../data:/app/data
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: python -m flask run --host=0.0.0.0 --port=5000 --reload
```

Run with: `docker-compose -f docker-compose.dev.yml up`

### Production Setup

Uses the standard `docker-compose.yml` with:
- No source code mount (baked into image)
- Production environment
- Auto-restart policy
- Health checks enabled

## Multi-Platform Build

Build for multiple architectures:

```bash
# Setup buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t codeguard:latest \
  -f Dockerfile \
  ..
```

## Optimization

### Reduce Image Size

```dockerfile
# Use alpine base
FROM python:3.11-alpine

# Multi-stage build
FROM python:3.11 AS builder
# Build dependencies
FROM python:3.11-slim AS runtime
# Copy only runtime files
```

### Layer Caching

Order Dockerfile commands by change frequency:
1. System dependencies (rarely change)
2. Python dependencies (change occasionally)
3. Application code (changes frequently)

## Troubleshooting

### View Logs

```bash
# Follow logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs codeguard
```

### Access Container Shell

```bash
# Using docker-compose
docker-compose exec codeguard /bin/bash

# Using docker
docker exec -it codeguard /bin/bash
```

### Debug Build Issues

```bash
# Build with no cache
docker-compose build --no-cache

# Build with progress output
docker-compose build --progress=plain
```

### Common Issues

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use 5001 on host
```

**Permission errors:**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER data/
```

**Database locked:**
```bash
# Ensure SQLite database is not being accessed outside container
docker-compose down
# Remove lock file if exists
rm data/codeguard.db-lock
```

## Security Considerations

1. **Run as non-root user**:
```dockerfile
RUN useradd -m -u 1000 codeguard
USER codeguard
```

2. **Scan for vulnerabilities**:
```bash
docker scan codeguard:latest
```

3. **Use specific base image versions**:
```dockerfile
FROM python:3.11.5-slim  # Not :latest
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Docker Image
  run: |
    docker build -t codeguard:${{ github.sha }} -f docker/Dockerfile .

- name: Push to Registry
  run: |
    docker push codeguard:${{ github.sha }}
```

## Resources

- **CPU**: 2 cores recommended
- **Memory**: 2GB minimum, 4GB recommended
- **Disk**: 10GB for application + data
- **Network**: Port 5000 exposed
