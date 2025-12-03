"""
Voting System for Plagiarism Detection

This module implements a weighted voting system that aggregates results from
multiple plagiarism detectors (Token, AST, Hash) to make a final decision
on whether code plagiarism has occurred.

The system uses configurable thresholds and weights for each detector,
computes a confidence score, and returns comprehensive voting results.

The system now supports configuration presets for different use cases:
- Standard preset: All three detectors active (for 50+ line assignments)
- Simple preset: Hash detector disabled (for <50 line simple problems)
"""

import logging
from typing import Dict, Optional, Any
import math


# Configure logging
logger = logging.getLogger(__name__)


class VotingSystem:
    """
    Weighted voting system for plagiarism detection.

    This class aggregates similarity scores from multiple detectors using
    a weighted voting mechanism. Supports configuration presets for different
    use cases (standard vs. simple problems).

    Detectors can be disabled by setting weight=0.0, which is useful for
    scenarios where certain detectors are ineffective (e.g., hash detector
    on <50 line files).

    Attributes:
        config (Dict[str, Any]): Configuration containing thresholds and weights
            for each detector, plus decision_threshold.
        token_config (Dict[str, float]): Token detector configuration.
        ast_config (Dict[str, float]): AST detector configuration.
        hash_config (Dict[str, float]): Hash detector configuration.
        decision_threshold (float): Minimum weighted votes needed for plagiarism
            detection (default: 50% of total weighted votes).
        total_votes (float): Sum of all active detector weights.

    Examples:
        >>> from src.core import get_preset_config
        >>> # Standard preset: all detectors active
        >>> system = VotingSystem(get_preset_config("standard"))
        >>> result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)
        >>> print(result['is_plagiarized'])
        True

        >>> # Simple preset: hash detector disabled
        >>> system = VotingSystem(get_preset_config("simple"))
        >>> result = system.vote(token_sim=0.75, ast_sim=0.82, hash_sim=0.65)
        >>> print(system.total_votes)
        4.0
    """

    # Default configuration
    DEFAULT_CONFIG = {
        "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.3},
        "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
        "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VotingSystem with configuration preset.

        Args:
            config: Configuration dictionary from get_preset_config().
                   If None, uses STANDARD_PRESET as default.
                   Format: {
                       'token': {
                           'threshold': float (0.0-1.0),
                           'weight': float (>= 0, use 0 to disable detector),
                           'confidence_weight': float (0.0-1.0)
                       },
                       'ast': {...},
                       'hash': {...},
                       'decision_threshold': float (0.0-1.0, percentage of total votes)
                   }

        Raises:
            ValueError: If configuration contains invalid values (thresholds
                       not in [0,1], negative weights, or confidence weights
                       don't sum to 1.0).

        Examples:
            >>> # Use standard preset (default)
            >>> system = VotingSystem()

            >>> # Use simple preset
            >>> from src.core import get_preset_config
            >>> system = VotingSystem(get_preset_config("simple"))

            >>> # Custom configuration
            >>> custom_config = {
            ...     'token': {'threshold': 0.70, 'weight': 1.0, 'confidence_weight': 0.3},
            ...     'ast': {'threshold': 0.80, 'weight': 2.0, 'confidence_weight': 0.4},
            ...     'hash': {'threshold': 0.60, 'weight': 0.0, 'confidence_weight': 0.3},
            ...     'decision_threshold': 0.50
            ... }
            >>> system = VotingSystem(custom_config)
        """
        # Load default configuration if none provided
        if config is None:
            try:
                from src.core.config_presets import get_preset_config
                config = get_preset_config("standard")
                logger.info("No config provided, using STANDARD preset as default")
            except ImportError:
                # Fallback to hardcoded default if import fails
                config = self.DEFAULT_CONFIG.copy()
                logger.warning("Could not import config_presets, using DEFAULT_CONFIG")

        # Store configuration
        self.config = config

        # Validate configuration
        self._validate_config()

        # Extract detector configs for easy access
        self.token_config = self.config['token']
        self.ast_config = self.config['ast']
        self.hash_config = self.config['hash']

        # Calculate total votes (sum of active detector weights)
        self.total_votes = (
            self.token_config['weight'] +
            self.ast_config['weight'] +
            self.hash_config['weight']
        )

        # Maintain backwards compatibility with old attribute name
        self.total_possible_votes = self.total_votes

        # Decision threshold (default 50% of total votes)
        decision_threshold_pct = self.config.get('decision_threshold', 0.50)
        self.decision_threshold = self.total_votes * decision_threshold_pct

        # Log configuration
        logger.info(
            f"VotingSystem initialized with {self.total_votes:.1f} total votes "
            f"(decision threshold: {self.decision_threshold:.1f})"
        )

        # Log disabled detectors
        if self.token_config['weight'] == 0.0:
            logger.info("Token detector DISABLED (weight=0.0)")
        if self.ast_config['weight'] == 0.0:
            logger.info("AST detector DISABLED (weight=0.0)")
        if self.hash_config['weight'] == 0.0:
            logger.info("Hash detector DISABLED (weight=0.0)")

    def _validate_config(self) -> None:
        """
        Validate the configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid.
        """
        required_detectors = {"token", "ast", "hash"}
        config_keys = set(self.config.keys())

        # Remove optional decision_threshold key for validation
        detector_keys = config_keys - {"decision_threshold"}

        if detector_keys != required_detectors:
            raise ValueError(
                f"Configuration must contain exactly these detectors: {required_detectors}, "
                f"got: {detector_keys}"
            )

        # Validate decision_threshold if present
        if "decision_threshold" in self.config:
            decision_threshold = self.config["decision_threshold"]
            if not (0.0 <= decision_threshold <= 1.0):
                raise ValueError(
                    f"decision_threshold must be in [0.0, 1.0], got {decision_threshold}"
                )

        confidence_sum = 0.0

        for detector_name, params in self.config.items():
            # Skip non-detector keys
            if detector_name == "decision_threshold":
                continue
            # Validate threshold
            if "threshold" not in params:
                raise ValueError(f"Missing 'threshold' for {detector_name}")
            threshold = params["threshold"]
            if not (0.0 <= threshold <= 1.0):
                raise ValueError(
                    f"Threshold for {detector_name} must be in [0.0, 1.0], " f"got {threshold}"
                )

            # Validate weight
            if "weight" not in params:
                raise ValueError(f"Missing 'weight' for {detector_name}")
            weight = params["weight"]
            if weight < 0:
                raise ValueError(f"Weight for {detector_name} must be non-negative, got {weight}")
            # Note: weight=0.0 is allowed to disable a detector

            # Validate confidence weight
            if "confidence_weight" not in params:
                raise ValueError(f"Missing 'confidence_weight' for {detector_name}")
            conf_weight = params["confidence_weight"]
            if not (0.0 <= conf_weight <= 1.0):
                raise ValueError(
                    f"Confidence weight for {detector_name} must be in [0.0, 1.0], "
                    f"got {conf_weight}"
                )
            confidence_sum += conf_weight

        # Validate confidence weights sum to 1.0 (with small epsilon tolerance)
        if not math.isclose(confidence_sum, 1.0, abs_tol=1e-6):
            raise ValueError(f"Confidence weights must sum to 1.0, got {confidence_sum}")

    def _validate_similarity_score(self, score: float, detector_name: str) -> None:
        """
        Validate a similarity score is within valid range.

        Args:
            score: The similarity score to validate.
            detector_name: Name of the detector for error messages.

        Raises:
            ValueError: If score is None, NaN, or outside [0.0, 1.0].
        """
        if score is None:
            raise ValueError(f"{detector_name} similarity score cannot be None")

        if math.isnan(score):
            raise ValueError(f"{detector_name} similarity score is NaN")

        if math.isinf(score):
            raise ValueError(f"{detector_name} similarity score is infinite")

        if not (0.0 <= score <= 1.0):
            raise ValueError(
                f"{detector_name} similarity score must be in [0.0, 1.0], " f"got {score}"
            )

    def vote(self, token_sim: float, ast_sim: float, hash_sim: float) -> Dict[str, Any]:
        """
        Make plagiarism decision using weighted voting.

        This method:
        1. Validates all input similarity scores
        2. Compares each score against its detector's threshold
        3. Calculates weighted votes from detectors that voted "plagiarized"
        4. Skips disabled detectors (weight=0.0)
        5. Makes a final decision based on the decision threshold
        6. Computes confidence score using only ACTIVE detectors

        Args:
            token_sim: Token detector similarity [0.0, 1.0]
            ast_sim: AST detector similarity [0.0, 1.0]
            hash_sim: Hash detector similarity [0.0, 1.0]

        Returns:
            Dictionary containing:
                - is_plagiarized (bool): True if total_votes_cast >= decision_threshold
                - confidence_score (float): Weighted confidence in [0.0, 1.0]
                - votes (Dict[str, float]): Individual detector vote weights
                - total_votes_cast (float): Sum of weights from "yes" votes
                - decision_threshold (float): Threshold used for decision
                - total_possible_votes (float): Total votes available
                - individual_scores (Dict[str, float]): Raw similarity scores

        Raises:
            ValueError: If any similarity score is invalid (None, NaN, or
                       outside [0.0, 1.0]).

        Examples:
            >>> from src.core import get_preset_config
            >>> # Standard preset: all detectors active
            >>> system = VotingSystem(get_preset_config("standard"))
            >>> result = system.vote(0.75, 0.85, 0.65)
            >>> result['is_plagiarized']
            True
            >>> result['total_votes_cast']
            4.5

            >>> # Simple preset: hash disabled
            >>> system = VotingSystem(get_preset_config("simple"))
            >>> result = system.vote(0.75, 0.82, 0.65)
            >>> result['votes']['hash']
            0.0
            >>> result['total_possible_votes']
            4.0
        """
        # Validate all inputs
        self._validate_similarity_score(token_sim, "Token")
        self._validate_similarity_score(ast_sim, "AST")
        self._validate_similarity_score(hash_sim, "Hash")

        # Map scores to detector names
        scores = {"token": token_sim, "ast": ast_sim, "hash": hash_sim}

        # Determine individual detector votes
        votes = {}
        total_votes_cast = 0.0

        # Token detector vote
        if token_sim >= self.token_config['threshold']:
            votes['token'] = self.token_config['weight']
            total_votes_cast += self.token_config['weight']
            logger.debug(
                f"Token voted YES (score={token_sim:.3f}, "
                f"threshold={self.token_config['threshold']:.2f})"
            )
        else:
            votes['token'] = 0.0
            logger.debug(
                f"Token voted NO (score={token_sim:.3f}, "
                f"threshold={self.token_config['threshold']:.2f})"
            )

        # AST detector vote
        if ast_sim >= self.ast_config['threshold']:
            votes['ast'] = self.ast_config['weight']
            total_votes_cast += self.ast_config['weight']
            logger.debug(
                f"AST voted YES (score={ast_sim:.3f}, "
                f"threshold={self.ast_config['threshold']:.2f})"
            )
        else:
            votes['ast'] = 0.0
            logger.debug(
                f"AST voted NO (score={ast_sim:.3f}, "
                f"threshold={self.ast_config['threshold']:.2f})"
            )

        # Hash detector vote (skip if disabled)
        if self.hash_config['weight'] > 0.0:
            if hash_sim >= self.hash_config['threshold']:
                votes['hash'] = self.hash_config['weight']
                total_votes_cast += self.hash_config['weight']
                logger.debug(
                    f"Hash voted YES (score={hash_sim:.3f}, "
                    f"threshold={self.hash_config['threshold']:.2f})"
                )
            else:
                votes['hash'] = 0.0
                logger.debug(
                    f"Hash voted NO (score={hash_sim:.3f}, "
                    f"threshold={self.hash_config['threshold']:.2f})"
                )
        else:
            votes['hash'] = 0.0
            logger.debug("Hash detector SKIPPED (disabled, weight=0.0)")

        # Make final decision
        is_plagiarized = total_votes_cast >= self.decision_threshold

        # Calculate confidence (only from active detectors)
        confidence_score = self._calculate_confidence(token_sim, ast_sim, hash_sim)

        # Enhanced debug logging
        logger.info("=" * 60)
        logger.info("VOTING DECISION:")
        logger.info(f"  Token: score={token_sim:.3f}, threshold={self.token_config['threshold']:.2f}, "
                   f"weight={self.token_config['weight']:.1f}, vote={votes['token']:.1f}")
        logger.info(f"  AST:   score={ast_sim:.3f}, threshold={self.ast_config['threshold']:.2f}, "
                   f"weight={self.ast_config['weight']:.1f}, vote={votes['ast']:.1f}")
        logger.info(f"  Hash:  score={hash_sim:.3f}, threshold={self.hash_config['threshold']:.2f}, "
                   f"weight={self.hash_config['weight']:.1f}, vote={votes['hash']:.1f}")
        logger.info(f"  Total votes cast: {total_votes_cast:.2f} / {self.total_votes:.1f} possible")
        logger.info(f"  Decision threshold: {self.decision_threshold:.2f} ({self.decision_threshold/self.total_votes*100:.0f}%)")
        logger.info(f"  Required votes: {self.decision_threshold:.2f}")
        logger.info(f"  RESULT: {'PLAGIARISM DETECTED' if is_plagiarized else 'CLEAR'} (confidence={confidence_score:.3f})")
        logger.info("=" * 60)

        # Construct result dictionary
        result = {
            "is_plagiarized": is_plagiarized,
            "confidence_score": confidence_score,
            "votes": votes,
            "weighted_votes": total_votes_cast,  # Backwards compatibility
            "total_votes_cast": total_votes_cast,
            "decision_threshold": self.decision_threshold,
            "total_possible_votes": self.total_votes,
            "individual_scores": {"token": token_sim, "ast": ast_sim, "hash": hash_sim},
        }

        return result

    def _calculate_confidence(self, token_score: float, ast_score: float, hash_score: float) -> float:
        """
        Calculate confidence score using only ACTIVE detectors.

        Detectors with weight=0.0 are excluded from confidence calculation.
        This prevents disabled detectors from affecting confidence.

        Args:
            token_score: Token similarity [0.0, 1.0]
            ast_score: AST similarity [0.0, 1.0]
            hash_score: Hash similarity [0.0, 1.0]

        Returns:
            Weighted confidence score [0.0, 1.0]

        Examples:
            >>> from src.core import get_preset_config
            >>> # Simple preset: hash disabled, should ignore hash score
            >>> system = VotingSystem(get_preset_config("simple"))
            >>> # Even with low hash score, confidence should be high
            >>> conf = system._calculate_confidence(0.80, 0.90, 0.20)
            >>> conf > 0.70
            True
        """
        # Collect active detector scores and weights
        active_scores = []
        active_weights = []

        # Token detector
        if self.token_config['weight'] > 0.0:
            active_scores.append(token_score)
            active_weights.append(self.token_config['confidence_weight'])

        # AST detector
        if self.ast_config['weight'] > 0.0:
            active_scores.append(ast_score)
            active_weights.append(self.ast_config['confidence_weight'])

        # Hash detector (may be disabled in simple preset)
        if self.hash_config['weight'] > 0.0:
            active_scores.append(hash_score)
            active_weights.append(self.hash_config['confidence_weight'])

        # Normalize weights to sum to 1.0
        total_weight = sum(active_weights)
        if total_weight == 0:
            logger.warning("No active detectors for confidence calculation")
            return 0.0

        normalized_weights = [w / total_weight for w in active_weights]

        # Calculate weighted confidence
        confidence = sum(score * weight for score, weight in zip(active_scores, normalized_weights))

        # Clamp to [0.0, 1.0] (should already be in range, but ensure)
        confidence = min(1.0, max(0.0, confidence))

        logger.debug(
            f"Confidence: {confidence:.3f} "
            f"(active_detectors={len(active_scores)}, "
            f"weights={[f'{w:.2f}' for w in normalized_weights]})"
        )

        return confidence

    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update voting system configuration.

        Useful for switching between presets during runtime.

        Args:
            config: New configuration dictionary

        Example:
            >>> from src.core import get_preset_config
            >>> system = VotingSystem(get_preset_config("standard"))
            >>> # Switch to simple preset
            >>> system.update_config(get_preset_config("simple"))
            >>> print(system.total_votes)
            4.0
        """
        self.__init__(config)
        logger.info("Configuration updated")

    def get_detector_info(self, detector_name: str) -> Dict[str, float]:
        """
        Get configuration information for a specific detector.

        Args:
            detector_name: Name of the detector ('token', 'ast', or 'hash').

        Returns:
            Dictionary containing threshold, weight, and confidence_weight.

        Raises:
            KeyError: If detector_name is not recognized.
        """
        if detector_name not in self.config:
            raise KeyError(
                f"Unknown detector: {detector_name}. " f"Available: {list(self.config.keys())}"
            )
        return self.config[detector_name].copy()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the voting system configuration.

        Returns:
            Dictionary containing system configuration and thresholds.
        """
        detector_names = ['token', 'ast', 'hash']
        return {
            "detectors": detector_names,
            "detector_configs": {name: self.get_detector_info(name) for name in detector_names},
            "total_possible_votes": self.total_votes,
            "decision_threshold": self.decision_threshold,
            "decision_threshold_percentage": (
                self.decision_threshold / self.total_votes * 100
            ) if self.total_votes > 0 else 0,
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the VotingSystem for debugging.

        Returns:
            String representation showing configuration details.
        """
        detector_info = ", ".join(
            f"{name}(th={cfg['threshold']:.2f}, w={cfg['weight']})"
            for name in ['token', 'ast', 'hash']
            if name in self.config
            for cfg in [self.config[name]]
        )
        return (
            f"VotingSystem("
            f"detectors=[{detector_info}], "
            f"decision_threshold={self.decision_threshold:.2f}/{self.total_votes}"
            f")"
        )

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            Formatted string describing the voting system.
        """
        lines = ["VotingSystem Configuration:"]
        for name in ['token', 'ast', 'hash']:
            if name in self.config:
                cfg = self.config[name]
                status = " (DISABLED)" if cfg['weight'] == 0.0 else ""
                lines.append(
                    f"  {name.upper()}: threshold={cfg['threshold']:.2f}, "
                    f"weight={cfg['weight']}, confidence_weight={cfg['confidence_weight']:.2f}"
                    f"{status}"
                )
        lines.append(f"Total Possible Votes: {self.total_votes:.1f}")
        threshold_pct = (self.decision_threshold / self.total_votes * 100) if self.total_votes > 0 else 0
        lines.append(f"Decision Threshold: {self.decision_threshold:.1f} ({threshold_pct:.0f}%)")
        return "\n".join(lines)
