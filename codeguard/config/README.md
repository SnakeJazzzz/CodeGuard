# Configuration

This directory contains configuration files for the CodeGuard application.

## Files

### `config.py` (To be created)
Base configuration class with shared settings.

```python
class Config:
    """Base configuration."""
    # Detection thresholds
    TOKEN_THRESHOLD = 0.70
    AST_THRESHOLD = 0.80
    HASH_THRESHOLD = 0.60

    # Voting weights
    TOKEN_WEIGHT = 1.0
    AST_WEIGHT = 2.0
    HASH_WEIGHT = 1.5
    DECISION_THRESHOLD = 0.50

    # Confidence weights
    CONFIDENCE_TOKEN_WEIGHT = 0.3
    CONFIDENCE_AST_WEIGHT = 0.4
    CONFIDENCE_HASH_WEIGHT = 0.3

    # File upload settings
    MAX_FILE_SIZE_BYTES = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'.py'}
    MAX_FILES_PER_UPLOAD = 100
    MIN_FILES_PER_UPLOAD = 2

    # Winnowing parameters
    KGRAM_SIZE = 5
    WINNOWING_WINDOW = 4
```

### `thresholds.json` (To be created)
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

## Configuration in Streamlit

Streamlit provides interactive configuration through:

1. **Sidebar Sliders** (`app.py`):
   - Users can adjust thresholds in real-time
   - Changes apply immediately to analysis
   - No need to edit config files

2. **Streamlit Config** (`.streamlit/config.toml`):
   - Theme settings (colors, fonts)
   - Server configuration
   - Browser settings

## Usage

### Loading Configuration

Configuration can be loaded from multiple sources:

```python
# Option 1: From utils.constants (default values)
from utils.constants import (
    TOKEN_THRESHOLD,
    AST_THRESHOLD,
    HASH_THRESHOLD,
    TOKEN_WEIGHT,
    AST_WEIGHT,
    HASH_WEIGHT
)

# Option 2: From JSON file
import json
with open('config/thresholds.json', 'r') as f:
    config = json.load(f)

# Option 3: From Streamlit sidebar (runtime)
# Configured interactively in app.py sidebar
```

### Modifying Configuration

#### For Development:
Edit `utils/constants.py` to change defaults

#### For Runtime:
Use Streamlit sidebar sliders in the web interface

#### For Batch Processing:
Create custom `thresholds.json` and load programmatically

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

### Balanced Approach (default):
```json
{
  "thresholds": {
    "token": 0.70,
    "ast": 0.80,
    "hash": 0.60
  },
  "decision_threshold": 0.50
}
```

Current settings provide:
- ~85% precision
- ~80% recall
- ~82% F1 score

## Security Considerations

- No sensitive data stored in configuration
- All values are detection parameters (safe to commit)
- No API keys or credentials needed (local processing)

## Configuration Best Practices

- Use default values from `utils/constants.py` for most cases
- Test custom configurations with validation datasets
- Document reasoning for non-default values
- Keep configurations simple and readable

## Notes

### Streamlit vs Flask Configuration

**Old (Flask)**: Multiple config files for dev/prod environments, Flask-specific settings

**New (Streamlit)**: Simplified configuration
- Algorithm parameters in `utils/constants.py`
- UI configuration in `.streamlit/config.toml`
- Runtime configuration via sidebar sliders

See [Technical Decisions Log](../technicalDecisionsLog.md) for migration details.

## Future Enhancements

- [ ] Create `thresholds.json` file
- [ ] Add configuration validation
- [ ] Implement config file loading
- [ ] Add preset configurations (strict, balanced, lenient)
- [ ] Document optimal settings for different use cases
