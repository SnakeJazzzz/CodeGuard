#!/usr/bin/env python3
"""
Quick Mode Comparison Summary Printer

Prints a concise summary of mode comparison results to terminal.
"""

import csv
from pathlib import Path
from typing import Dict, List


def load_metrics(csv_path: Path) -> List[Dict]:
    """Load metrics from CSV file"""
    metrics = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['tp'] = int(row['tp'])
            row['fp'] = int(row['fp'])
            row['tn'] = int(row['tn'])
            row['fn'] = int(row['fn'])
            row['precision'] = float(row['precision'])
            row['recall'] = float(row['recall'])
            row['f1'] = float(row['f1'])
            row['accuracy'] = float(row['accuracy'])
            metrics.append(row)
    return metrics


def print_summary(metrics: List[Dict]):
    """Print formatted summary"""
    print("\n" + "="*80)
    print("CodeGuard Mode Effectiveness Comparison - Quick Summary")
    print("="*80)

    # Calculate overall averages
    simple_metrics = [m for m in metrics if m['mode'] == 'SIMPLE']
    standard_metrics = [m for m in metrics if m['mode'] == 'STANDARD']

    simple_avg_f1 = sum(m['f1'] for m in simple_metrics) / len(simple_metrics)
    standard_avg_f1 = sum(m['f1'] for m in standard_metrics) / len(standard_metrics)

    simple_avg_precision = sum(m['precision'] for m in simple_metrics) / len(simple_metrics)
    standard_avg_precision = sum(m['precision'] for m in standard_metrics) / len(standard_metrics)

    simple_avg_recall = sum(m['recall'] for m in simple_metrics) / len(simple_metrics)
    standard_avg_recall = sum(m['recall'] for m in standard_metrics) / len(standard_metrics)

    print("\n*** OVERALL WINNER ***")
    winner = "STANDARD" if standard_avg_f1 > simple_avg_f1 else "SIMPLE"
    margin = abs(standard_avg_f1 - simple_avg_f1) / min(standard_avg_f1, simple_avg_f1) * 100
    print(f"{winner} mode wins overall with {max(simple_avg_f1, standard_avg_f1)*100:.2f}% avg F1")
    print(f"Margin: {margin:.1f}% better than {'SIMPLE' if winner == 'STANDARD' else 'STANDARD'}")

    print("\n*** OVERALL METRICS ***")
    print(f"{'Metric':<20} {'SIMPLE':<15} {'STANDARD':<15} {'Winner':<15}")
    print("-" * 65)
    print(f"{'Avg F1 Score':<20} {simple_avg_f1*100:>6.2f}%        {standard_avg_f1*100:>6.2f}%        {winner:<15}")
    print(f"{'Avg Precision':<20} {simple_avg_precision*100:>6.2f}%        {standard_avg_precision*100:>6.2f}%        {'SIMPLE' if simple_avg_precision > standard_avg_precision else 'STANDARD':<15}")
    print(f"{'Avg Recall':<20} {simple_avg_recall*100:>6.2f}%        {standard_avg_recall*100:>6.2f}%        {'SIMPLE' if simple_avg_recall > standard_avg_recall else 'STANDARD':<15}")

    print("\n*** PROBLEM-BY-PROBLEM BREAKDOWN ***")
    print(f"{'Problem':<25} {'Mode':<10} {'F1':<10} {'Precision':<12} {'Recall':<10} {'FP':<6} {'FN':<6}")
    print("-" * 80)

    problems = ['FizzBuzzProblem', 'RockPaperScissors', 'astar_pathfinding', 'inventory_ice_cream_shop']
    for problem in problems:
        for mode in ['SIMPLE', 'STANDARD']:
            m = next((metric for metric in metrics if metric['problem'] == problem and metric['mode'] == mode), None)
            if m:
                print(f"{problem:<25} {mode:<10} {m['f1']*100:>6.2f}%   {m['precision']*100:>6.2f}%      {m['recall']*100:>6.2f}%    {m['fp']:<6} {m['fn']:<6}")

    print("\n*** KEY FINDINGS ***")
    print("\n1. SIMPLE mode WINS on small files (<50 lines):")
    fizz_simple = next(m for m in metrics if m['problem'] == 'FizzBuzzProblem' and m['mode'] == 'SIMPLE')
    fizz_standard = next(m for m in metrics if m['problem'] == 'FizzBuzzProblem' and m['mode'] == 'STANDARD')
    print(f"   - FizzBuzz F1: SIMPLE {fizz_simple['f1']*100:.2f}% vs STANDARD {fizz_standard['f1']*100:.2f}%")
    print(f"   - Margin: {(fizz_simple['f1'] - fizz_standard['f1']) / fizz_standard['f1'] * 100:.1f}% improvement")
    print(f"   - False Positives: SIMPLE {fizz_simple['fp']} vs STANDARD {fizz_standard['fp']}")
    print(f"   - FP Reduction: {(fizz_standard['fp'] - fizz_simple['fp']) / fizz_standard['fp'] * 100:.1f}%")

    print("\n2. STANDARD mode WINS on medium files (50-150 lines):")
    rps_simple = next(m for m in metrics if m['problem'] == 'RockPaperScissors' and m['mode'] == 'SIMPLE')
    rps_standard = next(m for m in metrics if m['problem'] == 'RockPaperScissors' and m['mode'] == 'STANDARD')
    print(f"   - RockPaperScissors F1: STANDARD {rps_standard['f1']*100:.2f}% vs SIMPLE {rps_simple['f1']*100:.2f}%")
    print(f"   - Margin: {(rps_standard['f1'] - rps_simple['f1']) / rps_simple['f1'] * 100:.1f}% improvement")
    print(f"   - Recall: STANDARD {rps_standard['recall']*100:.1f}% vs SIMPLE {rps_simple['recall']*100:.1f}%")

    print("\n3. Modes CONVERGE on complex files (>130 lines):")
    astar_simple = next(m for m in metrics if m['problem'] == 'astar_pathfinding' and m['mode'] == 'SIMPLE')
    astar_standard = next(m for m in metrics if m['problem'] == 'astar_pathfinding' and m['mode'] == 'STANDARD')
    inventory_simple = next(m for m in metrics if m['problem'] == 'inventory_ice_cream_shop' and m['mode'] == 'SIMPLE')
    inventory_standard = next(m for m in metrics if m['problem'] == 'inventory_ice_cream_shop' and m['mode'] == 'STANDARD')
    print(f"   - astar F1: SIMPLE {astar_simple['f1']*100:.2f}% vs STANDARD {astar_standard['f1']*100:.2f}% (IDENTICAL)")
    print(f"   - inventory F1: SIMPLE {inventory_simple['f1']*100:.2f}% vs STANDARD {inventory_standard['f1']*100:.2f}% (IDENTICAL)")

    print("\n*** RECOMMENDATIONS ***")
    print("\n  Use SIMPLE mode for:")
    print("    - Files < 50 lines (FizzBuzz, palindromes, simple algorithms)")
    print("    - When precision is critical (minimize false accusations)")
    print("    - Constrained problems with limited solution space")
    print("")
    print("  Use STANDARD mode for:")
    print("    - Files 50+ lines (games, web apps, complex algorithms)")
    print("    - When recall is critical (catch all plagiarism)")
    print("    - Open-ended projects with high implementation diversity")

    print("\n" + "="*80)
    print("Full analysis available in docs/MODE_EFFECTIVENESS_ANALYSIS.md")
    print("Detailed results in analysis_results/mode_comparison_detailed.csv")
    print("="*80 + "\n")


def main():
    """Main entry point"""
    # Find metrics CSV
    base_dir = Path(__file__).parent.parent
    metrics_path = base_dir / 'analysis_results' / 'mode_comparison_metrics.csv'

    if not metrics_path.exists():
        print(f"ERROR: Metrics file not found at {metrics_path}")
        print("Please run compare_all_modes.py first.")
        return

    # Load and print summary
    metrics = load_metrics(metrics_path)
    print_summary(metrics)


if __name__ == '__main__':
    main()
