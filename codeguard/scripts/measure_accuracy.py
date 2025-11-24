#!/usr/bin/env python3
"""
Accuracy Measurement Script for CodeGuard Plagiarism Detection System

This script validates the detection system's accuracy by testing against
a curated dataset of known plagiarism cases and legitimate code pairs.

Metrics calculated:
    - Precision: TP / (TP + FP)
    - Recall: TP / (TP + FN)
    - F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
    - Accuracy: (TP + TN) / (TP + TN + FP + FN)

Author: CodeGuard Team
Date: 2024-11-24
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


class AccuracyMeasurement:
    """
    Comprehensive accuracy measurement system for plagiarism detection.

    This class loads validation datasets, runs all detectors, aggregates
    results using the voting system, and calculates performance metrics.
    """

    def __init__(self, validation_dir: Path):
        """
        Initialize the accuracy measurement system.

        Args:
            validation_dir: Path to validation-datasets directory
        """
        self.validation_dir = validation_dir
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

    def load_test_pairs(self) -> List[Tuple[Path, Path, bool]]:
        """
        Load all test file pairs from validation datasets.

        Returns:
            List of tuples: (file1_path, file2_path, expected_plagiarism)
        """
        pairs = []

        # Load plagiarized pairs (True Positives expected)
        plagiarized_dir = self.validation_dir / "plagiarized"
        if plagiarized_dir.exists():
            # Pair up files based on naming convention
            pairs.extend(self._pair_files(plagiarized_dir, expected_result=True))

        # Load legitimate pairs (True Negatives expected)
        legitimate_dir = self.validation_dir / "legitimate"
        if legitimate_dir.exists():
            # Pair consecutive files
            pairs.extend(self._pair_files_consecutive(legitimate_dir, expected_result=False))

        # Load obfuscated pairs (True Positives expected - should detect despite obfuscation)
        obfuscated_dir = self.validation_dir / "obfuscated"
        if obfuscated_dir.exists():
            pairs.extend(self._pair_files(obfuscated_dir, expected_result=True))

        return pairs

    def _pair_files(self, directory: Path, expected_result: bool) -> List[Tuple[Path, Path, bool]]:
        """
        Pair files in a directory based on naming patterns.

        Expects patterns like:
            - name_original.py and name_copied.py
            - name_original.py and name_renamed.py
            - name_original.py and name_obfuscated.py

        Args:
            directory: Directory containing files to pair
            expected_result: Expected plagiarism detection result

        Returns:
            List of file pairs with expected result
        """
        pairs = []
        files = sorted([f for f in directory.glob("*.py") if f.is_file()])

        # Group files by base name
        file_groups = {}
        for file in files:
            # Extract base name (everything before the last underscore)
            parts = file.stem.split("_")
            if len(parts) >= 2:
                base_name = "_".join(parts[:-1])
                if base_name not in file_groups:
                    file_groups[base_name] = []
                file_groups[base_name].append(file)

        # Create pairs from groups
        for base_name, group_files in file_groups.items():
            if len(group_files) == 2:
                pairs.append((group_files[0], group_files[1], expected_result))

        return pairs

    def _pair_files_consecutive(
        self, directory: Path, expected_result: bool
    ) -> List[Tuple[Path, Path, bool]]:
        """
        Pair consecutive files in a directory.

        Used for legitimate code where files are independent implementations
        of different algorithms.

        Args:
            directory: Directory containing files
            expected_result: Expected plagiarism detection result

        Returns:
            List of consecutive file pairs with expected result
        """
        pairs = []
        files = sorted([f for f in directory.glob("*.py") if f.is_file()])

        # Pair consecutive files
        for i in range(len(files) - 1):
            pairs.append((files[i], files[i + 1], expected_result))

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
        with open(file1, "r", encoding="utf-8") as f:
            source1 = f.read()

        with open(file2, "r", encoding="utf-8") as f:
            source2 = f.read()

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
        Run complete validation across all test pairs.
        """
        print("=" * 80)
        print("CodeGuard Plagiarism Detection - Accuracy Validation")
        print("=" * 80)
        print()

        # Load test pairs
        test_pairs = self.load_test_pairs()
        print(f"Loaded {len(test_pairs)} test pairs")
        print()

        # Count expected outcomes
        expected_plagiarism = sum(1 for _, _, is_plag in test_pairs if is_plag)
        expected_legitimate = len(test_pairs) - expected_plagiarism
        print(f"Expected plagiarism cases: {expected_plagiarism}")
        print(f"Expected legitimate cases: {expected_legitimate}")
        print()

        # Run analysis on each pair
        print("Running analysis...")
        print("-" * 80)

        for i, (file1, file2, expected_plagiarism) in enumerate(test_pairs, 1):
            print(f"\n[{i}/{len(test_pairs)}] Analyzing: {file1.name} vs {file2.name}")
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

            # Classify results
            self.classify_result("token", token_detected, expected_plagiarism)
            self.classify_result("ast", ast_detected, expected_plagiarism)
            self.classify_result("hash", hash_detected, expected_plagiarism)
            self.classify_result("voting", voting_detected, expected_plagiarism)

            # Store test case
            self.test_cases.append(
                {
                    "file1": str(file1),
                    "file2": str(file2),
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
        print("ACCURACY METRICS")
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
            f"(Target: >=85%) {'✓' if voting_metrics['precision'] >= 0.85 else '✗'}"
        )
        print(
            f"Recall:    {voting_metrics['recall']:.2%} "
            f"(Target: >=80%) {'✓' if voting_metrics['recall'] >= 0.80 else '✗'}"
        )
        print(
            f"F1 Score:  {voting_metrics['f1_score']:.2%} "
            f"(Target: >=82%) {'✓' if voting_metrics['f1_score'] >= 0.82 else '✗'}"
        )
        print("=" * 80)
        print()

    def save_report(self, output_path: Path) -> None:
        """
        Save comprehensive accuracy report to markdown file.

        Args:
            output_path: Path to save the report
        """
        with open(output_path, "w", encoding="utf-8") as f:
            # Write header
            f.write("# CodeGuard Plagiarism Detection - Accuracy Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            voting_metrics = self.calculate_metrics("voting")
            f.write(
                f"The CodeGuard plagiarism detection system was evaluated against "
                f"{len(self.test_cases)} test cases comprising known plagiarism pairs "
                f"and legitimate code samples. The system achieved the following metrics "
                f"using the weighted voting ensemble:\n\n"
            )
            f.write(f"- **Precision:** {voting_metrics['precision']:.2%}\n")
            f.write(f"- **Recall:** {voting_metrics['recall']:.2%}\n")
            f.write(f"- **F1 Score:** {voting_metrics['f1_score']:.2%}\n")
            f.write(f"- **Accuracy:** {voting_metrics['accuracy']:.2%}\n\n")

            # Methodology
            f.write("## Methodology\n\n")
            f.write("### Test Dataset Composition\n\n")
            f.write("The validation dataset consists of three categories:\n\n")
            f.write(
                "1. **Plagiarized Code Pairs:** Near-identical code with minimal changes "
                "(whitespace, comments, variable names)\n"
            )
            f.write(
                "2. **Legitimate Code Pairs:** Different implementations of different "
                "algorithms (e.g., bubble sort vs merge sort)\n"
            )
            f.write(
                "3. **Obfuscated Code Pairs:** Plagiarized code with deliberate obfuscation "
                "(renamed variables, reordered functions)\n\n"
            )

            f.write("### Detection Pipeline\n\n")
            f.write("Each file pair is analyzed through a three-stage detection pipeline:\n\n")
            f.write(
                "1. **Token Detector:** Lexical analysis using Jaccard and Cosine "
                "similarity on code tokens\n"
            )
            f.write(
                "2. **AST Detector:** Structural analysis using normalized Abstract Syntax "
                "Trees\n"
            )
            f.write(
                "3. **Hash Detector:** Fingerprinting using Winnowing algorithm for "
                "partial match detection\n\n"
            )
            f.write(
                "Results are aggregated using a weighted voting system with the following "
                "configuration:\n\n"
            )
            f.write("| Detector | Threshold | Weight |\n")
            f.write("|----------|-----------|--------|\n")
            f.write("| Token    | 0.70      | 1.0x   |\n")
            f.write("| AST      | 0.80      | 2.0x   |\n")
            f.write("| Hash     | 0.60      | 1.5x   |\n\n")
            f.write(
                "Plagiarism is flagged when weighted votes reach 50% of the total "
                "possible weighted votes (2.25 out of 4.5).\n\n"
            )

            # Results Table
            f.write("## Results\n\n")
            f.write("### Overall Performance Metrics\n\n")
            f.write(
                "| Detector    | TP | FP | TN | FN | Precision | Recall | F1 Score | Accuracy |\n"
            )
            f.write(
                "|-------------|----|----|----|----|-----------| -------|----------|----------|\n"
            )

            for detector_name in ["token", "ast", "hash", "voting"]:
                metrics = self.calculate_metrics(detector_name)
                detector_display = (
                    detector_name.upper() if detector_name != "voting" else "Voting System"
                )

                f.write(
                    f"| {detector_display:<11} | "
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

            # Detailed Results
            f.write("### Detailed Test Case Results\n\n")
            f.write("| File Pair | Expected | Token | AST | Hash | Voting | Result |\n")
            f.write("|-----------|----------|-------|-----|------|--------|--------|\n")

            for case in self.test_cases:
                file1_name = Path(case["file1"]).stem
                file2_name = Path(case["file2"]).stem
                expected = "Plagiarism" if case["expected"] else "Legitimate"
                token_result = "✓" if case["decisions"]["token"] == case["expected"] else "✗"
                ast_result = "✓" if case["decisions"]["ast"] == case["expected"] else "✗"
                hash_result = "✓" if case["decisions"]["hash"] == case["expected"] else "✗"
                voting_result = "✓" if case["decisions"]["voting"] == case["expected"] else "✗"
                overall = "PASS" if case["decisions"]["voting"] == case["expected"] else "FAIL"

                f.write(
                    f"| {file1_name} vs {file2_name} | {expected} | "
                    f"{token_result} | {ast_result} | {hash_result} | "
                    f"{voting_result} | **{overall}** |\n"
                )

            f.write("\n")

            # Analysis
            f.write("## Analysis\n\n")
            f.write("### Detector Performance Comparison\n\n")

            token_metrics = self.calculate_metrics("token")
            ast_metrics = self.calculate_metrics("ast")
            hash_metrics = self.calculate_metrics("hash")

            f.write("**Token Detector:**\n")
            f.write(
                f"- Achieved {token_metrics['precision']:.2%} precision and "
                f"{token_metrics['recall']:.2%} recall\n"
            )
            f.write(
                "- Strengths: Fast execution, good baseline for exact copies\n"
            )
            f.write(
                "- Weaknesses: Easily defeated by variable renaming and structural changes\n\n"
            )

            f.write("**AST Detector:**\n")
            f.write(
                f"- Achieved {ast_metrics['precision']:.2%} precision and "
                f"{ast_metrics['recall']:.2%} recall\n"
            )
            f.write(
                "- Strengths: Immune to variable renaming, detects structural similarity "
                "effectively\n"
            )
            f.write(
                "- Weaknesses: Cannot detect if algorithms are fundamentally different\n\n"
            )

            f.write("**Hash Detector:**\n")
            f.write(
                f"- Achieved {hash_metrics['precision']:.2%} precision and "
                f"{hash_metrics['recall']:.2%} recall\n"
            )
            f.write(
                "- Strengths: Detects partial copying and scattered plagiarism\n"
            )
            f.write(
                "- Weaknesses: May produce false positives on common code patterns\n\n"
            )

            f.write("**Voting System:**\n")
            f.write(
                f"- Achieved {voting_metrics['precision']:.2%} precision and "
                f"{voting_metrics['recall']:.2%} recall\n"
            )
            f.write(
                "- Strengths: Balances individual detector weaknesses, provides robust "
                "decision-making\n"
            )
            f.write(
                "- The 2.0x weight on AST detector reflects its superior reliability for "
                "structural plagiarism\n\n"
            )

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
                    "target metrics for academic deployment:\n\n"
                )
            else:
                f.write(
                    "The CodeGuard plagiarism detection system performance relative to "
                    "target metrics:\n\n"
                )

            f.write(
                f"- Precision: {voting_metrics['precision']:.2%} "
                f"(Target: ≥85%) "
                f"{'✓ ACHIEVED' if voting_metrics['precision'] >= 0.85 else '✗ NOT MET'}\n"
            )
            f.write(
                f"- Recall: {voting_metrics['recall']:.2%} "
                f"(Target: ≥80%) "
                f"{'✓ ACHIEVED' if voting_metrics['recall'] >= 0.80 else '✗ NOT MET'}\n"
            )
            f.write(
                f"- F1 Score: {voting_metrics['f1_score']:.2%} "
                f"(Target: ≥82%) "
                f"{'✓ ACHIEVED' if voting_metrics['f1_score'] >= 0.82 else '✗ NOT MET'}\n\n"
            )

            if target_met:
                f.write(
                    "The system demonstrates high accuracy in distinguishing between "
                    "plagiarized and legitimate code submissions. The weighted voting "
                    "ensemble effectively combines the strengths of lexical, structural, "
                    "and fingerprint-based detection methods.\n\n"
                )
            else:
                f.write("### Recommendations\n\n")
                if voting_metrics["precision"] < 0.85:
                    f.write(
                        "- **Improve Precision:** Increase detection thresholds or adjust "
                        "voting weights to reduce false positives\n"
                    )
                if voting_metrics["recall"] < 0.80:
                    f.write(
                        "- **Improve Recall:** Lower detection thresholds or add more "
                        "sophisticated detection methods to catch more plagiarism cases\n"
                    )
                f.write(
                    "- Expand validation dataset with more edge cases\n"
                )
                f.write(
                    "- Consider tuning individual detector thresholds based on observed "
                    "false positive/negative patterns\n\n"
                )

            # Appendix
            f.write("## Appendix\n\n")
            f.write("### Test Dataset Files\n\n")
            f.write("**Plagiarized Pairs:**\n")
            for case in self.test_cases:
                if case["expected"]:
                    f.write(f"- {Path(case['file1']).name} vs {Path(case['file2']).name}\n")

            f.write("\n**Legitimate Pairs:**\n")
            for case in self.test_cases:
                if not case["expected"]:
                    f.write(f"- {Path(case['file1']).name} vs {Path(case['file2']).name}\n")

            f.write("\n### Configuration\n\n")
            f.write("```json\n")
            f.write(json.dumps(self.voting_system.config, indent=2))
            f.write("\n```\n")

        print(f"Report saved to: {output_path}")


def main():
    """
    Main entry point for accuracy measurement script.
    """
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    validation_dir = project_root / "validation-datasets"
    docs_dir = project_root / "docs"

    # Ensure docs directory exists
    docs_dir.mkdir(exist_ok=True)

    # Create accuracy measurement instance
    measurement = AccuracyMeasurement(validation_dir)

    # Run validation
    measurement.run_validation()

    # Print results
    measurement.print_results()

    # Save report
    report_path = docs_dir / "ACCURACY_REPORT.md"
    measurement.save_report(report_path)

    print(f"\nValidation complete! Report saved to: {report_path}")


if __name__ == "__main__":
    main()
