#!/usr/bin/env python3
"""
Example usage of voting system with configuration presets.

This script demonstrates how to use the preset system for different
plagiarism detection scenarios.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config_presets import get_preset_config, get_preset_summary
from src.voting.voting_system import VotingSystem


def example_standard_preset():
    """Example: Using standard preset for typical assignments (50+ lines)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Standard Preset (Typical Assignments)")
    print("="*70)

    # Load standard preset
    config = get_preset_config("standard")
    system = VotingSystem(config)

    print("\nConfiguration:")
    print(system)

    # Simulate detector scores from a realistic assignment
    print("\nScenario: Comparing two Rock-Paper-Scissors implementations")
    print("-" * 70)

    token_score = 0.75
    ast_score = 0.85
    hash_score = 0.65

    print(f"Token similarity: {token_score:.3f}")
    print(f"AST similarity: {ast_score:.3f}")
    print(f"Hash similarity: {hash_score:.3f}")

    result = system.vote(token_score, ast_score, hash_score)

    print(f"\nResult:")
    print(f"  Decision: {'PLAGIARISM' if result['is_plagiarized'] else 'NOT PLAGIARISM'}")
    print(f"  Confidence: {result['confidence_score']:.3f}")
    print(f"  Votes cast: {result['total_votes_cast']:.1f}/{result['total_possible_votes']:.1f}")
    print(f"  Individual votes:")
    print(f"    - Token: {result['votes']['token']:.1f}")
    print(f"    - AST: {result['votes']['ast']:.1f}")
    print(f"    - Hash: {result['votes']['hash']:.1f}")


def example_simple_preset():
    """Example: Using simple preset for constrained problems (<50 lines)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Simple Preset (FizzBuzz-like Problems)")
    print("="*70)

    # Load simple preset
    config = get_preset_config("simple")
    system = VotingSystem(config)

    print("\nConfiguration:")
    print(system)

    # Simulate detector scores from a simple problem
    print("\nScenario: Comparing two FizzBuzz implementations")
    print("-" * 70)

    token_score = 0.75
    ast_score = 0.82  # Just below threshold (0.85)
    hash_score = 0.65  # Ignored (hash disabled)

    print(f"Token similarity: {token_score:.3f}")
    print(f"AST similarity: {ast_score:.3f}")
    print(f"Hash similarity: {hash_score:.3f} (will be ignored - hash disabled)")

    result = system.vote(token_score, ast_score, hash_score)

    print(f"\nResult:")
    print(f"  Decision: {'PLAGIARISM' if result['is_plagiarized'] else 'NOT PLAGIARISM'}")
    print(f"  Confidence: {result['confidence_score']:.3f}")
    print(f"  Votes cast: {result['total_votes_cast']:.1f}/{result['total_possible_votes']:.1f}")
    print(f"  Individual votes:")
    print(f"    - Token: {result['votes']['token']:.1f}")
    print(f"    - AST: {result['votes']['ast']:.1f} (threshold not met: 0.82 < 0.85)")
    print(f"    - Hash: {result['votes']['hash']:.1f} (disabled)")


def example_switching_presets():
    """Example: Switching between presets at runtime"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Switching Presets at Runtime")
    print("="*70)

    # Start with standard preset
    system = VotingSystem(get_preset_config("standard"))
    print("\nInitial configuration: Standard preset")
    print(f"Total votes: {system.total_votes}")

    # Analyze first assignment (typical assignment)
    print("\nAnalyzing Assignment 1 (complex project)...")
    result1 = system.vote(0.75, 0.85, 0.65)
    print(f"  Decision: {'PLAGIARISM' if result1['is_plagiarized'] else 'NOT PLAGIARISM'}")

    # Switch to simple preset for next assignment
    print("\nSwitching to simple preset for next assignment...")
    system.update_config(get_preset_config("simple"))
    print(f"Total votes: {system.total_votes}")

    # Analyze second assignment (simple problem)
    print("\nAnalyzing Assignment 2 (FizzBuzz)...")
    result2 = system.vote(0.75, 0.82, 0.65)
    print(f"  Decision: {'PLAGIARISM' if result2['is_plagiarized'] else 'NOT PLAGIARISM'}")


def example_custom_configuration():
    """Example: Creating custom configuration"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Configuration")
    print("="*70)

    # Create custom config (e.g., for very short code snippets)
    custom_config = {
        'token': {'threshold': 0.65, 'weight': 2.0, 'confidence_weight': 0.5},
        'ast': {'threshold': 0.90, 'weight': 2.0, 'confidence_weight': 0.5},
        'hash': {'threshold': 0.60, 'weight': 0.0, 'confidence_weight': 0.0},  # Disabled
        'decision_threshold': 0.50
    }

    system = VotingSystem(custom_config)

    print("\nCustom configuration:")
    print(system)

    print("\nScenario: Very short code snippet (10 lines)")
    print("-" * 70)

    result = system.vote(0.70, 0.85, 0.50)

    print(f"\nResult:")
    print(f"  Decision: {'PLAGIARISM' if result['is_plagiarized'] else 'NOT PLAGIARISM'}")
    print(f"  Confidence: {result['confidence_score']:.3f}")
    print(f"  Votes cast: {result['total_votes_cast']:.1f}/{result['total_possible_votes']:.1f}")


def example_preset_summaries():
    """Example: Displaying preset summaries"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Preset Summaries")
    print("="*70)

    print("\n" + get_preset_summary("standard"))
    print("\n" + get_preset_summary("simple"))


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("VOTING SYSTEM PRESET USAGE EXAMPLES")
    print("="*70)

    example_standard_preset()
    example_simple_preset()
    example_switching_presets()
    example_custom_configuration()
    example_preset_summaries()

    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Use 'standard' preset for typical assignments (50+ lines)")
    print("  2. Use 'simple' preset for constrained problems (<50 lines)")
    print("  3. Hash detector is disabled in simple preset (weight=0.0)")
    print("  4. Confidence calculation automatically adjusts for disabled detectors")
    print("  5. You can switch presets at runtime using update_config()")
    print("  6. Custom configurations are also supported")
    print()


if __name__ == "__main__":
    main()
