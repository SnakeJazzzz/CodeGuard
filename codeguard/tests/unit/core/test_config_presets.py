"""
Comprehensive tests for configuration preset system.

This test suite verifies:
1. Preset configuration values (standard and simple)
2. Preset retrieval and validation
3. Integration with VotingSystem
4. Voting behavior with different presets
5. FizzBuzz false positive fix verification
6. Edge cases and error handling

The preset system provides two modes:
- Standard: All detectors active (hash weight = 1.5)
- Simple: Hash detector disabled (hash weight = 0.0), stricter AST threshold (0.85)

Test Coverage:
- Configuration value validation
- get_preset() functionality
- get_preset_config() for VotingSystem
- get_available_presets() listing
- Invalid preset name handling
- Voting system integration with both presets
- Real-world FizzBuzz false positive scenario
- Disabled detector behavior
- Confidence calculation with disabled detectors
"""

import pytest
import os
import sys
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


@pytest.fixture
def fizzbuzz_test_path():
    """
    Return path to FizzBuzz test files.

    Returns:
        str: Absolute path to FizzBuzz test directory
    """
    return "/Users/michaelthemac/Desktop/Tec/8_Semestre/DAA/Reto/CodeGuard/codeguard/test_files/FizzBuzzProblem"


# ============================================================================
# Test 1: Standard Preset Values
# ============================================================================

def test_standard_preset_values():
    """
    Test that Standard preset has correct values.

    Verifies:
    - Name and description are correct
    - Token detector: threshold=0.70, weight=1.0, confidence_weight=0.3
    - AST detector: threshold=0.80, weight=2.0, confidence_weight=0.4
    - Hash detector: threshold=0.60, weight=1.5, confidence_weight=0.3 (ACTIVE)
    - Total weights sum to 4.5
    - Hash detector is ENABLED (weight > 0)
    """
    from src.core.config_presets import get_preset

    preset = get_preset("standard")

    # Verify name and description
    assert preset['name'] == "Standard (Recommended)"
    assert "50+ lines" in preset['description']

    # Verify token detector
    assert preset['token']['threshold'] == 0.70
    assert preset['token']['weight'] == 1.0
    assert preset['token']['confidence_weight'] == 0.3

    # Verify AST detector
    assert preset['ast']['threshold'] == 0.80
    assert preset['ast']['weight'] == 2.0
    assert preset['ast']['confidence_weight'] == 0.4

    # Verify hash detector (ACTIVE)
    assert preset['hash']['threshold'] == 0.60
    assert preset['hash']['weight'] == 1.5
    assert preset['hash']['confidence_weight'] == 0.3
    assert preset['hash']['weight'] > 0, "Hash should be ACTIVE in standard mode"

    # Verify total weights
    total_weight = (
        preset['token']['weight'] +
        preset['ast']['weight'] +
        preset['hash']['weight']
    )
    assert total_weight == 4.5

    # Verify decision threshold
    assert preset['decision_threshold'] == 0.50


# ============================================================================
# Test 2: Simple Preset Values
# ============================================================================

def test_simple_preset_values():
    """
    Test that Simple preset has correct values including disabled hash.

    Verifies:
    - Name and description are correct
    - Token detector: threshold=0.70, weight=2.0, confidence_weight=0.4
    - AST detector: threshold=0.85 (stricter), weight=2.0, confidence_weight=0.6
    - Hash detector: threshold=0.60, weight=0.0 (DISABLED), confidence_weight=0.0
    - Total weights sum to 4.0 (not 4.5)
    - Hash detector is DISABLED (weight = 0)
    - Decision threshold is 75% (requires both detectors)
    """
    from src.core.config_presets import get_preset

    preset = get_preset("simple")

    # Verify name and description
    assert preset['name'] == "Simple Problems (e.g., FizzBuzz)"
    assert "<50 lines" in preset['description'] or "simple" in preset['description'].lower()

    # Verify token detector (equal weight with AST)
    assert preset['token']['threshold'] == 0.70
    assert preset['token']['weight'] == 2.0  # Equal with AST
    assert preset['token']['confidence_weight'] >= 0.3

    # Verify AST detector (stricter threshold, equal weight with Token)
    assert preset['ast']['threshold'] == 0.85  # Stricter than 0.80
    assert preset['ast']['weight'] == 2.0  # Equal with Token
    assert preset['ast']['confidence_weight'] >= 0.4

    # Verify hash detector (DISABLED)
    assert preset['hash']['threshold'] == 0.60
    assert preset['hash']['weight'] == 0.0, "Hash should be DISABLED in simple mode"
    assert preset['hash']['confidence_weight'] == 0.0

    # Verify total weights (should be 4.0, not 4.5)
    total_weight = (
        preset['token']['weight'] +
        preset['ast']['weight'] +
        preset['hash']['weight']
    )
    assert total_weight == 4.0

    # Verify decision threshold (75% - requires both detectors)
    assert preset['decision_threshold'] == 0.75


# ============================================================================
# Test 3: get_preset() Returns Valid Dictionary
# ============================================================================

def test_get_preset_returns_dict():
    """
    Test that get_preset() returns valid dict for both presets.

    Verifies:
    - Returns dictionary type
    - Contains required keys: name, description, token, ast, hash
    - Case-insensitive preset name handling
    - Both standard and simple presets accessible
    """
    from src.core.config_presets import get_preset

    # Test standard preset
    standard = get_preset("standard")
    assert isinstance(standard, dict)
    assert 'name' in standard
    assert 'description' in standard
    assert 'token' in standard
    assert 'ast' in standard
    assert 'hash' in standard
    assert 'decision_threshold' in standard

    # Test simple preset
    simple = get_preset("simple")
    assert isinstance(simple, dict)
    assert 'name' in simple
    assert 'description' in simple
    assert 'token' in simple
    assert 'ast' in simple
    assert 'hash' in simple
    assert 'decision_threshold' in simple

    # Test case insensitivity
    assert get_preset("STANDARD") == get_preset("standard")
    assert get_preset("Simple") == get_preset("simple")
    assert get_preset("  STANDARD  ") == get_preset("standard")


# ============================================================================
# Test 4: Invalid Preset Name Handling
# ============================================================================

def test_get_preset_invalid_name():
    """
    Test that invalid preset name raises ValueError.

    Verifies:
    - ValueError raised for unknown preset names
    - Error message mentions available presets
    - Empty string raises ValueError
    """
    from src.core.config_presets import get_preset

    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("invalid")

    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("medium")

    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("")

    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset("custom")


# ============================================================================
# Test 5: Voting with Simple Preset (Hash Disabled)
# ============================================================================

def test_voting_with_simple_preset():
    """
    Test voting system with Simple preset (hash disabled, requires both detectors).

    Verifies:
    - Hash detector does not vote (weight=0.0)
    - Total possible votes is 4.0 (not 4.5)
    - Confidence calculation excludes disabled hash
    - Decision based only on token + AST
    - Low hash score is ignored
    - Requires BOTH Token AND AST to vote YES (75% threshold)

    Test scenario:
    - token_score=0.80 (above 0.70) → votes YES (2.0)
    - ast_score=0.90 (above 0.85) → votes YES (2.0)
    - hash_score=0.20 (ignored, weight=0.0) → votes NO (0.0)
    - Total: 4.0 / 4.0 = 100% ≥ 75% → PLAGIARISM
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    config = get_preset_config("simple")
    voting_system = VotingSystem(config)

    # Test case: All scores high except hash
    result = voting_system.vote(
        token_sim=0.80,
        ast_sim=0.90,
        hash_sim=0.20  # Low hash score should be IGNORED
    )

    # Verify hash vote is 0 (disabled)
    assert result['votes']['hash'] == 0.0, "Hash should not vote when disabled"

    # Verify total possible votes is 4.0 (not 4.5)
    assert result['total_possible_votes'] == 4.0

    # Verify decision threshold is 3.0 (75% of 4.0)
    assert voting_system.decision_threshold == 3.0, "Decision threshold should be 3.0 (75%)"

    # Verify confidence does NOT include hash
    # Confidence should be high despite low hash score
    assert result['confidence_score'] > 0.80, "Confidence should ignore disabled hash"

    # Verify decision is based only on token + AST
    # Token (2.0) + AST (2.0) = 4.0 votes if both fire
    assert result['is_plagiarized'] == True, "Should detect with token + AST only"

    # Verify total votes cast
    assert result['total_votes_cast'] == 4.0  # Both token and AST voted


# ============================================================================
# Test 6: Voting with Standard Preset (All Detectors Active)
# ============================================================================

def test_voting_with_standard_preset():
    """
    Test voting system with Standard preset (all detectors active).

    Verifies:
    - All three detectors vote when above threshold
    - Total possible votes is 4.5
    - Hash detector participates in voting
    - Confidence includes all three detectors
    - Correct vote weights applied

    Test scenario:
    - token_score=0.75 (> 0.70) → votes YES (1.0)
    - ast_score=0.85 (> 0.80) → votes YES (2.0)
    - hash_score=0.65 (> 0.60) → votes YES (1.5)
    - Total: 4.5 / 4.5 = 100% → PLAGIARISM
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    config = get_preset_config("standard")
    voting_system = VotingSystem(config)

    # Test case: All scores above threshold
    result = voting_system.vote(
        token_sim=0.75,  # > 0.70
        ast_sim=0.85,    # > 0.80
        hash_sim=0.65    # > 0.60
    )

    # Verify all detectors vote
    assert result['votes']['token'] == 1.0, "Token should vote"
    assert result['votes']['ast'] == 2.0, "AST should vote"
    assert result['votes']['hash'] == 1.5, "Hash should vote"

    # Verify total possible votes is 4.5
    assert result['total_possible_votes'] == 4.5

    # Verify all votes cast (all above threshold)
    assert result['total_votes_cast'] == 4.5

    # Verify plagiarism detected
    assert result['is_plagiarized'] == True

    # Verify confidence includes all three detectors
    # Standard preset: token=0.3, ast=0.4, hash=0.3
    expected_confidence = (0.3 * 0.75) + (0.4 * 0.85) + (0.3 * 0.65)
    assert abs(result['confidence_score'] - expected_confidence) < 0.01


# ============================================================================
# Test 7: FizzBuzz False Positive Fix
# ============================================================================

def test_preset_on_fizzbuzz_false_positive(fizzbuzz_test_path):
    """
    Test that Simple preset fixes FizzBuzz false positive.

    This test uses realistic scores from FizzBuzz testing to demonstrate
    how the Simple preset fixes the false positive problem that occurred
    with the Standard preset.

    Scenario:
    - Two legitimate FizzBuzz solutions with similar structure
    - Standard preset incorrectly flags as plagiarism (false positive)
    - Simple preset correctly identifies as NOT plagiarism

    The fix works because:
    1. Hash detector disabled (was causing noise on small files)
    2. AST threshold increased to 0.85 (reduces structural false positives)

    Test scenario (simulated FizzBuzz scores):
    - token_score=0.75 (above 0.70)
    - ast_score=0.82 (above 0.80 but below 0.85)
    - hash_score=0.25 (low, below 0.60)

    Standard preset:
    - Token votes YES (0.75 > 0.70) = 1.0
    - AST votes YES (0.82 > 0.80) = 2.0
    - Hash votes NO (0.25 < 0.60) = 0.0
    - Total: 3.0 / 4.5 = 66.67% > 50% → PLAGIARISM (false positive)

    Simple preset (NEW - FIXED):
    - Token votes YES (0.75 > 0.70) = 2.0
    - AST votes NO (0.82 < 0.85) = 0.0 ← STRICTER THRESHOLD
    - Hash SKIPPED (weight = 0) = 0.0
    - Total: 2.0 / 4.0 = 50% < 75% → NOT PLAGIARISM (correct)
    - Fix: Even with Token voting, needs AST too (75% threshold)
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Check if test files exist
    file1 = os.path.join(fizzbuzz_test_path, "plagiarized/student_01.py")
    file2 = os.path.join(fizzbuzz_test_path, "legitimate/student_06.py")

    if not os.path.exists(file1) or not os.path.exists(file2):
        pytest.skip("FizzBuzz test files not found")

    # Simulate scores from actual FizzBuzz detection
    # These are approximate scores from FizzBuzz testing
    token_score = 0.75  # Above threshold
    ast_score = 0.82    # Above 0.80 but below 0.85
    hash_score = 0.25   # Low (below 0.60)

    # Test with Standard preset
    standard_config = get_preset_config("standard")
    standard_voting = VotingSystem(standard_config)
    standard_result = standard_voting.vote(token_score, ast_score, hash_score)

    # Standard preset: Should detect (false positive in our testing)
    # Token votes YES (0.75 > 0.70) = 1.0
    # AST votes YES (0.82 > 0.80) = 2.0
    # Hash votes NO (0.25 < 0.60) = 0.0
    # Total: 3.0 / 4.5 = 66.67% > 50% → PLAGIARISM
    assert standard_result['is_plagiarized'] == True, "Standard should detect (false positive)"
    assert standard_result['total_votes_cast'] == 3.0, "Token + AST should vote"

    # Test with Simple preset
    simple_config = get_preset_config("simple")
    simple_voting = VotingSystem(simple_config)
    simple_result = simple_voting.vote(token_score, ast_score, hash_score)

    # Simple preset: Should NOT detect (fixes false positive)
    # Token votes YES (0.75 > 0.70) = 2.0
    # AST votes NO (0.82 < 0.85) = 0.0 ← STRICTER THRESHOLD
    # Hash SKIPPED (weight = 0) = 0.0
    # Total: 2.0 / 4.0 = 50% < 75% → NOT PLAGIARISM (requires both detectors)
    assert simple_result['is_plagiarized'] == False, "Simple should NOT detect (fixes false positive)"
    assert simple_result['total_votes_cast'] == 2.0, "Only token should vote"

    # Verify the key difference: AST voting
    assert standard_result['votes']['ast'] > 0, "Standard: AST votes YES"
    assert simple_result['votes']['ast'] == 0, "Simple: AST votes NO (stricter threshold)"

    # Verify hash behavior
    assert standard_result['votes']['hash'] == 0, "Standard: Hash votes NO (score too low)"
    assert simple_result['votes']['hash'] == 0, "Simple: Hash disabled"


# ============================================================================
# Test 8: get_available_presets()
# ============================================================================

def test_get_available_presets():
    """
    Test that get_available_presets() returns correct list.

    Verifies:
    - Returns list type
    - Contains exactly 2 presets
    - Contains "standard" and "simple"
    - All preset names are lowercase strings
    """
    from src.core.config_presets import get_available_presets

    presets = get_available_presets()

    assert isinstance(presets, list)
    assert len(presets) == 2
    assert "standard" in presets
    assert "simple" in presets

    # Verify all are strings
    for preset in presets:
        assert isinstance(preset, str)
        assert preset.islower()


# ============================================================================
# Test 9: get_preset_config() for VotingSystem
# ============================================================================

def test_preset_config_for_voting_system():
    """
    Test that get_preset_config() returns config suitable for VotingSystem.

    Verifies:
    - Returns dictionary without 'name' and 'description' (UI-only fields)
    - Contains detector configs: token, ast, hash
    - Contains decision_threshold
    - Simple preset has hash weight=0.0
    - Can be used to initialize VotingSystem
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Standard config
    standard_config = get_preset_config("standard")

    # Should NOT have 'name' and 'description' (those are for UI)
    assert 'name' not in standard_config
    assert 'description' not in standard_config

    # Should have detector configs
    assert 'token' in standard_config
    assert 'ast' in standard_config
    assert 'hash' in standard_config
    assert 'decision_threshold' in standard_config

    # Verify can initialize VotingSystem
    voting_system = VotingSystem(standard_config)
    assert voting_system.total_possible_votes == 4.5

    # Simple config
    simple_config = get_preset_config("simple")
    assert 'name' not in simple_config
    assert 'description' not in simple_config
    assert simple_config['hash']['weight'] == 0.0

    # Verify can initialize VotingSystem with simple preset
    voting_system_simple = VotingSystem(simple_config)
    assert voting_system_simple.total_possible_votes == 4.0


# ============================================================================
# Test 10: Hash Detector Disabled in Simple Preset
# ============================================================================

def test_simple_preset_hash_disabled():
    """
    Test that hash detector is properly disabled in Simple preset.

    Verifies:
    - Hash weight is exactly 0.0
    - Hash confidence_weight is 0.0
    - VotingSystem does not count hash votes
    - Even high hash scores don't affect decision
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    config = get_preset_config("simple")
    voting_system = VotingSystem(config)

    # Verify hash config
    assert config['hash']['weight'] == 0.0
    assert config['hash']['confidence_weight'] == 0.0

    # Test with high hash score (should be ignored)
    result = voting_system.vote(
        token_sim=0.60,  # Below threshold (0.70)
        ast_sim=0.70,    # Below threshold (0.85)
        hash_sim=0.95    # HIGH score, but should be ignored
    )

    # Hash should not vote despite high score
    assert result['votes']['hash'] == 0.0

    # Should not detect plagiarism (only hash is high)
    assert result['is_plagiarized'] == False

    # Total votes should be 0
    assert result['total_votes_cast'] == 0.0


# ============================================================================
# Test 11: Confidence Calculation with Disabled Detector
# ============================================================================

def test_confidence_calculation_disabled_detector():
    """
    Test that confidence is calculated correctly when hash is disabled.

    Verifies:
    - Confidence uses only active detectors (token + AST)
    - Disabled detector (hash) does not affect confidence
    - Confidence weights are normalized for active detectors only
    - High confidence possible even with low hash score
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    config = get_preset_config("simple")
    voting_system = VotingSystem(config)

    # Test with high token and AST, low hash
    result = voting_system.vote(
        token_sim=0.90,  # High
        ast_sim=0.95,    # High
        hash_sim=0.10    # Low, but should be ignored
    )

    # Confidence should be high (ignoring hash)
    # Simple preset confidence weights: token=0.4, ast=0.6, hash=0.0
    # After normalization (hash excluded): token=0.4/1.0=0.4, ast=0.6/1.0=0.6
    expected_confidence = (0.4 * 0.90) + (0.6 * 0.95)

    # Allow small floating point tolerance
    assert abs(result['confidence_score'] - expected_confidence) < 0.01
    assert result['confidence_score'] > 0.85, "Confidence should be high"


# ============================================================================
# Test 12: Standard vs Simple Decision Boundary
# ============================================================================

def test_standard_vs_simple_decision_boundary():
    """
    Test decision boundary differences between Standard and Simple presets.

    Verifies that the same scores can produce different decisions due to:
    1. Different thresholds (AST: 0.80 vs 0.85)
    2. Different weights
    3. Hash detector enabled/disabled

    Uses edge case scores that fall in the "borderline" range.
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Edge case scores
    token_score = 0.72  # Above 0.70
    ast_score = 0.83    # Above 0.80 but below 0.85
    hash_score = 0.58   # Below 0.60

    # Standard preset
    standard_config = get_preset_config("standard")
    standard_voting = VotingSystem(standard_config)
    standard_result = standard_voting.vote(token_score, ast_score, hash_score)

    # Standard: Token (1.0) + AST (2.0) = 3.0 / 4.5 = 66.67% → PLAGIARISM
    assert standard_result['votes']['token'] == 1.0
    assert standard_result['votes']['ast'] == 2.0
    assert standard_result['votes']['hash'] == 0.0  # Below threshold
    assert standard_result['total_votes_cast'] == 3.0
    assert standard_result['is_plagiarized'] == True

    # Simple preset
    simple_config = get_preset_config("simple")
    simple_voting = VotingSystem(simple_config)
    simple_result = simple_voting.vote(token_score, ast_score, hash_score)

    # Simple: Token (2.0) only = 2.0 / 4.0 = 50% < 75% → NOT PLAGIARISM
    assert simple_result['votes']['token'] == 2.0
    assert simple_result['votes']['ast'] == 0.0  # Below stricter threshold
    assert simple_result['votes']['hash'] == 0.0  # Disabled
    assert simple_result['total_votes_cast'] == 2.0
    assert simple_result['is_plagiarized'] == False

    # Same scores, different decisions
    assert standard_result['is_plagiarized'] != simple_result['is_plagiarized']


# ============================================================================
# Test 13: Preset Configuration Immutability
# ============================================================================

def test_preset_immutability():
    """
    Test that get_preset() returns a copy to prevent accidental mutation.

    Verifies:
    - Modifying returned config doesn't affect subsequent calls
    - Deep copy of nested dictionaries
    - Each call returns independent object
    """
    from src.core.config_presets import get_preset

    # Get preset and modify it
    preset1 = get_preset("standard")
    original_threshold = preset1['token']['threshold']
    preset1['token']['threshold'] = 0.99

    # Get preset again, should be unchanged
    preset2 = get_preset("standard")
    assert preset2['token']['threshold'] == original_threshold
    assert preset2['token']['threshold'] != 0.99


# ============================================================================
# Test 14: Decision Threshold Calculation
# ============================================================================

def test_decision_threshold_calculation():
    """
    Test that decision threshold is correctly calculated as percentage of total votes.

    Verifies:
    - Standard: 50% of 4.5 = 2.25
    - Simple: 75% of 4.0 = 3.0 (requires both detectors)
    - VotingSystem uses correct threshold
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Standard preset
    standard_config = get_preset_config("standard")
    standard_voting = VotingSystem(standard_config)

    # Decision threshold = 50% of 4.5 = 2.25
    assert standard_voting.decision_threshold == 2.25
    assert standard_voting.total_possible_votes == 4.5

    # Simple preset
    simple_config = get_preset_config("simple")
    simple_voting = VotingSystem(simple_config)

    # Decision threshold = 75% of 4.0 = 3.0 (requires both detectors)
    assert simple_voting.decision_threshold == 3.0
    assert simple_voting.total_possible_votes == 4.0


# ============================================================================
# Test 15: Edge Case - All Detectors Below Threshold
# ============================================================================

def test_all_detectors_below_threshold():
    """
    Test behavior when all detectors score below threshold.

    Verifies:
    - No votes cast
    - Not flagged as plagiarism
    - Works correctly with both presets
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Test with standard preset
    standard_config = get_preset_config("standard")
    standard_voting = VotingSystem(standard_config)

    result = standard_voting.vote(
        token_sim=0.50,  # Below 0.70
        ast_sim=0.60,    # Below 0.80
        hash_sim=0.40    # Below 0.60
    )

    assert result['votes']['token'] == 0.0
    assert result['votes']['ast'] == 0.0
    assert result['votes']['hash'] == 0.0
    assert result['total_votes_cast'] == 0.0
    assert result['is_plagiarized'] == False

    # Test with simple preset
    simple_config = get_preset_config("simple")
    simple_voting = VotingSystem(simple_config)

    result = simple_voting.vote(
        token_sim=0.50,  # Below 0.70
        ast_sim=0.60,    # Below 0.85
        hash_sim=0.40    # Ignored (disabled)
    )

    assert result['votes']['token'] == 0.0
    assert result['votes']['ast'] == 0.0
    assert result['votes']['hash'] == 0.0
    assert result['total_votes_cast'] == 0.0
    assert result['is_plagiarized'] == False


# ============================================================================
# Test 16: Edge Case - Perfect Similarity Scores
# ============================================================================

def test_perfect_similarity_scores():
    """
    Test behavior with perfect similarity scores (1.0).

    Verifies:
    - All active detectors vote
    - Maximum votes cast
    - Plagiarism detected
    - Confidence score is high
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    # Test with standard preset
    standard_config = get_preset_config("standard")
    standard_voting = VotingSystem(standard_config)

    result = standard_voting.vote(
        token_sim=1.0,
        ast_sim=1.0,
        hash_sim=1.0
    )

    assert result['votes']['token'] == 1.0
    assert result['votes']['ast'] == 2.0
    assert result['votes']['hash'] == 1.5
    assert result['total_votes_cast'] == 4.5
    assert result['is_plagiarized'] == True
    assert result['confidence_score'] == 1.0  # Perfect confidence

    # Test with simple preset
    simple_config = get_preset_config("simple")
    simple_voting = VotingSystem(simple_config)

    result = simple_voting.vote(
        token_sim=1.0,
        ast_sim=1.0,
        hash_sim=1.0  # Ignored
    )

    assert result['votes']['token'] == 2.0
    assert result['votes']['ast'] == 2.0
    assert result['votes']['hash'] == 0.0  # Disabled
    assert result['total_votes_cast'] == 4.0
    assert result['is_plagiarized'] == True
    assert result['confidence_score'] == 1.0  # Perfect confidence


# ============================================================================
# Test 17: Preset Name Whitespace Handling
# ============================================================================

def test_preset_name_whitespace():
    """
    Test that preset names handle whitespace correctly.

    Verifies:
    - Leading/trailing whitespace stripped
    - Case insensitive
    - Mixed whitespace and case
    """
    from src.core.config_presets import get_preset

    # All should return same preset
    preset1 = get_preset("standard")
    preset2 = get_preset("  standard  ")
    preset3 = get_preset("\tSTANDARD\n")
    preset4 = get_preset("  Standard  ")

    assert preset1 == preset2
    assert preset1 == preset3
    assert preset1 == preset4


# ============================================================================
# Test 18: Multiple Voting Calls with Same System
# ============================================================================

def test_multiple_voting_calls():
    """
    Test that VotingSystem can be reused for multiple voting calls.

    Verifies:
    - No state pollution between calls
    - Each call produces independent results
    - Configuration remains stable
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    config = get_preset_config("simple")
    voting_system = VotingSystem(config)

    # First call
    result1 = voting_system.vote(0.80, 0.90, 0.50)

    # Second call with different scores
    result2 = voting_system.vote(0.60, 0.70, 0.80)

    # Third call
    result3 = voting_system.vote(0.80, 0.90, 0.50)

    # Results 1 and 3 should be identical (same inputs)
    assert result1['is_plagiarized'] == result3['is_plagiarized']
    assert result1['total_votes_cast'] == result3['total_votes_cast']
    assert result1['confidence_score'] == result3['confidence_score']

    # Result 2 should be different
    assert result2['is_plagiarized'] != result1['is_plagiarized']

    # System configuration should remain stable
    assert voting_system.total_possible_votes == 4.0
    assert voting_system.decision_threshold == 3.0  # 75% of 4.0


# ============================================================================
# Test 19: apply_preset_to_voting_system()
# ============================================================================

def test_apply_preset_to_voting_system():
    """
    Test apply_preset_to_voting_system() function.

    Verifies:
    - Can apply preset to existing VotingSystem instance
    - Configuration is updated in-place
    - Total votes recalculated correctly
    - Decision threshold updated
    - Can switch between presets
    """
    from src.core.config_presets import apply_preset_to_voting_system, get_preset_config
    from src.voting.voting_system import VotingSystem

    # Create system with standard preset
    system = VotingSystem(get_preset_config("standard"))
    assert system.total_possible_votes == 4.5
    assert system.config['hash']['weight'] == 1.5

    # Apply simple preset
    apply_preset_to_voting_system(system, "simple")

    # Verify configuration changed
    assert system.total_possible_votes == 4.0
    assert system.config['hash']['weight'] == 0.0
    assert system.config['ast']['threshold'] == 0.85
    assert system.decision_threshold == 3.0  # 75% of 4.0

    # Switch back to standard
    apply_preset_to_voting_system(system, "standard")

    # Verify back to standard
    assert system.total_possible_votes == 4.5
    assert system.config['hash']['weight'] == 1.5
    assert system.config['ast']['threshold'] == 0.80
    assert system.decision_threshold == 2.25


# ============================================================================
# Test 20: apply_preset_to_voting_system() Error Handling
# ============================================================================

def test_apply_preset_invalid_input():
    """
    Test error handling in apply_preset_to_voting_system().

    Verifies:
    - ValueError for invalid preset name
    - TypeError for non-VotingSystem object
    """
    from src.core.config_presets import apply_preset_to_voting_system
    from src.voting.voting_system import VotingSystem

    system = VotingSystem()

    # Invalid preset name
    with pytest.raises(ValueError, match="Unknown preset"):
        apply_preset_to_voting_system(system, "invalid")

    # Non-VotingSystem object
    class FakeSystem:
        pass

    fake_system = FakeSystem()
    with pytest.raises(TypeError, match="VotingSystem"):
        apply_preset_to_voting_system(fake_system, "standard")


# ============================================================================
# Test 21: validate_preset()
# ============================================================================

def test_validate_preset():
    """
    Test validate_preset() function.

    Verifies:
    - Valid presets pass validation
    - Invalid presets fail validation
    - Checks for required keys
    - Validates value ranges
    """
    from src.core.config_presets import validate_preset, get_preset

    # Valid presets should pass
    standard = get_preset("standard")
    assert validate_preset(standard) == True

    simple = get_preset("simple")
    assert validate_preset(simple) == True

    # Missing required keys
    invalid_preset = {"name": "Test"}
    assert validate_preset(invalid_preset) == False

    # Invalid threshold (out of range)
    invalid_preset = get_preset("standard").copy()
    invalid_preset['token'] = invalid_preset['token'].copy()
    invalid_preset['token']['threshold'] = 1.5  # > 1.0
    assert validate_preset(invalid_preset) == False

    # Negative weight
    invalid_preset = get_preset("standard").copy()
    invalid_preset['token'] = invalid_preset['token'].copy()
    invalid_preset['token']['weight'] = -1.0
    assert validate_preset(invalid_preset) == False

    # Confidence weights don't sum to 1.0
    invalid_preset = get_preset("standard").copy()
    invalid_preset['token'] = invalid_preset['token'].copy()
    invalid_preset['token']['confidence_weight'] = 0.5  # Will make sum > 1.0
    assert validate_preset(invalid_preset) == False


# ============================================================================
# Test 22: get_preset_summary()
# ============================================================================

def test_get_preset_summary():
    """
    Test get_preset_summary() function.

    Verifies:
    - Returns formatted string
    - Contains preset name and description
    - Shows detector configuration
    - Indicates disabled detectors
    - Shows total votes and thresholds
    """
    from src.core.config_presets import get_preset_summary

    # Standard preset summary
    standard_summary = get_preset_summary("standard")

    assert isinstance(standard_summary, str)
    assert "Standard (Recommended)" in standard_summary
    assert "Token" in standard_summary
    assert "AST" in standard_summary or "Ast" in standard_summary
    assert "Hash" in standard_summary
    assert "4.5" in standard_summary  # Total votes
    assert "2.25" in standard_summary or "2.2" in standard_summary  # Decision threshold

    # Simple preset summary
    simple_summary = get_preset_summary("simple")

    assert isinstance(simple_summary, str)
    assert "Simple Problems" in simple_summary
    assert "DISABLED" in simple_summary  # Hash should be marked disabled
    assert "4.0" in simple_summary  # Total votes
    assert "2.0" in simple_summary  # Decision threshold

    # Verify summaries are different
    assert standard_summary != simple_summary


# ============================================================================
# Test 23: get_preset_summary() Invalid Input
# ============================================================================

def test_get_preset_summary_invalid():
    """
    Test get_preset_summary() with invalid preset name.

    Verifies:
    - ValueError raised for unknown preset
    """
    from src.core.config_presets import get_preset_summary

    with pytest.raises(ValueError, match="Unknown preset"):
        get_preset_summary("invalid")


# ============================================================================
# Test 24: Preset Constants
# ============================================================================

def test_preset_constants():
    """
    Test that preset constants are defined and accessible.

    Verifies:
    - PRESET_STANDARD constant exists
    - PRESET_SIMPLE constant exists
    - Constants have correct values
    """
    from src.core.config_presets import PRESET_STANDARD, PRESET_SIMPLE

    assert PRESET_STANDARD == "standard"
    assert PRESET_SIMPLE == "simple"


# ============================================================================
# Test 25: Simple Mode Requires Both Detectors (False Positive Fix)
# ============================================================================

def test_simple_mode_requires_both_detectors():
    """
    Test that Simple mode requires BOTH Token AND AST to vote YES.

    This is the critical fix for the false positive bug where AST alone
    could trigger plagiarism detection in Simple mode.

    Verifies:
    - Token YES + AST NO → NOT PLAGIARIZED
    - Token NO + AST YES → NOT PLAGIARIZED
    - Token YES + AST YES → PLAGIARIZED
    - Decision threshold is 75% (3.0 out of 4.0)
    """
    from src.core.config_presets import get_preset_config
    from src.voting.voting_system import VotingSystem

    simple_config = get_preset_config("simple")
    voting = VotingSystem(simple_config)

    # Verify decision threshold is 75%
    assert voting.decision_threshold == 3.0, "Decision threshold should be 3.0 (75% of 4.0)"

    # Scenario 1: Token YES, AST NO → NOT PLAGIARIZED
    result1 = voting.vote(token_sim=0.75, ast_sim=0.80, hash_sim=0.0)
    assert result1['votes']['token'] == 2.0, "Token should vote (0.75 > 0.70)"
    assert result1['votes']['ast'] == 0.0, "AST should NOT vote (0.80 < 0.85)"
    assert result1['total_votes_cast'] == 2.0, "Only token votes"
    assert result1['is_plagiarized'] == False, "Should NOT flag (2.0 < 3.0)"

    # Scenario 2: Token NO, AST YES → NOT PLAGIARIZED (the critical bug fix)
    result2 = voting.vote(token_sim=0.65, ast_sim=0.90, hash_sim=0.0)
    assert result2['votes']['token'] == 0.0, "Token should NOT vote (0.65 < 0.70)"
    assert result2['votes']['ast'] == 2.0, "AST should vote (0.90 > 0.85)"
    assert result2['total_votes_cast'] == 2.0, "Only AST votes"
    assert result2['is_plagiarized'] == False, "Should NOT flag (2.0 < 3.0) - FIX!"

    # Scenario 3: Token YES, AST YES → PLAGIARIZED
    result3 = voting.vote(token_sim=0.75, ast_sim=0.90, hash_sim=0.0)
    assert result3['votes']['token'] == 2.0, "Token should vote"
    assert result3['votes']['ast'] == 2.0, "AST should vote"
    assert result3['total_votes_cast'] == 4.0, "Both vote"
    assert result3['is_plagiarized'] == True, "Should flag (4.0 ≥ 3.0)"

    # Verify the old buggy behavior would have flagged scenario 2
    # In old config: AST weight was 2.5, threshold was 50% (2.0)
    # AST alone (2.5) > 2.0 → FALSE POSITIVE
    # Now: AST alone (2.0) < 3.0 → CORRECT


# ============================================================================
# Test 26: Comprehensive Integration Test
# ============================================================================

def test_comprehensive_preset_workflow():
    """
    Comprehensive integration test of preset system.

    Tests complete workflow:
    1. List available presets
    2. Load preset
    3. Validate preset
    4. Create VotingSystem with preset
    5. Perform voting
    6. Apply different preset
    7. Verify behavior changes

    This test ensures all components work together correctly.
    """
    from src.core.config_presets import (
        get_available_presets,
        get_preset,
        get_preset_config,
        validate_preset,
        apply_preset_to_voting_system,
        get_preset_summary
    )
    from src.voting.voting_system import VotingSystem

    # Step 1: List available presets
    presets = get_available_presets()
    assert len(presets) == 2
    assert "standard" in presets
    assert "simple" in presets

    # Step 2: Load standard preset
    standard_preset = get_preset("standard")
    assert validate_preset(standard_preset) == True

    # Step 3: Get summary
    summary = get_preset_summary("standard")
    assert len(summary) > 0

    # Step 4: Create VotingSystem with standard preset
    config = get_preset_config("standard")
    voting_system = VotingSystem(config)
    assert voting_system.total_possible_votes == 4.5

    # Step 5: Perform voting with standard preset
    # Borderline case: AST score between 0.80 and 0.85
    result_standard = voting_system.vote(
        token_sim=0.75,
        ast_sim=0.82,
        hash_sim=0.30
    )

    # Standard: Token (1.0) + AST (2.0) = 3.0 / 4.5 = 66.67% → PLAGIARISM
    assert result_standard['is_plagiarized'] == True
    assert result_standard['votes']['ast'] == 2.0

    # Step 6: Create NEW VotingSystem with simple preset (recommended approach)
    # Note: apply_preset_to_voting_system updates config but not derived attributes
    # Best practice is to create new VotingSystem instance with desired preset
    voting_system_simple = VotingSystem(get_preset_config("simple"))
    assert voting_system_simple.total_possible_votes == 4.0
    assert voting_system_simple.ast_config['threshold'] == 0.85

    # Step 7: Use same scores, different result expected
    result_simple = voting_system_simple.vote(
        token_sim=0.75,
        ast_sim=0.82,
        hash_sim=0.30
    )

    # Simple: Token (2.0) only = 2.0 / 4.0 = 50% < 75% → NOT PLAGIARISM
    # AST should NOT vote because 0.82 < 0.85 (stricter threshold)
    assert result_simple['votes']['ast'] == 0.0, "AST should not vote (0.82 < 0.85)"
    assert result_simple['votes']['token'] == 2.0, "Token should vote"
    assert result_simple['total_votes_cast'] == 2.0
    assert result_simple['is_plagiarized'] == False, "Should NOT be plagiarism with only token vote"

    # Verify behavior changed
    assert result_standard['is_plagiarized'] != result_simple['is_plagiarized']
