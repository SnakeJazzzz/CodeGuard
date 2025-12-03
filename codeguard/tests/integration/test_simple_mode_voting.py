"""
Integration Test 4: Simple Mode Voting Logic

Purpose:
    Verify Simple mode requires BOTH Token AND AST to vote YES.

Bug Fixed:
    Task 14 - Simple mode voting logic (required both Token AND AST to vote YES)

Test Coverage:
    - Simple mode requires higher consensus (75% threshold)
    - Both Token AND AST must vote YES for plagiarism detection
    - Single detector cannot trigger plagiarism in Simple mode
    - Comparison with Standard mode voting behavior

Author: CodeGuard Team
Date: 2025-12-03
"""

import pytest
from src.core.config_presets import get_preset_config, PRESET_STANDARD, PRESET_SIMPLE
from src.voting.voting_system import VotingSystem


class TestSimpleModeVotingLogic:
    """Test suite for Simple mode voting requirements."""

    def test_simple_mode_requires_both_detectors(self):
        """
        Test that Simple mode requires BOTH Token AND AST to vote YES.

        Simple mode configuration:
            - Token weight: 2.0
            - AST weight: 2.0
            - Hash weight: 0.0 (disabled)
            - Total votes: 4.0
            - Decision threshold: 75% (3.0 votes)

        For plagiarism to be detected, need 3.0 out of 4.0 votes.
        Since Token + AST = 2.0 + 2.0 = 4.0, BOTH must vote YES.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Verify Simple mode configuration
        assert voting.total_possible_votes == 4.0, \
            "Simple mode should have 4.0 total votes"
        assert voting.decision_threshold == 3.0, \
            "Simple mode should require 3.0 votes (75%)"

        # Case 1: BOTH vote YES - should detect plagiarism
        result1 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.0)
        assert result1['votes']['token'] == 2.0, "Token should vote YES"
        assert result1['votes']['ast'] == 2.0, "AST should vote YES"
        assert result1['total_votes_cast'] == 4.0, "Total should be 4.0"
        assert result1['is_plagiarized'] == True, \
            "BOTH detectors voting YES should trigger plagiarism"

        # Case 2: Only Token votes YES - should NOT detect
        result2 = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=0.0)
        assert result2['votes']['token'] == 2.0, "Token should vote YES"
        assert result2['votes']['ast'] == 0.0, "AST should vote NO (below 0.85 threshold)"
        assert result2['total_votes_cast'] == 2.0, "Total should be 2.0"
        assert result2['is_plagiarized'] == False, \
            "Only Token voting YES should NOT trigger plagiarism (2.0 < 3.0)"

        # Case 3: Only AST votes YES - should NOT detect
        result3 = voting.vote(token_sim=0.65, ast_sim=0.90, hash_sim=0.0)
        assert result3['votes']['token'] == 0.0, "Token should vote NO (below 0.70 threshold)"
        assert result3['votes']['ast'] == 2.0, "AST should vote YES"
        assert result3['total_votes_cast'] == 2.0, "Total should be 2.0"
        assert result3['is_plagiarized'] == False, \
            "Only AST voting YES should NOT trigger plagiarism (2.0 < 3.0)"

        # Case 4: Neither votes YES - should NOT detect
        result4 = voting.vote(token_sim=0.60, ast_sim=0.75, hash_sim=0.0)
        assert result4['votes']['token'] == 0.0, "Token should vote NO"
        assert result4['votes']['ast'] == 0.0, "AST should vote NO"
        assert result4['total_votes_cast'] == 0.0, "Total should be 0.0"
        assert result4['is_plagiarized'] == False, \
            "Neither detector voting YES should NOT trigger plagiarism"

    def test_simple_mode_stricter_than_standard(self):
        """
        Test that Simple mode is more conservative than Standard mode.

        Same scores should be more likely to trigger plagiarism in
        Standard mode than in Simple mode.
        """
        # Create both voting systems
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test case: Token YES, AST NO, Hash YES in Standard mode
        # Standard thresholds: Token=0.70, AST=0.80, Hash=0.60
        # Simple thresholds: Token=0.70, AST=0.85, Hash=0.60
        token_sim, ast_sim, hash_sim = 0.75, 0.82, 0.65

        # Standard mode: Token (1.0) + AST (2.0) + Hash (1.5) = 4.5
        # Decision threshold: 2.25 (50%)
        result_standard = voting_standard.vote(token_sim, ast_sim, hash_sim)

        # Simple mode: Token (2.0) + AST (0.0) + Hash (0.0) = 2.0
        # Decision threshold: 3.0 (75%)
        result_simple = voting_simple.vote(token_sim, ast_sim, hash_sim)

        # Standard should detect (4.5 >= 2.25)
        assert result_standard['is_plagiarized'] == True, \
            f"Standard mode should detect (votes: {result_standard['total_votes_cast']})"

        # Simple should NOT detect (2.0 < 3.0, AST below 0.85 threshold)
        assert result_simple['is_plagiarized'] == False, \
            f"Simple mode should NOT detect (votes: {result_simple['total_votes_cast']})"

    def test_simple_mode_reduces_false_positives(self):
        """
        Test that Simple mode reduces false positives on edge cases.

        Scenarios where only one detector has high confidence should
        not trigger plagiarism in Simple mode.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Scenario 1: High token, medium AST (potential false positive)
        result1 = voting.vote(token_sim=0.95, ast_sim=0.75, hash_sim=0.0)
        assert result1['is_plagiarized'] == False, \
            "High token alone should not trigger plagiarism in Simple mode"

        # Scenario 2: Medium token, high AST (potential false positive)
        result2 = voting.vote(token_sim=0.60, ast_sim=0.95, hash_sim=0.0)
        assert result2['is_plagiarized'] == False, \
            "High AST alone should not trigger plagiarism in Simple mode"

        # Scenario 3: Both detectors barely meet thresholds (true positive)
        result3 = voting.vote(token_sim=0.70, ast_sim=0.85, hash_sim=0.0)
        assert result3['is_plagiarized'] == True, \
            "Both detectors meeting thresholds should trigger plagiarism in Simple mode"

    def test_simple_mode_ast_threshold_stricter(self):
        """
        Test that Simple mode uses stricter AST threshold (0.85 vs 0.80).

        This helps reduce false positives on simple problems where
        AST similarity can be high due to limited structural variation.
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Score between the two thresholds (0.80 < score < 0.85)
        ast_score = 0.82

        # Standard: AST threshold = 0.80, so 0.82 should vote YES
        result_standard = voting_standard.vote(token_sim=0.75, ast_sim=ast_score, hash_sim=0.65)
        assert result_standard['votes']['ast'] > 0.0, \
            "Standard mode: AST should vote YES with score 0.82 (threshold 0.80)"

        # Simple: AST threshold = 0.85, so 0.82 should vote NO
        result_simple = voting_simple.vote(token_sim=0.75, ast_sim=ast_score, hash_sim=0.65)
        assert result_simple['votes']['ast'] == 0.0, \
            "Simple mode: AST should vote NO with score 0.82 (threshold 0.85)"

    def test_simple_mode_decision_threshold_percentage(self):
        """
        Test that Simple mode requires 75% consensus vs Standard's 50%.

        Simple: 3.0 / 4.0 = 75%
        Standard: 2.25 / 4.5 = 50%
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Calculate percentages
        standard_pct = (voting_standard.decision_threshold / voting_standard.total_possible_votes) * 100
        simple_pct = (voting_simple.decision_threshold / voting_simple.total_possible_votes) * 100

        assert abs(standard_pct - 50.0) < 0.1, \
            f"Standard mode should require 50% consensus, got {standard_pct:.1f}%"
        assert abs(simple_pct - 75.0) < 0.1, \
            f"Simple mode should require 75% consensus, got {simple_pct:.1f}%"

    def test_simple_mode_equal_detector_weights(self):
        """
        Test that Simple mode gives equal weight to Token and AST.

        Token weight = AST weight = 2.0
        This ensures neither detector can trigger plagiarism alone.
        """
        config = get_preset_config(PRESET_SIMPLE)

        assert config['token']['weight'] == 2.0, \
            "Token weight should be 2.0 in Simple mode"
        assert config['ast']['weight'] == 2.0, \
            "AST weight should be 2.0 in Simple mode"
        assert config['token']['weight'] == config['ast']['weight'], \
            "Token and AST should have equal weights in Simple mode"

    def test_boundary_case_exactly_75_percent(self):
        """
        Test plagiarism detection at exactly 75% threshold.

        With 3.0 votes out of 4.0 total, should detect plagiarism.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Both detectors vote YES = 4.0 votes (100%)
        result1 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.0)
        assert result1['is_plagiarized'] == True, \
            "100% consensus should detect plagiarism"

        # Only Token votes YES = 2.0 votes (50%)
        result2 = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=0.0)
        assert result2['is_plagiarized'] == False, \
            "50% consensus should NOT detect plagiarism (below 75% threshold)"


class TestSimpleModeEdgeCases:
    """Test edge cases specific to Simple mode voting."""

    def test_hash_score_ignored_in_simple_mode(self):
        """
        Test that hash score has no effect on Simple mode decisions.

        Even perfect hash score should not affect outcome.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test with perfect hash score
        result1 = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=1.0)

        # Test with zero hash score
        result2 = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=0.0)

        # Results should be identical
        assert result1['is_plagiarized'] == result2['is_plagiarized'], \
            "Hash score should not affect plagiarism decision in Simple mode"
        assert result1['total_votes_cast'] == result2['total_votes_cast'], \
            "Hash score should not affect total votes in Simple mode"

    def test_minimum_scores_for_detection(self):
        """
        Test minimum similarity scores required for plagiarism detection.

        Simple mode requires:
            - Token >= 0.70 (threshold)
            - AST >= 0.85 (threshold)
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Exactly at thresholds - should detect
        result1 = voting.vote(token_sim=0.70, ast_sim=0.85, hash_sim=0.0)
        assert result1['is_plagiarized'] == True, \
            "Scores exactly at thresholds should detect plagiarism"

        # Just below AST threshold - should NOT detect
        result2 = voting.vote(token_sim=0.70, ast_sim=0.849, hash_sim=0.0)
        assert result2['is_plagiarized'] == False, \
            "AST score below threshold should NOT detect plagiarism"

        # Just below Token threshold - should NOT detect
        result3 = voting.vote(token_sim=0.699, ast_sim=0.85, hash_sim=0.0)
        assert result3['is_plagiarized'] == False, \
            "Token score below threshold should NOT detect plagiarism"

    def test_high_confidence_single_detector_rejected(self):
        """
        Test that even very high confidence from single detector is rejected.

        This is key for reducing false positives in Simple mode.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Perfect token score, but AST below threshold
        result1 = voting.vote(token_sim=1.0, ast_sim=0.84, hash_sim=0.0)
        assert result1['is_plagiarized'] == False, \
            "Perfect token score should not override AST requirement"

        # Perfect AST score, but Token below threshold
        result2 = voting.vote(token_sim=0.69, ast_sim=1.0, hash_sim=0.0)
        assert result2['is_plagiarized'] == False, \
            "Perfect AST score should not override Token requirement"

    def test_confidence_score_with_two_detectors(self):
        """
        Test confidence calculation uses only Token and AST in Simple mode.

        Hash should not contribute to confidence even if it has a score.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Get confidence weights
        token_conf_weight = voting.config['token']['confidence_weight']
        ast_conf_weight = voting.config['ast']['confidence_weight']
        hash_conf_weight = voting.config['hash']['confidence_weight']

        # Verify hash confidence weight is 0.0
        assert hash_conf_weight == 0.0, \
            "Hash confidence weight should be 0.0 in Simple mode"

        # Verify token + ast confidence weights sum to 1.0
        total_conf = token_conf_weight + ast_conf_weight
        assert abs(total_conf - 1.0) < 0.01, \
            f"Token + AST confidence weights should sum to 1.0, got {total_conf}"

        # Test confidence calculation
        result = voting.vote(token_sim=0.80, ast_sim=0.90, hash_sim=0.95)

        # Expected confidence (only token and ast)
        expected_conf = (0.80 * token_conf_weight) + (0.90 * ast_conf_weight)

        assert abs(result['confidence_score'] - expected_conf) < 0.01, \
            f"Confidence should ignore hash score, expected {expected_conf}, got {result['confidence_score']}"


class TestStandardVsSimpleComparison:
    """Compare voting behavior between Standard and Simple modes."""

    def test_same_scores_different_outcomes(self):
        """
        Test cases where Standard detects but Simple does not.

        This demonstrates Simple mode's reduced false positive rate.
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test case 1: Medium AST (0.82), passes Standard but fails Simple
        scores1 = (0.75, 0.82, 0.65)
        result_std1 = voting_standard.vote(*scores1)
        result_sim1 = voting_simple.vote(*scores1)

        assert result_std1['is_plagiarized'] == True, \
            "Standard should detect with AST 0.82 (threshold 0.80)"
        assert result_sim1['is_plagiarized'] == False, \
            "Simple should NOT detect with AST 0.82 (threshold 0.85)"

        # Test case 2: Low token (0.65), AST YES, Hash YES in Standard
        scores2 = (0.65, 0.85, 0.70)
        result_std2 = voting_standard.vote(*scores2)
        result_sim2 = voting_simple.vote(*scores2)

        # Standard: Token NO (0.0) + AST YES (2.0) + Hash YES (1.5) = 3.5 >= 2.25
        assert result_std2['is_plagiarized'] == True, \
            "Standard should detect with AST + Hash agreement"

        # Simple: Token NO (0.0) + AST YES (2.0) + Hash disabled (0.0) = 2.0 < 3.0
        assert result_sim2['is_plagiarized'] == False, \
            "Simple should NOT detect without Token agreement"

    def test_both_modes_agree_on_clear_cases(self):
        """
        Test that both modes agree on clear plagiarism and clear non-plagiarism.
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Clear plagiarism: all scores high
        scores1 = (0.95, 0.95, 0.95)
        result_std1 = voting_standard.vote(*scores1)
        result_sim1 = voting_simple.vote(*scores1)

        assert result_std1['is_plagiarized'] == True, \
            "Standard should detect clear plagiarism"
        assert result_sim1['is_plagiarized'] == True, \
            "Simple should detect clear plagiarism"

        # Clear non-plagiarism: all scores low
        scores2 = (0.30, 0.30, 0.30)
        result_std2 = voting_standard.vote(*scores2)
        result_sim2 = voting_simple.vote(*scores2)

        assert result_std2['is_plagiarized'] == False, \
            "Standard should NOT detect clear non-plagiarism"
        assert result_sim2['is_plagiarized'] == False, \
            "Simple should NOT detect clear non-plagiarism"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
