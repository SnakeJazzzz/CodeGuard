"""
Confidence calculator for plagiarism detection voting system.

This module provides functions to calculate confidence scores from detector outputs,
determine confidence levels, and analyze agreement between detectors.

The confidence score represents how certain the system is about its plagiarism
determination, based on weighted combination of detector similarities and their
agreement level.
"""

import logging
from typing import Dict, Optional
import statistics

# Configure logging
logger = logging.getLogger(__name__)


def calculate_confidence(
    token: float, ast: float, hash: float, weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate overall confidence score from individual detector scores.

    The confidence score is a weighted average of the three detector similarity
    scores, indicating how confident the system is about the plagiarism determination.

    Args:
        token: Token detector similarity score [0.0, 1.0]
        ast: AST detector similarity score [0.0, 1.0]
        hash: Hash detector similarity score [0.0, 1.0]
        weights: Optional custom weights dict with keys 'token', 'ast', 'hash'.
                Defaults to {'token': 0.3, 'ast': 0.4, 'hash': 0.3}

    Returns:
        float: Confidence score in range [0.0, 1.0]

    Raises:
        ValueError: If any input score is outside [0.0, 1.0] range
        ValueError: If weights don't sum to 1.0 (within 1e-9 tolerance)
        ValueError: If weights dict has invalid keys
        TypeError: If inputs are not numeric

    Examples:
        >>> calculate_confidence(0.8, 0.9, 0.7)
        0.82

        >>> calculate_confidence(0.5, 0.5, 0.5, {'token': 0.2, 'ast': 0.6, 'hash': 0.2})
        0.5

        >>> calculate_confidence(1.2, 0.5, 0.5)  # doctest: +SKIP
        ValueError: Token score must be in range [0.0, 1.0], got 1.2
    """
    # Set default weights if not provided
    if weights is None:
        weights = {"token": 0.3, "ast": 0.4, "hash": 0.3}

    # Type validation
    try:
        token = float(token)
        ast = float(ast)
        hash_val = float(hash)
    except (TypeError, ValueError) as e:
        raise TypeError(f"All detector scores must be numeric: {e}")

    # Validate input ranges
    if not 0.0 <= token <= 1.0:
        raise ValueError(f"Token score must be in range [0.0, 1.0], got {token}")
    if not 0.0 <= ast <= 1.0:
        raise ValueError(f"AST score must be in range [0.0, 1.0], got {ast}")
    if not 0.0 <= hash_val <= 1.0:
        raise ValueError(f"Hash score must be in range [0.0, 1.0], got {hash_val}")

    # Validate weights dictionary
    required_keys = {"token", "ast", "hash"}
    if set(weights.keys()) != required_keys:
        raise ValueError(
            f"Weights must contain exactly keys {required_keys}, " f"got {set(weights.keys())}"
        )

    # Validate weights are numeric and positive
    try:
        weight_values = {k: float(v) for k, v in weights.items()}
    except (TypeError, ValueError) as e:
        raise TypeError(f"All weights must be numeric: {e}")

    for key, value in weight_values.items():
        if value < 0:
            raise ValueError(f"Weight '{key}' must be non-negative, got {value}")

    # Validate weights sum to 1.0 (with floating-point tolerance)
    weight_sum = sum(weight_values.values())
    if abs(weight_sum - 1.0) > 1e-9:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_sum}. " f"Current weights: {weight_values}"
        )

    # Calculate weighted confidence
    confidence = (
        weight_values["token"] * token
        + weight_values["ast"] * ast
        + weight_values["hash"] * hash_val
    )

    # Clamp to [0.0, 1.0] to handle floating-point errors
    confidence = max(0.0, min(1.0, confidence))

    logger.debug(
        f"Calculated confidence: {confidence:.4f} "
        f"(token={token:.4f}, ast={ast:.4f}, hash={hash_val:.4f}, "
        f"weights={weight_values})"
    )

    return confidence


def get_confidence_level(confidence: float) -> str:
    """
    Convert numeric confidence score to human-readable level.

    Maps confidence scores to descriptive labels for easier interpretation
    by end users.

    Args:
        confidence: Confidence score in range [0.0, 1.0]

    Returns:
        str: One of 'Very High', 'High', 'Medium', 'Low', 'Very Low'

    Raises:
        ValueError: If confidence is outside [0.0, 1.0] range
        TypeError: If confidence is not numeric

    Examples:
        >>> get_confidence_level(0.95)
        'Very High'

        >>> get_confidence_level(0.80)
        'High'

        >>> get_confidence_level(0.65)
        'Medium'

        >>> get_confidence_level(0.40)
        'Low'

        >>> get_confidence_level(0.15)
        'Very Low'

        >>> get_confidence_level(1.5)  # doctest: +SKIP
        ValueError: Confidence must be in range [0.0, 1.0], got 1.5
    """
    # Type validation
    try:
        confidence = float(confidence)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Confidence must be numeric: {e}")

    # Range validation
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be in range [0.0, 1.0], got {confidence}")

    # Determine level based on thresholds
    if confidence >= 0.90:
        level = "Very High"
    elif confidence >= 0.75:
        level = "High"
    elif confidence >= 0.50:
        level = "Medium"
    elif confidence >= 0.25:
        level = "Low"
    else:
        level = "Very Low"

    logger.debug(f"Confidence {confidence:.4f} mapped to level '{level}'")

    return level


def analyze_detector_agreement(token: float, ast: float, hash: float) -> Dict[str, any]:
    """
    Analyze agreement level between the three detectors.

    Provides statistical analysis of detector consensus and actionable
    recommendations based on disagreement patterns. High variance or
    large differences between detectors may indicate specific types of
    plagiarism or edge cases requiring human review.

    Args:
        token: Token detector similarity score [0.0, 1.0]
        ast: AST detector similarity score [0.0, 1.0]
        hash: Hash detector similarity score [0.0, 1.0]

    Returns:
        Dict with keys:
            - 'agreement_level': str - 'Strong', 'Moderate', 'Weak', or 'Poor'
            - 'variance': float - Statistical variance of the three scores
            - 'max_difference': float - Maximum minus minimum score
            - 'recommendations': List[str] - Actionable recommendations

    Raises:
        ValueError: If any input score is outside [0.0, 1.0] range
        TypeError: If inputs are not numeric

    Agreement Level Determination:
        - 'Strong': max_difference < 0.15 (all detectors agree closely)
        - 'Moderate': max_difference < 0.30 (reasonable agreement)
        - 'Weak': max_difference < 0.50 (significant disagreement)
        - 'Poor': max_difference >= 0.50 (detectors strongly disagree)

    Examples:
        >>> result = analyze_detector_agreement(0.85, 0.88, 0.83)
        >>> result['agreement_level']
        'Strong'
        >>> result['max_difference'] < 0.15
        True

        >>> result = analyze_detector_agreement(0.9, 0.5, 0.4)
        >>> result['agreement_level']
        'Poor'
        >>> 'significant disagreement' in result['recommendations'][0].lower()
        True
    """
    # Type validation
    try:
        token = float(token)
        ast = float(ast)
        hash_val = float(hash)
    except (TypeError, ValueError) as e:
        raise TypeError(f"All detector scores must be numeric: {e}")

    # Validate input ranges
    if not 0.0 <= token <= 1.0:
        raise ValueError(f"Token score must be in range [0.0, 1.0], got {token}")
    if not 0.0 <= ast <= 1.0:
        raise ValueError(f"AST score must be in range [0.0, 1.0], got {ast}")
    if not 0.0 <= hash_val <= 1.0:
        raise ValueError(f"Hash score must be in range [0.0, 1.0], got {hash_val}")

    scores = [token, ast, hash_val]

    # Calculate variance (population variance, not sample)
    variance = statistics.variance(scores) if len(scores) > 1 else 0.0

    # Calculate max difference
    max_score = max(scores)
    min_score = min(scores)
    max_difference = max_score - min_score

    # Determine agreement level
    if max_difference < 0.15:
        agreement_level = "Strong"
    elif max_difference < 0.30:
        agreement_level = "Moderate"
    elif max_difference < 0.50:
        agreement_level = "Weak"
    else:
        agreement_level = "Poor"

    # Generate recommendations based on analysis
    recommendations = []

    # High variance recommendation
    if variance > 0.05:  # Variance threshold for "high disagreement"
        recommendations.append(
            "Review individual detector results - significant disagreement detected"
        )

    # Identify which detector is significantly different
    # Threshold for "much higher": at least 0.20 above the average of other two
    avg_threshold = 0.20

    # Check if AST is much higher
    other_avg = (token + hash_val) / 2
    if ast - other_avg >= avg_threshold:
        recommendations.append(
            "Possible structural plagiarism with obfuscation - "
            "AST detector shows high similarity while others are lower"
        )

    # Check if Hash is much higher
    other_avg = (token + ast) / 2
    if hash_val - other_avg >= avg_threshold:
        recommendations.append(
            "Possible scattered or partial copying - "
            "Hash detector shows high similarity while others are lower"
        )

    # Check if Token is much higher
    other_avg = (ast + hash_val) / 2
    if token - other_avg >= avg_threshold:
        recommendations.append(
            "Possible direct copy with structural changes - "
            "Token detector shows high similarity while others are lower"
        )

    # Check for all low scores
    if max_score < 0.30:
        recommendations.append("All detectors show low similarity - likely not plagiarism")

    # Check for all high scores
    if min_score > 0.80:
        recommendations.append("All detectors show high similarity - strong evidence of plagiarism")

    # Check for moderate agreement with all scores in middle range
    if 0.40 <= min_score and max_score <= 0.70 and max_difference < 0.20:
        recommendations.append(
            "Moderate similarity across all detectors - manual review recommended"
        )

    # If no specific recommendations, add general guidance
    if not recommendations:
        if agreement_level in ["Strong", "Moderate"]:
            recommendations.append("Detectors show good agreement - result is reliable")
        else:
            recommendations.append(
                "Detector disagreement suggests edge case - manual review recommended"
            )

    result = {
        "agreement_level": agreement_level,
        "variance": variance,
        "max_difference": max_difference,
        "recommendations": recommendations,
    }

    logger.debug(
        f"Detector agreement analysis: {agreement_level} "
        f"(variance={variance:.4f}, max_diff={max_difference:.4f}, "
        f"scores=[token={token:.4f}, ast={ast:.4f}, hash={hash_val:.4f}])"
    )

    return result
