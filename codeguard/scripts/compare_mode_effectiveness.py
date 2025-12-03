"""
Compare Simple Mode vs Standard Mode effectiveness on validation datasets.

This script evaluates the accuracy improvements of Simple Mode over Standard Mode
by testing both configurations on the validation datasets and measuring:
- True Positives (TP): Correctly identified plagiarism cases
- False Positives (FP): Legitimate code incorrectly flagged as plagiarism
- True Negatives (TN): Correctly identified legitimate code
- False Negatives (FN): Missed plagiarism cases
- Precision: TP / (TP + FP) - How many flagged cases are actually plagiarism?
- Recall: TP / (TP + FN) - How many plagiarism cases did we catch?
- F1 Score: Harmonic mean of precision and recall
- Accuracy: (TP + TN) / (TP + TN + FP + FN) - Overall correctness

The script works with the existing validation-datasets structure:
- plagiarized/: Known plagiarism pairs (should detect)
- legitimate/: Different implementations (should not detect)

Usage:
    python scripts/compare_mode_effectiveness.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem
from src.core import get_preset_config


def load_file(filepath: Path) -> str:
    """
    Load file contents.

    Args:
        filepath: Path to file to load

    Returns:
        File contents as string
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def count_lines(code: str) -> int:
    """
    Count lines of code (non-empty, non-comment).

    Args:
        code: Source code string

    Returns:
        Number of lines
    """
    lines = code.strip().split('\n')
    return len([line for line in lines if line.strip() and not line.strip().startswith('#')])


def run_comparison(file1_path: Path, file2_path: Path, config: dict) -> dict:
    """
    Run detection pipeline with given config.

    Args:
        file1_path: Path to first file
        file2_path: Path to second file
        config: Configuration dictionary for VotingSystem

    Returns:
        Dictionary with detection results
    """
    # Load files
    code1 = load_file(file1_path)
    code2 = load_file(file2_path)

    # Initialize detectors
    token_detector = TokenDetector()
    ast_detector = ASTDetector()
    hash_detector = HashDetector()

    # Run detectors (they return float scores directly)
    token_score = token_detector.compare(code1, code2)
    ast_score = ast_detector.compare(code1, code2)

    # Conditionally run hash detector
    if config['hash']['weight'] > 0:
        hash_score = hash_detector.compare(code1, code2)
    else:
        hash_score = 0.0

    # Voting
    voting_system = VotingSystem(config)
    result = voting_system.vote(token_score, ast_score, hash_score)

    return {
        'is_plagiarism': result['is_plagiarized'],
        'confidence': result['confidence_score'],
        'token_score': token_score,
        'ast_score': ast_score,
        'hash_score': hash_score,
        'votes': result['total_votes_cast'],
        'total_votes': result['total_possible_votes']
    }


def identify_plagiarism_pairs(plagiarized_dir: Path) -> List[Tuple[str, str, str]]:
    """
    Identify plagiarism pairs from the plagiarized directory.

    Expects naming conventions like:
    - *_original.py and *_copied.py
    - *_original.py and *_renamed.py
    - *_original.py and *_reordered.py

    Args:
        plagiarized_dir: Path to plagiarized directory

    Returns:
        List of (file1_name, file2_name, type) tuples
    """
    files = sorted(plagiarized_dir.glob("*.py"))
    pairs = []

    # Build a mapping of base names to files
    file_map = {}
    for f in files:
        name = f.name

        # Extract base name (remove suffixes like _original, _copied, etc.)
        if '_original.py' in name:
            base = name.replace('_original.py', '')
            if base not in file_map:
                file_map[base] = {}
            file_map[base]['original'] = name
        elif '_copied.py' in name:
            base = name.replace('_copied.py', '')
            if base not in file_map:
                file_map[base] = {}
            file_map[base]['copied'] = name
        elif '_renamed.py' in name:
            base = name.replace('_renamed.py', '')
            if base not in file_map:
                file_map[base] = {}
            file_map[base]['renamed'] = name
        elif '_reordered.py' in name:
            base = name.replace('_reordered.py', '')
            if base not in file_map:
                file_map[base] = {}
            file_map[base]['reordered'] = name

    # Create pairs from the mapping
    for base, versions in file_map.items():
        if 'original' in versions:
            original = versions['original']

            if 'copied' in versions:
                pairs.append((original, versions['copied'], 'exact_copy'))
            if 'renamed' in versions:
                pairs.append((original, versions['renamed'], 'renamed'))
            if 'reordered' in versions:
                pairs.append((original, versions['reordered'], 'reordered'))

    return pairs


def evaluate_dataset(
    plagiarized_dir: Path,
    legitimate_dir: Path,
    preset_name: str,
    config: dict
) -> dict:
    """
    Evaluate a dataset with a specific preset configuration.

    Args:
        plagiarized_dir: Path to plagiarized files directory
        legitimate_dir: Path to legitimate files directory
        preset_name: Name of the preset being tested
        config: Configuration dictionary for VotingSystem

    Returns:
        Dictionary with TP, FP, TN, FN, precision, recall, F1, accuracy
    """
    # Identify plagiarism pairs
    plagiarism_pairs = identify_plagiarism_pairs(plagiarized_dir)

    # Get legitimate files (all are different implementations)
    legitimate_files = sorted(legitimate_dir.glob("*.py"))

    # Track results
    results = {
        'TP': 0,  # True Positives
        'FP': 0,  # False Positives
        'TN': 0,  # True Negatives
        'FN': 0,  # False Negatives
        'details': []
    }

    print(f"\n  Evaluating plagiarism pairs...")
    # Test plagiarism pairs (should detect)
    for file1_name, file2_name, plag_type in plagiarism_pairs:
        file1_path = plagiarized_dir / file1_name
        file2_path = plagiarized_dir / file2_name

        # Run detection
        result = run_comparison(file1_path, file2_path, config)

        is_detected = result['is_plagiarism']

        if is_detected:
            results['TP'] += 1
            classification = 'TP'
        else:
            results['FN'] += 1
            classification = 'FN'

        # Store details
        results['details'].append({
            'file1': file1_name,
            'file2': file2_name,
            'expected': 'PLAGIARISM',
            'detected': 'PLAGIARISM' if is_detected else 'LEGITIMATE',
            'classification': classification,
            'type': plag_type,
            'confidence': result['confidence'],
            'votes': result['votes'],
            'total_votes': result['total_votes'],
            'token_score': result['token_score'],
            'ast_score': result['ast_score'],
            'hash_score': result['hash_score']
        })

    print(f"  Testing legitimate pairs...")
    # Test legitimate pairs (should NOT detect)
    # Compare each legitimate file against all others
    for i, file1 in enumerate(legitimate_files):
        for file2 in legitimate_files[i+1:]:
            # Run detection
            result = run_comparison(file1, file2, config)

            is_detected = result['is_plagiarism']

            if is_detected:
                results['FP'] += 1
                classification = 'FP'
            else:
                results['TN'] += 1
                classification = 'TN'

            # Store details
            results['details'].append({
                'file1': file1.name,
                'file2': file2.name,
                'expected': 'LEGITIMATE',
                'detected': 'PLAGIARISM' if is_detected else 'LEGITIMATE',
                'classification': classification,
                'type': 'different_implementations',
                'confidence': result['confidence'],
                'votes': result['votes'],
                'total_votes': result['total_votes'],
                'token_score': result['token_score'],
                'ast_score': result['ast_score'],
                'hash_score': result['hash_score']
            })

    # Calculate metrics
    tp = results['TP']
    fp = results['FP']
    tn = results['TN']
    fn = results['FN']

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0

    results['metrics'] = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'accuracy': accuracy
    }

    return results


def generate_report(
    standard_results: dict,
    simple_results: dict,
    dataset_name: str
) -> str:
    """
    Generate markdown comparison report.

    Args:
        standard_results: Results from Standard Mode
        simple_results: Results from Simple Mode
        dataset_name: Name of the dataset being evaluated

    Returns:
        Markdown formatted report string
    """

    # Calculate improvements
    fp_improvement = standard_results['FP'] - simple_results['FP']
    precision_improvement = simple_results['metrics']['precision'] - standard_results['metrics']['precision']
    accuracy_improvement = simple_results['metrics']['accuracy'] - standard_results['metrics']['accuracy']
    recall_change = simple_results['metrics']['recall'] - standard_results['metrics']['recall']

    report = f"""# Mode Effectiveness Comparison Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dataset:** {dataset_name}

## Executive Summary

This report compares the effectiveness of **Standard Mode** vs **Simple Mode** on the validation datasets.
The goal is to measure accuracy improvements and identify which mode is best suited for different types of code.

---

## Dataset: {dataset_name}

### Standard Mode (All 3 Detectors)
- **True Positives:** {standard_results['TP']} (correctly identified plagiarism)
- **False Positives:** {standard_results['FP']} (legitimate code flagged as plagiarism)
- **True Negatives:** {standard_results['TN']} (correctly identified legitimate code)
- **False Negatives:** {standard_results['FN']} (missed plagiarism)
- **Precision:** {standard_results['metrics']['precision']:.2%}
- **Recall:** {standard_results['metrics']['recall']:.2%}
- **F1 Score:** {standard_results['metrics']['f1_score']:.2%}
- **Accuracy:** {standard_results['metrics']['accuracy']:.2%}

### Simple Mode (Token + AST Only)
- **True Positives:** {simple_results['TP']} (correctly identified plagiarism)
- **False Positives:** {simple_results['FP']} (legitimate code flagged as plagiarism)
- **True Negatives:** {simple_results['TN']} (correctly identified legitimate code)
- **False Negatives:** {simple_results['FN']} (missed plagiarism)
- **Precision:** {simple_results['metrics']['precision']:.2%}
- **Recall:** {simple_results['metrics']['recall']:.2%}
- **F1 Score:** {simple_results['metrics']['f1_score']:.2%}
- **Accuracy:** {simple_results['metrics']['accuracy']:.2%}

### Comparison Summary

| Metric | Standard Mode | Simple Mode | Improvement |
|--------|---------------|-------------|-------------|
| Precision | {standard_results['metrics']['precision']:.2%} | {simple_results['metrics']['precision']:.2%} | {precision_improvement:+.2%} |
| Recall | {standard_results['metrics']['recall']:.2%} | {simple_results['metrics']['recall']:.2%} | {recall_change:+.2%} |
| F1 Score | {standard_results['metrics']['f1_score']:.2%} | {simple_results['metrics']['f1_score']:.2%} | {simple_results['metrics']['f1_score'] - standard_results['metrics']['f1_score']:+.2%} |
| Accuracy | {standard_results['metrics']['accuracy']:.2%} | {simple_results['metrics']['accuracy']:.2%} | {accuracy_improvement:+.2%} |
| False Positives | {standard_results['FP']} | {simple_results['FP']} | {fp_improvement:+d} |
| False Negatives | {standard_results['FN']} | {simple_results['FN']} | {standard_results['FN'] - simple_results['FN']:+d} |

---

## Detailed Analysis

### False Positives Analysis

**Standard Mode False Positives ({standard_results['FP']}):**
"""

    # Add false positive details for Standard mode
    for detail in standard_results['details']:
        if detail['classification'] == 'FP':
            report += f"\n- **{detail['file1']}** vs **{detail['file2']}**\n"
            report += f"  - Confidence: {detail['confidence']:.2%}\n"
            report += f"  - Votes: {detail['votes']:.2f}/{detail['total_votes']:.2f}\n"
            report += f"  - Token: {detail['token_score']:.2%}, AST: {detail['ast_score']:.2%}, Hash: {detail['hash_score']:.2%}\n"

    if standard_results['FP'] == 0:
        report += "\nNone - Perfect precision!\n"

    report += f"\n**Simple Mode False Positives ({simple_results['FP']}):**\n"

    # Add false positive details for Simple mode
    for detail in simple_results['details']:
        if detail['classification'] == 'FP':
            report += f"\n- **{detail['file1']}** vs **{detail['file2']}**\n"
            report += f"  - Confidence: {detail['confidence']:.2%}\n"
            report += f"  - Votes: {detail['votes']:.2f}/{detail['total_votes']:.2f}\n"
            report += f"  - Token: {detail['token_score']:.2%}, AST: {detail['ast_score']:.2%}, Hash: {detail['hash_score']:.2%}\n"

    if simple_results['FP'] == 0:
        report += "\nNone - Perfect precision!\n"

    report += "\n### False Negatives Analysis\n\n"
    report += f"**Standard Mode False Negatives ({standard_results['FN']}):**\n"

    # Add false negative details for Standard mode
    for detail in standard_results['details']:
        if detail['classification'] == 'FN':
            report += f"\n- **{detail['file1']}** vs **{detail['file2']}** ({detail['type']})\n"
            report += f"  - Confidence: {detail['confidence']:.2%}\n"
            report += f"  - Votes: {detail['votes']:.2f}/{detail['total_votes']:.2f}\n"
            report += f"  - Token: {detail['token_score']:.2%}, AST: {detail['ast_score']:.2%}, Hash: {detail['hash_score']:.2%}\n"

    if standard_results['FN'] == 0:
        report += "\nNone - Perfect recall!\n"

    report += f"\n**Simple Mode False Negatives ({simple_results['FN']}):**\n"

    # Add false negative details for Simple mode
    for detail in simple_results['details']:
        if detail['classification'] == 'FN':
            report += f"\n- **{detail['file1']}** vs **{detail['file2']}** ({detail['type']})\n"
            report += f"  - Confidence: {detail['confidence']:.2%}\n"
            report += f"  - Votes: {detail['votes']:.2f}/{detail['total_votes']:.2f}\n"
            report += f"  - Token: {detail['token_score']:.2%}, AST: {detail['ast_score']:.2%}, Hash: {detail['hash_score']:.2%}\n"

    if simple_results['FN'] == 0:
        report += "\nNone - Perfect recall!\n"

    report += "\n---\n\n## Conclusion\n\n"

    # Generate conclusion based on results
    if precision_improvement > 0:
        report += f"Simple Mode shows **{precision_improvement:.2%} improvement in precision** over Standard Mode.\n"
    elif precision_improvement < 0:
        report += f"Standard Mode shows **{abs(precision_improvement):.2%} better precision** than Simple Mode.\n"
    else:
        report += "Both modes achieve **equal precision**.\n"

    report += "\n"

    if recall_change > 0:
        report += f"Simple Mode shows **{recall_change:.2%} improvement in recall** over Standard Mode.\n"
    elif recall_change < 0:
        report += f"Standard Mode shows **{abs(recall_change):.2%} better recall** than Simple Mode.\n"
    else:
        report += "Both modes achieve **equal recall**.\n"

    report += "\n"

    if fp_improvement > 0:
        report += f"Simple Mode **reduces false positives by {fp_improvement}** compared to Standard Mode.\n"
    elif fp_improvement < 0:
        report += f"Standard Mode **reduces false positives by {abs(fp_improvement)}** compared to Simple Mode.\n"
    else:
        report += "Both modes generate **equal false positives**.\n"

    report += "\n### Recommendations\n\n"

    # Provide recommendations based on dataset characteristics
    if simple_results['metrics']['precision'] > standard_results['metrics']['precision']:
        report += "- **Use Simple Mode** for this type of code to reduce false positives\n"
    else:
        report += "- **Use Standard Mode** for this type of code for better precision\n"

    if simple_results['metrics']['recall'] > standard_results['metrics']['recall']:
        report += "- Simple Mode catches more plagiarism cases (higher recall)\n"
    elif standard_results['metrics']['recall'] > simple_results['metrics']['recall']:
        report += "- Standard Mode catches more plagiarism cases (higher recall)\n"

    if simple_results['metrics']['f1_score'] > standard_results['metrics']['f1_score']:
        report += "- **Simple Mode provides better overall balance** (higher F1 score)\n"
    else:
        report += "- **Standard Mode provides better overall balance** (higher F1 score)\n"

    report += "\n---\n\n"
    report += "## Configuration Details\n\n"
    report += "### Standard Mode\n"
    report += "- Token: threshold=0.70, weight=1.0\n"
    report += "- AST: threshold=0.80, weight=2.0\n"
    report += "- Hash: threshold=0.60, weight=1.5\n"
    report += "- Decision threshold: 50% (2.25/4.5 votes required)\n\n"

    report += "### Simple Mode\n"
    report += "- Token: threshold=0.70, weight=2.0\n"
    report += "- AST: threshold=0.85, weight=2.0\n"
    report += "- Hash: threshold=0.60, weight=0.0 (DISABLED)\n"
    report += "- Decision threshold: 75% (3.0/4.0 votes required)\n"

    return report


def main():
    """Main execution."""
    print("=" * 80)
    print("MODE EFFECTIVENESS COMPARISON TEST")
    print("=" * 80)
    print()

    # Paths
    project_root = Path(__file__).parent.parent
    validation_dir = project_root / "validation-datasets"
    plagiarized_dir = validation_dir / "plagiarized"
    legitimate_dir = validation_dir / "legitimate"

    # Check paths exist
    if not plagiarized_dir.exists():
        print(f"ERROR: Plagiarized dataset not found: {plagiarized_dir}")
        return 1
    if not legitimate_dir.exists():
        print(f"ERROR: Legitimate dataset not found: {legitimate_dir}")
        return 1

    # Load configs
    print("Loading preset configurations...")
    standard_config = get_preset_config("standard")
    simple_config = get_preset_config("simple")
    print(f"  Standard Mode: {standard_config['decision_threshold']:.0%} threshold")
    print(f"  Simple Mode: {simple_config['decision_threshold']:.0%} threshold")
    print()

    # Test with validation datasets
    print("Testing validation datasets...")
    print("-" * 80)

    # Standard Mode
    print("\nRunning Standard Mode evaluation...")
    standard_results = evaluate_dataset(
        plagiarized_dir, legitimate_dir,
        "standard", standard_config
    )

    # Simple Mode
    print("\nRunning Simple Mode evaluation...")
    simple_results = evaluate_dataset(
        plagiarized_dir, legitimate_dir,
        "simple", simple_config
    )

    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Print summary
    print("Validation Dataset Results:")
    print(f"  Standard Mode:")
    print(f"    Precision: {standard_results['metrics']['precision']:.2%}")
    print(f"    Recall:    {standard_results['metrics']['recall']:.2%}")
    print(f"    F1 Score:  {standard_results['metrics']['f1_score']:.2%}")
    print(f"    Accuracy:  {standard_results['metrics']['accuracy']:.2%}")
    print(f"    FP: {standard_results['FP']}, FN: {standard_results['FN']}")
    print()

    print(f"  Simple Mode:")
    print(f"    Precision: {simple_results['metrics']['precision']:.2%}")
    print(f"    Recall:    {simple_results['metrics']['recall']:.2%}")
    print(f"    F1 Score:  {simple_results['metrics']['f1_score']:.2%}")
    print(f"    Accuracy:  {simple_results['metrics']['accuracy']:.2%}")
    print(f"    FP: {simple_results['FP']}, FN: {simple_results['FN']}")
    print()

    # Calculate improvements
    fp_improvement = standard_results['FP'] - simple_results['FP']
    precision_improvement = simple_results['metrics']['precision'] - standard_results['metrics']['precision']

    print("Comparison:")
    if fp_improvement > 0:
        print(f"  False Positives: Reduced by {fp_improvement} (Simple Mode better)")
    elif fp_improvement < 0:
        print(f"  False Positives: Increased by {abs(fp_improvement)} (Standard Mode better)")
    else:
        print(f"  False Positives: Equal")

    if precision_improvement > 0:
        print(f"  Precision: Improved by {precision_improvement:.2%} (Simple Mode better)")
    elif precision_improvement < 0:
        print(f"  Precision: Decreased by {abs(precision_improvement):.2%} (Standard Mode better)")
    else:
        print(f"  Precision: Equal")

    print()

    # Generate report
    print("Generating detailed report...")
    report = generate_report(standard_results, simple_results, "Validation Dataset")

    # Save report
    report_path = project_root / "docs" / "MODE_COMPARISON_REPORT.md"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {report_path}")

    # Also save raw results as JSON for further analysis
    results_json = {
        'timestamp': datetime.now().isoformat(),
        'dataset': 'validation-dataset',
        'standard_mode': {
            'metrics': standard_results['metrics'],
            'TP': standard_results['TP'],
            'FP': standard_results['FP'],
            'TN': standard_results['TN'],
            'FN': standard_results['FN'],
            'details': standard_results['details']
        },
        'simple_mode': {
            'metrics': simple_results['metrics'],
            'TP': simple_results['TP'],
            'FP': simple_results['FP'],
            'TN': simple_results['TN'],
            'FN': simple_results['FN'],
            'details': simple_results['details']
        }
    }

    json_path = project_root / "docs" / "mode_comparison_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2)

    print(f"Raw results saved to: {json_path}")
    print()
    print("=" * 80)
    print("DONE!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
