"""
Integration Test 3: Simple Mode UI Configuration

Purpose:
    Verify hash detector configuration changes correctly when switching modes.

Bug Fixed:
    Task 13 - Hide hash controls in Simple mode (hash sliders shown when disabled)

Test Coverage:
    - Hash detector disabled in Simple mode
    - Hash detector enabled in Standard mode
    - Configuration state preserved across mode switches
    - Hash weight and threshold handled correctly

Note:
    This test focuses on backend configuration state, not UI rendering.
    UI rendering is handled by Streamlit and tested manually.

Author: CodeGuard Team
Date: 2025-12-03
"""

import pytest
from src.core.config_presets import (
    get_preset_config,
    apply_preset_to_voting_system,
    PRESET_STANDARD,
    PRESET_SIMPLE
)
from src.voting.voting_system import VotingSystem


class TestSimpleModeConfiguration:
    """Test suite for Simple mode hash detector configuration."""

    def test_hash_disabled_in_simple_mode(self):
        """
        Test that hash detector is disabled in Simple mode.

        Simple mode should set hash weight to 0.0, effectively disabling
        the hash detector from voting.
        """
        config = get_preset_config(PRESET_SIMPLE)
        voting = VotingSystem(config)

        # Verify hash weight is 0.0 (disabled)
        assert voting.config['hash']['weight'] == 0.0, \
            "Hash detector should be disabled in Simple mode (weight=0.0)"

        # Verify hash detector does not contribute to total votes
        assert voting.total_possible_votes == 4.0, \
            f"Simple mode total votes should be 4.0 (no hash), got {voting.total_possible_votes}"

        # Run a vote and verify hash doesn't contribute
        result = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.95)
        assert result['votes']['hash'] == 0.0, \
            "Hash should not vote when disabled in Simple mode"

    def test_hash_enabled_in_standard_mode(self):
        """
        Test that hash detector is enabled in Standard mode.

        Standard mode should set hash weight to 1.5.
        """
        config = get_preset_config(PRESET_STANDARD)
        voting = VotingSystem(config)

        # Verify hash weight is 1.5 (enabled)
        assert voting.config['hash']['weight'] == 1.5, \
            "Hash detector should be enabled in Standard mode (weight=1.5)"

        # Verify hash detector contributes to total votes
        assert voting.total_possible_votes == 4.5, \
            f"Standard mode total votes should be 4.5 (includes hash), got {voting.total_possible_votes}"

        # Run a vote and verify hash contributes
        result = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.95)
        assert result['votes']['hash'] > 0.0, \
            "Hash should vote when enabled in Standard mode"

    def test_hash_threshold_preserved_when_switching_modes(self):
        """
        Test that hash threshold value is preserved when switching between modes.

        Even though hash is disabled in Simple mode, its threshold value
        should be preserved for when switching back to Standard mode.
        """
        # Start with Standard mode
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        standard_hash_threshold = voting.config['hash']['threshold']

        # Switch to Simple mode
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)
        simple_hash_threshold = voting.config['hash']['threshold']

        # Hash threshold should be preserved (both modes use 0.60)
        assert simple_hash_threshold == standard_hash_threshold, \
            "Hash threshold should be preserved when switching to Simple mode"

        # Modify hash threshold in Simple mode
        custom_config = voting.config.copy()
        custom_config['hash']['threshold'] = 0.75
        voting.update_config(custom_config)

        # Switch back to Standard mode
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        # Hash threshold should be reset to Standard default
        assert voting.config['hash']['threshold'] == standard_hash_threshold, \
            "Hash threshold should reset to Standard default when switching back"

    def test_hash_weight_changes_when_switching_modes(self):
        """
        Test that hash weight correctly changes when switching between modes.

        Standard: hash weight = 1.5
        Simple: hash weight = 0.0
        """
        # Start with Standard mode
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        assert voting.config['hash']['weight'] == 1.5, \
            "Standard mode should have hash weight 1.5"

        # Switch to Simple mode
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)
        assert voting.config['hash']['weight'] == 0.0, \
            "Simple mode should have hash weight 0.0"

        # Switch back to Standard mode
        apply_preset_to_voting_system(voting, PRESET_STANDARD)
        assert voting.config['hash']['weight'] == 1.5, \
            "Standard mode should restore hash weight 1.5"

    def test_hash_confidence_weight_in_simple_mode(self):
        """
        Test that hash confidence weight is 0.0 in Simple mode.

        This ensures hash doesn't contribute to confidence calculation
        when disabled.
        """
        config = get_preset_config(PRESET_SIMPLE)
        voting = VotingSystem(config)

        # Verify hash confidence weight is 0.0
        assert voting.config['hash']['confidence_weight'] == 0.0, \
            "Hash confidence weight should be 0.0 in Simple mode"

        # Verify token and ast confidence weights sum to 1.0
        token_conf = voting.config['token']['confidence_weight']
        ast_conf = voting.config['ast']['confidence_weight']
        total_conf = token_conf + ast_conf

        assert abs(total_conf - 1.0) < 0.01, \
            f"Token + AST confidence weights should sum to 1.0 in Simple mode, got {total_conf}"

    def test_mode_switch_updates_total_votes(self):
        """
        Test that switching modes correctly updates total_possible_votes.

        Standard: 4.5 votes (1.0 + 2.0 + 1.5)
        Simple: 4.0 votes (2.0 + 2.0 + 0.0)
        """
        # Start with Standard
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        assert voting.total_possible_votes == 4.5, \
            "Standard mode should have 4.5 total votes"

        # Switch to Simple
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)
        assert voting.total_possible_votes == 4.0, \
            "Simple mode should have 4.0 total votes"

        # Switch back to Standard
        apply_preset_to_voting_system(voting, PRESET_STANDARD)
        assert voting.total_possible_votes == 4.5, \
            "Standard mode should restore 4.5 total votes"

    def test_mode_switch_updates_decision_threshold(self):
        """
        Test that switching modes correctly updates decision_threshold.

        Standard: 2.25 votes needed (50% of 4.5)
        Simple: 3.0 votes needed (75% of 4.0)
        """
        # Start with Standard
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        expected_standard = 4.5 * 0.50  # 2.25

        assert abs(voting.decision_threshold - expected_standard) < 0.01, \
            f"Standard mode should have {expected_standard} decision threshold, got {voting.decision_threshold}"

        # Switch to Simple
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)
        expected_simple = 4.0 * 0.75  # 3.0

        assert abs(voting.decision_threshold - expected_simple) < 0.01, \
            f"Simple mode should have {expected_simple} decision threshold, got {voting.decision_threshold}"

        # Switch back to Standard
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        assert abs(voting.decision_threshold - expected_standard) < 0.01, \
            f"Standard mode should restore {expected_standard} decision threshold, got {voting.decision_threshold}"

    def test_hash_never_votes_in_simple_mode_regardless_of_score(self):
        """
        Test that hash never votes in Simple mode, even with perfect score.

        This validates the UI bug fix: even if hash threshold slider is
        somehow visible/modified in Simple mode, hash should never vote.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test with perfect hash score
        result1 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=1.0)
        assert result1['votes']['hash'] == 0.0, \
            "Hash should not vote even with perfect score in Simple mode"

        # Test with zero hash score
        result2 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.0)
        assert result2['votes']['hash'] == 0.0, \
            "Hash should not vote even with zero score in Simple mode"

        # Both results should have identical hash votes
        assert result1['votes']['hash'] == result2['votes']['hash'], \
            "Hash votes should be identical regardless of score in Simple mode"

    def test_hash_threshold_changes_ignored_in_simple_mode(self):
        """
        Test that changing hash threshold in Simple mode has no effect.

        This is the core of the UI bug fix: hash controls should not
        affect voting when hash is disabled.
        """
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Test with low hash threshold
        voting.config['hash']['threshold'] = 0.10
        result1 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.50)

        # Test with high hash threshold
        voting.config['hash']['threshold'] = 0.99
        result2 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.50)

        # Results should be identical (hash threshold doesn't matter)
        assert result1['votes']['hash'] == result2['votes']['hash'] == 0.0, \
            "Hash threshold changes should not affect voting in Simple mode"
        assert result1['total_votes_cast'] == result2['total_votes_cast'], \
            "Total votes should be identical regardless of hash threshold in Simple mode"
        assert result1['is_plagiarized'] == result2['is_plagiarized'], \
            "Plagiarism decision should be identical regardless of hash threshold in Simple mode"


class TestModeTransitionEdgeCases:
    """Test edge cases when transitioning between modes."""

    def test_rapid_mode_switching(self):
        """
        Test that rapid mode switching maintains correct configuration.

        Switch between modes multiple times and verify configuration
        remains correct.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Switch modes 10 times
        for i in range(10):
            if i % 2 == 0:
                apply_preset_to_voting_system(voting, PRESET_SIMPLE)
                assert voting.config['hash']['weight'] == 0.0, \
                    f"Iteration {i}: Hash should be disabled in Simple mode"
                assert voting.total_possible_votes == 4.0, \
                    f"Iteration {i}: Total votes should be 4.0 in Simple mode"
            else:
                apply_preset_to_voting_system(voting, PRESET_STANDARD)
                assert voting.config['hash']['weight'] == 1.5, \
                    f"Iteration {i}: Hash should be enabled in Standard mode"
                assert voting.total_possible_votes == 4.5, \
                    f"Iteration {i}: Total votes should be 4.5 in Standard mode"

    def test_mode_switch_with_custom_config(self):
        """
        Test switching modes after customizing configuration.

        Custom values should be overwritten by preset defaults.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Customize all values
        custom_config = voting.config.copy()
        custom_config['token']['threshold'] = 0.99
        custom_config['ast']['threshold'] = 0.99
        custom_config['hash']['threshold'] = 0.99
        custom_config['hash']['weight'] = 5.0
        voting.update_config(custom_config)

        # Switch to Simple mode
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)

        # Verify Simple preset defaults applied (not custom values)
        simple_config = get_preset_config(PRESET_SIMPLE)
        assert voting.config['token']['threshold'] == simple_config['token']['threshold'], \
            "Token threshold should be Simple preset default, not custom value"
        assert voting.config['ast']['threshold'] == simple_config['ast']['threshold'], \
            "AST threshold should be Simple preset default, not custom value"
        assert voting.config['hash']['weight'] == 0.0, \
            "Hash weight should be 0.0 in Simple mode, not custom value"

    def test_hash_detector_results_persist_across_mode_switch(self):
        """
        Test that hash similarity scores are preserved when switching modes.

        Even though hash doesn't vote in Simple mode, the raw similarity
        score should still be available in results.
        """
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))

        token_sim, ast_sim, hash_sim = 0.75, 0.90, 0.65

        # Run in Standard mode
        result_standard = voting_standard.vote(token_sim, ast_sim, hash_sim)

        # Run in Simple mode
        result_simple = voting_simple.vote(token_sim, ast_sim, hash_sim)

        # Raw scores should be identical in both modes
        assert result_standard['individual_scores']['hash'] == hash_sim, \
            "Standard mode should preserve hash score"
        assert result_simple['individual_scores']['hash'] == hash_sim, \
            "Simple mode should preserve hash score"

        # But hash votes should differ
        assert result_standard['votes']['hash'] > 0.0, \
            "Hash should vote in Standard mode"
        assert result_simple['votes']['hash'] == 0.0, \
            "Hash should not vote in Simple mode"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
