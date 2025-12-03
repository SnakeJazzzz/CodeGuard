"""
Integration Test 1: Threshold Application

Purpose:
    Verify that changing threshold sliders actually affects voting decisions.

Bug Fixed:
    Task 11 - Threshold application bug (sidebar values weren't applied to voting)

Test Coverage:
    - Threshold changes affect individual detector votes
    - Voting totals change accordingly
    - Configuration is applied correctly
    - All three detectors (Token, AST, Hash) respond to threshold changes

Author: CodeGuard Team
Date: 2025-12-03
"""

import pytest
from src.core.config_presets import get_preset_config, PRESET_STANDARD, PRESET_SIMPLE
from src.voting.voting_system import VotingSystem


class TestThresholdApplication:
    """Test suite for threshold application functionality."""

    def test_token_threshold_affects_voting(self):
        """
        Test that changing Token threshold affects its voting decision.

        Scenario:
            - Use known similarity scores: Token=0.72, AST=0.87, Hash=0.65
            - Test with default threshold (0.70) - should vote YES
            - Test with raised threshold (0.90) - should vote NO
        """
        config = get_preset_config(PRESET_STANDARD)

        # Test 1: Default threshold (0.70) - Token should vote YES
        config['token']['threshold'] = 0.70
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['token'] > 0.0, \
            f"Token should vote YES (0.72 > 0.70), but voted: {result['votes']['token']}"
        assert result['votes']['token'] == config['token']['weight'], \
            f"Token vote should equal its weight ({config['token']['weight']}), got {result['votes']['token']}"

        # Test 2: Raised threshold (0.90) - Token should vote NO
        config['token']['threshold'] = 0.90
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['token'] == 0.0, \
            f"Token should vote NO (0.72 < 0.90), but voted: {result['votes']['token']}"

    def test_ast_threshold_affects_voting(self):
        """
        Test that changing AST threshold affects its voting decision.

        Scenario:
            - Use known similarity scores: Token=0.72, AST=0.87, Hash=0.65
            - Test with default threshold (0.80) - should vote YES
            - Test with raised threshold (0.95) - should vote NO
        """
        config = get_preset_config(PRESET_STANDARD)

        # Test 1: Default threshold (0.80) - AST should vote YES
        config['ast']['threshold'] = 0.80
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['ast'] > 0.0, \
            f"AST should vote YES (0.87 > 0.80), but voted: {result['votes']['ast']}"
        assert result['votes']['ast'] == config['ast']['weight'], \
            f"AST vote should equal its weight ({config['ast']['weight']}), got {result['votes']['ast']}"

        # Test 2: Raised threshold (0.95) - AST should vote NO
        config['ast']['threshold'] = 0.95
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['ast'] == 0.0, \
            f"AST should vote NO (0.87 < 0.95), but voted: {result['votes']['ast']}"

    def test_hash_threshold_affects_voting(self):
        """
        Test that changing Hash threshold affects its voting decision.

        Scenario:
            - Use known similarity scores: Token=0.72, AST=0.87, Hash=0.65
            - Test with default threshold (0.60) - should vote YES
            - Test with raised threshold (0.75) - should vote NO
        """
        config = get_preset_config(PRESET_STANDARD)

        # Test 1: Default threshold (0.60) - Hash should vote YES
        config['hash']['threshold'] = 0.60
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['hash'] > 0.0, \
            f"Hash should vote YES (0.65 > 0.60), but voted: {result['votes']['hash']}"
        assert result['votes']['hash'] == config['hash']['weight'], \
            f"Hash vote should equal its weight ({config['hash']['weight']}), got {result['votes']['hash']}"

        # Test 2: Raised threshold (0.75) - Hash should vote NO
        config['hash']['threshold'] = 0.75
        voting = VotingSystem(config)
        result = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        assert result['votes']['hash'] == 0.0, \
            f"Hash should vote NO (0.65 < 0.75), but voted: {result['votes']['hash']}"

    def test_voting_totals_change_with_thresholds(self):
        """
        Test that changing thresholds changes the total votes cast.

        This is the critical integration test that validates Task 11 fix:
        sidebar threshold changes must actually affect the voting outcome.
        """
        config = get_preset_config(PRESET_STANDARD)

        # Scenario 1: All detectors vote YES (all thresholds below scores)
        config['token']['threshold'] = 0.70
        config['ast']['threshold'] = 0.80
        config['hash']['threshold'] = 0.60
        voting = VotingSystem(config)
        result1 = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        # Scenario 2: Only AST and Hash vote YES (Token threshold raised)
        config['token']['threshold'] = 0.90
        config['ast']['threshold'] = 0.80
        config['hash']['threshold'] = 0.60
        voting = VotingSystem(config)
        result2 = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        # Scenario 3: Only Hash votes YES (Token and AST thresholds raised)
        config['token']['threshold'] = 0.90
        config['ast']['threshold'] = 0.95
        config['hash']['threshold'] = 0.60
        voting = VotingSystem(config)
        result3 = voting.vote(token_sim=0.72, ast_sim=0.87, hash_sim=0.65)

        # Calculate expected votes based on standard preset weights
        # Standard: Token=1.0, AST=2.0, Hash=1.5
        expected_votes_1 = 1.0 + 2.0 + 1.5  # All vote YES = 4.5
        expected_votes_2 = 0.0 + 2.0 + 1.5  # AST + Hash = 3.5
        expected_votes_3 = 0.0 + 0.0 + 1.5  # Hash only = 1.5

        assert abs(result1['total_votes_cast'] - expected_votes_1) < 0.01, \
            f"Scenario 1: Expected {expected_votes_1} votes, got {result1['total_votes_cast']}"

        assert abs(result2['total_votes_cast'] - expected_votes_2) < 0.01, \
            f"Scenario 2: Expected {expected_votes_2} votes, got {result2['total_votes_cast']}"

        assert abs(result3['total_votes_cast'] - expected_votes_3) < 0.01, \
            f"Scenario 3: Expected {expected_votes_3} votes, got {result3['total_votes_cast']}"

    def test_plagiarism_decision_changes_with_thresholds(self):
        """
        Test that threshold changes can flip the plagiarism decision.

        This validates the end-to-end impact of threshold changes on
        the final plagiarism verdict.
        """
        config = get_preset_config(PRESET_STANDARD)

        # Use moderate similarity scores
        token_sim, ast_sim, hash_sim = 0.72, 0.82, 0.58

        # Scenario 1: Lenient thresholds - should detect plagiarism
        config['token']['threshold'] = 0.70
        config['ast']['threshold'] = 0.80
        config['hash']['threshold'] = 0.55
        voting = VotingSystem(config)
        result1 = voting.vote(token_sim, ast_sim, hash_sim)

        # Scenario 2: Strict thresholds - should NOT detect plagiarism
        config['token']['threshold'] = 0.75
        config['ast']['threshold'] = 0.85
        config['hash']['threshold'] = 0.65
        voting = VotingSystem(config)
        result2 = voting.vote(token_sim, ast_sim, hash_sim)

        # Lenient thresholds: Token YES (1.0) + AST YES (2.0) + Hash YES (1.5) = 4.5
        # Decision threshold = 50% of 4.5 = 2.25, so 4.5 >= 2.25 => PLAGIARISM
        assert result1['is_plagiarized'] == True, \
            f"Lenient thresholds should detect plagiarism (votes: {result1['total_votes_cast']:.2f})"

        # Strict thresholds: All vote NO = 0.0
        # 0.0 < 2.25 => NO PLAGIARISM
        assert result2['is_plagiarized'] == False, \
            f"Strict thresholds should NOT detect plagiarism (votes: {result2['total_votes_cast']:.2f})"

    def test_threshold_precision_boundary_cases(self):
        """
        Test threshold behavior at exact boundary values.

        Edge cases:
            - Score exactly equal to threshold
            - Score 0.001 above threshold
            - Score 0.001 below threshold
        """
        config = get_preset_config(PRESET_STANDARD)
        config['token']['threshold'] = 0.75
        config['ast']['threshold'] = 0.80
        config['hash']['threshold'] = 0.60

        voting = VotingSystem(config)

        # Test exact equality (score = threshold)
        # By convention, >= threshold means vote YES
        result = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=0.60)
        assert result['votes']['token'] > 0.0, "Score equal to threshold should vote YES"
        assert result['votes']['ast'] > 0.0, "Score equal to threshold should vote YES"
        assert result['votes']['hash'] > 0.0, "Score equal to threshold should vote YES"

        # Test just above threshold
        result = voting.vote(token_sim=0.751, ast_sim=0.801, hash_sim=0.601)
        assert result['votes']['token'] > 0.0, "Score above threshold should vote YES"
        assert result['votes']['ast'] > 0.0, "Score above threshold should vote YES"
        assert result['votes']['hash'] > 0.0, "Score above threshold should vote YES"

        # Test just below threshold
        result = voting.vote(token_sim=0.749, ast_sim=0.799, hash_sim=0.599)
        assert result['votes']['token'] == 0.0, "Score below threshold should vote NO"
        assert result['votes']['ast'] == 0.0, "Score below threshold should vote NO"
        assert result['votes']['hash'] == 0.0, "Score below threshold should vote NO"

    def test_threshold_changes_persist_across_multiple_votes(self):
        """
        Test that threshold configuration persists correctly across multiple
        vote() calls on the same VotingSystem instance.

        This ensures configuration isn't reset between votes.
        """
        config = get_preset_config(PRESET_STANDARD)
        config['token']['threshold'] = 0.85
        config['ast']['threshold'] = 0.90
        config['hash']['threshold'] = 0.70

        voting = VotingSystem(config)

        # Call vote() multiple times with different scores
        for i in range(5):
            token_sim = 0.70 + (i * 0.05)  # 0.70, 0.75, 0.80, 0.85, 0.90
            ast_sim = 0.85 + (i * 0.02)     # 0.85, 0.87, 0.89, 0.91, 0.93
            hash_sim = 0.60 + (i * 0.03)    # 0.60, 0.63, 0.66, 0.69, 0.72

            result = voting.vote(token_sim, ast_sim, hash_sim)

            # Verify thresholds are still applied correctly
            if token_sim >= 0.85:
                assert result['votes']['token'] > 0.0, \
                    f"Iteration {i}: Token threshold not applied correctly"
            else:
                assert result['votes']['token'] == 0.0, \
                    f"Iteration {i}: Token threshold not applied correctly"

            if ast_sim >= 0.90:
                assert result['votes']['ast'] > 0.0, \
                    f"Iteration {i}: AST threshold not applied correctly"
            else:
                assert result['votes']['ast'] == 0.0, \
                    f"Iteration {i}: AST threshold not applied correctly"

            if hash_sim >= 0.70:
                assert result['votes']['hash'] > 0.0, \
                    f"Iteration {i}: Hash threshold not applied correctly"
            else:
                assert result['votes']['hash'] == 0.0, \
                    f"Iteration {i}: Hash threshold not applied correctly"


class TestThresholdApplicationSimpleMode:
    """Test threshold application in Simple mode (hash disabled)."""

    def test_hash_threshold_ignored_when_disabled(self):
        """
        Test that hash threshold has no effect when hash detector is disabled.

        In Simple mode, hash weight is 0.0, so changing hash threshold
        should not affect voting outcome.
        """
        config = get_preset_config(PRESET_SIMPLE)

        # Verify hash is disabled in simple mode
        assert config['hash']['weight'] == 0.0, \
            "Hash should be disabled in Simple mode"

        # Test with very low hash threshold
        config['hash']['threshold'] = 0.10
        voting = VotingSystem(config)
        result1 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.95)

        # Test with very high hash threshold
        config['hash']['threshold'] = 0.99
        voting = VotingSystem(config)
        result2 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.95)

        # Results should be identical (hash threshold changes don't matter)
        assert result1['votes']['hash'] == 0.0, "Hash should not vote when disabled"
        assert result2['votes']['hash'] == 0.0, "Hash should not vote when disabled"
        assert result1['total_votes_cast'] == result2['total_votes_cast'], \
            "Hash threshold changes should not affect total votes when disabled"
        assert result1['is_plagiarized'] == result2['is_plagiarized'], \
            "Hash threshold changes should not affect plagiarism decision when disabled"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
