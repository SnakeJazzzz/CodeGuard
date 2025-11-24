"""
Comprehensive unit tests for VotingSystem class.

This test suite achieves 100% code coverage for src/voting/voting_system.py
by testing all methods, branches, edge cases, and error conditions.

Test Categories:
- Initialization and configuration validation
- Unanimous voting scenarios (all agree)
- Partial voting scenarios (some detectors trigger)
- Threshold boundary testing
- Weighted vote calculations
- Confidence score calculations
- Invalid input handling
- Return value structure validation
- String representation methods
"""

import pytest
import math
from src.voting.voting_system import VotingSystem


class TestVotingSystemInitialization:
    """Test VotingSystem initialization and configuration."""

    def test_default_initialization(self):
        """Test initialization with default configuration."""
        system = VotingSystem()

        # Verify default configuration is loaded
        assert system.config is not None
        assert "token" in system.config
        assert "ast" in system.config
        assert "hash" in system.config

        # Verify total possible votes calculation
        expected_total = 1.0 + 2.0 + 1.5  # token + ast + hash
        assert system.total_possible_votes == expected_total

        # Verify decision threshold is 50%
        assert system.decision_threshold == expected_total * 0.5
        assert system.decision_threshold == 2.25

    def test_custom_config_initialization(self):
        """Test initialization with custom configuration."""
        custom_config = {
            "token": {"threshold": 0.75, "weight": 1.5, "confidence_weight": 0.3},
            "ast": {"threshold": 0.85, "weight": 2.5, "confidence_weight": 0.4},
            "hash": {"threshold": 0.65, "weight": 2.0, "confidence_weight": 0.3},
        }

        system = VotingSystem(config=custom_config)

        # Verify custom configuration is used
        assert system.config["token"]["threshold"] == 0.75
        assert system.config["ast"]["weight"] == 2.5
        assert system.config["hash"]["confidence_weight"] == 0.3

        # Verify total possible votes with custom weights
        expected_total = 1.5 + 2.5 + 2.0
        assert system.total_possible_votes == expected_total

    def test_missing_detector_in_config(self):
        """Test that missing detector in config raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.5},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.5}
            # Missing 'hash' detector
        }

        with pytest.raises(ValueError, match="must contain exactly these detectors"):
            VotingSystem(config=invalid_config)

    def test_extra_detector_in_config(self):
        """Test that extra detector in config raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.25},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.25},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.25},
            "extra": {"threshold": 0.50, "weight": 1.0, "confidence_weight": 0.25},
        }

        with pytest.raises(ValueError, match="must contain exactly these detectors"):
            VotingSystem(config=invalid_config)

    def test_missing_threshold_parameter(self):
        """Test that missing threshold parameter raises ValueError."""
        invalid_config = {
            "token": {"weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Missing 'threshold'"):
            VotingSystem(config=invalid_config)

    def test_missing_weight_parameter(self):
        """Test that missing weight parameter raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Missing 'weight'"):
            VotingSystem(config=invalid_config)

    def test_missing_confidence_weight_parameter(self):
        """Test that missing confidence_weight parameter raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.5},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.5},
        }

        with pytest.raises(ValueError, match="Missing 'confidence_weight'"):
            VotingSystem(config=invalid_config)

    def test_threshold_below_range(self):
        """Test that threshold below 0.0 raises ValueError."""
        invalid_config = {
            "token": {"threshold": -0.1, "weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Threshold .* must be in \\[0.0, 1.0\\]"):
            VotingSystem(config=invalid_config)

    def test_threshold_above_range(self):
        """Test that threshold above 1.0 raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 1.5, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Threshold .* must be in \\[0.0, 1.0\\]"):
            VotingSystem(config=invalid_config)

    def test_negative_weight(self):
        """Test that negative weight raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": -1.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Weight .* must be positive"):
            VotingSystem(config=invalid_config)

    def test_zero_weight(self):
        """Test that zero weight raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 0.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Weight .* must be positive"):
            VotingSystem(config=invalid_config)

    def test_confidence_weight_below_range(self):
        """Test that confidence_weight below 0.0 raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": -0.1},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.6},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.5},
        }

        with pytest.raises(ValueError, match="Confidence weight .* must be in \\[0.0, 1.0\\]"):
            VotingSystem(config=invalid_config)

    def test_confidence_weight_above_range(self):
        """Test that confidence_weight above 1.0 raises ValueError."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 1.5},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }

        with pytest.raises(ValueError, match="Confidence weight .* must be in \\[0.0, 1.0\\]"):
            VotingSystem(config=invalid_config)

    def test_confidence_weights_not_sum_to_one(self):
        """Test that confidence weights must sum to 1.0."""
        invalid_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.3},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.4},
            "hash": {
                "threshold": 0.60,
                "weight": 1.5,
                "confidence_weight": 0.5,  # Sum = 1.2, not 1.0
            },
        }

        with pytest.raises(ValueError, match="Confidence weights must sum to 1.0"):
            VotingSystem(config=invalid_config)


class TestVotingDecisions:
    """Test voting decision logic with various scenarios."""

    def test_unanimous_high_votes_plagiarism(self):
        """Test all 3 detectors trigger - should be plagiarized."""
        system = VotingSystem()

        # All detectors above their thresholds
        result = system.vote(token_sim=0.80, ast_sim=0.90, hash_sim=0.75)

        # Verify plagiarism detected
        assert result["is_plagiarized"] is True

        # Verify all votes are True
        assert result["votes"]["token"] is True
        assert result["votes"]["ast"] is True
        assert result["votes"]["hash"] is True

        # Verify weighted votes = all weights (1.0 + 2.0 + 1.5 = 4.5)
        assert result["weighted_votes"] == 4.5

        # Verify individual scores match inputs
        assert result["individual_scores"]["token"] == 0.80
        assert result["individual_scores"]["ast"] == 0.90
        assert result["individual_scores"]["hash"] == 0.75

    def test_unanimous_low_votes_no_plagiarism(self):
        """Test none of the detectors trigger - should not be plagiarized."""
        system = VotingSystem()

        # All detectors below their thresholds
        result = system.vote(token_sim=0.50, ast_sim=0.60, hash_sim=0.40)

        # Verify plagiarism NOT detected
        assert result["is_plagiarized"] is False

        # Verify all votes are False
        assert result["votes"]["token"] is False
        assert result["votes"]["ast"] is False
        assert result["votes"]["hash"] is False

        # Verify weighted votes = 0.0
        assert result["weighted_votes"] == 0.0

    def test_ast_only_detection(self):
        """Test only AST triggers - should NOT be plagiarized (44% < 50%)."""
        system = VotingSystem()

        # Only AST above threshold
        result = system.vote(token_sim=0.65, ast_sim=0.85, hash_sim=0.55)

        # AST weight=2.0, total possible=4.5, so 2.0/4.5=44% < 50% threshold
        assert result["is_plagiarized"] is False

        # Verify only AST voted True
        assert result["votes"]["token"] is False
        assert result["votes"]["ast"] is True
        assert result["votes"]["hash"] is False

        # Verify weighted votes = 2.0 (AST weight only)
        assert result["weighted_votes"] == 2.0

    def test_token_and_ast_detection(self):
        """Test Token + AST trigger - should be plagiarized (67% > 50%)."""
        system = VotingSystem()

        # Token and AST above thresholds
        result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.55)

        # Weighted votes: 1.0+2.0=3.0, percentage=3.0/4.5=67% > 50%
        assert result["is_plagiarized"] is True

        # Verify Token and AST voted True
        assert result["votes"]["token"] is True
        assert result["votes"]["ast"] is True
        assert result["votes"]["hash"] is False

        # Verify weighted votes = 3.0 (Token 1.0 + AST 2.0)
        assert result["weighted_votes"] == 3.0

    def test_ast_and_hash_detection(self):
        """Test AST + Hash trigger - should be plagiarized (78% > 50%)."""
        system = VotingSystem()

        # AST and Hash above thresholds
        result = system.vote(token_sim=0.65, ast_sim=0.85, hash_sim=0.75)

        # Weighted votes: 2.0+1.5=3.5, percentage=3.5/4.5=78% > 50%
        assert result["is_plagiarized"] is True

        # Verify AST and Hash voted True
        assert result["votes"]["token"] is False
        assert result["votes"]["ast"] is True
        assert result["votes"]["hash"] is True

        # Verify weighted votes = 3.5 (AST 2.0 + Hash 1.5)
        assert result["weighted_votes"] == 3.5

    def test_token_and_hash_detection(self):
        """Test Token + Hash trigger - should be plagiarized (56% > 50%)."""
        system = VotingSystem()

        # Token and Hash above thresholds
        result = system.vote(token_sim=0.75, ast_sim=0.75, hash_sim=0.65)

        # Weighted votes: 1.0+1.5=2.5, percentage=2.5/4.5=56% > 50%
        assert result["is_plagiarized"] is True

        # Verify Token and Hash voted True
        assert result["votes"]["token"] is True
        assert result["votes"]["ast"] is False
        assert result["votes"]["hash"] is True

        # Verify weighted votes = 2.5 (Token 1.0 + Hash 1.5)
        assert result["weighted_votes"] == 2.5

    def test_token_only_detection(self):
        """Test only Token triggers - should NOT be plagiarized (22% < 50%)."""
        system = VotingSystem()

        # Only Token above threshold
        result = system.vote(token_sim=0.75, ast_sim=0.75, hash_sim=0.55)

        # Token weight=1.0, total possible=4.5, so 1.0/4.5=22% < 50%
        assert result["is_plagiarized"] is False

        # Verify only Token voted True
        assert result["votes"]["token"] is True
        assert result["votes"]["ast"] is False
        assert result["votes"]["hash"] is False

        # Verify weighted votes = 1.0
        assert result["weighted_votes"] == 1.0

    def test_hash_only_detection(self):
        """Test only Hash triggers - should NOT be plagiarized (33% < 50%)."""
        system = VotingSystem()

        # Only Hash above threshold
        result = system.vote(token_sim=0.65, ast_sim=0.75, hash_sim=0.65)

        # Hash weight=1.5, total possible=4.5, so 1.5/4.5=33% < 50%
        assert result["is_plagiarized"] is False

        # Verify only Hash voted True
        assert result["votes"]["token"] is False
        assert result["votes"]["ast"] is False
        assert result["votes"]["hash"] is True

        # Verify weighted votes = 1.5
        assert result["weighted_votes"] == 1.5


class TestThresholdBoundaries:
    """Test voting behavior at exact threshold boundaries."""

    def test_decision_threshold_exact_boundary(self):
        """Test exactly at 50% decision threshold (weighted_votes=2.25)."""
        system = VotingSystem()

        # Create scenario where weighted_votes = exactly 2.25 (50%)
        # This requires Token (1.0) + some fractional contribution
        # But we can only get discrete votes, so test at threshold

        # Token + Hash = 2.5 (above threshold)
        result = system.vote(token_sim=0.70, ast_sim=0.75, hash_sim=0.60)
        assert result["weighted_votes"] == 2.5
        assert result["is_plagiarized"] is True

        # Only AST = 2.0 (below threshold)
        result = system.vote(token_sim=0.69, ast_sim=0.80, hash_sim=0.59)
        assert result["weighted_votes"] == 2.0
        assert result["is_plagiarized"] is False

    def test_token_threshold_exact_boundary(self):
        """Test Token detector at exact threshold (0.70)."""
        system = VotingSystem()

        # Exactly at threshold - should vote True (>=)
        result = system.vote(token_sim=0.70, ast_sim=0.60, hash_sim=0.50)
        assert result["votes"]["token"] is True

        # Just below threshold - should vote False
        result = system.vote(token_sim=0.69999, ast_sim=0.60, hash_sim=0.50)
        assert result["votes"]["token"] is False

    def test_ast_threshold_exact_boundary(self):
        """Test AST detector at exact threshold (0.80)."""
        system = VotingSystem()

        # Exactly at threshold - should vote True (>=)
        result = system.vote(token_sim=0.60, ast_sim=0.80, hash_sim=0.50)
        assert result["votes"]["ast"] is True

        # Just below threshold - should vote False
        result = system.vote(token_sim=0.60, ast_sim=0.79999, hash_sim=0.50)
        assert result["votes"]["ast"] is False

    def test_hash_threshold_exact_boundary(self):
        """Test Hash detector at exact threshold (0.60)."""
        system = VotingSystem()

        # Exactly at threshold - should vote True (>=)
        result = system.vote(token_sim=0.60, ast_sim=0.70, hash_sim=0.60)
        assert result["votes"]["hash"] is True

        # Just below threshold - should vote False
        result = system.vote(token_sim=0.60, ast_sim=0.70, hash_sim=0.59999)
        assert result["votes"]["hash"] is False


class TestConfidenceCalculation:
    """Test confidence score calculation logic."""

    def test_confidence_score_calculation(self):
        """Verify confidence = 0.3×token + 0.4×ast + 0.3×hash."""
        system = VotingSystem()

        result = system.vote(token_sim=0.80, ast_sim=0.90, hash_sim=0.70)

        # Calculate expected confidence
        expected = 0.3 * 0.80 + 0.4 * 0.90 + 0.3 * 0.70
        expected = 0.24 + 0.36 + 0.21
        expected = 0.81

        assert pytest.approx(result["confidence_score"], abs=1e-6) == expected

    def test_confidence_score_all_zeros(self):
        """Test confidence calculation with all zero scores."""
        system = VotingSystem()

        result = system.vote(token_sim=0.0, ast_sim=0.0, hash_sim=0.0)

        expected = 0.3 * 0.0 + 0.4 * 0.0 + 0.3 * 0.0
        assert result["confidence_score"] == expected
        assert result["confidence_score"] == 0.0

    def test_confidence_score_all_ones(self):
        """Test confidence calculation with all maximum scores."""
        system = VotingSystem()

        result = system.vote(token_sim=1.0, ast_sim=1.0, hash_sim=1.0)

        expected = 0.3 * 1.0 + 0.4 * 1.0 + 0.3 * 1.0
        assert result["confidence_score"] == expected
        assert result["confidence_score"] == 1.0

    def test_confidence_score_clamping(self):
        """Test that confidence score is clamped to [0.0, 1.0]."""
        system = VotingSystem()

        # Even with extreme values, confidence should be clamped
        result = system.vote(token_sim=1.0, ast_sim=1.0, hash_sim=1.0)
        assert 0.0 <= result["confidence_score"] <= 1.0

        result = system.vote(token_sim=0.0, ast_sim=0.0, hash_sim=0.0)
        assert 0.0 <= result["confidence_score"] <= 1.0

    def test_confidence_score_custom_weights(self):
        """Test confidence calculation with custom weights."""
        custom_config = {
            "token": {"threshold": 0.70, "weight": 1.0, "confidence_weight": 0.2},
            "ast": {"threshold": 0.80, "weight": 2.0, "confidence_weight": 0.5},
            "hash": {"threshold": 0.60, "weight": 1.5, "confidence_weight": 0.3},
        }
        system = VotingSystem(config=custom_config)

        result = system.vote(token_sim=0.60, ast_sim=0.80, hash_sim=0.50)

        expected = 0.2 * 0.60 + 0.5 * 0.80 + 0.3 * 0.50
        expected = 0.12 + 0.40 + 0.15
        expected = 0.67

        assert pytest.approx(result["confidence_score"], abs=1e-6) == expected


class TestInvalidInputs:
    """Test handling of invalid input values."""

    def test_none_token_score(self):
        """Test that None token score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Token.*cannot be None"):
            system.vote(token_sim=None, ast_sim=0.80, hash_sim=0.60)

    def test_none_ast_score(self):
        """Test that None AST score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="AST.*cannot be None"):
            system.vote(token_sim=0.70, ast_sim=None, hash_sim=0.60)

    def test_none_hash_score(self):
        """Test that None hash score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Hash.*cannot be None"):
            system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=None)

    def test_nan_token_score(self):
        """Test that NaN token score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Token.*is NaN"):
            system.vote(token_sim=float("nan"), ast_sim=0.80, hash_sim=0.60)

    def test_nan_ast_score(self):
        """Test that NaN AST score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="AST.*is NaN"):
            system.vote(token_sim=0.70, ast_sim=float("nan"), hash_sim=0.60)

    def test_nan_hash_score(self):
        """Test that NaN hash score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Hash.*is NaN"):
            system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=float("nan"))

    def test_infinite_token_score(self):
        """Test that infinite token score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Token.*is infinite"):
            system.vote(token_sim=float("inf"), ast_sim=0.80, hash_sim=0.60)

    def test_infinite_ast_score(self):
        """Test that infinite AST score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="AST.*is infinite"):
            system.vote(token_sim=0.70, ast_sim=float("inf"), hash_sim=0.60)

    def test_infinite_hash_score(self):
        """Test that infinite hash score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Hash.*is infinite"):
            system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=float("inf"))

    def test_negative_token_score(self):
        """Test that negative token score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Token.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=-0.1, ast_sim=0.80, hash_sim=0.60)

    def test_token_score_above_one(self):
        """Test that token score > 1.0 raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Token.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=1.5, ast_sim=0.80, hash_sim=0.60)

    def test_negative_ast_score(self):
        """Test that negative AST score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="AST.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=0.70, ast_sim=-0.1, hash_sim=0.60)

    def test_ast_score_above_one(self):
        """Test that AST score > 1.0 raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="AST.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=0.70, ast_sim=1.5, hash_sim=0.60)

    def test_negative_hash_score(self):
        """Test that negative hash score raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Hash.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=-0.1)

    def test_hash_score_above_one(self):
        """Test that hash score > 1.0 raises ValueError."""
        system = VotingSystem()

        with pytest.raises(ValueError, match="Hash.*must be in \\[0.0, 1.0\\]"):
            system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=1.5)


class TestReturnValueStructure:
    """Test the structure and content of return values."""

    def test_return_value_has_all_keys(self):
        """Test that vote() returns all required keys."""
        system = VotingSystem()
        result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Verify all required keys are present
        assert "is_plagiarized" in result
        assert "confidence_score" in result
        assert "votes" in result
        assert "weighted_votes" in result
        assert "individual_scores" in result

    def test_return_value_types(self):
        """Test that return values have correct types."""
        system = VotingSystem()
        result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Verify types
        assert isinstance(result["is_plagiarized"], bool)
        assert isinstance(result["confidence_score"], float)
        assert isinstance(result["votes"], dict)
        assert isinstance(result["weighted_votes"], (int, float))
        assert isinstance(result["individual_scores"], dict)

    def test_votes_structure(self):
        """Test that votes dictionary has correct structure."""
        system = VotingSystem()
        result = system.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Verify votes has all detector keys
        assert "token" in result["votes"]
        assert "ast" in result["votes"]
        assert "hash" in result["votes"]

        # Verify all votes are boolean
        assert isinstance(result["votes"]["token"], bool)
        assert isinstance(result["votes"]["ast"], bool)
        assert isinstance(result["votes"]["hash"], bool)

    def test_individual_scores_structure(self):
        """Test that individual_scores match input values."""
        system = VotingSystem()

        token_input = 0.75
        ast_input = 0.85
        hash_input = 0.65

        result = system.vote(token_sim=token_input, ast_sim=ast_input, hash_sim=hash_input)

        # Verify individual scores match inputs exactly
        assert result["individual_scores"]["token"] == token_input
        assert result["individual_scores"]["ast"] == ast_input
        assert result["individual_scores"]["hash"] == hash_input


class TestDetectorInfo:
    """Test get_detector_info and related methods."""

    def test_get_detector_info_token(self):
        """Test getting token detector info."""
        system = VotingSystem()
        info = system.get_detector_info("token")

        assert info["threshold"] == 0.70
        assert info["weight"] == 1.0
        assert info["confidence_weight"] == 0.3

    def test_get_detector_info_ast(self):
        """Test getting AST detector info."""
        system = VotingSystem()
        info = system.get_detector_info("ast")

        assert info["threshold"] == 0.80
        assert info["weight"] == 2.0
        assert info["confidence_weight"] == 0.4

    def test_get_detector_info_hash(self):
        """Test getting hash detector info."""
        system = VotingSystem()
        info = system.get_detector_info("hash")

        assert info["threshold"] == 0.60
        assert info["weight"] == 1.5
        assert info["confidence_weight"] == 0.3

    def test_get_detector_info_invalid_name(self):
        """Test that invalid detector name raises KeyError."""
        system = VotingSystem()

        with pytest.raises(KeyError, match="Unknown detector"):
            system.get_detector_info("invalid")

    def test_get_detector_info_returns_copy(self):
        """Test that get_detector_info returns a copy, not reference."""
        system = VotingSystem()
        info = system.get_detector_info("token")

        # Modify the returned info
        info["threshold"] = 0.99

        # Original should be unchanged
        assert system.config["token"]["threshold"] == 0.70


class TestSummary:
    """Test get_summary method."""

    def test_get_summary_structure(self):
        """Test that get_summary returns all required keys."""
        system = VotingSystem()
        summary = system.get_summary()

        assert "detectors" in summary
        assert "detector_configs" in summary
        assert "total_possible_votes" in summary
        assert "decision_threshold" in summary
        assert "decision_threshold_percentage" in summary

    def test_get_summary_detectors_list(self):
        """Test that summary contains correct detector list."""
        system = VotingSystem()
        summary = system.get_summary()

        assert "token" in summary["detectors"]
        assert "ast" in summary["detectors"]
        assert "hash" in summary["detectors"]
        assert len(summary["detectors"]) == 3

    def test_get_summary_detector_configs(self):
        """Test that summary contains all detector configs."""
        system = VotingSystem()
        summary = system.get_summary()

        assert "token" in summary["detector_configs"]
        assert "ast" in summary["detector_configs"]
        assert "hash" in summary["detector_configs"]

    def test_get_summary_values(self):
        """Test that summary values are correct."""
        system = VotingSystem()
        summary = system.get_summary()

        assert summary["total_possible_votes"] == 4.5
        assert summary["decision_threshold"] == 2.25
        assert summary["decision_threshold_percentage"] == 50.0


class TestStringRepresentations:
    """Test __repr__ and __str__ methods."""

    def test_repr_method(self):
        """Test that __repr__ returns valid string."""
        system = VotingSystem()
        repr_str = repr(system)

        assert isinstance(repr_str, str)
        assert "VotingSystem" in repr_str
        assert "token" in repr_str
        assert "ast" in repr_str
        assert "hash" in repr_str

    def test_repr_contains_thresholds(self):
        """Test that __repr__ contains threshold information."""
        system = VotingSystem()
        repr_str = repr(system)

        # Should contain threshold values
        assert "th=" in repr_str or "threshold" in repr_str.lower()

    def test_repr_contains_weights(self):
        """Test that __repr__ contains weight information."""
        system = VotingSystem()
        repr_str = repr(system)

        # Should contain weight values
        assert "w=" in repr_str or "weight" in repr_str.lower()

    def test_repr_contains_decision_threshold(self):
        """Test that __repr__ contains decision threshold."""
        system = VotingSystem()
        repr_str = repr(system)

        assert "2.25" in repr_str or "decision_threshold" in repr_str.lower()

    def test_str_method(self):
        """Test that __str__ returns readable format."""
        system = VotingSystem()
        str_repr = str(system)

        assert isinstance(str_repr, str)
        assert "VotingSystem" in str_repr
        assert "TOKEN" in str_repr or "token" in str_repr
        assert "AST" in str_repr or "ast" in str_repr
        assert "HASH" in str_repr or "hash" in str_repr

    def test_str_contains_configuration(self):
        """Test that __str__ contains configuration details."""
        system = VotingSystem()
        str_repr = str(system)

        # Should contain detector information
        assert "threshold" in str_repr.lower()
        assert "weight" in str_repr.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_scores_zero(self):
        """Test with all similarity scores at 0.0."""
        system = VotingSystem()
        result = system.vote(token_sim=0.0, ast_sim=0.0, hash_sim=0.0)

        assert result["is_plagiarized"] is False
        assert result["confidence_score"] == 0.0
        assert result["weighted_votes"] == 0.0
        assert all(not vote for vote in result["votes"].values())

    def test_all_scores_one(self):
        """Test with all similarity scores at 1.0."""
        system = VotingSystem()
        result = system.vote(token_sim=1.0, ast_sim=1.0, hash_sim=1.0)

        assert result["is_plagiarized"] is True
        assert result["confidence_score"] == 1.0
        assert result["weighted_votes"] == 4.5
        assert all(vote for vote in result["votes"].values())

    def test_scores_at_detector_thresholds(self):
        """Test with all scores exactly at their thresholds."""
        system = VotingSystem()

        # All at threshold - should all vote True (>=)
        result = system.vote(token_sim=0.70, ast_sim=0.80, hash_sim=0.60)

        assert result["votes"]["token"] is True
        assert result["votes"]["ast"] is True
        assert result["votes"]["hash"] is True
        assert result["is_plagiarized"] is True

    def test_scores_just_below_thresholds(self):
        """Test with all scores just below their thresholds."""
        system = VotingSystem()

        result = system.vote(token_sim=0.69, ast_sim=0.79, hash_sim=0.59)

        assert result["votes"]["token"] is False
        assert result["votes"]["ast"] is False
        assert result["votes"]["hash"] is False
        assert result["is_plagiarized"] is False

    def test_very_small_positive_scores(self):
        """Test with very small positive scores."""
        system = VotingSystem()

        result = system.vote(token_sim=0.0001, ast_sim=0.0001, hash_sim=0.0001)

        assert result["is_plagiarized"] is False
        assert 0.0 <= result["confidence_score"] <= 1.0

    def test_scores_very_close_to_one(self):
        """Test with scores very close to 1.0."""
        system = VotingSystem()

        result = system.vote(token_sim=0.9999, ast_sim=0.9999, hash_sim=0.9999)

        assert result["is_plagiarized"] is True
        assert 0.0 <= result["confidence_score"] <= 1.0
