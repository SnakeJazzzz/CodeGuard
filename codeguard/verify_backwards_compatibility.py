#!/usr/bin/env python3
"""
Verify backwards compatibility with existing code.

This script ensures that the preset integration doesn't break
existing code that uses the old API.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.voting.voting_system import VotingSystem


def test_default_initialization():
    """Test that default initialization still works"""
    print("\n" + "="*70)
    print("TEST: Default Initialization (Old API)")
    print("="*70)

    # Old code: VotingSystem() with no arguments
    system = VotingSystem()

    assert system.config is not None
    assert "token" in system.config
    assert "ast" in system.config
    assert "hash" in system.config

    # Should use standard preset by default
    assert system.total_possible_votes == 4.5
    assert system.decision_threshold == 2.25

    print("✓ Default initialization works")
    print(f"✓ total_possible_votes: {system.total_possible_votes}")
    print(f"✓ decision_threshold: {system.decision_threshold}")
    return True


def test_custom_config_old_format():
    """Test that old custom config format still works"""
    print("\n" + "="*70)
    print("TEST: Custom Config (Old Format)")
    print("="*70)

    # Old format: config without decision_threshold
    custom_config = {
        "token": {"threshold": 0.75, "weight": 1.5, "confidence_weight": 0.3},
        "ast": {"threshold": 0.85, "weight": 2.5, "confidence_weight": 0.4},
        "hash": {"threshold": 0.65, "weight": 2.0, "confidence_weight": 0.3},
    }

    system = VotingSystem(config=custom_config)

    assert system.config["token"]["threshold"] == 0.75
    assert system.config["ast"]["weight"] == 2.5
    assert system.total_possible_votes == 6.0  # 1.5 + 2.5 + 2.0

    print("✓ Old custom config format works")
    print(f"✓ total_possible_votes: {system.total_possible_votes}")
    return True


def test_vote_return_structure():
    """Test that vote() return structure hasn't changed"""
    print("\n" + "="*70)
    print("TEST: Vote Return Structure")
    print("="*70)

    system = VotingSystem()
    result = system.vote(0.75, 0.85, 0.65)

    # Old fields (must be present)
    assert "is_plagiarized" in result
    assert "confidence_score" in result
    assert "votes" in result
    assert "weighted_votes" in result
    assert "individual_scores" in result

    # New fields (added, but shouldn't break old code)
    assert "total_votes_cast" in result
    assert "decision_threshold" in result
    assert "total_possible_votes" in result

    # Verify backwards compatibility aliases
    assert result["weighted_votes"] == result["total_votes_cast"]

    print("✓ Vote return structure is backwards compatible")
    print(f"✓ Old fields present: is_plagiarized, confidence_score, votes, weighted_votes, individual_scores")
    print(f"✓ New fields added: total_votes_cast, decision_threshold, total_possible_votes")
    return True


def test_vote_behavior():
    """Test that vote() behavior hasn't changed for standard config"""
    print("\n" + "="*70)
    print("TEST: Vote Behavior (Standard Config)")
    print("="*70)

    system = VotingSystem()

    # All detectors vote YES
    result = system.vote(0.75, 0.85, 0.65)

    assert result["is_plagiarized"] == True
    assert result["votes"]["token"] == True or result["votes"]["token"] == 1.0
    assert result["votes"]["ast"] == True or result["votes"]["ast"] == 2.0
    assert result["votes"]["hash"] == True or result["votes"]["hash"] == 1.5
    assert result["weighted_votes"] == 4.5

    print("✓ Vote behavior correct (all detectors vote YES)")
    print(f"✓ Decision: {'PLAGIARISM' if result['is_plagiarized'] else 'NOT PLAGIARISM'}")
    print(f"✓ Weighted votes: {result['weighted_votes']}")

    # Only token votes YES
    result2 = system.vote(0.75, 0.75, 0.55)

    assert result2["is_plagiarized"] == False
    assert result2["votes"]["token"] == True or result2["votes"]["token"] == 1.0
    assert result2["votes"]["ast"] == False or result2["votes"]["ast"] == 0.0
    assert result2["votes"]["hash"] == False or result2["votes"]["hash"] == 0.0
    assert result2["weighted_votes"] == 1.0

    print("✓ Vote behavior correct (only token votes YES)")
    print(f"✓ Decision: {'PLAGIARISM' if result2['is_plagiarized'] else 'NOT PLAGIARISM'}")
    print(f"✓ Weighted votes: {result2['weighted_votes']}")

    return True


def test_attributes_still_exist():
    """Test that all old attributes still exist"""
    print("\n" + "="*70)
    print("TEST: Attributes Exist")
    print("="*70)

    system = VotingSystem()

    # Old attributes
    assert hasattr(system, "config")
    assert hasattr(system, "total_possible_votes")
    assert hasattr(system, "decision_threshold")

    # New attributes (shouldn't break anything)
    assert hasattr(system, "total_votes")
    assert hasattr(system, "token_config")
    assert hasattr(system, "ast_config")
    assert hasattr(system, "hash_config")

    # Verify alias
    assert system.total_possible_votes == system.total_votes

    print("✓ All old attributes still exist")
    print("✓ total_possible_votes is alias for total_votes")
    return True


def test_methods_still_work():
    """Test that all old methods still work"""
    print("\n" + "="*70)
    print("TEST: Methods Still Work")
    print("="*70)

    system = VotingSystem()

    # Test vote()
    result = system.vote(0.75, 0.85, 0.65)
    assert result is not None
    print("✓ vote() works")

    # Test get_detector_info()
    token_info = system.get_detector_info("token")
    assert "threshold" in token_info
    assert "weight" in token_info
    assert "confidence_weight" in token_info
    print("✓ get_detector_info() works")

    # Test get_summary()
    summary = system.get_summary()
    assert "detectors" in summary
    assert "total_possible_votes" in summary
    assert "decision_threshold" in summary
    print("✓ get_summary() works")

    # Test __str__()
    str_repr = str(system)
    assert "VotingSystem Configuration:" in str_repr
    print("✓ __str__() works")

    # Test __repr__()
    repr_str = repr(system)
    assert "VotingSystem" in repr_str
    print("✓ __repr__() works")

    return True


def main():
    """Run all backwards compatibility tests"""
    print("\n" + "="*70)
    print("BACKWARDS COMPATIBILITY VERIFICATION")
    print("="*70)

    tests = [
        ("Default Initialization", test_default_initialization),
        ("Custom Config (Old Format)", test_custom_config_old_format),
        ("Vote Return Structure", test_vote_return_structure),
        ("Vote Behavior", test_vote_behavior),
        ("Attributes Exist", test_attributes_still_exist),
        ("Methods Still Work", test_methods_still_work),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except AssertionError as e:
            print(f"\n✗✗✗ TEST FAILED: {name} ✗✗✗")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
        except Exception as e:
            print(f"\n✗✗✗ TEST ERROR: {name} ✗✗✗")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print("\n" + "="*70)
    print("BACKWARDS COMPATIBILITY SUMMARY")
    print("="*70)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "="*70)
        print("ALL BACKWARDS COMPATIBILITY TESTS PASSED!")
        print("="*70)
        print("\nConclusion: The preset integration maintains full backwards")
        print("compatibility with existing code. Old code will continue to work")
        print("without any modifications.")
        return 0
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED - BACKWARDS COMPATIBILITY BROKEN")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
