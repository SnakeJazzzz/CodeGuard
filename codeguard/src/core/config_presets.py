"""
Configuration presets for CodeGuard voting system.

This module defines preset configurations optimized for different types of
plagiarism detection scenarios based on comprehensive testing results.

Testing Results:
---------------
Standard Preset (Realistic code, 50+ lines):
- Rock-Paper-Scissors test: 100% precision, 100% recall
- Total possible votes: 4.5
- Decision threshold: 2.25 (50% of total)
- All three detectors enabled with balanced weights

Simple Preset (Constrained problems, <50 lines):
- FizzBuzz test: Improved precision by requiring both detectors
- Total possible votes: 4.0
- Decision threshold: 3.0 (75% of total) - requires BOTH Token AND AST
- Hash detector DISABLED (0% precision on <50 line files)
- AST threshold increased to 0.85 to reduce false positives
- Equal weights (2.0 each) ensure no single detector can flag alone

Key Findings:
------------
1. Hash detector is ineffective on simple problems (<50 lines)
   - Reason: Insufficient code volume for robust fingerprinting
   - Solution: Disable by setting weight to 0.0

2. AST detector too sensitive on simple problems
   - Reason: Limited structural variation in constrained problems
   - Solution: Increase threshold from 0.80 to 0.85

3. Token detector remains reliable across both scenarios
   - Maintained at 0.70 threshold for consistency

Usage:
------
    from src.core.config_presets import get_preset, apply_preset_to_voting_system
    from src.voting.voting_system import VotingSystem

    # Load simple preset for FizzBuzz-like problems
    config = get_preset("simple")
    print(f"Using preset: {config['name']}")

    # Create voting system with preset - use get_preset_config()
    config = get_preset_config("simple")
    voting_system = VotingSystem(config)

    # Or apply preset to existing system
    voting_system = VotingSystem()
    apply_preset_to_voting_system(voting_system, "simple")

    # List available presets
    presets = get_available_presets()
    print(f"Available presets: {presets}")

Preset Selection Guidelines:
---------------------------
Use STANDARD preset when:
- Analyzing realistic assignments (50+ lines)
- Code has sufficient structural complexity
- Multiple functions/classes expected
- Examples: web apps, data processors, games

Use SIMPLE preset when:
- Analyzing constrained problems (<50 lines)
- Limited algorithmic variation expected
- Single-function solutions common
- Examples: FizzBuzz, Fibonacci, palindrome checkers
"""

from typing import Dict, List, Any
import math
import logging

logger = logging.getLogger(__name__)

# Preset name constants
PRESET_STANDARD = "standard"
PRESET_SIMPLE = "simple"

# Standard preset: For typical assignments (50+ lines)
# Uses all three detectors with balanced weights
STANDARD_PRESET = {
    "name": "Standard (Recommended)",
    "description": "For typical assignments (50+ lines). Uses all three detectors with balanced weights.",
    "token": {
        "threshold": 0.70,
        "weight": 1.0,
        "confidence_weight": 0.3
    },
    "ast": {
        "threshold": 0.80,
        "weight": 2.0,
        "confidence_weight": 0.4
    },
    "hash": {
        "threshold": 0.60,
        "weight": 1.5,
        "confidence_weight": 0.3
    },
    "decision_threshold": 0.50  # 50% of total weighted votes (2.25 out of 4.5)
}

# Simple preset: For constrained problems (<50 lines)
# Hash detector disabled, stricter AST threshold, requires both Token AND AST agreement
SIMPLE_PRESET = {
    "name": "Simple Problems (e.g., FizzBuzz)",
    "description": "For simple problems (<50 lines). Hash detector disabled, requires both Token and AST agreement.",
    "token": {
        "threshold": 0.70,
        "weight": 2.0,  # Equal weight with AST to require both
        "confidence_weight": 0.4  # Normalized for two active detectors
    },
    "ast": {
        "threshold": 0.85,  # Stricter than standard to reduce false positives
        "weight": 2.0,      # Equal weight with Token to require both
        "confidence_weight": 0.6  # Normalized for two active detectors
    },
    "hash": {
        "threshold": 0.60,
        "weight": 0.0,      # DISABLED - ineffective on <50 line files
        "confidence_weight": 0.0  # DISABLED
    },
    "decision_threshold": 0.75  # 75% of total votes (3.0 out of 4.0) - requires both detectors
}

# Preset registry
_PRESETS = {
    PRESET_STANDARD: STANDARD_PRESET,
    PRESET_SIMPLE: SIMPLE_PRESET,
}


def get_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get preset configuration by name.

    Args:
        preset_name: Name of the preset to retrieve ("standard" or "simple").
                    Case-insensitive.

    Returns:
        Dictionary containing the preset configuration with keys:
        - name (str): Display name of the preset
        - description (str): Human-readable description
        - token (dict): Token detector config (threshold, weight, confidence_weight)
        - ast (dict): AST detector config (threshold, weight, confidence_weight)
        - hash (dict): Hash detector config (threshold, weight, confidence_weight)
        - decision_threshold (float): Voting decision threshold as percentage

    Raises:
        ValueError: If preset_name is not recognized.

    Example:
        >>> config = get_preset("standard")
        >>> print(config["name"])
        Standard (Recommended)
        >>> print(config["token"]["threshold"])
        0.7

        >>> config = get_preset("SIMPLE")  # Case-insensitive
        >>> print(config["hash"]["weight"])
        0.0
    """
    preset_key = preset_name.lower().strip()

    if preset_key not in _PRESETS:
        available = ", ".join(f"'{p}'" for p in _PRESETS.keys())
        raise ValueError(
            f"Unknown preset: '{preset_name}'. "
            f"Available presets: {available}"
        )

    # Return a deep copy to prevent accidental mutation
    preset = _PRESETS[preset_key]
    return {
        "name": preset["name"],
        "description": preset["description"],
        "token": preset["token"].copy(),
        "ast": preset["ast"].copy(),
        "hash": preset["hash"].copy(),
        "decision_threshold": preset["decision_threshold"]
    }


def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """
    Get preset configuration suitable for VotingSystem initialization.

    This function returns only the detector configurations and decision_threshold,
    excluding the 'name' and 'description' fields that VotingSystem doesn't need.

    Args:
        preset_name: Name of the preset to retrieve ("standard" or "simple").
                    Case-insensitive.

    Returns:
        Dictionary containing only the configuration keys needed by VotingSystem:
        - token (dict): Token detector config
        - ast (dict): AST detector config
        - hash (dict): Hash detector config
        - decision_threshold (float): Voting decision threshold

    Raises:
        ValueError: If preset_name is not recognized.

    Example:
        >>> from src.voting.voting_system import VotingSystem
        >>> config = get_preset_config("simple")
        >>> system = VotingSystem(config)
        >>> print(system.total_possible_votes)
        4.0
    """
    preset = get_preset(preset_name)

    # Extract only the configuration keys needed by VotingSystem
    return {
        "token": preset["token"],
        "ast": preset["ast"],
        "hash": preset["hash"],
        "decision_threshold": preset["decision_threshold"]
    }


def get_available_presets() -> List[str]:
    """
    Get list of available preset names.

    Returns:
        List of preset name strings (lowercase).

    Example:
        >>> presets = get_available_presets()
        >>> print(presets)
        ['standard', 'simple']
        >>> for preset in presets:
        ...     config = get_preset(preset)
        ...     print(f"{preset}: {config['name']}")
        standard: Standard (Recommended)
        simple: Simple Problems (e.g., FizzBuzz)
    """
    return list(_PRESETS.keys())


def apply_preset_to_voting_system(voting_system, preset_name: str):
    """
    Apply preset configuration to an existing VotingSystem instance.

    This function updates the voting system's configuration in-place,
    modifying detector thresholds, weights, confidence weights, and
    decision threshold.

    Args:
        voting_system: VotingSystem instance to update.
        preset_name: Name of the preset to apply ("standard" or "simple").
                    Case-insensitive.

    Returns:
        The updated VotingSystem instance (same object, modified in-place).

    Raises:
        ValueError: If preset_name is not recognized.
        TypeError: If voting_system is not a VotingSystem instance.

    Example:
        >>> from src.voting.voting_system import VotingSystem
        >>> system = VotingSystem()
        >>> print(system.config["ast"]["threshold"])
        0.8

        >>> apply_preset_to_voting_system(system, "simple")
        >>> print(system.config["ast"]["threshold"])
        0.85
        >>> print(system.config["hash"]["weight"])
        0.0

        >>> # Total possible votes recalculated
        >>> print(system.total_possible_votes)
        4.0

    Note:
        This function validates the preset configuration before applying it
        to ensure all weights and thresholds are valid. The voting system's
        internal state (total_possible_votes, decision_threshold) is
        automatically recalculated after applying the preset.
    """
    # Get preset configuration
    preset = get_preset(preset_name)

    # Validate that the object has the expected attributes
    if not hasattr(voting_system, 'config'):
        raise TypeError(
            "voting_system must be a VotingSystem instance with a 'config' attribute"
        )

    # Extract detector configurations (exclude name and description)
    new_config = {
        "token": preset["token"],
        "ast": preset["ast"],
        "hash": preset["hash"],
        "decision_threshold": preset["decision_threshold"]
    }

    # Validate the preset configuration before applying
    if not validate_preset(preset):
        raise ValueError(f"Preset '{preset_name}' has invalid configuration")

    # Update the voting system's configuration
    voting_system.config = new_config

    # Recalculate total possible votes
    voting_system.total_possible_votes = sum(
        detector["weight"]
        for name, detector in new_config.items()
        if name != "decision_threshold" and isinstance(detector, dict) and "weight" in detector
    )

    # Recalculate decision threshold based on percentage
    decision_threshold_pct = new_config.get("decision_threshold", 0.5)
    voting_system.decision_threshold = voting_system.total_possible_votes * decision_threshold_pct

    logger.info(
        f"Applied preset '{preset_name}' to VotingSystem. "
        f"Total possible votes: {voting_system.total_possible_votes}, "
        f"Decision threshold: {voting_system.decision_threshold}"
    )

    return voting_system


def validate_preset(preset: Dict[str, Any]) -> bool:
    """
    Validate preset configuration structure and values.

    Checks that:
    1. Required keys are present (name, description, token, ast, hash)
    2. Each detector has threshold, weight, and confidence_weight
    3. Thresholds are in [0.0, 1.0]
    4. Weights are non-negative (0.0 allowed for disabled detectors)
    5. Confidence weights are in [0.0, 1.0] and sum to 1.0
    6. Decision threshold is in [0.0, 1.0]

    Args:
        preset: Preset configuration dictionary to validate.

    Returns:
        True if preset is valid, False otherwise.

    Example:
        >>> valid_preset = get_preset("standard")
        >>> validate_preset(valid_preset)
        True

        >>> invalid_preset = {"name": "Test", "token": {"threshold": 1.5}}
        >>> validate_preset(invalid_preset)
        False
    """
    try:
        # Check required keys
        required_keys = {"name", "description", "token", "ast", "hash"}
        if not required_keys.issubset(preset.keys()):
            logger.error(f"Preset missing required keys: {required_keys - preset.keys()}")
            return False

        # Validate each detector configuration
        detectors = ["token", "ast", "hash"]
        confidence_sum = 0.0

        for detector in detectors:
            if detector not in preset:
                logger.error(f"Missing detector: {detector}")
                return False

            config = preset[detector]

            # Check required fields
            if not all(k in config for k in ["threshold", "weight", "confidence_weight"]):
                logger.error(f"Detector {detector} missing required fields")
                return False

            # Validate threshold [0.0, 1.0]
            threshold = config["threshold"]
            if not (0.0 <= threshold <= 1.0):
                logger.error(f"Invalid threshold for {detector}: {threshold}")
                return False

            # Validate weight (non-negative, 0.0 allowed for disabled detectors)
            weight = config["weight"]
            if weight < 0:
                logger.error(f"Negative weight for {detector}: {weight}")
                return False

            # Validate confidence weight [0.0, 1.0]
            conf_weight = config["confidence_weight"]
            if not (0.0 <= conf_weight <= 1.0):
                logger.error(f"Invalid confidence weight for {detector}: {conf_weight}")
                return False

            confidence_sum += conf_weight

        # Validate confidence weights sum to 1.0 (with tolerance for floating point)
        if not math.isclose(confidence_sum, 1.0, abs_tol=1e-6):
            logger.error(f"Confidence weights sum to {confidence_sum}, expected 1.0")
            return False

        # Validate decision threshold if present
        if "decision_threshold" in preset:
            decision_threshold = preset["decision_threshold"]
            if not (0.0 <= decision_threshold <= 1.0):
                logger.error(f"Invalid decision threshold: {decision_threshold}")
                return False

        return True

    except (TypeError, KeyError, ValueError) as e:
        logger.error(f"Validation error: {e}")
        return False


def get_preset_summary(preset_name: str) -> str:
    """
    Get a human-readable summary of a preset configuration.

    Args:
        preset_name: Name of the preset ("standard" or "simple").

    Returns:
        Formatted string describing the preset configuration.

    Raises:
        ValueError: If preset_name is not recognized.

    Example:
        >>> print(get_preset_summary("standard"))
        Preset: Standard (Recommended)
        Description: For typical assignments (50+ lines). Uses all three detectors...

        Detector Configuration:
          Token:  threshold=0.70, weight=1.0, confidence=0.3
          AST:    threshold=0.80, weight=2.0, confidence=0.4
          Hash:   threshold=0.60, weight=1.5, confidence=0.3

        Total Possible Votes: 4.5
        Decision Threshold: 2.25 (50%)

    Example (Simple preset):
        >>> print(get_preset_summary("simple"))
        Preset: Simple Problems (e.g., FizzBuzz)
        Description: For simple problems (<50 lines). Hash detector disabled...

        Detector Configuration:
          Token:  threshold=0.70, weight=2.0, confidence=0.4
          AST:    threshold=0.85, weight=2.0, confidence=0.6
          Hash:   threshold=0.60, weight=0.0, confidence=0.0 (DISABLED)

        Total Possible Votes: 4.0
        Decision Threshold: 3.00 (75%)
    """
    preset = get_preset(preset_name)

    # Calculate total votes and decision threshold
    total_votes = sum(
        preset[detector]["weight"]
        for detector in ["token", "ast", "hash"]
    )
    decision_pct = preset.get("decision_threshold", 0.5)
    decision_votes = total_votes * decision_pct

    lines = [
        f"Preset: {preset['name']}",
        f"Description: {preset['description']}",
        "",
        "Detector Configuration:"
    ]

    for detector in ["token", "ast", "hash"]:
        cfg = preset[detector]
        status = " (DISABLED)" if cfg["weight"] == 0.0 else ""
        lines.append(
            f"  {detector.capitalize():6s}: "
            f"threshold={cfg['threshold']:.2f}, "
            f"weight={cfg['weight']:.1f}, "
            f"confidence={cfg['confidence_weight']:.1f}"
            f"{status}"
        )

    lines.extend([
        "",
        f"Total Possible Votes: {total_votes:.1f}",
        f"Decision Threshold: {decision_votes:.2f} ({decision_pct*100:.0f}%)"
    ])

    return "\n".join(lines)
