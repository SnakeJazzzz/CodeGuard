"""
Threshold manager for plagiarism detection voting system.

This module provides the ThresholdManager class for managing detection thresholds
and voting weights. It supports loading from configuration files, runtime modification,
and validation of all parameters.

Thresholds determine when a detector "votes" for plagiarism, while weights determine
the relative importance of each detector's vote.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)


class ThresholdManager:
    """
    Manages thresholds and weights for the plagiarism detection voting system.

    This class provides centralized management of:
    - Detection thresholds (minimum similarity to trigger a vote)
    - Voting weights (relative importance of each detector)
    - Confidence calculation weights
    - Overall decision threshold

    Attributes:
        _thresholds: Dict of detector thresholds (token, ast, hash)
        _weights: Dict of voting weights (token, ast, hash)
        _confidence_weights: Dict of confidence calculation weights
        _decision_threshold: Overall threshold for plagiarism decision

    Default Configuration:
        Thresholds: Token=0.70, AST=0.80, Hash=0.60
        Weights: Token=1.0, AST=2.0, Hash=1.5
        Confidence Weights: Token=0.3, AST=0.4, Hash=0.3
        Decision Threshold: 0.50

    Example:
        >>> manager = ThresholdManager()
        >>> manager.get_threshold('ast')
        0.8
        >>> manager.set_threshold('token', 0.75)
        >>> manager.get_weight('ast')
        2.0
    """

    # Default configuration values
    DEFAULT_THRESHOLDS = {
        'token': 0.70,
        'ast': 0.80,
        'hash': 0.60
    }

    DEFAULT_WEIGHTS = {
        'token': 1.0,
        'ast': 2.0,
        'hash': 1.5
    }

    DEFAULT_CONFIDENCE_WEIGHTS = {
        'token': 0.3,
        'ast': 0.4,
        'hash': 0.3
    }

    DEFAULT_DECISION_THRESHOLD = 0.50

    VALID_DETECTORS = {'token', 'ast', 'hash'}

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ThresholdManager with default or loaded configuration.

        Args:
            config_path: Optional path to JSON configuration file.
                        If provided, loads configuration from file.
                        If None, uses default values.

        Raises:
            FileNotFoundError: If config_path is provided but file doesn't exist
            ValueError: If loaded configuration is invalid
            json.JSONDecodeError: If config file contains invalid JSON

        Example:
            >>> manager = ThresholdManager()  # Use defaults
            >>> manager = ThresholdManager('/path/to/config.json')  # Load from file
        """
        # Initialize with defaults
        self._thresholds = self.DEFAULT_THRESHOLDS.copy()
        self._weights = self.DEFAULT_WEIGHTS.copy()
        self._confidence_weights = self.DEFAULT_CONFIDENCE_WEIGHTS.copy()
        self._decision_threshold = self.DEFAULT_DECISION_THRESHOLD

        # Load from file if path provided
        if config_path is not None:
            self.load_from_file(config_path)
        else:
            logger.info("ThresholdManager initialized with default configuration")

        # Validate initial configuration
        self.validate_thresholds()

    def get_threshold(self, detector: str) -> float:
        """
        Get threshold value for specified detector.

        Args:
            detector: Detector name ('token', 'ast', or 'hash')

        Returns:
            float: Threshold value in range [0.0, 1.0]

        Raises:
            ValueError: If detector name is invalid

        Example:
            >>> manager = ThresholdManager()
            >>> manager.get_threshold('ast')
            0.8
            >>> manager.get_threshold('invalid')  # doctest: +SKIP
            ValueError: Invalid detector name 'invalid'
        """
        detector = detector.lower()
        if detector not in self.VALID_DETECTORS:
            raise ValueError(
                f"Invalid detector name '{detector}'. "
                f"Must be one of {self.VALID_DETECTORS}"
            )

        return self._thresholds[detector]

    def set_threshold(self, detector: str, value: float) -> None:
        """
        Set threshold value for specified detector.

        Args:
            detector: Detector name ('token', 'ast', or 'hash')
            value: Threshold value in range [0.0, 1.0]

        Raises:
            ValueError: If detector name is invalid or value out of range
            TypeError: If value is not numeric

        Example:
            >>> manager = ThresholdManager()
            >>> manager.set_threshold('token', 0.75)
            >>> manager.get_threshold('token')
            0.75
            >>> manager.set_threshold('token', 1.5)  # doctest: +SKIP
            ValueError: Threshold must be in range [0.0, 1.0]
        """
        detector = detector.lower()
        if detector not in self.VALID_DETECTORS:
            raise ValueError(
                f"Invalid detector name '{detector}'. "
                f"Must be one of {self.VALID_DETECTORS}"
            )

        # Type validation
        try:
            value = float(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Threshold value must be numeric: {e}")

        # Range validation
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"Threshold must be in range [0.0, 1.0], got {value}"
            )

        old_value = self._thresholds[detector]
        self._thresholds[detector] = value

        logger.info(
            f"Updated {detector} threshold: {old_value:.4f} -> {value:.4f}"
        )

    def get_weight(self, detector: str) -> float:
        """
        Get voting weight for specified detector.

        Args:
            detector: Detector name ('token', 'ast', or 'hash')

        Returns:
            float: Voting weight (must be > 0.0)

        Raises:
            ValueError: If detector name is invalid

        Example:
            >>> manager = ThresholdManager()
            >>> manager.get_weight('ast')
            2.0
            >>> manager.get_weight('token')
            1.0
        """
        detector = detector.lower()
        if detector not in self.VALID_DETECTORS:
            raise ValueError(
                f"Invalid detector name '{detector}'. "
                f"Must be one of {self.VALID_DETECTORS}"
            )

        return self._weights[detector]

    def set_weight(self, detector: str, value: float) -> None:
        """
        Set voting weight for specified detector.

        Args:
            detector: Detector name ('token', 'ast', or 'hash')
            value: Weight value (must be > 0.0)

        Raises:
            ValueError: If detector name is invalid or value <= 0.0
            TypeError: If value is not numeric

        Example:
            >>> manager = ThresholdManager()
            >>> manager.set_weight('token', 1.5)
            >>> manager.get_weight('token')
            1.5
            >>> manager.set_weight('ast', -1.0)  # doctest: +SKIP
            ValueError: Weight must be positive
        """
        detector = detector.lower()
        if detector not in self.VALID_DETECTORS:
            raise ValueError(
                f"Invalid detector name '{detector}'. "
                f"Must be one of {self.VALID_DETECTORS}"
            )

        # Type validation
        try:
            value = float(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Weight value must be numeric: {e}")

        # Positive validation
        if value <= 0.0:
            raise ValueError(
                f"Weight must be positive (> 0.0), got {value}"
            )

        old_value = self._weights[detector]
        self._weights[detector] = value

        logger.info(
            f"Updated {detector} weight: {old_value:.4f} -> {value:.4f}"
        )

    def get_confidence_weight(self, detector: str) -> float:
        """
        Get confidence calculation weight for specified detector.

        Args:
            detector: Detector name ('token', 'ast', or 'hash')

        Returns:
            float: Confidence weight in range [0.0, 1.0]

        Raises:
            ValueError: If detector name is invalid

        Example:
            >>> manager = ThresholdManager()
            >>> manager.get_confidence_weight('ast')
            0.4
        """
        detector = detector.lower()
        if detector not in self.VALID_DETECTORS:
            raise ValueError(
                f"Invalid detector name '{detector}'. "
                f"Must be one of {self.VALID_DETECTORS}"
            )

        return self._confidence_weights[detector]

    def get_decision_threshold(self) -> float:
        """
        Get the overall decision threshold for plagiarism determination.

        Returns:
            float: Decision threshold in range [0.0, 1.0]

        Example:
            >>> manager = ThresholdManager()
            >>> manager.get_decision_threshold()
            0.5
        """
        return self._decision_threshold

    def set_decision_threshold(self, value: float) -> None:
        """
        Set the overall decision threshold for plagiarism determination.

        Args:
            value: Decision threshold in range [0.0, 1.0]

        Raises:
            ValueError: If value is outside [0.0, 1.0]
            TypeError: If value is not numeric

        Example:
            >>> manager = ThresholdManager()
            >>> manager.set_decision_threshold(0.6)
            >>> manager.get_decision_threshold()
            0.6
        """
        try:
            value = float(value)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Decision threshold must be numeric: {e}")

        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"Decision threshold must be in range [0.0, 1.0], got {value}"
            )

        old_value = self._decision_threshold
        self._decision_threshold = value

        logger.info(
            f"Updated decision threshold: {old_value:.4f} -> {value:.4f}"
        )

    def validate_thresholds(self) -> bool:
        """
        Validate all thresholds and weights.

        Validates that:
        - All thresholds are in [0.0, 1.0]
        - All voting weights are > 0.0
        - Decision threshold is in [0.0, 1.0]
        - All required detectors are present

        Returns:
            bool: True if all validations pass

        Raises:
            ValueError: If any validation fails

        Example:
            >>> manager = ThresholdManager()
            >>> manager.validate_thresholds()
            True
        """
        # Validate all detectors are present
        for detector in self.VALID_DETECTORS:
            if detector not in self._thresholds:
                raise ValueError(f"Missing threshold for detector '{detector}'")
            if detector not in self._weights:
                raise ValueError(f"Missing weight for detector '{detector}'")
            if detector not in self._confidence_weights:
                raise ValueError(
                    f"Missing confidence weight for detector '{detector}'"
                )

        # Validate threshold ranges
        for detector, threshold in self._thresholds.items():
            if not isinstance(threshold, (int, float)):
                raise ValueError(
                    f"Threshold for '{detector}' must be numeric, "
                    f"got {type(threshold)}"
                )
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(
                    f"Threshold for '{detector}' must be in [0.0, 1.0], "
                    f"got {threshold}"
                )

        # Validate weight positivity
        for detector, weight in self._weights.items():
            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Weight for '{detector}' must be numeric, "
                    f"got {type(weight)}"
                )
            if weight <= 0.0:
                raise ValueError(
                    f"Weight for '{detector}' must be positive, got {weight}"
                )

        # Validate confidence weights
        for detector, weight in self._confidence_weights.items():
            if not isinstance(weight, (int, float)):
                raise ValueError(
                    f"Confidence weight for '{detector}' must be numeric, "
                    f"got {type(weight)}"
                )
            if not 0.0 <= weight <= 1.0:
                raise ValueError(
                    f"Confidence weight for '{detector}' must be in [0.0, 1.0], "
                    f"got {weight}"
                )

        # Validate decision threshold
        if not isinstance(self._decision_threshold, (int, float)):
            raise ValueError(
                f"Decision threshold must be numeric, "
                f"got {type(self._decision_threshold)}"
            )
        if not 0.0 <= self._decision_threshold <= 1.0:
            raise ValueError(
                f"Decision threshold must be in [0.0, 1.0], "
                f"got {self._decision_threshold}"
            )

        logger.debug("All thresholds and weights validated successfully")
        return True

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from JSON file.

        Expected JSON structure:
        {
            "thresholds": {"token": 0.7, "ast": 0.8, "hash": 0.6},
            "weights": {"token": 1.0, "ast": 2.0, "hash": 1.5},
            "confidence_weights": {"token": 0.3, "ast": 0.4, "hash": 0.3},
            "decision_threshold": 0.5
        }

        Args:
            config_path: Path to JSON configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file contains invalid JSON
            ValueError: If configuration is invalid

        Example:
            >>> manager = ThresholdManager()
            >>> manager.load_from_file('/path/to/config.json')
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        logger.info(f"Loading configuration from {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in configuration file: {e.msg}",
                e.doc,
                e.pos
            )

        # Load thresholds
        if 'thresholds' in config:
            if not isinstance(config['thresholds'], dict):
                raise ValueError("'thresholds' must be a dictionary")
            for detector, value in config['thresholds'].items():
                if detector in self.VALID_DETECTORS:
                    self.set_threshold(detector, value)
                else:
                    logger.warning(
                        f"Ignoring unknown detector '{detector}' in thresholds"
                    )

        # Load weights
        if 'weights' in config:
            if not isinstance(config['weights'], dict):
                raise ValueError("'weights' must be a dictionary")
            for detector, value in config['weights'].items():
                if detector in self.VALID_DETECTORS:
                    self.set_weight(detector, value)
                else:
                    logger.warning(
                        f"Ignoring unknown detector '{detector}' in weights"
                    )

        # Load confidence weights
        if 'confidence_weights' in config:
            if not isinstance(config['confidence_weights'], dict):
                raise ValueError("'confidence_weights' must be a dictionary")
            self._confidence_weights = {}
            for detector, value in config['confidence_weights'].items():
                if detector in self.VALID_DETECTORS:
                    try:
                        value = float(value)
                        if not 0.0 <= value <= 1.0:
                            raise ValueError(
                                f"Confidence weight for '{detector}' must be "
                                f"in [0.0, 1.0], got {value}"
                            )
                        self._confidence_weights[detector] = value
                    except (TypeError, ValueError) as e:
                        raise ValueError(
                            f"Invalid confidence weight for '{detector}': {e}"
                        )
                else:
                    logger.warning(
                        f"Ignoring unknown detector '{detector}' "
                        f"in confidence_weights"
                    )

        # Load decision threshold
        if 'decision_threshold' in config:
            self.set_decision_threshold(config['decision_threshold'])

        # Validate loaded configuration
        self.validate_thresholds()

        logger.info(f"Configuration loaded successfully from {config_path}")

    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to JSON file.

        Args:
            config_path: Path where configuration should be saved

        Raises:
            IOError: If file cannot be written
            ValueError: If current configuration is invalid

        Example:
            >>> manager = ThresholdManager()
            >>> manager.save_to_file('/path/to/config.json')
        """
        # Validate before saving
        self.validate_thresholds()

        config_path = Path(config_path)

        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config = self.get_config()

        logger.info(f"Saving configuration to {config_path}")

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, sort_keys=True)
        except IOError as e:
            raise IOError(f"Failed to write configuration file: {e}")

        logger.info(f"Configuration saved successfully to {config_path}")

    def get_config(self) -> Dict:
        """
        Get current configuration as dictionary.

        Returns:
            Dict: Complete configuration including thresholds, weights,
                 confidence_weights, and decision_threshold

        Example:
            >>> manager = ThresholdManager()
            >>> config = manager.get_config()
            >>> 'thresholds' in config
            True
            >>> 'weights' in config
            True
        """
        return {
            'thresholds': self._thresholds.copy(),
            'weights': self._weights.copy(),
            'confidence_weights': self._confidence_weights.copy(),
            'decision_threshold': self._decision_threshold
        }

    def reset_to_defaults(self) -> None:
        """
        Reset all configuration values to defaults.

        Example:
            >>> manager = ThresholdManager()
            >>> manager.set_threshold('token', 0.5)
            >>> manager.reset_to_defaults()
            >>> manager.get_threshold('token')
            0.7
        """
        self._thresholds = self.DEFAULT_THRESHOLDS.copy()
        self._weights = self.DEFAULT_WEIGHTS.copy()
        self._confidence_weights = self.DEFAULT_CONFIDENCE_WEIGHTS.copy()
        self._decision_threshold = self.DEFAULT_DECISION_THRESHOLD

        logger.info("Configuration reset to defaults")

    def __repr__(self) -> str:
        """String representation of ThresholdManager."""
        return (
            f"ThresholdManager("
            f"thresholds={self._thresholds}, "
            f"weights={self._weights}, "
            f"decision_threshold={self._decision_threshold})"
        )
