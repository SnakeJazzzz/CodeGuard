"""
Voting System for Plagiarism Detection

This module implements a weighted voting system that aggregates results from
multiple plagiarism detectors (Token, AST, Hash) to make a final decision
on whether code plagiarism has occurred.

The system uses configurable thresholds and weights for each detector,
computes a confidence score, and returns comprehensive voting results.
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
    a weighted voting mechanism. Each detector has a threshold and weight:
    - Token Detector: threshold=0.70, weight=1.0x
    - AST Detector: threshold=0.80, weight=2.0x (highest reliability)
    - Hash Detector: threshold=0.60, weight=1.5x

    A decision is made when weighted votes reach 50% of the total possible
    weighted votes (2.25 out of 4.5).

    Attributes:
        config (Dict[str, Dict[str, float]]): Configuration containing thresholds
            and weights for each detector.
        decision_threshold (float): Minimum weighted votes needed for plagiarism
            detection (default: 50% of total weighted votes).
        total_possible_votes (float): Sum of all detector weights.

    Example:
        >>> system = VotingSystem()
        >>> result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)
        >>> print(result['is_plagiarized'])
        True
        >>> print(f"Confidence: {result['confidence_score']:.2f}")
        Confidence: 0.75
    """

    # Default configuration
    DEFAULT_CONFIG = {
        'token': {
            'threshold': 0.70,
            'weight': 1.0,
            'confidence_weight': 0.3
        },
        'ast': {
            'threshold': 0.80,
            'weight': 2.0,
            'confidence_weight': 0.4
        },
        'hash': {
            'threshold': 0.60,
            'weight': 1.5,
            'confidence_weight': 0.3
        }
    }

    def __init__(self, config: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize the VotingSystem with optional custom configuration.

        Args:
            config: Optional dictionary containing detector configurations.
                   Format: {
                       'detector_name': {
                           'threshold': float (0.0-1.0),
                           'weight': float (> 0),
                           'confidence_weight': float (0.0-1.0)
                       }
                   }
                   If None, uses DEFAULT_CONFIG.

        Raises:
            ValueError: If configuration contains invalid values (thresholds
                       not in [0,1], negative weights, or confidence weights
                       don't sum to 1.0).
        """
        # Use default config if none provided
        self.config = config if config is not None else self.DEFAULT_CONFIG.copy()

        # Validate configuration
        self._validate_config()

        # Calculate total possible weighted votes (exclude decision_threshold)
        self.total_possible_votes = sum(
            detector['weight'] for detector in self.config.values()
            if isinstance(detector, dict) and 'weight' in detector
        )

        # Decision threshold: use custom if provided, otherwise 50% of total weighted votes
        if 'decision_threshold' in self.config:
            # Config contains a percentage (0.0-1.0)
            decision_threshold_pct = self.config['decision_threshold']
            self.decision_threshold = self.total_possible_votes * decision_threshold_pct
        else:
            # Default to 50% of total weighted votes
            self.decision_threshold = self.total_possible_votes * 0.5

        logger.info(
            f"VotingSystem initialized with {len([k for k in self.config.keys() if k != 'decision_threshold'])} detectors. "
            f"Total possible votes: {self.total_possible_votes}, "
            f"Decision threshold: {self.decision_threshold}"
        )

    def _validate_config(self) -> None:
        """
        Validate the configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid.
        """
        required_detectors = {'token', 'ast', 'hash'}
        config_keys = set(self.config.keys())

        # Remove optional decision_threshold key for validation
        detector_keys = config_keys - {'decision_threshold'}

        if detector_keys != required_detectors:
            raise ValueError(
                f"Configuration must contain exactly these detectors: {required_detectors}, "
                f"got: {detector_keys}"
            )

        # Validate decision_threshold if present
        if 'decision_threshold' in self.config:
            decision_threshold = self.config['decision_threshold']
            if not (0.0 <= decision_threshold <= 1.0):
                raise ValueError(
                    f"decision_threshold must be in [0.0, 1.0], got {decision_threshold}"
                )

        confidence_sum = 0.0

        for detector_name, params in self.config.items():
            # Skip non-detector keys
            if detector_name == 'decision_threshold':
                continue
            # Validate threshold
            if 'threshold' not in params:
                raise ValueError(f"Missing 'threshold' for {detector_name}")
            threshold = params['threshold']
            if not (0.0 <= threshold <= 1.0):
                raise ValueError(
                    f"Threshold for {detector_name} must be in [0.0, 1.0], "
                    f"got {threshold}"
                )

            # Validate weight
            if 'weight' not in params:
                raise ValueError(f"Missing 'weight' for {detector_name}")
            weight = params['weight']
            if weight <= 0:
                raise ValueError(
                    f"Weight for {detector_name} must be positive, got {weight}"
                )

            # Validate confidence weight
            if 'confidence_weight' not in params:
                raise ValueError(f"Missing 'confidence_weight' for {detector_name}")
            conf_weight = params['confidence_weight']
            if not (0.0 <= conf_weight <= 1.0):
                raise ValueError(
                    f"Confidence weight for {detector_name} must be in [0.0, 1.0], "
                    f"got {conf_weight}"
                )
            confidence_sum += conf_weight

        # Validate confidence weights sum to 1.0 (with small epsilon tolerance)
        if not math.isclose(confidence_sum, 1.0, abs_tol=1e-6):
            raise ValueError(
                f"Confidence weights must sum to 1.0, got {confidence_sum}"
            )

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
                f"{detector_name} similarity score must be in [0.0, 1.0], "
                f"got {score}"
            )

    def vote(
        self,
        token_sim: float,
        ast_sim: float,
        hash_sim: float
    ) -> Dict[str, Any]:
        """
        Aggregate detector results using weighted voting to determine plagiarism.

        This method:
        1. Validates all input similarity scores
        2. Compares each score against its detector's threshold
        3. Calculates weighted votes from detectors that voted "plagiarized"
        4. Makes a final decision based on the decision threshold
        5. Computes a confidence score from weighted similarity scores

        Args:
            token_sim: Token-based similarity score (0.0-1.0).
            ast_sim: AST-based similarity score (0.0-1.0).
            hash_sim: Hash-based similarity score (0.0-1.0).

        Returns:
            Dictionary containing:
                - is_plagiarized (bool): True if weighted_votes >= decision_threshold
                - confidence_score (float): Weighted confidence in [0.0, 1.0]
                - votes (Dict[str, bool]): Individual detector votes
                - weighted_votes (float): Sum of weights from "yes" votes
                - individual_scores (Dict[str, float]): Raw similarity scores

        Raises:
            ValueError: If any similarity score is invalid (None, NaN, or
                       outside [0.0, 1.0]).

        Example:
            >>> system = VotingSystem()
            >>> result = system.vote(0.75, 0.85, 0.65)
            >>> result['is_plagiarized']
            True
            >>> result['weighted_votes']
            4.5
        """
        # Validate all inputs
        self._validate_similarity_score(token_sim, 'Token')
        self._validate_similarity_score(ast_sim, 'AST')
        self._validate_similarity_score(hash_sim, 'Hash')

        # Map scores to detector names
        scores = {
            'token': token_sim,
            'ast': ast_sim,
            'hash': hash_sim
        }

        # Determine individual detector votes
        votes = {}
        weighted_votes = 0.0

        for detector_name, score in scores.items():
            threshold = self.config[detector_name]['threshold']
            weight = self.config[detector_name]['weight']

            # Cast vote: True if score meets or exceeds threshold
            vote_result = score >= threshold
            votes[detector_name] = vote_result

            # Add weight if detector voted True
            if vote_result:
                weighted_votes += weight

            logger.debug(
                f"{detector_name.upper()} Detector: score={score:.3f}, "
                f"threshold={threshold:.2f}, vote={vote_result}, weight={weight}"
            )

        # Make final decision
        is_plagiarized = weighted_votes >= self.decision_threshold

        # Calculate confidence score (weighted average of similarity scores)
        confidence_score = sum(
            scores[detector_name] * self.config[detector_name]['confidence_weight']
            for detector_name in scores.keys()
        )

        # Clamp confidence to [0.0, 1.0] (should already be in range, but ensure)
        confidence_score = min(1.0, max(0.0, confidence_score))

        logger.info(
            f"Voting decision: is_plagiarized={is_plagiarized}, "
            f"weighted_votes={weighted_votes:.2f}/{self.total_possible_votes}, "
            f"confidence={confidence_score:.3f}"
        )

        # Construct result dictionary
        result = {
            'is_plagiarized': is_plagiarized,
            'confidence_score': confidence_score,
            'votes': votes,
            'weighted_votes': weighted_votes,
            'individual_scores': {
                'token': token_sim,
                'ast': ast_sim,
                'hash': hash_sim
            }
        }

        return result

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
                f"Unknown detector: {detector_name}. "
                f"Available: {list(self.config.keys())}"
            )
        return self.config[detector_name].copy()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the voting system configuration.

        Returns:
            Dictionary containing system configuration and thresholds.
        """
        return {
            'detectors': list(self.config.keys()),
            'detector_configs': {
                name: self.get_detector_info(name)
                for name in self.config.keys()
            },
            'total_possible_votes': self.total_possible_votes,
            'decision_threshold': self.decision_threshold,
            'decision_threshold_percentage': (
                self.decision_threshold / self.total_possible_votes * 100
            )
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the VotingSystem for debugging.

        Returns:
            String representation showing configuration details.
        """
        detector_info = ', '.join(
            f"{name}(th={cfg['threshold']:.2f}, w={cfg['weight']})"
            for name, cfg in self.config.items()
        )
        return (
            f"VotingSystem("
            f"detectors=[{detector_info}], "
            f"decision_threshold={self.decision_threshold:.2f}/{self.total_possible_votes}"
            f")"
        )

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            Formatted string describing the voting system.
        """
        lines = ["VotingSystem Configuration:"]
        for name, cfg in self.config.items():
            lines.append(
                f"  {name.upper()}: threshold={cfg['threshold']:.2f}, "
                f"weight={cfg['weight']}, confidence_weight={cfg['confidence_weight']:.2f}"
            )
        lines.append(f"Total Possible Votes: {self.total_possible_votes}")
        lines.append(f"Decision Threshold: {self.decision_threshold} (50%)")
        return '\n'.join(lines)
