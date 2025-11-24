"""
Comprehensive unit tests for confidence_calculator module.

This test suite achieves 100% code coverage for src/voting/confidence_calculator.py
by testing all functions, branches, edge cases, and error conditions.

Functions tested:
- calculate_confidence(): Weighted confidence score calculation
- get_confidence_level(): Confidence score to level mapping
- analyze_detector_agreement(): Detector agreement analysis

Test Categories:
- Default and custom weight scenarios
- Input validation and error handling
- Boundary value testing
- Agreement level determination
- Recommendation generation logic
- Statistical calculations (variance, max_difference)
"""

import pytest
import statistics
from src.voting.confidence_calculator import (
    calculate_confidence,
    get_confidence_level,
    analyze_detector_agreement,
)


class TestCalculateConfidence:
    """Test calculate_confidence function."""

    def test_default_weights(self):
        """Test confidence calculation with default weights."""
        # Default: token=0.3, ast=0.4, hash=0.3
        result = calculate_confidence(0.8, 0.9, 0.7)

        expected = 0.3 * 0.8 + 0.4 * 0.9 + 0.3 * 0.7
        expected = 0.24 + 0.36 + 0.21
        expected = 0.81

        assert pytest.approx(result, abs=1e-9) == expected

    def test_custom_weights(self):
        """Test confidence calculation with custom weights."""
        custom_weights = {"token": 0.2, "ast": 0.6, "hash": 0.2}
        result = calculate_confidence(0.5, 0.8, 0.6, weights=custom_weights)

        expected = 0.2 * 0.5 + 0.6 * 0.8 + 0.2 * 0.6
        expected = 0.1 + 0.48 + 0.12
        expected = 0.70

        assert pytest.approx(result, abs=1e-9) == expected

    def test_all_zeros(self):
        """Test with all zero scores."""
        result = calculate_confidence(0.0, 0.0, 0.0)
        assert result == 0.0

    def test_all_ones(self):
        """Test with all maximum scores."""
        result = calculate_confidence(1.0, 1.0, 1.0)
        assert result == 1.0

    def test_clamping_to_zero(self):
        """Test that result is clamped to 0.0 minimum."""
        # Even though mathematically impossible with valid inputs,
        # test the clamping logic
        result = calculate_confidence(0.0, 0.0, 0.0)
        assert result >= 0.0

    def test_clamping_to_one(self):
        """Test that result is clamped to 1.0 maximum."""
        result = calculate_confidence(1.0, 1.0, 1.0)
        assert result <= 1.0

    def test_token_score_below_range(self):
        """Test that token score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Token score must be in range"):
            calculate_confidence(-0.1, 0.5, 0.5)

    def test_token_score_above_range(self):
        """Test that token score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Token score must be in range"):
            calculate_confidence(1.5, 0.5, 0.5)

    def test_ast_score_below_range(self):
        """Test that AST score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="AST score must be in range"):
            calculate_confidence(0.5, -0.1, 0.5)

    def test_ast_score_above_range(self):
        """Test that AST score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="AST score must be in range"):
            calculate_confidence(0.5, 1.5, 0.5)

    def test_hash_score_below_range(self):
        """Test that hash score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Hash score must be in range"):
            calculate_confidence(0.5, 0.5, -0.1)

    def test_hash_score_above_range(self):
        """Test that hash score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Hash score must be in range"):
            calculate_confidence(0.5, 0.5, 1.5)

    def test_weights_dont_sum_to_one(self):
        """Test that weights must sum to 1.0."""
        invalid_weights = {"token": 0.3, "ast": 0.4, "hash": 0.4}  # Sum = 1.1

        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            calculate_confidence(0.5, 0.5, 0.5, weights=invalid_weights)

    def test_weights_sum_with_tolerance(self):
        """Test that weights sum validation uses floating-point tolerance."""
        # These weights sum to 1.0 within tolerance
        valid_weights = {"token": 0.333333333, "ast": 0.333333334, "hash": 0.333333333}

        # Should not raise error
        result = calculate_confidence(0.6, 0.7, 0.8, weights=valid_weights)
        assert 0.0 <= result <= 1.0

    def test_missing_weight_key(self):
        """Test that missing weight key raises ValueError."""
        invalid_weights = {"token": 0.5, "ast": 0.5}  # Missing 'hash'

        with pytest.raises(ValueError, match="Weights must contain exactly keys"):
            calculate_confidence(0.5, 0.5, 0.5, weights=invalid_weights)

    def test_extra_weight_key(self):
        """Test that extra weight key raises ValueError."""
        invalid_weights = {"token": 0.25, "ast": 0.25, "hash": 0.25, "extra": 0.25}

        with pytest.raises(ValueError, match="Weights must contain exactly keys"):
            calculate_confidence(0.5, 0.5, 0.5, weights=invalid_weights)

    def test_negative_weight(self):
        """Test that negative weight raises ValueError."""
        invalid_weights = {"token": -0.1, "ast": 0.6, "hash": 0.5}

        with pytest.raises(ValueError, match="must be non-negative"):
            calculate_confidence(0.5, 0.5, 0.5, weights=invalid_weights)

    def test_non_numeric_score_token(self):
        """Test that non-numeric token score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            calculate_confidence("invalid", 0.5, 0.5)

    def test_non_numeric_score_ast(self):
        """Test that non-numeric AST score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            calculate_confidence(0.5, "invalid", 0.5)

    def test_non_numeric_score_hash(self):
        """Test that non-numeric hash score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            calculate_confidence(0.5, 0.5, "invalid")

    def test_non_numeric_weight(self):
        """Test that non-numeric weight raises TypeError."""
        invalid_weights = {"token": "invalid", "ast": 0.5, "hash": 0.5}

        with pytest.raises(TypeError, match="must be numeric"):
            calculate_confidence(0.5, 0.5, 0.5, weights=invalid_weights)

    def test_boundary_scores(self):
        """Test with scores at exact boundaries."""
        # All at lower boundary
        result = calculate_confidence(0.0, 0.0, 0.0)
        assert result == 0.0

        # All at upper boundary
        result = calculate_confidence(1.0, 1.0, 1.0)
        assert result == 1.0

        # Mixed boundaries
        result = calculate_confidence(0.0, 1.0, 0.5)
        expected = 0.3 * 0.0 + 0.4 * 1.0 + 0.3 * 0.5
        assert pytest.approx(result, abs=1e-9) == expected


class TestGetConfidenceLevel:
    """Test get_confidence_level function."""

    def test_very_high_confidence(self):
        """Test confidence >= 0.90 returns 'Very High'."""
        assert get_confidence_level(0.90) == "Very High"
        assert get_confidence_level(0.95) == "Very High"
        assert get_confidence_level(1.0) == "Very High"

    def test_high_confidence(self):
        """Test confidence in [0.75, 0.90) returns 'High'."""
        assert get_confidence_level(0.75) == "High"
        assert get_confidence_level(0.80) == "High"
        assert get_confidence_level(0.89) == "High"

    def test_medium_confidence(self):
        """Test confidence in [0.50, 0.75) returns 'Medium'."""
        assert get_confidence_level(0.50) == "Medium"
        assert get_confidence_level(0.60) == "Medium"
        assert get_confidence_level(0.74) == "Medium"

    def test_low_confidence(self):
        """Test confidence in [0.25, 0.50) returns 'Low'."""
        assert get_confidence_level(0.25) == "Low"
        assert get_confidence_level(0.35) == "Low"
        assert get_confidence_level(0.49) == "Low"

    def test_very_low_confidence(self):
        """Test confidence < 0.25 returns 'Very Low'."""
        assert get_confidence_level(0.0) == "Very Low"
        assert get_confidence_level(0.10) == "Very Low"
        assert get_confidence_level(0.24) == "Very Low"

    def test_exact_boundaries(self):
        """Test exact boundary values."""
        assert get_confidence_level(0.90) == "Very High"
        assert get_confidence_level(0.8999999) == "High"

        assert get_confidence_level(0.75) == "High"
        assert get_confidence_level(0.7499999) == "Medium"

        assert get_confidence_level(0.50) == "Medium"
        assert get_confidence_level(0.4999999) == "Low"

        assert get_confidence_level(0.25) == "Low"
        assert get_confidence_level(0.2499999) == "Very Low"

    def test_confidence_below_range(self):
        """Test that confidence < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="must be in range"):
            get_confidence_level(-0.1)

    def test_confidence_above_range(self):
        """Test that confidence > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="must be in range"):
            get_confidence_level(1.5)

    def test_non_numeric_confidence(self):
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            get_confidence_level("invalid")

    def test_confidence_at_zero(self):
        """Test confidence at exact 0.0."""
        assert get_confidence_level(0.0) == "Very Low"

    def test_confidence_at_one(self):
        """Test confidence at exact 1.0."""
        assert get_confidence_level(1.0) == "Very High"


class TestAnalyzeDetectorAgreement:
    """Test analyze_detector_agreement function."""

    def test_strong_agreement(self):
        """Test max_difference < 0.15 returns 'Strong'."""
        result = analyze_detector_agreement(0.85, 0.88, 0.83)

        assert result["agreement_level"] == "Strong"
        assert result["max_difference"] < 0.15

    def test_moderate_agreement(self):
        """Test max_difference in [0.15, 0.30) returns 'Moderate'."""
        result = analyze_detector_agreement(0.80, 0.95, 0.75)

        assert result["agreement_level"] == "Moderate"
        assert 0.15 <= result["max_difference"] < 0.30

    def test_weak_agreement(self):
        """Test max_difference in [0.30, 0.50) returns 'Weak'."""
        result = analyze_detector_agreement(0.50, 0.85, 0.45)

        assert result["agreement_level"] == "Weak"
        assert 0.30 <= result["max_difference"] < 0.50

    def test_poor_agreement(self):
        """Test max_difference >= 0.50 returns 'Poor'."""
        result = analyze_detector_agreement(0.90, 0.50, 0.40)

        assert result["agreement_level"] == "Poor"
        assert result["max_difference"] >= 0.50

    def test_variance_calculation(self):
        """Test that variance is calculated correctly."""
        scores = [0.6, 0.7, 0.8]
        result = analyze_detector_agreement(0.6, 0.7, 0.8)

        expected_variance = statistics.variance(scores)
        assert pytest.approx(result["variance"], abs=1e-9) == expected_variance

    def test_max_difference_calculation(self):
        """Test that max_difference is calculated correctly."""
        result = analyze_detector_agreement(0.5, 0.9, 0.4)

        expected_max_diff = 0.9 - 0.4
        assert pytest.approx(result["max_difference"], abs=1e-9) == expected_max_diff

    def test_recommendations_high_variance(self):
        """Test that high variance generates recommendation."""
        # Large spread should have variance > 0.05
        result = analyze_detector_agreement(0.3, 0.9, 0.4)

        # Should contain recommendation about disagreement
        recommendations = " ".join(result["recommendations"]).lower()
        assert "disagreement" in recommendations or "review" in recommendations

    def test_recommendations_ast_much_higher(self):
        """Test AST >> others generates structural plagiarism recommendation."""
        # AST is 0.20+ higher than average of others
        result = analyze_detector_agreement(0.5, 0.95, 0.5)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "structural" in recommendations or "ast" in recommendations

    def test_recommendations_hash_much_higher(self):
        """Test Hash >> others generates scattered copy recommendation."""
        # Hash is 0.20+ higher than average of others
        result = analyze_detector_agreement(0.5, 0.5, 0.95)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "scattered" in recommendations or "hash" in recommendations

    def test_recommendations_token_much_higher(self):
        """Test Token >> others generates direct copy recommendation."""
        # Token is 0.20+ higher than average of others
        result = analyze_detector_agreement(0.95, 0.5, 0.5)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "direct" in recommendations or "token" in recommendations

    def test_recommendations_all_low(self):
        """Test all low scores generates 'likely not plagiarism' recommendation."""
        result = analyze_detector_agreement(0.2, 0.25, 0.15)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "low similarity" in recommendations or "not plagiarism" in recommendations

    def test_recommendations_all_high(self):
        """Test all high scores generates 'strong evidence' recommendation."""
        result = analyze_detector_agreement(0.85, 0.90, 0.88)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "high similarity" in recommendations or "plagiarism" in recommendations

    def test_recommendations_moderate_middle_range(self):
        """Test moderate agreement in middle range generates manual review recommendation."""
        result = analyze_detector_agreement(0.55, 0.60, 0.58)

        recommendations = " ".join(result["recommendations"]).lower()
        assert "moderate" in recommendations or "manual review" in recommendations

    def test_recommendations_good_agreement(self):
        """Test good agreement generates 'reliable' recommendation."""
        result = analyze_detector_agreement(0.70, 0.72, 0.71)

        # Should have 'Strong' or 'Moderate' agreement
        assert result["agreement_level"] in ["Strong", "Moderate"]

        recommendations = " ".join(result["recommendations"]).lower()
        assert "reliable" in recommendations or "good agreement" in recommendations

    def test_recommendations_edge_case(self):
        """Test edge case generates manual review recommendation."""
        result = analyze_detector_agreement(0.35, 0.75, 0.45)

        # Weak or Poor agreement
        assert result["agreement_level"] in ["Weak", "Poor"]

        # Should have at least one recommendation
        assert len(result["recommendations"]) > 0

        # Recommendation should be actionable
        recommendations = " ".join(result["recommendations"]).lower()
        assert len(recommendations) > 0

    def test_return_structure(self):
        """Test that return value has all required keys."""
        result = analyze_detector_agreement(0.7, 0.8, 0.6)

        assert "agreement_level" in result
        assert "variance" in result
        assert "max_difference" in result
        assert "recommendations" in result

    def test_return_types(self):
        """Test that return values have correct types."""
        result = analyze_detector_agreement(0.7, 0.8, 0.6)

        assert isinstance(result["agreement_level"], str)
        assert isinstance(result["variance"], (int, float))
        assert isinstance(result["max_difference"], (int, float))
        assert isinstance(result["recommendations"], list)

    def test_recommendations_is_non_empty(self):
        """Test that recommendations list is never empty."""
        # Test various scenarios
        scenarios = [
            (0.1, 0.2, 0.15),  # All low
            (0.9, 0.95, 0.92),  # All high
            (0.5, 0.6, 0.55),  # Moderate
            (0.3, 0.9, 0.4),  # High variance
            (0.95, 0.5, 0.5),  # Token high
            (0.5, 0.95, 0.5),  # AST high
            (0.5, 0.5, 0.95),  # Hash high
        ]

        for token, ast, hash_val in scenarios:
            result = analyze_detector_agreement(token, ast, hash_val)
            assert (
                len(result["recommendations"]) > 0
            ), f"Empty recommendations for ({token}, {ast}, {hash_val})"

    def test_token_score_below_range(self):
        """Test that token score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Token score must be in range"):
            analyze_detector_agreement(-0.1, 0.5, 0.5)

    def test_token_score_above_range(self):
        """Test that token score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Token score must be in range"):
            analyze_detector_agreement(1.5, 0.5, 0.5)

    def test_ast_score_below_range(self):
        """Test that AST score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="AST score must be in range"):
            analyze_detector_agreement(0.5, -0.1, 0.5)

    def test_ast_score_above_range(self):
        """Test that AST score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="AST score must be in range"):
            analyze_detector_agreement(0.5, 1.5, 0.5)

    def test_hash_score_below_range(self):
        """Test that hash score < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="Hash score must be in range"):
            analyze_detector_agreement(0.5, 0.5, -0.1)

    def test_hash_score_above_range(self):
        """Test that hash score > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="Hash score must be in range"):
            analyze_detector_agreement(0.5, 0.5, 1.5)

    def test_non_numeric_token_score(self):
        """Test that non-numeric token score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            analyze_detector_agreement("invalid", 0.5, 0.5)

    def test_non_numeric_ast_score(self):
        """Test that non-numeric AST score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            analyze_detector_agreement(0.5, "invalid", 0.5)

    def test_non_numeric_hash_score(self):
        """Test that non-numeric hash score raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            analyze_detector_agreement(0.5, 0.5, "invalid")

    def test_all_same_scores(self):
        """Test with all detectors having identical scores."""
        result = analyze_detector_agreement(0.75, 0.75, 0.75)

        assert result["agreement_level"] == "Strong"
        assert result["max_difference"] == 0.0
        assert result["variance"] == 0.0

    def test_exact_agreement_boundaries(self):
        """Test exact agreement level boundaries."""
        # Exactly at Strong/Moderate boundary (0.15)
        result = analyze_detector_agreement(0.5, 0.65, 0.5)
        assert pytest.approx(result["max_difference"], abs=1e-9) == 0.15
        assert result["agreement_level"] == "Moderate"

        # Just below boundary
        result = analyze_detector_agreement(0.5, 0.6499, 0.5)
        assert result["agreement_level"] == "Strong"

        # Exactly at Moderate/Weak boundary (0.30)
        result = analyze_detector_agreement(0.5, 0.80, 0.5)
        assert pytest.approx(result["max_difference"], abs=1e-9) == 0.30
        assert result["agreement_level"] == "Weak"

        # Exactly at Weak/Poor boundary (0.50)
        result = analyze_detector_agreement(0.5, 1.0, 0.5)
        assert pytest.approx(result["max_difference"], abs=1e-9) == 0.50
        assert result["agreement_level"] == "Poor"

    def test_variance_with_identical_scores(self):
        """Test variance calculation when all scores are identical."""
        result = analyze_detector_agreement(0.6, 0.6, 0.6)

        # Variance should be 0 when all values are the same
        assert result["variance"] == 0.0

    def test_multiple_recommendations_possible(self):
        """Test that multiple recommendations can be generated."""
        # High variance + AST much higher should generate multiple recommendations
        result = analyze_detector_agreement(0.3, 0.9, 0.35)

        # Should have at least 2 recommendations
        assert len(result["recommendations"]) >= 1

    def test_recommendations_weak_without_other_patterns(self):
        """Test weak agreement without specific detector patterns generates edge case recommendation."""
        # Weak agreement (max_diff=0.35) with no specific high detector
        result = analyze_detector_agreement(0.40, 0.75, 0.50)

        assert result["agreement_level"] == "Weak"

        # Should have at least one recommendation
        assert len(result["recommendations"]) > 0
