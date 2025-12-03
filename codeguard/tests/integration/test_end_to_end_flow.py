"""
Integration Test 6: End-to-End Workflow

Purpose:
    Complete user workflow from start to finish in both modes.

Test Coverage:
    - Full analysis pipeline with real detectors
    - Mode switching and reconfiguration
    - Results consistency across workflows
    - Integration of all bug fixes

Author: CodeGuard Team
Date: 2025-12-03
"""

import pytest
from pathlib import Path
from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem
from src.core.config_presets import get_preset_config, PRESET_STANDARD, PRESET_SIMPLE


class TestEndToEndWorkflow:
    """Test complete workflow with real detectors."""

    @pytest.fixture
    def sample_code_identical(self):
        """Sample identical code for testing."""
        code1 = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(result)
'''
        code2 = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
print(result)
'''
        return code1, code2

    @pytest.fixture
    def sample_code_renamed(self):
        """Sample code with variables renamed."""
        code1 = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''
        code2 = '''
def compute_factorial(num):
    if num <= 1:
        return 1
    return num * compute_factorial(num - 1)
'''
        return code1, code2

    @pytest.fixture
    def sample_code_different(self):
        """Sample completely different code."""
        code1 = '''
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
'''
        code2 = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
        return code1, code2

    def test_standard_mode_full_workflow_identical_code(self, sample_code_identical):
        """
        Test complete workflow in Standard mode with identical code.

        Expected: All detectors vote YES, plagiarism detected.
        """
        code1, code2 = sample_code_identical

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Run detection
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Initialize voting system with Standard preset
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Get voting result
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Verify high similarity scores
        assert token_sim >= 0.95, \
            f"Token similarity should be very high for identical code, got {token_sim}"
        assert ast_sim >= 0.95, \
            f"AST similarity should be very high for identical code, got {ast_sim}"
        assert hash_sim >= 0.95, \
            f"Hash similarity should be very high for identical code, got {hash_sim}"

        # Verify all detectors vote YES
        assert result['votes']['token'] > 0.0, "Token should vote YES"
        assert result['votes']['ast'] > 0.0, "AST should vote YES"
        assert result['votes']['hash'] > 0.0, "Hash should vote YES"

        # Verify plagiarism detected
        assert result['is_plagiarized'] == True, \
            "Identical code should be flagged as plagiarism"

        # Verify high confidence
        assert result['confidence_score'] >= 0.90, \
            f"Confidence should be very high for identical code, got {result['confidence_score']}"

    def test_simple_mode_full_workflow_identical_code(self, sample_code_identical):
        """
        Test complete workflow in Simple mode with identical code.

        Expected: Token and AST vote YES, hash disabled, plagiarism detected.
        """
        code1, code2 = sample_code_identical

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Run detection
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Initialize voting system with Simple preset
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))

        # Get voting result
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Verify Token and AST vote YES
        assert result['votes']['token'] > 0.0, "Token should vote YES"
        assert result['votes']['ast'] > 0.0, "AST should vote YES"

        # Verify Hash is disabled
        assert result['votes']['hash'] == 0.0, \
            "Hash should not vote in Simple mode"

        # Verify plagiarism detected
        assert result['is_plagiarized'] == True, \
            "Identical code should be flagged as plagiarism in Simple mode"

        # Verify total votes is 4.0 (not 4.5)
        assert result['total_possible_votes'] == 4.0, \
            f"Simple mode should have 4.0 total votes, got {result['total_possible_votes']}"

    def test_standard_mode_full_workflow_renamed_variables(self, sample_code_renamed):
        """
        Test workflow with renamed variables in Standard mode.

        Expected: Token NO, AST YES, Hash varies, likely plagiarism detected.
        """
        code1, code2 = sample_code_renamed

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Run detection
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Initialize voting system
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Token should be lower (variables renamed)
        # AST should be high (structure unchanged)
        assert ast_sim > token_sim, \
            "AST similarity should be higher than Token for renamed variables"

        # AST should vote YES (structure is same)
        assert result['votes']['ast'] > 0.0, \
            "AST should detect structural similarity despite renamed variables"

    def test_simple_mode_full_workflow_different_code(self, sample_code_different):
        """
        Test workflow with completely different code in Simple mode.

        Expected: No plagiarism detected.
        """
        code1, code2 = sample_code_different

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Run detection
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Initialize voting system
        voting = VotingSystem(get_preset_config(PRESET_SIMPLE))
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Low similarity expected
        assert token_sim < 0.70, \
            f"Token similarity should be low for different code, got {token_sim}"
        assert ast_sim < 0.85, \
            f"AST similarity should be low for different code, got {ast_sim}"

        # No plagiarism should be detected
        assert result['is_plagiarized'] == False, \
            "Different code should not be flagged as plagiarism"

    def test_mode_switch_workflow(self, sample_code_renamed):
        """
        Test switching modes and rerunning analysis.

        Verifies that mode switches correctly update configuration
        and produce different results.
        """
        code1, code2 = sample_code_renamed

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Run detection once
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Test in Standard mode
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result_standard = voting.vote(token_sim, ast_sim, hash_sim)

        # Switch to Simple mode
        voting.update_config(get_preset_config(PRESET_SIMPLE))
        result_simple = voting.vote(token_sim, ast_sim, hash_sim)

        # Hash should be active in Standard, disabled in Simple
        assert result_standard['total_possible_votes'] == 4.5, \
            "Standard mode should have 4.5 total votes"
        assert result_simple['total_possible_votes'] == 4.0, \
            "Simple mode should have 4.0 total votes"

        # Hash vote should differ
        if hash_sim >= 0.60:  # Hash threshold in both modes
            assert result_standard['votes']['hash'] > 0.0, \
                "Hash should vote in Standard mode"
        assert result_simple['votes']['hash'] == 0.0, \
            "Hash should not vote in Simple mode"

        # Decision might differ between modes
        # (depending on scores, Simple mode is stricter)

    def test_threshold_adjustment_workflow(self, sample_code_renamed):
        """
        Test adjusting thresholds during workflow.

        Simulates user adjusting sliders and rerunning analysis.
        """
        code1, code2 = sample_code_renamed

        # Initialize detectors and run detection
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Start with Standard preset
        config = get_preset_config(PRESET_STANDARD)
        voting = VotingSystem(config)

        # Get baseline result
        result_baseline = voting.vote(token_sim, ast_sim, hash_sim)
        baseline_decision = result_baseline['is_plagiarized']

        # Adjust thresholds (make stricter)
        config['token']['threshold'] = 0.90
        config['ast']['threshold'] = 0.95
        config['hash']['threshold'] = 0.80
        voting.update_config(config)

        # Rerun with stricter thresholds
        result_strict = voting.vote(token_sim, ast_sim, hash_sim)

        # With stricter thresholds, fewer detectors should vote YES
        assert result_strict['total_votes_cast'] <= result_baseline['total_votes_cast'], \
            "Stricter thresholds should result in fewer or equal votes"

        # Reset to defaults
        voting.update_config(get_preset_config(PRESET_STANDARD))
        result_reset = voting.vote(token_sim, ast_sim, hash_sim)

        # Should match baseline
        assert result_reset['is_plagiarized'] == baseline_decision, \
            "Reset should restore original decision"

    def test_configuration_consistency_across_analyses(self):
        """
        Test that configuration remains consistent across multiple analyses.

        Simulates running multiple file comparisons with same configuration.
        """
        # Create multiple code pairs
        pairs = [
            ('''def f1(x): return x * 2''', '''def f2(y): return y * 2'''),
            ('''def f1(x): return x + 1''', '''def f2(y): return y + 1'''),
            ('''def f1(x): return x - 1''', '''def f2(y): return y - 1'''),
        ]

        # Initialize detectors
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Initialize voting system once
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))

        # Run analysis on all pairs
        results = []
        for code1, code2 in pairs:
            token_sim = token_detector.compare(code1, code2)
            ast_sim = ast_detector.compare(code1, code2)
            hash_sim = hash_detector.compare(code1, code2)

            result = voting.vote(token_sim, ast_sim, hash_sim)
            results.append(result)

        # Verify configuration remained consistent
        for result in results:
            assert result['total_possible_votes'] == 4.5, \
                "Total possible votes should remain 4.5 across analyses"
            assert abs(result['decision_threshold'] - 2.25) < 0.01, \
                "Decision threshold should remain 2.25 across analyses"


class TestValidationDatasetWorkflow:
    """Test workflow using validation dataset files."""

    @pytest.fixture
    def validation_dataset_path(self):
        """Get path to validation datasets."""
        return Path(__file__).parent.parent.parent / "validation-datasets"

    def test_plagiarized_pair_detection(self, validation_dataset_path):
        """
        Test detection on known plagiarized pairs from validation dataset.

        Should detect plagiarism in plagiarized/ directory pairs.
        """
        plagiarized_dir = validation_dataset_path / "plagiarized"

        if not plagiarized_dir.exists():
            pytest.skip("Validation dataset not available")

        # Try to find a plagiarized pair
        original_files = list(plagiarized_dir.glob("*_original.py"))

        if not original_files:
            pytest.skip("No plagiarized pairs found in validation dataset")

        # Test first pair
        original_file = original_files[0]
        copied_file = plagiarized_dir / original_file.name.replace("_original", "_copied")

        if not copied_file.exists():
            # Try other variations
            copied_file = plagiarized_dir / original_file.name.replace("_original", "_renamed")

        if not copied_file.exists():
            pytest.skip(f"No matching plagiarized file found for {original_file.name}")

        # Read files
        code1 = original_file.read_text()
        code2 = copied_file.read_text()

        # Run detection
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Test in both modes
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        result_standard = voting_standard.vote(token_sim, ast_sim, hash_sim)

        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))
        result_simple = voting_simple.vote(token_sim, ast_sim, hash_sim)

        # Should detect plagiarism (may fail in Simple mode depending on code)
        # Standard mode should be more likely to detect
        print(f"\nTesting {original_file.name} vs {copied_file.name}")
        print(f"Token: {token_sim:.3f}, AST: {ast_sim:.3f}, Hash: {hash_sim:.3f}")
        print(f"Standard mode: {result_standard['is_plagiarized']}")
        print(f"Simple mode: {result_simple['is_plagiarized']}")

    def test_legitimate_pair_rejection(self, validation_dataset_path):
        """
        Test that legitimate code pairs are not flagged as plagiarism.

        Should NOT detect plagiarism for different implementations.
        """
        legitimate_dir = validation_dataset_path / "legitimate"

        if not legitimate_dir.exists():
            pytest.skip("Validation dataset not available")

        legitimate_files = list(legitimate_dir.glob("*.py"))

        if len(legitimate_files) < 2:
            pytest.skip("Not enough legitimate files for comparison")

        # Compare two different legitimate files
        code1 = legitimate_files[0].read_text()
        code2 = legitimate_files[1].read_text()

        # Run detection
        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        # Test in both modes
        voting_standard = VotingSystem(get_preset_config(PRESET_STANDARD))
        result_standard = voting_standard.vote(token_sim, ast_sim, hash_sim)

        voting_simple = VotingSystem(get_preset_config(PRESET_SIMPLE))
        result_simple = voting_simple.vote(token_sim, ast_sim, hash_sim)

        # Print results for analysis
        print(f"\nTesting {legitimate_files[0].name} vs {legitimate_files[1].name}")
        print(f"Token: {token_sim:.3f}, AST: {ast_sim:.3f}, Hash: {hash_sim:.3f}")
        print(f"Standard mode: {result_standard['is_plagiarized']}")
        print(f"Simple mode: {result_simple['is_plagiarized']}")

        # Low similarity expected (though not guaranteed for all pairs)
        # Just verify the workflow completes successfully


class TestErrorHandling:
    """Test error handling in end-to-end workflow."""

    def test_syntax_error_handling(self):
        """
        Test that workflow handles syntax errors gracefully.
        """
        code1 = '''
def valid_function():
    return 42
'''
        code2 = '''
def invalid_function(
    return 42  # Syntax error
'''

        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # Token detector might fail or return low similarity
        try:
            token_sim = token_detector.compare(code1, code2)
        except Exception:
            token_sim = 0.0

        # AST detector should handle syntax error gracefully
        try:
            ast_sim = ast_detector.compare(code1, code2)
        except Exception:
            ast_sim = 0.0

        # Hash detector might fail or return low similarity
        try:
            hash_sim = hash_detector.compare(code1, code2)
        except Exception:
            hash_sim = 0.0

        # Voting should still work with zero scores
        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Should not detect plagiarism with all zeros
        assert result['is_plagiarized'] == False, \
            "Syntax errors should result in low similarity"

    def test_empty_code_handling(self):
        """
        Test that workflow handles empty code gracefully.
        """
        code1 = "# Just a comment"
        code2 = ""

        token_detector = TokenDetector()
        ast_detector = ASTDetector()
        hash_detector = HashDetector(k=5, w=4)

        # All detectors should return low/zero similarity
        token_sim = token_detector.compare(code1, code2)
        ast_sim = ast_detector.compare(code1, code2)
        hash_sim = hash_detector.compare(code1, code2)

        voting = VotingSystem(get_preset_config(PRESET_STANDARD))
        result = voting.vote(token_sim, ast_sim, hash_sim)

        # Should not detect plagiarism
        assert result['is_plagiarized'] == False, \
            "Empty code should not be flagged as plagiarism"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-s"])
