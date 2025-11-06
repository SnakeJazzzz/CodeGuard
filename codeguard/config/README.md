# Configuration

This directory contains configuration files for the CodeGuard application.

## Files

### `config.py`
Base configuration class with shared settings.

```python
class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Directory paths
    UPLOAD_FOLDER = '/app/data/uploads'
    RESULTS_FOLDER = '/app/data/results'
    DATABASE_PATH = '/app/data/codeguard.db'

    # File upload settings
    ALLOWED_EXTENSIONS = {'.py'}
    MAX_FILES_PER_UPLOAD = 100
    MIN_FILES_PER_UPLOAD = 2

    # Processing settings
    PROCESSING_TIMEOUT = 120  # seconds
```

### `development.py`
Development environment configuration.

```python
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = '/app/logs/codeguard-dev.log'

    # Database
    DATABASE_ECHO = True  # Echo SQL queries

    # Performance
    ENABLE_PROFILING = True
```

### `production.py`
Production environment configuration.

```python
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/app/logs/codeguard-prod.log'

    # Database
    DATABASE_ECHO = False

    # Performance
    ENABLE_PROFILING = False

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
```

### `thresholds.json`
Detection algorithm thresholds and voting weights.

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
  "decision_threshold": 0.50,
  "confidence_weights": {
    "token": 0.3,
    "ast": 0.4,
    "hash": 0.3
  },
  "winnowing": {
    "kgram_size": 5,
    "window_size": 4
  }
}
```

## Usage

### Loading Configuration

```python
from config.config import Config
from config.development import DevelopmentConfig
from config.production import ProductionConfig
import os

# Select configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')

if env == 'production':
    app.config.from_object(ProductionConfig)
elif env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)
```

### Environment Variables

Set environment-specific values:

```bash
# Development
export FLASK_ENV=development
export SECRET_KEY=dev-key-for-testing

# Production
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_PATH=/data/production/codeguard.db
```

### Threshold Configuration

Load and modify thresholds:

```python
from voting.thresholds import ThresholdManager

# Load from config file
threshold_mgr = ThresholdManager('config/thresholds.json')

# Modify at runtime
threshold_mgr.set_threshold('ast', 0.85)
threshold_mgr.set_weight('hash', 2.0)

# Save modified configuration
threshold_mgr.save_config('config/thresholds_custom.json')
```

## Configuration Hierarchy

```
Config (base)
├── DevelopmentConfig
├── ProductionConfig
└── TestingConfig
```

## Threshold Tuning

### For Higher Precision (fewer false positives):
```json
{
  "thresholds": {
    "token": 0.75,
    "ast": 0.85,
    "hash": 0.65
  },
  "decision_threshold": 0.60
}
```

### For Higher Recall (fewer false negatives):
```json
{
  "thresholds": {
    "token": 0.65,
    "ast": 0.75,
    "hash": 0.55
  },
  "decision_threshold": 0.40
}
```

## Security Considerations

1. **Secret Key**: Never commit production secret keys to version control
2. **Paths**: Use absolute paths in Docker environment
3. **File Size Limits**: Prevent denial of service attacks
4. **Debug Mode**: Always disable in production

## Configuration Best Practices

- Use environment variables for sensitive data
- Keep configuration files in version control (except secrets)
- Document all configuration options
- Use different configurations for dev/test/prod
- Validate configuration on application startup
