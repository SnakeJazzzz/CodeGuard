"""
Integration Test 5: Voting Results Display

Purpose:
    Verify hash detector correctly appears/disappears in results based on mode.

Bug Fixed:
    Task 15 - Hash columns not returning after mode switch

Test Coverage:
    - Hash results hidden in Simple mode
    - Hash results visible in Standard mode
    - Results structure correct for both modes
    - No stale data from previous mode

Note:
    This test validates the results data structure, not UI rendering.
    It ensures the voting system returns correct results for display.

Author: CodeGuard Team
Date: 2025-12-03
"""

import pytest
from src.core.config_presets import get_preset_config, PRESET_STANDARD, PRESET_SIMPLE
from src.voting.voting_system import VotingSystem


class TestVotingResultsStructure:
    """Test suite for voting results data structure."""

    def test_standard_mode_includes_all_detectors(self):
        """
        Test that Standard mode results include all three detectors.

        Results should contain:
            - Token vote and score
            - AST vote and score
            - Hash vote and score
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Verify all detectors present in votes
        assert 'token' in result['votes'], "Token should be in results"
        assert 'ast' in result['votes'], "AST should be in results"
        assert 'hash' in result['votes'], "Hash should be in results"

        # Verify all detectors present in individual scores
        assert 'token' in result['individual_scores'], "Token score should be in results"
        assert 'ast' in result['individual_scores'], "AST score should be in results"
        assert 'hash' in result['individual_scores'], "Hash score should be in results"

        # Verify hash has actual vote value (not zero in Standard mode)
        assert result['votes']['hash'] > 0.0, \
            "Hash should have non-zero vote in Standard mode when score exceeds threshold"

    def test_simple_mode_includes_all_detectors_but_hash_disabled(self):
        """
        Test that Simple mode results include all detectors, but hash votes 0.

        Results should still contain hash score for transparency, but vote is 0.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))
        result = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.95)

        # Verify all detectors present in votes
        assert 'token' in result['votes'], "Token should be in results"
        assert 'ast' in result['votes'], "AST should be in results"
        assert 'hash' in result['votes'], "Hash should be in results"

        # Verify all detectors present in individual scores
        assert 'token' in result['individual_scores'], "Token score should be in results"
        assert 'ast' in result['individual_scores'], "AST score should be in results"
        assert 'hash' in result['individual_scores'], "Hash score should be in results"

        # Verify hash vote is zero (disabled)
        assert result['votes']['hash'] == 0.0, \
            "Hash vote should be 0.0 in Simple mode (disabled)"

        # Verify hash score is still present (for transparency)
        assert result['individual_scores']['hash'] == 0.95, \
            "Hash score should still be preserved in results"

    def test_total_votes_excludes_disabled_detectors(self):
        """
        Test that total_votes_cast only includes active detectors.

        Standard: Can include hash votes
        Simple: Should never include hash votes
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test with high scores (all detectors would vote YES if enabled)
        token_sim, ast_sim, hash_sim = 0.95, 0.95, 0.95

        # Standard mode: all three vote
        result_std = voting_standard.vote(token_sim, ast_sim, hash_sim)
        expected_std = 1.0 + 2.0 + 1.5  # Token + AST + Hash = 4.5

        assert abs(result_std['total_votes_cast'] - expected_std) < 0.01, \
            f"Standard total votes should be {expected_std}, got {result_std['total_votes_cast']}"

        # Simple mode: only token and ast vote
        result_sim = voting_simple.vote(token_sim, ast_sim, hash_sim)
        expected_sim = 2.0 + 2.0  # Token + AST = 4.0 (hash disabled)

        assert abs(result_sim['total_votes_cast'] - expected_sim) < 0.01, \
            f"Simple total votes should be {expected_sim}, got {result_sim['total_votes_cast']}"

    def test_total_possible_votes_reflects_mode(self):
        """
        Test that total_possible_votes reflects the mode configuration.

        Standard: 4.5 (includes hash weight 1.5)
        Simple: 4.0 (hash weight is 0.0)
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        result_std = voting_standard.vote(token_sim=0.5, ast_sim=0.5, hash_sim=0.5)
        result_sim = voting_simple.vote(token_sim=0.5, ast_sim=0.5, hash_sim=0.5)

        assert result_std['total_possible_votes'] == 4.5, \
            f"Standard total possible votes should be 4.5, got {result_std['total_possible_votes']}"

        assert result_sim['total_possible_votes'] == 4.0, \
            f"Simple total possible votes should be 4.0, got {result_sim['total_possible_votes']}"

    def test_decision_threshold_reflects_mode(self):
        """
        Test that decision_threshold in results reflects the mode.

        Standard: 2.25 (50% of 4.5)
        Simple: 3.0 (75% of 4.0)
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        result_std = voting_standard.vote(token_sim=0.5, ast_sim=0.5, hash_sim=0.5)
        result_sim = voting_simple.vote(token_sim=0.5, ast_sim=0.5, hash_sim=0.5)

        assert abs(result_std['decision_threshold'] - 2.25) < 0.01, \
            f"Standard decision threshold should be 2.25, got {result_std['decision_threshold']}"

        assert abs(result_sim['decision_threshold'] - 3.0) < 0.01, \
            f"Simple decision threshold should be 3.0, got {result_sim['decision_threshold']}"


class TestResultsDisplayCompatibility:
    """Test that results are suitable for display in both modes."""

    def test_detector_agreement_calculation_standard(self):
        """
        Test detector agreement for Standard mode (3 detectors).

        Agreement = number of detectors that voted YES / total active detectors
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # All three agree
        result1 = voting.vote(token_sim=0.95, ast_sim=0.95, hash_sim=0.95)
        yes_votes1 = sum(1 for v in result1['votes'].values() if v > 0)
        assert yes_votes1 == 3, "All three detectors should vote YES"

        # Two agree (token and ast)
        result2 = voting.vote(token_sim=0.95, ast_sim=0.95, hash_sim=0.50)
        yes_votes2 = sum(1 for v in result2['votes'].values() if v > 0)
        assert yes_votes2 == 2, "Two detectors should vote YES"

        # One agrees (only ast)
        result3 = voting.vote(token_sim=0.50, ast_sim=0.95, hash_sim=0.50)
        yes_votes3 = sum(1 for v in result3['votes'].values() if v > 0)
        assert yes_votes3 == 1, "One detector should vote YES"

    def test_detector_agreement_calculation_simple(self):
        """
        Test detector agreement for Simple mode (2 active detectors).

        Hash should not be counted in agreement calculation.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Both active detectors agree
        result1 = voting.vote(token_sim=0.95, ast_sim=0.95, hash_sim=0.95)
        # Count only token and ast (hash is disabled)
        active_yes = sum(1 for k, v in result1['votes'].items()
                        if k != 'hash' and v > 0)
        assert active_yes == 2, "Both active detectors should vote YES"

        # One active detector agrees
        result2 = voting.vote(token_sim=0.95, ast_sim=0.80, hash_sim=0.95)
        active_yes2 = sum(1 for k, v in result2['votes'].items()
                         if k != 'hash' and v > 0)
        assert active_yes2 == 1, "One active detector should vote YES"

        # Verify hash vote is always 0
        assert result1['votes']['hash'] == 0.0, "Hash should not vote in Simple mode"
        assert result2['votes']['hash'] == 0.0, "Hash should not vote in Simple mode"

    def test_confidence_score_calculation_standard(self):
        """
        Test confidence score uses all three detectors in Standard mode.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Get confidence weights
        token_weight = voting.config['token']['confidence_weight']
        ast_weight = voting.config['ast']['confidence_weight']
        hash_weight = voting.config['hash']['confidence_weight']

        # All weights should be positive
        assert token_weight > 0, "Token confidence weight should be positive"
        assert ast_weight > 0, "AST confidence weight should be positive"
        assert hash_weight > 0, "Hash confidence weight should be positive"

        # Weights should sum to 1.0
        total = token_weight + ast_weight + hash_weight
        assert abs(total - 1.0) < 0.01, \
            f"Confidence weights should sum to 1.0, got {total}"

        # Test confidence calculation
        token_sim, ast_sim, hash_sim = 0.80, 0.90, 0.70
        result = voting.vote(token_sim, ast_sim, hash_sim)

        expected_conf = (token_sim * token_weight +
                        ast_sim * ast_weight +
                        hash_sim * hash_weight)

        assert abs(result['confidence_score'] - expected_conf) < 0.01, \
            f"Confidence should be {expected_conf}, got {result['confidence_score']}"

    def test_confidence_score_calculation_simple(self):
        """
        Test confidence score uses only token and ast in Simple mode.

        Hash confidence weight should be 0.0.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Get confidence weights
        token_weight = voting.config['token']['confidence_weight']
        ast_weight = voting.config['ast']['confidence_weight']
        hash_weight = voting.config['hash']['confidence_weight']

        # Hash weight should be 0
        assert hash_weight == 0.0, "Hash confidence weight should be 0.0 in Simple mode"

        # Token and AST weights should sum to 1.0
        total = token_weight + ast_weight
        assert abs(total - 1.0) < 0.01, \
            f"Token + AST confidence weights should sum to 1.0, got {total}"

        # Test confidence calculation (hash should not contribute)
        token_sim, ast_sim, hash_sim = 0.80, 0.90, 0.10
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Expected: only token and ast contribute
        expected_conf = (token_sim * token_weight + ast_sim * ast_weight)

        assert abs(result['confidence_score'] - expected_conf) < 0.01, \
            f"Confidence should ignore hash, expected {expected_conf}, got {result['confidence_score']}"


class TestResultsConsistency:
    """Test that results are consistent across multiple calls."""

    def test_same_input_same_output_standard(self):
        """
        Test that same input produces same output in Standard mode.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Run same test 5 times
        results = []
        for _ in range(5):
            result = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)
            results.append(result)

        # All results should be identical
        for i in range(1, 5):
            assert results[i]['is_plagiarized'] == results[0]['is_plagiarized'], \
                f"Result {i} plagiarism decision differs from result 0"
            assert abs(results[i]['total_votes_cast'] - results[0]['total_votes_cast']) < 0.01, \
                f"Result {i} total votes differs from result 0"
            assert abs(results[i]['confidence_score'] - results[0]['confidence_score']) < 0.01, \
                f"Result {i} confidence differs from result 0"

    def test_same_input_same_output_simple(self):
        """
        Test that same input produces same output in Simple mode.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Run same test 5 times
        results = []
        for _ in range(5):
            result = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.65)
            results.append(result)

        # All results should be identical
        for i in range(1, 5):
            assert results[i]['is_plagiarized'] == results[0]['is_plagiarized'], \
                f"Result {i} plagiarism decision differs from result 0"
            assert abs(results[i]['total_votes_cast'] - results[0]['total_votes_cast']) < 0.01, \
                f"Result {i} total votes differs from result 0"
            assert abs(results[i]['confidence_score'] - results[0]['confidence_score']) < 0.01, \
                f"Result {i} confidence differs from result 0"
            assert results[i]['votes']['hash'] == 0.0, \
                f"Result {i} hash vote should be 0.0 in Simple mode"

    def test_no_stale_data_after_mode_switch(self):
        """
        Test that switching modes doesn't leave stale data.

        After switching from Standard to Simple, hash votes should be 0.
        After switching from Simple to Standard, hash votes should work.
        """
        # Start with Standard
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result_std = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Hash should vote in Standard
        assert result_std['votes']['hash'] > 0.0, \
            "Hash should vote in Standard mode"

        # Switch to Simple
        voting.update_config(get_preset_config(PRESET_SIMPLE))
        result_sim = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Hash should NOT vote in Simple (no stale data)
        assert result_sim['votes']['hash'] == 0.0, \
            "Hash should not vote in Simple mode (no stale data from Standard)"

        # Switch back to Standard
        voting.update_config(get_preset_config(PRESET_STANDARD))
        result_std2 = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Hash should vote again in Standard (no stale data from Simple)
        assert result_std2['votes']['hash'] > 0.0, \
            "Hash should vote in Standard mode after switching from Simple"

        # Results should match original Standard result
        assert result_std2['is_plagiarized'] == result_std['is_plagiarized'], \
            "Standard results should be consistent after mode switch"


class TestResultsFormatting:
    """Test that results are formatted correctly for display."""

    def test_all_required_fields_present_standard(self):
        """
        Test that all required fields are present in Standard mode results.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Required top-level fields
        assert 'is_plagiarized' in result, "Missing is_plagiarized field"
        assert 'confidence_score' in result, "Missing confidence_score field"
        assert 'votes' in result, "Missing votes field"
        assert 'total_votes_cast' in result, "Missing total_votes_cast field"
        assert 'decision_threshold' in result, "Missing decision_threshold field"
        assert 'total_possible_votes' in result, "Missing total_possible_votes field"
        assert 'individual_scores' in result, "Missing individual_scores field"

        # Required votes subfields
        assert 'token' in result['votes'], "Missing token vote"
        assert 'ast' in result['votes'], "Missing ast vote"
        assert 'hash' in result['votes'], "Missing hash vote"

        # Required scores subfields
        assert 'token' in result['individual_scores'], "Missing token score"
        assert 'ast' in result['individual_scores'], "Missing ast score"
        assert 'hash' in result['individual_scores'], "Missing hash score"

    def test_all_required_fields_present_simple(self):
        """
        Test that all required fields are present in Simple mode results.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))
        result = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.65)

        # All same fields as Standard mode
        assert 'is_plagiarized' in result, "Missing is_plagiarized field"
        assert 'confidence_score' in result, "Missing confidence_score field"
        assert 'votes' in result, "Missing votes field"
        assert 'total_votes_cast' in result, "Missing total_votes_cast field"
        assert 'decision_threshold' in result, "Missing decision_threshold field"
        assert 'total_possible_votes' in result, "Missing total_possible_votes field"
        assert 'individual_scores' in result, "Missing individual_scores field"

        # All three detectors still present (hash just votes 0)
        assert 'token' in result['votes'], "Missing token vote"
        assert 'ast' in result['votes'], "Missing ast vote"
        assert 'hash' in result['votes'], "Missing hash vote"

        assert 'token' in result['individual_scores'], "Missing token score"
        assert 'ast' in result['individual_scores'], "Missing ast score"
        assert 'hash' in result['individual_scores'], "Missing hash score"

    def test_numeric_fields_have_correct_types(self):
        """
        Test that all numeric fields have correct types and ranges.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim=0.75, ast_sim=0.85, hash_sim=0.65)

        # Boolean field
        assert isinstance(result['is_plagiarized'], bool), \
            "is_plagiarized should be boolean"

        # Float fields in [0.0, 1.0]
        assert isinstance(result['confidence_score'], float), \
            "confidence_score should be float"
        assert 0.0 <= result['confidence_score'] <= 1.0, \
            f"confidence_score should be in [0.0, 1.0], got {result['confidence_score']}"

        # Similarity scores in [0.0, 1.0]
        for detector, score in result['individual_scores'].items():
            assert isinstance(score, float), \
                f"{detector} score should be float"
            assert 0.0 <= score <= 1.0, \
                f"{detector} score should be in [0.0, 1.0], got {score}"

        # Vote weights (non-negative floats)
        for detector, vote in result['votes'].items():
            assert isinstance(vote, (int, float)), \
                f"{detector} vote should be numeric"
            assert vote >= 0.0, \
                f"{detector} vote should be non-negative, got {vote}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
