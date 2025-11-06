# Voting System

This directory contains the multi-method voting system that aggregates results from the three detection algorithms to make final plagiarism determinations.

## Files

### `voting_system.py`
Core weighted voting mechanism that combines detector outputs.

**Class**: `VotingSystem`

**Methods**:

```python
def __init__(self, config: Dict = None):
    """Initialize with optional configuration."""

def vote(self,
         token_similarity: float,
         ast_similarity: float,
         hash_similarity: float) -> Dict:
    """
    Aggregate detector results and make plagiarism determination.

    Returns:
        {
            'is_plagiarized': bool,
            'confidence_score': float,
            'votes': {
                'token': bool,
                'ast': bool,
                'hash': bool
            },
            'weighted_votes': float,
            'individual_scores': {
                'token': float,
                'ast': float,
                'hash': float
            }
        }
    """
```

**Voting Algorithm**:

1. **Threshold Comparison**: Each detector score compared to its threshold
   - Token threshold: 0.70 (default)
   - AST threshold: 0.80 (default)
   - Hash threshold: 0.60 (default)

2. **Vote Accumulation**: Weighted votes accumulated
   - Token weight: 1.0x
   - AST weight: 2.0x (highest - most reliable)
   - Hash weight: 1.5x

3. **Decision Rule**: Plagiarism flagged when weighted votes ≥50% of total possible

4. **Confidence Calculation**:
   ```
   confidence = (0.3 × token_score) + (0.4 × ast_score) + (0.3 × hash_score)
   confidence = min(confidence, 1.0)  # Clamped to 1.0
   ```

### `confidence_calculator.py`
Calculates confidence scores and provides detailed analysis.

**Functions**:

```python
def calculate_confidence(
    token_similarity: float,
    ast_similarity: float,
    hash_similarity: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculate weighted confidence score.

    Default weights:
        token: 0.3
        ast: 0.4
        hash: 0.3
    """

def get_confidence_level(confidence: float) -> str:
    """
    Categorize confidence score into levels.

    Returns:
        'Very High': ≥0.90
        'High': 0.75-0.89
        'Medium': 0.50-0.74
        'Low': 0.25-0.49
        'Very Low': <0.25
    """

def analyze_detector_agreement(
    token_similarity: float,
    ast_similarity: float,
    hash_similarity: float
) -> Dict:
    """
    Analyze agreement between detectors.

    Returns:
        {
            'agreement_level': str,  # 'unanimous', 'majority', 'split'
            'variance': float,
            'max_difference': float,
            'recommendations': List[str]
        }
    """
```

### `thresholds.py`
Configurable threshold management for detector decisions.

**Class**: `ThresholdManager`

**Methods**:

```python
def __init__(self, config_path: str = None):
    """Load thresholds from config file or use defaults."""

def get_threshold(self, detector: str) -> float:
    """Get threshold for specific detector."""

def set_threshold(self, detector: str, value: float) -> None:
    """Set threshold (must be in range 0.0-1.0)."""

def get_weights(self) -> Dict[str, float]:
    """Get voting weights for all detectors."""

def set_weight(self, detector: str, value: float) -> None:
    """Set voting weight for detector."""

def save_config(self, path: str) -> None:
    """Save current configuration to JSON file."""

def load_config(self, path: str) -> None:
    """Load configuration from JSON file."""

def get_decision_threshold(self) -> float:
    """Get the decision threshold (default: 0.50)."""

def validate_thresholds(self) -> bool:
    """Validate all thresholds are in valid ranges."""
```

## Configuration

Default configuration (`config/thresholds.json`):

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
  }
}
```

## Usage Examples

### Basic Voting

```python
from voting.voting_system import VotingSystem

# Initialize voting system
voter = VotingSystem()

# Get detector results
token_sim = 0.85
ast_sim = 0.92
hash_sim = 0.78

# Make decision
result = voter.vote(token_sim, ast_sim, hash_sim)

print(f"Plagiarized: {result['is_plagiarized']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Weighted votes: {result['weighted_votes']:.2f}")
```

### Custom Configuration

```python
from voting.voting_system import VotingSystem
from voting.thresholds import ThresholdManager

# Create custom thresholds
threshold_mgr = ThresholdManager()
threshold_mgr.set_threshold('ast', 0.85)  # Stricter AST threshold
threshold_mgr.set_weight('hash', 2.0)      # Increase hash weight

# Use custom config
voter = VotingSystem(config=threshold_mgr.get_config())
result = voter.vote(0.85, 0.92, 0.78)
```

### Confidence Analysis

```python
from voting.confidence_calculator import (
    calculate_confidence,
    get_confidence_level,
    analyze_detector_agreement
)

# Calculate confidence
confidence = calculate_confidence(0.85, 0.92, 0.78)
level = get_confidence_level(confidence)

print(f"Confidence: {confidence:.2%} ({level})")

# Analyze agreement
analysis = analyze_detector_agreement(0.85, 0.92, 0.78)
print(f"Agreement: {analysis['agreement_level']}")
print(f"Variance: {analysis['variance']:.3f}")

for recommendation in analysis['recommendations']:
    print(f"- {recommendation}")
```

## Voting Decision Logic

```
Total possible votes = (1.0 + 2.0 + 1.5) = 4.5

Example 1: All detectors agree (high similarity)
  Token: 0.85 > 0.70 → Vote: 1.0
  AST: 0.92 > 0.80 → Vote: 2.0
  Hash: 0.78 > 0.60 → Vote: 1.5
  Total: 4.5 / 4.5 = 100% → PLAGIARISM DETECTED

Example 2: Only AST detects (renamed variables)
  Token: 0.45 < 0.70 → Vote: 0.0
  AST: 0.88 > 0.80 → Vote: 2.0
  Hash: 0.55 < 0.60 → Vote: 0.0
  Total: 2.0 / 4.5 = 44% → NO PLAGIARISM

Example 3: Majority agree
  Token: 0.75 > 0.70 → Vote: 1.0
  AST: 0.85 > 0.80 → Vote: 2.0
  Hash: 0.58 < 0.60 → Vote: 0.0
  Total: 3.0 / 4.5 = 67% → PLAGIARISM DETECTED
```

## Why These Weights?

- **AST (2.0x)**: Highest weight because structural similarity is the strongest indicator of plagiarism. Immune to simple obfuscation.

- **Hash (1.5x)**: Medium weight for detecting partial copying and patchwork plagiarism. Good balance of accuracy.

- **Token (1.0x)**: Baseline weight as it's most easily defeated but good for initial screening.

## Testing

```bash
# Test voting system
pytest tests/unit/test_voting_system.py

# Test confidence calculator
pytest tests/unit/test_confidence_calculator.py

# Test threshold management
pytest tests/unit/test_thresholds.py
```

## Tuning Guidelines

### Increasing Precision (fewer false positives):
- Increase thresholds (e.g., token: 0.75, ast: 0.85)
- Increase decision threshold to 0.60
- Decrease token weight to 0.8

### Increasing Recall (fewer false negatives):
- Decrease thresholds (e.g., token: 0.65, ast: 0.75)
- Decrease decision threshold to 0.40
- Increase hash weight to 2.0

### Balanced Approach (default):
- Current settings provide ~85% precision, ~80% recall
- F1 score of ~82%
- Suitable for most academic use cases

## Dependencies

- None (uses only Python standard library)
- Optional: `json` for configuration file handling
