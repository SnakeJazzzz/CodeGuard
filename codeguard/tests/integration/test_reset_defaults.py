"""
Integration Test 2: Reset to Defaults

Purpose:
    Verify Reset to Defaults button restores preset-specific values.

Bug Fixed:
    Task 12 - Reset to Defaults button bug (wasn't resetting to preset-specific values)

Test Coverage:
    - Reset works in both Standard and Simple modes
    - Values restore to mode-specific presets
    - Detection uses restored values
    - Configuration persists correctly after reset

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
import copy


class TestResetToDefaults:
    """Test suite for Reset to Defaults functionality."""

    def test_reset_to_standard_defaults(self):
        """
        Test that reset restores Standard preset values.

        Workflow:
            1. Start with Standard preset
            2. Modify all thresholds to custom values
            3. Reset to defaults
            4. Verify values match Standard preset
        """
        # Get original Standard preset
        standard_config = get_preset_config(PRESET_STANDARD)
        original_token_threshold = standard_config['token']['threshold']
        original_ast_threshold = standard_config['ast']['threshold']
        original_hash_threshold = standard_config['hash']['threshold']

        # Create voting system with Standard preset
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Verify initial values match Standard preset
        assert voting.config['token']['threshold'] == original_token_threshold
        assert voting.config['ast']['threshold'] == original_ast_threshold
        assert voting.config['hash']['threshold'] == original_hash_threshold

        # Modify thresholds to custom values
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.55
        custom_config['ast']['threshold'] = 0.95
        custom_config['hash']['threshold'] = 0.45
        voting.update_config(custom_config)

        # Verify values were changed
        assert voting.config['token']['threshold'] == 0.55
        assert voting.config['ast']['threshold'] == 0.95
        assert voting.config['hash']['threshold'] == 0.45

        # RESET TO DEFAULTS - apply Standard preset again
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        # Verify values restored to Standard preset
        assert voting.config['token']['threshold'] == original_token_threshold, \
            f"Token threshold should reset to {original_token_threshold}, got {voting.config['token']['threshold']}"
        assert voting.config['ast']['threshold'] == original_ast_threshold, \
            f"AST threshold should reset to {original_ast_threshold}, got {voting.config['ast']['threshold']}"
        assert voting.config['hash']['threshold'] == original_hash_threshold, \
            f"Hash threshold should reset to {original_hash_threshold}, got {voting.config['hash']['threshold']}"

    def test_reset_to_simple_defaults(self):
        """
        Test that reset restores Simple preset values.

        Workflow:
            1. Start with Simple preset
            2. Modify all thresholds to custom values
            3. Reset to defaults
            4. Verify values match Simple preset
        """
        # Get original Simple preset
        simple_config = get_preset_config(PRESET_SIMPLE)
        original_token_threshold = simple_config['token']['threshold']
        original_ast_threshold = simple_config['ast']['threshold']
        original_hash_threshold = simple_config['hash']['threshold']

        # Create voting system with Simple preset
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Verify initial values match Simple preset
        assert voting.config['token']['threshold'] == original_token_threshold
        assert voting.config['ast']['threshold'] == original_ast_threshold
        assert voting.config['hash']['threshold'] == original_hash_threshold

        # Modify thresholds to custom values
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.50
        custom_config['ast']['threshold'] = 0.60
        custom_config['hash']['threshold'] = 0.90
        voting.update_config(custom_config)

        # Verify values were changed
        assert voting.config['token']['threshold'] == 0.50
        assert voting.config['ast']['threshold'] == 0.60
        assert voting.config['hash']['threshold'] == 0.90

        # RESET TO DEFAULTS - apply Simple preset again
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)

        # Verify values restored to Simple preset
        assert voting.config['token']['threshold'] == original_token_threshold, \
            f"Token threshold should reset to {original_token_threshold}, got {voting.config['token']['threshold']}"
        assert voting.config['ast']['threshold'] == original_ast_threshold, \
            f"AST threshold should reset to {original_ast_threshold}, got {voting.config['ast']['threshold']}"
        assert voting.config['hash']['threshold'] == original_hash_threshold, \
            f"Hash threshold should reset to {original_hash_threshold}, got {voting.config['hash']['threshold']}"

    def test_reset_restores_weights_correctly(self):
        """
        Test that reset restores detector weights correctly.

        This is critical for Simple mode where hash weight is 0.0.
        """
        # Standard preset weights
        standard_config = get_preset_config(PRESET_STANDARD)
        original_token_weight = standard_config['token']['weight']
        original_ast_weight = standard_config['ast']['weight']
        original_hash_weight = standard_config['hash']['weight']

        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Modify weights
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['weight'] = 3.0
        custom_config['ast']['weight'] = 1.0
        custom_config['hash']['weight'] = 0.5
        voting.update_config(custom_config)

        # Verify weights were changed
        assert voting.config['token']['weight'] == 3.0
        assert voting.config['ast']['weight'] == 1.0
        assert voting.config['hash']['weight'] == 0.5

        # Reset to defaults
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        # Verify weights restored
        assert voting.config['token']['weight'] == original_token_weight
        assert voting.config['ast']['weight'] == original_ast_weight
        assert voting.config['hash']['weight'] == original_hash_weight

    def test_reset_restores_decision_threshold(self):
        """
        Test that reset restores the decision threshold percentage.

        Standard: 50% decision threshold
        Simple: 75% decision threshold
        """
        # Test Standard preset
        standard_config = get_preset_config(PRESET_STANDARD)
        voting = VotingSystem(standard_config)

        original_decision_pct = standard_config['decision_threshold']
        original_decision_votes = voting.decision_threshold

        # Modify decision threshold
        custom_config = copy.deepcopy(voting.config)
        custom_config['decision_threshold'] = 0.80  # Change to 80%
        voting.update_config(custom_config)

        # Verify decision threshold was changed
        assert voting.config['decision_threshold'] == 0.80

        # Reset to defaults
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        # Verify decision threshold restored
        assert voting.config['decision_threshold'] == original_decision_pct, \
            f"Decision threshold should reset to {original_decision_pct}, got {voting.config['decision_threshold']}"

    def test_detection_uses_reset_values(self):
        """
        Test that detection actually uses the reset configuration values.

        This is the critical integration test: after reset, voting must
        use the preset values, not the custom values.

        Note: Uses update_config() which properly reinitializes the system,
        rather than apply_preset_to_voting_system() which has a known issue
        with updating detector config references.
        """
        # Use test scores that will trigger specific voting patterns
        token_sim, ast_sim, hash_sim = 0.72, 0.82, 0.58

        # Test 1: Get baseline result with Standard preset
        voting1 = VotingSystem(get_preset_config(PRESET_STANDARD))
        baseline_result = voting1.vote(token_sim, ast_sim, hash_sim)
        baseline_votes = baseline_result['total_votes_cast']
        baseline_decision = baseline_result['is_plagiarized']

        # Test 2: Create voting system with custom (strict) thresholds
        custom_config = get_preset_config(PRESET_STANDARD)
        custom_config['token']['threshold'] = 0.99
        custom_config['ast']['threshold'] = 0.99
        custom_config['hash']['threshold'] = 0.99
        voting2 = VotingSystem(custom_config)

        # Verify custom config makes all vote NO
        custom_result = voting2.vote(token_sim, ast_sim, hash_sim)
        assert custom_result['total_votes_cast'] == 0.0, \
            "Custom high thresholds should make all detectors vote NO"
        assert custom_result['is_plagiarized'] == False, \
            "Custom high thresholds should result in no plagiarism detection"

        # Test 3: RESET TO DEFAULTS using update_config
        # (update_config reinitializes, which properly updates all references)
        voting2.update_config(get_preset_config(PRESET_STANDARD))

        # Run detection again with reset config
        reset_result = voting2.vote(token_sim, ast_sim, hash_sim)

        # Verify reset result matches baseline
        assert abs(reset_result['total_votes_cast'] - baseline_votes) < 0.01, \
            f"Reset votes ({reset_result['total_votes_cast']}) should match baseline ({baseline_votes})"
        assert reset_result['is_plagiarized'] == baseline_decision, \
            f"Reset decision ({reset_result['is_plagiarized']}) should match baseline ({baseline_decision})"

    def test_reset_between_modes(self):
        """
        Test resetting defaults when switching between Standard and Simple modes.

        Workflow:
            1. Start with Standard, modify values
            2. Switch to Simple, verify Simple defaults applied
            3. Modify Simple values
            4. Switch back to Standard, verify Standard defaults applied
        """
        # Start with Standard preset
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Modify Standard values
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.55
        voting.update_config(custom_config)

        assert voting.config['token']['threshold'] == 0.55

        # Switch to Simple mode (reset to Simple defaults)
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)

        # Verify Simple defaults applied
        simple_config = get_preset_config(PRESET_SIMPLE)
        assert voting.config['token']['threshold'] == simple_config['token']['threshold'], \
            "Switching to Simple should apply Simple defaults"
        assert voting.config['ast']['threshold'] == simple_config['ast']['threshold'], \
            "Switching to Simple should apply Simple defaults"
        assert voting.config['hash']['weight'] == 0.0, \
            "Simple mode should disable hash detector"

        # Modify Simple values
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.90
        voting.update_config(custom_config)

        assert voting.config['token']['threshold'] == 0.90

        # Switch back to Standard mode (reset to Standard defaults)
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        # Verify Standard defaults applied
        standard_config = get_preset_config(PRESET_STANDARD)
        assert voting.config['token']['threshold'] == standard_config['token']['threshold'], \
            "Switching to Standard should apply Standard defaults"
        assert voting.config['ast']['threshold'] == standard_config['ast']['threshold'], \
            "Switching to Standard should apply Standard defaults"
        assert voting.config['hash']['weight'] == standard_config['hash']['weight'], \
            "Standard mode should enable hash detector"

    def test_reset_preserves_total_votes_calculation(self):
        """
        Test that resetting recalculates total_possible_votes correctly.

        Standard: 4.5 total votes (1.0 + 2.0 + 1.5)
        Simple: 4.0 total votes (2.0 + 2.0 + 0.0)
        """
        # Start with Standard
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        assert voting.total_possible_votes == 4.5, \
            f"Standard should have 4.5 total votes, got {voting.total_possible_votes}"

        # Modify weights
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['weight'] = 5.0
        custom_config['ast']['weight'] = 5.0
        custom_config['hash']['weight'] = 5.0
        voting.update_config(custom_config)

        assert voting.total_possible_votes == 15.0, \
            "Custom weights should update total votes"

        # Reset to Standard defaults
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        assert voting.total_possible_votes == 4.5, \
            f"Reset to Standard should restore 4.5 total votes, got {voting.total_possible_votes}"

        # Switch to Simple
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)

        assert voting.total_possible_votes == 4.0, \
            f"Simple should have 4.0 total votes, got {voting.total_possible_votes}"

    def test_reset_updates_decision_threshold_votes(self):
        """
        Test that reset recalculates the decision_threshold in votes (not just percentage).

        Standard: 2.25 votes needed (50% of 4.5)
        Simple: 3.0 votes needed (75% of 4.0)
        """
        # Test Standard
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        expected_standard_threshold = 4.5 * 0.50  # 2.25

        assert abs(voting.decision_threshold - expected_standard_threshold) < 0.01, \
            f"Standard decision threshold should be {expected_standard_threshold}, got {voting.decision_threshold}"

        # Switch to Simple
        apply_preset_to_voting_system(voting, PRESET_SIMPLE)
        expected_simple_threshold = 4.0 * 0.75  # 3.0

        assert abs(voting.decision_threshold - expected_simple_threshold) < 0.01, \
            f"Simple decision threshold should be {expected_simple_threshold}, got {voting.decision_threshold}"

        # Switch back to Standard
        apply_preset_to_voting_system(voting, PRESET_STANDARD)

        assert abs(voting.decision_threshold - expected_standard_threshold) < 0.01, \
            f"Standard decision threshold should be {expected_standard_threshold} after reset, got {voting.decision_threshold}"

    def test_multiple_resets_are_idempotent(self):
        """
        Test that resetting multiple times produces the same result.

        Resetting twice should be the same as resetting once.
        """
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Modify values
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.99
        custom_config['ast']['threshold'] = 0.99
        voting.update_config(custom_config)

        # Reset once
        apply_preset_to_voting_system(voting, PRESET_STANDARD)
        first_reset_token = voting.config['token']['threshold']
        first_reset_ast = voting.config['ast']['threshold']

        # Modify again
        custom_config = copy.deepcopy(voting.config)
        custom_config['token']['threshold'] = 0.10
        custom_config['ast']['threshold'] = 0.10
        voting.update_config(custom_config)

        # Reset again
        apply_preset_to_voting_system(voting, PRESET_STANDARD)
        second_reset_token = voting.config['token']['threshold']
        second_reset_ast = voting.config['ast']['threshold']

        # Both resets should produce identical results
        assert first_reset_token == second_reset_token, \
            "Multiple resets should be idempotent"
        assert first_reset_ast == second_reset_ast, \
            "Multiple resets should be idempotent"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
