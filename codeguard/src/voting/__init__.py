"""
Voting system package for plagiarism detection.

This package provides weighted voting mechanisms to aggregate results
from multiple plagiarism detectors with configurable thresholds and weights.
"""

from .voting_system import VotingSystem
from .confidence_calculator import (
    calculate_confidence,
    get_confidence_level,
    analyze_detector_agreement,
)
from .thresholds import ThresholdManager

__all__ = [
    "VotingSystem",
    "calculate_confidence",
    "get_confidence_level",
    "analyze_detector_agreement",
    "ThresholdManager",
]
__version__ = "1.0.0"
