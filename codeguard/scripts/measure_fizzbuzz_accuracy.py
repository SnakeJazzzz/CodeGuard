#!/usr/bin/env python3
"""
FizzBuzz Dataset Effectiveness Test for CodeGuard Plagiarism Detection System

This script evaluates the detection system's performance on a realistic classroom
scenario with 20 FizzBuzz submissions:
- 4 plagiarized submissions (students 01-04)
- 16 legitimate submissions (students 05-20)

Test cases include:
- Exact copy with obfuscation (student_01 vs student_02)
- Multi-source mosaic plagiarism (student_03, student_04)
- Edge cases comparing different paradigms
- Representative legitimate comparisons

Metrics calculated:
    - Precision: TP / (TP + FP)
    - Recall: TP / (TP + FN)
    - F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
    - Accuracy: (TP + TN) / (TP + TN + FP + FN)

Author: CodeGuard Team
Date: 2024-11-25
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import json

# Add parent directory to path to import detectors
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem


class FizzBuzzEffectivenessTest:
    """
    Comprehensive effectiveness test for FizzBuzz plagiarism detection.

    This class tests the system against a realistic classroom scenario with
    known plagiarism cases and diverse legitimate implementations.
    """

    def __init__(self, fizzbuzz_dir: Path):
        """
        Initialize the effectiveness test system.

        Args:
            fizzbuzz_dir: Path to FizzBuzzProblem directory
        """
        self.fizzbuzz_dir = fizzbuzz_dir
        self.plagiarized_dir = fizzbuzz_dir / "plagiarized"
        self.legitimate_dir = fizzbuzz_dir / "legitimate"

        # Initialize detectors
        self.token_detector = TokenDetector()
        self.ast_detector = ASTDetector()
        self.hash_detector = HashDetector()
        self.voting_system = VotingSystem()

        # Results storage
        self.test_cases: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {
            "token": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
            "ast": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
            "hash": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
            "voting": {"TP": 0, "FP": 0, "TN": 0, "FN": 0},
        }

    def define_test_pairs(self) -> List[Tuple[Path, Path, bool, str]]:
        """
        Define all test pairs with expected results and descriptions.

        Returns:
            List of tuples: (file1_path, file2_path, expected_plagiarism, description)
        """
        pairs = []

        # === PLAGIARISM CASES (Should Be Detected) ===

        # 1. Exact copy with obfuscation (variable renaming + comments)
        pairs.append((
            self.plagiarized_dir / "student_01.py",
            self.plagiarized_dir / "student_02.py",
            True,
            "Exact copy with variable renaming and added comments"
        ))

        # 2. student_01 vs student_03 - 2-source mosaic
        pairs.append((
            self.plagiarized_dir / "student_01.py",
            self.plagiarized_dir / "student_03.py",
            True,
            "2-source mosaic: combined parts from student_01 and another source"
        ))

        # 3. student_01 vs student_04 - 3-source mosaic
        pairs.append((
            self.plagiarized_dir / "student_01.py",
            self.plagiarized_dir / "student_04.py",
            True,
            "3-source mosaic: more sophisticated combination"
        ))

        # 4. student_02 vs student_03 - Both have student_01 origin
        pairs.append((
            self.plagiarized_dir / "student_02.py",
            self.plagiarized_dir / "student_03.py",
            True,
            "Both derived from student_01 (obfuscation vs mosaic)"
        ))

        # 5. student_02 vs student_04 - Both have student_01 origin
        pairs.append((
            self.plagiarized_dir / "student_02.py",
            self.plagiarized_dir / "student_04.py",
            True,
            "Both derived from student_01 (obfuscation vs 3-source mosaic)"
        ))

        # 6. student_03 vs student_04 - Both are mosaics
        pairs.append((
            self.plagiarized_dir / "student_03.py",
            self.plagiarized_dir / "student_04.py",
            True,
            "Both are mosaics with potential structural overlap"
        ))

        # === EDGE CASES (Plagiarized vs Legitimate) ===

        # Test against different paradigms
        pairs.append((
            self.plagiarized_dir / "student_01.py",
            self.legitimate_dir / "student_05.py",
            False,
            "Edge: Basic if-elif vs string multiplication approach"
        ))

        pairs.append((
            self.plagiarized_dir / "student_01.py",
            self.legitimate_dir / "student_06.py",
            False,
            "Edge: Basic vs modulo optimization"
        ))

        pairs.append((
            self.plagiarized_dir / "student_02.py",
            self.legitimate_dir / "student_12.py",
            False,
            "Edge: Obfuscated basic vs OOP approach"
        ))

        # === LEGITIMATE CASES (Should NOT Be Detected) ===

        # Different paradigms should be clearly legitimate
        pairs.append((
            self.legitimate_dir / "student_05.py",  # String multiplication
            self.legitimate_dir / "student_06.py",  # Modulo optimization
            False,
            "Legitimate: String multiplication vs modulo optimization"
        ))

        pairs.append((
            self.legitimate_dir / "student_07.py",  # List comprehension
            self.legitimate_dir / "student_08.py",  # Lambda/map
            False,
            "Legitimate: List comprehension vs lambda/map"
        ))

        pairs.append((
            self.legitimate_dir / "student_09.py",  # Dictionary lookup
            self.legitimate_dir / "student_10.py",  # Ternary operator
            False,
            "Legitimate: Dictionary lookup vs ternary operator"
        ))

        pairs.append((
            self.legitimate_dir / "student_11.py",  # Generator
            self.legitimate_dir / "student_12.py",  # OOP class
            False,
            "Legitimate: Generator vs OOP class"
        ))

        pairs.append((
            self.legitimate_dir / "student_13.py",  # Recursion
            self.legitimate_dir / "student_14.py",  # Functional style
            False,
            "Legitimate: Recursion vs functional programming"
        ))

        pairs.append((
            self.legitimate_dir / "student_15.py",  # Pattern matching
            self.legitimate_dir / "student_16.py",  # Iterator class
            False,
            "Legitimate: Pattern matching vs iterator class"
        ))

        pairs.append((
            self.legitimate_dir / "student_17.py",  # Match statement
            self.legitimate_dir / "student_18.py",  # Walrus operator
            False,
            "Legitimate: Match statement vs walrus operator"
        ))

        pairs.append((
            self.legitimate_dir / "student_19.py",  # Advanced OOP
            self.legitimate_dir / "student_20.py",  # Decorator
            False,
            "Legitimate: Advanced OOP vs decorator pattern"
        ))

        # Cross-category comparisons (similar level of complexity)
        pairs.append((
            self.legitimate_dir / "student_05.py",  # String mult
            self.legitimate_dir / "student_09.py",  # Dict lookup
            False,
            "Legitimate: Two clever one-liners (different approaches)"
        ))

        pairs.append((
            self.legitimate_dir / "student_12.py",  # OOP basic
            self.legitimate_dir / "student_19.py",  # OOP advanced
            False,
            "Legitimate: Both OOP but different complexity levels"
        ))

        pairs.append((
            self.legitimate_dir / "student_06.py",  # Modulo opt
            self.legitimate_dir / "student_10.py",  # Ternary
            False,
            "Legitimate: Both use conditionals but different patterns"
        ))

        pairs.append((
            self.legitimate_dir / "student_08.py",  # Lambda/map
            self.legitimate_dir / "student_14.py",  # Functional
            False,
            "Legitimate: Both functional but different techniques"
        ))

        pairs.append((
            self.legitimate_dir / "student_11.py",  # Generator
            self.legitimate_dir / "student_16.py",  # Iterator
            False,
            "Legitimate: Generator vs custom iterator"
        ))

        return pairs

    def analyze_pair(self, file1: Path, file2: Path) -> Dict[str, Any]:
        """
        Analyze a pair of files using all detectors and voting system.

        Args:
            file1: Path to first file
            file2: Path to second file

        Returns:
            Dictionary containing all detector scores and voting result
        """
        # Read files
        try:
            with open(file1, "r", encoding="utf-8") as f:
                source1 = f.read()

            with open(file2, "r", encoding="utf-8") as f:
                source2 = f.read()
        except Exception as e:
            print(f"Error reading files: {e}")
            return {
                "file1": file1.name,
                "file2": file2.name,
                "token_score": 0.0,
                "ast_score": 0.0,
                "hash_score": 0.0,
                "voting_result": {"is_plagiarized": False, "confidence_score": 0.0},
                "error": str(e)
            }

        # Run all detectors
        token_score = self.token_detector.compare(source1, source2)
        ast_score = self.ast_detector.compare(source1, source2)
        hash_score = self.hash_detector.compare(source1, source2)

        # Get voting system decision
        voting_result = self.voting_system.vote(token_score, ast_score, hash_score)

        return {
            "file1": file1.name,
            "file2": file2.name,
            "token_score": token_score,
            "ast_score": ast_score,
            "hash_score": hash_score,
            "voting_result": voting_result,
        }

    def classify_result(self, detector_name: str, predicted: bool, actual: bool) -> None:
        """
        Classify a detection result as TP, FP, TN, or FN.

        Args:
            detector_name: Name of detector ('token', 'ast', 'hash', 'voting')
            predicted: Whether plagiarism was detected
            actual: Whether plagiarism actually exists
        """
        if predicted and actual:
            self.results[detector_name]["TP"] += 1
        elif predicted and not actual:
            self.results[detector_name]["FP"] += 1
        elif not predicted and not actual:
            self.results[detector_name]["TN"] += 1
        else:  # not predicted and actual
            self.results[detector_name]["FN"] += 1

    def run_validation(self) -> None:
        """
        Run complete validation across all defined test pairs.
        """
        print("=" * 80)
        print("CodeGuard FizzBuzz Dataset - Effectiveness Test")
        print("=" * 80)
        print()
        print("Testing against realistic classroom scenario:")
        print("  - 4 plagiarized submissions (students 01-04)")
        print("  - 16 legitimate submissions (students 05-20)")
        print()

        # Load test pairs
        test_pairs = self.define_test_pairs()
        print(f"Total test pairs: {len(test_pairs)}")
        print()

        # Count expected outcomes
        expected_plagiarism = sum(1 for _, _, is_plag, _ in test_pairs if is_plag)
        expected_legitimate = len(test_pairs) - expected_plagiarism
        print(f"Expected plagiarism cases: {expected_plagiarism}")
        print(f"Expected legitimate cases: {expected_legitimate}")
        print()

        # Run analysis on each pair
        print("Running analysis...")
        print("-" * 80)

        for i, (file1, file2, expected_plagiarism, description) in enumerate(test_pairs, 1):
            print(f"\n[{i}/{len(test_pairs)}] {description}")
            print(f"Files: {file1.name} vs {file2.name}")
            print(f"Expected: {'PLAGIARISM' if expected_plagiarism else 'LEGITIMATE'}")

            # Analyze the pair
            analysis = self.analyze_pair(file1, file2)

            # Get individual detector decisions
            token_threshold = self.voting_system.config["token"]["threshold"]
            ast_threshold = self.voting_system.config["ast"]["threshold"]
            hash_threshold = self.voting_system.config["hash"]["threshold"]

            token_detected = analysis["token_score"] >= token_threshold
            ast_detected = analysis["ast_score"] >= ast_threshold
            hash_detected = analysis["hash_score"] >= hash_threshold
            voting_detected = analysis["voting_result"]["is_plagiarized"]

            # Print scores
            print(f"  Token:  {analysis['token_score']:.3f} -> {'DETECT' if token_detected else 'PASS'}")
            print(f"  AST:    {analysis['ast_score']:.3f} -> {'DETECT' if ast_detected else 'PASS'}")
            print(f"  Hash:   {analysis['hash_score']:.3f} -> {'DETECT' if hash_detected else 'PASS'}")
            print(
                f"  Voting: {'PLAGIARISM' if voting_detected else 'LEGITIMATE'} "
                f"(confidence: {analysis['voting_result']['confidence_score']:.3f})"
            )

            # Determine if result is correct
            correct = voting_detected == expected_plagiarism
            status = "CORRECT" if correct else "INCORRECT"
            print(f"  Result: {status}")

            # Classify results for each detector
            self.classify_result("token", token_detected, expected_plagiarism)
            self.classify_result("ast", ast_detected, expected_plagiarism)
            self.classify_result("hash", hash_detected, expected_plagiarism)
            self.classify_result("voting", voting_detected, expected_plagiarism)

            # Store test case
            self.test_cases.append(
                {
                    "file1": str(file1),
                    "file2": str(file2),
                    "description": description,
                    "expected": expected_plagiarism,
                    "scores": {
                        "token": analysis["token_score"],
                        "ast": analysis["ast_score"],
                        "hash": analysis["hash_score"],
                    },
                    "decisions": {
                        "token": token_detected,
                        "ast": ast_detected,
                        "hash": hash_detected,
                        "voting": voting_detected,
                    },
                    "voting_confidence": analysis["voting_result"]["confidence_score"],
                    "correct": correct,
                }
            )

        print("\n" + "=" * 80)
        print("Analysis complete!")
        print("=" * 80)

    def calculate_metrics(self, detector_name: str) -> Dict[str, float]:
        """
        Calculate precision, recall, F1, and accuracy for a detector.

        Args:
            detector_name: Name of detector to calculate metrics for

        Returns:
            Dictionary containing all metrics
        """
        results = self.results[detector_name]
        TP = results["TP"]
        FP = results["FP"]
        TN = results["TN"]
        FN = results["FN"]

        # Calculate metrics
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
        f1_score = (
            2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        )
        accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else 0.0

        return {
            "TP": TP,
            "FP": FP,
            "TN": TN,
            "FN": FN,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
        }

    def print_results(self) -> None:
        """
        Print formatted results table with all metrics.
        """
        print("\n" + "=" * 80)
        print("EFFECTIVENESS METRICS")
        print("=" * 80)
        print()

        # Print header
        print(
            f"{'Detector':<15} {'TP':<6} {'FP':<6} {'TN':<6} {'FN':<6} "
            f"{'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Accuracy':<12}"
        )
        print("-" * 115)

        # Print metrics for each detector
        for detector_name in ["token", "ast", "hash", "voting"]:
            metrics = self.calculate_metrics(detector_name)

            detector_display = detector_name.upper() if detector_name != "voting" else "VOTING SYS"

            print(
                f"{detector_display:<15} "
                f"{metrics['TP']:<6} "
                f"{metrics['FP']:<6} "
                f"{metrics['TN']:<6} "
                f"{metrics['FN']:<6} "
                f"{metrics['precision']:<12.2%} "
                f"{metrics['recall']:<12.2%} "
                f"{metrics['f1_score']:<12.2%} "
                f"{metrics['accuracy']:<12.2%}"
            )

        print("=" * 115)
        print()

        # Print target achievement
        voting_metrics = self.calculate_metrics("voting")
        print("TARGET METRICS ACHIEVEMENT:")
        print("-" * 80)
        print(
            f"Precision: {voting_metrics['precision']:.2%} "
            f"(Target: >=85%) {'ACHIEVED' if voting_metrics['precision'] >= 0.85 else 'NOT MET'}"
        )
        print(
            f"Recall:    {voting_metrics['recall']:.2%} "
            f"(Target: >=80%) {'ACHIEVED' if voting_metrics['recall'] >= 0.80 else 'NOT MET'}"
        )
        print(
            f"F1 Score:  {voting_metrics['f1_score']:.2%} "
            f"(Target: >=82%) {'ACHIEVED' if voting_metrics['f1_score'] >= 0.82 else 'NOT MET'}"
        )
        print("=" * 80)
        print()

        # Print summary of incorrect classifications
        incorrect_cases = [case for case in self.test_cases if not case["correct"]]
        if incorrect_cases:
            print(f"INCORRECT CLASSIFICATIONS: {len(incorrect_cases)}")
            print("-" * 80)
            for case in incorrect_cases:
                file1_name = Path(case["file1"]).stem
                file2_name = Path(case["file2"]).stem
                expected = "PLAGIARISM" if case["expected"] else "LEGITIMATE"
                detected = "PLAGIARISM" if case["decisions"]["voting"] else "LEGITIMATE"
                print(f"  {file1_name} vs {file2_name}")
                print(f"    Expected: {expected}, Detected: {detected}")
                print(f"    Description: {case['description']}")
                print(f"    Confidence: {case['voting_confidence']:.3f}")
                print()
        else:
            print("ALL CLASSIFICATIONS CORRECT!")
            print()

    def save_report(self, output_path: Path) -> None:
        """
        Save comprehensive effectiveness report to markdown file.

        Args:
            output_path: Path to save the report
        """
        with open(output_path, "w", encoding="utf-8") as f:
            # Write header
            f.write("# CodeGuard FizzBuzz Dataset - Effectiveness Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            voting_metrics = self.calculate_metrics("voting")

            f.write(
                "This report evaluates the CodeGuard plagiarism detection system against "
                "a realistic classroom scenario: 20 student FizzBuzz submissions with "
                "known plagiarism cases and diverse legitimate implementations.\n\n"
            )

            f.write("### Test Dataset Composition\n\n")
            f.write("- **Total submissions:** 20 students\n")
            f.write("- **Plagiarized submissions:** 4 (students 01-04)\n")
            f.write("  - student_01: Original\n")
            f.write("  - student_02: Exact copy with variable renaming and comments\n")
            f.write("  - student_03: 2-source mosaic\n")
            f.write("  - student_04: 3-source mosaic\n")
            f.write("- **Legitimate submissions:** 16 (students 05-20)\n")
            f.write("  - Diverse implementations: string multiplication, OOP, recursion, generators, etc.\n\n")

            f.write(f"### Overall Performance\n\n")
            f.write(
                f"The CodeGuard system was evaluated on {len(self.test_cases)} test pairs "
                f"and achieved the following metrics:\n\n"
            )

            f.write("| Metric | Value | Target | Status |\n")
            f.write("|--------|-------|--------|--------|\n")
            f.write(
                f"| Precision | {voting_metrics['precision']:.2%} | >=85% | "
                f"{'ACHIEVED' if voting_metrics['precision'] >= 0.85 else 'NOT MET'} |\n"
            )
            f.write(
                f"| Recall | {voting_metrics['recall']:.2%} | >=80% | "
                f"{'ACHIEVED' if voting_metrics['recall'] >= 0.80 else 'NOT MET'} |\n"
            )
            f.write(
                f"| F1 Score | {voting_metrics['f1_score']:.2%} | >=82% | "
                f"{'ACHIEVED' if voting_metrics['f1_score'] >= 0.82 else 'NOT MET'} |\n"
            )
            f.write(f"| Accuracy | {voting_metrics['accuracy']:.2%} | - | - |\n\n")

            # Methodology
            f.write("## Methodology\n\n")
            f.write("### Test Scenario\n\n")
            f.write(
                "This test simulates a realistic classroom plagiarism scenario:\n\n"
            )
            f.write("**Plagiarism Cases:**\n")
            f.write("1. **Exact Copy with Obfuscation:** student_02 copied student_01 and renamed variables\n")
            f.write("2. **2-Source Mosaic:** student_03 combined code from two sources\n")
            f.write("3. **3-Source Mosaic:** student_04 combined code from three sources\n")
            f.write("4. **Cross-comparisons:** All plagiarized files compared against each other\n\n")

            f.write("**Legitimate Cases:**\n")
            f.write(
                "- 16 independent implementations using diverse approaches\n"
                "- String multiplication, dictionary lookup, OOP, recursion, generators, etc.\n"
                "- Representative pairwise comparisons to test false positive rate\n\n"
            )

            f.write("### Detection Pipeline\n\n")
            f.write("Each file pair is analyzed through:\n\n")
            f.write("1. **Token Detector:** Lexical similarity (Jaccard + Cosine)\n")
            f.write("2. **AST Detector:** Structural similarity (normalized AST)\n")
            f.write("3. **Hash Detector:** Fingerprinting (Winnowing algorithm)\n")
            f.write("4. **Voting System:** Weighted ensemble decision\n\n")

            f.write("**Voting Configuration:**\n\n")
            f.write("| Detector | Threshold | Weight | Rationale |\n")
            f.write("|----------|-----------|--------|----------|\n")
            f.write("| Token    | 0.70      | 1.0x   | Fast baseline, easily defeated |\n")
            f.write("| AST      | 0.80      | 2.0x   | Most reliable, structure-based |\n")
            f.write("| Hash     | 0.60      | 1.5x   | Detects partial copying |\n\n")

            # Results Table
            f.write("## Results\n\n")
            f.write("### Detector Performance\n\n")
            f.write(
                "| Detector | TP | FP | TN | FN | Precision | Recall | F1 Score | Accuracy |\n"
            )
            f.write(
                "|----------|----|----|----|----|-----------| -------|----------|----------|\n"
            )

            for detector_name in ["token", "ast", "hash", "voting"]:
                metrics = self.calculate_metrics(detector_name)
                detector_display = (
                    detector_name.upper() if detector_name != "voting" else "VOTING"
                )

                f.write(
                    f"| {detector_display:<8} | "
                    f"{metrics['TP']:<2} | "
                    f"{metrics['FP']:<2} | "
                    f"{metrics['TN']:<2} | "
                    f"{metrics['FN']:<2} | "
                    f"{metrics['precision']:>8.2%} | "
                    f"{metrics['recall']:>6.2%} | "
                    f"{metrics['f1_score']:>8.2%} | "
                    f"{metrics['accuracy']:>8.2%} |\n"
                )

            f.write("\n")

            # Detailed Results by Category
            f.write("### Detailed Test Results\n\n")

            # Plagiarism cases
            f.write("#### Plagiarism Detection (True Positives)\n\n")
            f.write("| File Pair | Description | Token | AST | Hash | Vote | Conf | Result |\n")
            f.write("|-----------|-------------|-------|-----|------|------|------|--------|\n")

            for case in self.test_cases:
                if case["expected"]:  # Plagiarism cases
                    file1_name = Path(case["file1"]).stem
                    file2_name = Path(case["file2"]).stem
                    desc_short = case["description"][:40] + "..." if len(case["description"]) > 40 else case["description"]

                    token_mark = "PASS" if case["decisions"]["token"] else "FAIL"
                    ast_mark = "PASS" if case["decisions"]["ast"] else "FAIL"
                    hash_mark = "PASS" if case["decisions"]["hash"] else "FAIL"
                    voting_mark = "PASS" if case["decisions"]["voting"] else "FAIL"

                    f.write(
                        f"| {file1_name} vs {file2_name} | {desc_short} | "
                        f"{token_mark} | {ast_mark} | {hash_mark} | "
                        f"{voting_mark} | {case['voting_confidence']:.2f} | "
                        f"{'CORRECT' if case['correct'] else 'MISSED'} |\n"
                    )

            f.write("\n")

            # Legitimate cases
            f.write("#### Legitimate Code (True Negatives)\n\n")
            f.write("| File Pair | Description | Token | AST | Hash | Vote | Conf | Result |\n")
            f.write("|-----------|-------------|-------|-----|------|------|------|--------|\n")

            for case in self.test_cases:
                if not case["expected"]:  # Legitimate cases
                    file1_name = Path(case["file1"]).stem
                    file2_name = Path(case["file2"]).stem
                    desc_short = case["description"][:40] + "..." if len(case["description"]) > 40 else case["description"]

                    token_mark = "PASS" if not case["decisions"]["token"] else "FAIL"
                    ast_mark = "PASS" if not case["decisions"]["ast"] else "FAIL"
                    hash_mark = "PASS" if not case["decisions"]["hash"] else "FAIL"
                    voting_mark = "PASS" if not case["decisions"]["voting"] else "FAIL"

                    f.write(
                        f"| {file1_name} vs {file2_name} | {desc_short} | "
                        f"{token_mark} | {ast_mark} | {hash_mark} | "
                        f"{voting_mark} | {case['voting_confidence']:.2f} | "
                        f"{'CORRECT' if case['correct'] else 'FALSE POS'} |\n"
                    )

            f.write("\n")

            # Analysis
            f.write("## Analysis\n\n")

            f.write("### Detector-by-Detector Performance\n\n")

            token_metrics = self.calculate_metrics("token")
            ast_metrics = self.calculate_metrics("ast")
            hash_metrics = self.calculate_metrics("hash")

            f.write("#### Token Detector\n\n")
            f.write(
                f"- **Precision:** {token_metrics['precision']:.2%}\n"
                f"- **Recall:** {token_metrics['recall']:.2%}\n"
                f"- **F1 Score:** {token_metrics['f1_score']:.2%}\n\n"
            )
            f.write("**Strengths:**\n")
            f.write("- Fast execution\n")
            f.write("- Good at detecting exact or near-exact copies\n\n")
            f.write("**Weaknesses:**\n")
            f.write("- Easily defeated by variable renaming and comment additions\n")
            f.write("- Cannot handle structural transformations\n\n")

            f.write("#### AST Detector\n\n")
            f.write(
                f"- **Precision:** {ast_metrics['precision']:.2%}\n"
                f"- **Recall:** {ast_metrics['recall']:.2%}\n"
                f"- **F1 Score:** {ast_metrics['f1_score']:.2%}\n\n"
            )
            f.write("**Strengths:**\n")
            f.write("- Immune to variable renaming and comment changes\n")
            f.write("- Detects structural similarity effectively\n")
            f.write("- Most reliable detector (2.0x weight justified)\n\n")
            f.write("**Weaknesses:**\n")
            f.write("- Cannot detect if fundamental algorithm is different\n")
            f.write("- More computationally expensive\n\n")

            f.write("#### Hash Detector\n\n")
            f.write(
                f"- **Precision:** {hash_metrics['precision']:.2%}\n"
                f"- **Recall:** {hash_metrics['recall']:.2%}\n"
                f"- **F1 Score:** {hash_metrics['f1_score']:.2%}\n\n"
            )
            f.write("**Strengths:**\n")
            f.write("- Detects partial and scattered plagiarism\n")
            f.write("- Good at finding mosaic plagiarism\n\n")
            f.write("**Weaknesses:**\n")
            f.write("- May produce false positives on common code patterns\n")
            f.write("- Threshold tuning is critical\n\n")

            f.write("#### Voting System\n\n")
            f.write(
                f"- **Precision:** {voting_metrics['precision']:.2%}\n"
                f"- **Recall:** {voting_metrics['recall']:.2%}\n"
                f"- **F1 Score:** {voting_metrics['f1_score']:.2%}\n\n"
            )
            f.write("**Strengths:**\n")
            f.write("- Balances individual detector weaknesses\n")
            f.write("- Provides robust decision-making through ensemble\n")
            f.write("- AST's 2.0x weight ensures structural similarity is prioritized\n\n")

            # Comparison with previous results
            f.write("### Comparison with Validation Dataset\n\n")
            f.write(
                "The FizzBuzz dataset represents a more challenging and realistic "
                "test scenario compared to the validation-datasets:\n\n"
            )
            f.write("**Validation Dataset Results (Session 5):**\n")
            f.write("- Precision: ~100%\n")
            f.write("- Recall: ~100%\n")
            f.write("- Simpler test cases with clear plagiarism/legitimate distinction\n\n")

            f.write("**FizzBuzz Dataset Results (Current):**\n")
            f.write(f"- Precision: {voting_metrics['precision']:.2%}\n")
            f.write(f"- Recall: {voting_metrics['recall']:.2%}\n")
            f.write("- More challenging: mosaic plagiarism, diverse implementations\n")
            f.write("- Closer to real-world classroom scenario\n\n")

            # Insights
            f.write("### Key Insights\n\n")

            f.write("1. **Obfuscation Detection:**\n")
            f.write("   - AST detector successfully catches simple variable renaming\n")
            f.write("   - student_01 vs student_02 should be detected with high confidence\n\n")

            f.write("2. **Mosaic Plagiarism:**\n")
            f.write("   - Multi-source mosaics (student_03, student_04) are more challenging\n")
            f.write("   - Hash detector plays crucial role in detecting scattered copying\n\n")

            f.write("3. **False Positive Prevention:**\n")
            f.write("   - Diverse legitimate implementations should score low\n")
            f.write("   - Different paradigms (OOP vs functional) clearly distinguishable\n\n")

            f.write("4. **Edge Cases:**\n")
            f.write("   - Plagiarized vs legitimate comparisons test boundary detection\n")
            f.write("   - System should correctly distinguish structural vs superficial similarity\n\n")

            # Conclusion
            f.write("## Conclusion\n\n")

            target_met = (
                voting_metrics["precision"] >= 0.85
                and voting_metrics["recall"] >= 0.80
                and voting_metrics["f1_score"] >= 0.82
            )

            if target_met:
                f.write(
                    "The CodeGuard plagiarism detection system **successfully meets** all "
                    "target metrics on the FizzBuzz dataset:\n\n"
                )
                f.write(
                    f"- Precision: {voting_metrics['precision']:.2%} (Target: >=85%) ACHIEVED\n"
                    f"- Recall: {voting_metrics['recall']:.2%} (Target: >=80%) ACHIEVED\n"
                    f"- F1 Score: {voting_metrics['f1_score']:.2%} (Target: >=82%) ACHIEVED\n\n"
                )
                f.write(
                    "The system demonstrates robust performance in a realistic classroom "
                    "scenario with diverse implementations and sophisticated plagiarism "
                    "techniques including mosaic plagiarism.\n\n"
                )
                f.write(
                    "**Recommendation:** The system is ready for academic deployment.\n\n"
                )
            else:
                f.write(
                    "The CodeGuard system's performance on the FizzBuzz dataset:\n\n"
                )
                f.write(
                    f"- Precision: {voting_metrics['precision']:.2%} (Target: >=85%) "
                    f"{'ACHIEVED' if voting_metrics['precision'] >= 0.85 else 'NOT MET'}\n"
                )
                f.write(
                    f"- Recall: {voting_metrics['recall']:.2%} (Target: >=80%) "
                    f"{'ACHIEVED' if voting_metrics['recall'] >= 0.80 else 'NOT MET'}\n"
                )
                f.write(
                    f"- F1 Score: {voting_metrics['f1_score']:.2%} (Target: >=82%) "
                    f"{'ACHIEVED' if voting_metrics['f1_score'] >= 0.82 else 'NOT MET'}\n\n"
                )

                f.write("### Recommendations\n\n")

                if voting_metrics["precision"] < 0.85:
                    f.write("**Improve Precision (Reduce False Positives):**\n")
                    f.write("- Increase detection thresholds\n")
                    f.write("- Adjust voting decision threshold upward\n")
                    f.write("- Review false positive cases for common patterns\n\n")

                if voting_metrics["recall"] < 0.80:
                    f.write("**Improve Recall (Reduce False Negatives):**\n")
                    f.write("- Lower detection thresholds, especially for Hash detector\n")
                    f.write("- Adjust voting decision threshold downward\n")
                    f.write("- Consider additional detection methods for mosaic plagiarism\n\n")

                f.write("**General Improvements:**\n")
                f.write("- Expand training data with more mosaic plagiarism examples\n")
                f.write("- Fine-tune detector weights based on observed patterns\n")
                f.write("- Consider confidence score thresholds for borderline cases\n\n")

            # Appendix
            f.write("## Appendix\n\n")

            f.write("### All Test Pairs\n\n")
            f.write("**Plagiarism Cases:**\n")
            for case in self.test_cases:
                if case["expected"]:
                    f.write(
                        f"- {Path(case['file1']).name} vs {Path(case['file2']).name}: "
                        f"{case['description']}\n"
                    )

            f.write("\n**Legitimate Cases:**\n")
            for case in self.test_cases:
                if not case["expected"]:
                    f.write(
                        f"- {Path(case['file1']).name} vs {Path(case['file2']).name}: "
                        f"{case['description']}\n"
                    )

            f.write("\n### Configuration\n\n")
            f.write("```json\n")
            f.write(json.dumps(self.voting_system.config, indent=2))
            f.write("\n```\n")

        print(f"\nReport saved to: {output_path}")


def main():
    """
    Main entry point for FizzBuzz effectiveness test.
    """
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    fizzbuzz_dir = project_root / "test_files" / "FizzBuzzProblem"
    docs_dir = project_root / "docs"

    # Validate FizzBuzz directory exists
    if not fizzbuzz_dir.exists():
        print(f"ERROR: FizzBuzz directory not found: {fizzbuzz_dir}")
        sys.exit(1)

    # Ensure docs directory exists
    docs_dir.mkdir(exist_ok=True)

    # Create effectiveness test instance
    print("Initializing FizzBuzz Effectiveness Test...")
    test = FizzBuzzEffectivenessTest(fizzbuzz_dir)

    # Run validation
    test.run_validation()

    # Print results
    test.print_results()

    # Save report
    report_path = docs_dir / "FIZZBUZZ_TEST_REPORT.md"
    test.save_report(report_path)

    print(f"\nEffectiveness test complete!")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
