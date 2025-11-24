# CodeGuard Quick Start Guide

This guide provides step-by-step instructions for using the CodeGuard plagiarism detection system.

## System Requirements

- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended for large file sets)
- Web browser (Chrome, Firefox, Safari, or Edge)
- 100MB disk space for installation
- Additional space for uploaded files and results

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/codeguard.git
cd codeguard
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

The database will be automatically initialized on first run. No manual setup required.

### Step 5: Launch Application

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## Using CodeGuard

### 1. Upload Files

**How to Upload:**
1. Navigate to the "Analysis" tab (default view)
2. Click the "Browse files" button or drag-and-drop files into the upload area
3. Select 2 to 100 Python (.py) files from your computer

**File Requirements:**
- **Format:** Python source files only (.py extension)
- **Size:** Maximum 16MB per file
- **Quantity:** Minimum 2 files, maximum 100 files
- **Encoding:** UTF-8 recommended

**Tips:**
- Upload all student submissions for a single assignment together
- Files are temporarily stored and automatically deleted after analysis
- Larger file sets take longer to analyze (see timing estimates below)

### 2. Run Analysis

**Basic Analysis:**
1. After uploading files, click the "Analyze Files" button
2. A progress bar will appear showing analysis progress
3. The system will compare every file against every other file
4. Wait for completion message

**Progress Tracking:**
- Total comparisons shown (N files = N*(N-1)/2 comparisons)
- Current comparison being analyzed
- Estimated time remaining
- Individual detector status (Token, AST, Hash)

**Estimated Analysis Times:**
| File Count | Comparisons | Typical Time |
|------------|-------------|--------------|
| 10 files   | 45 pairs    | ~10 seconds  |
| 25 files   | 300 pairs   | ~30 seconds  |
| 50 files   | 1,225 pairs | ~90 seconds  |
| 100 files  | 4,950 pairs | ~5 minutes   |

### 3. Understand Results

**Results Table:**

The main results table displays all file pair comparisons with the following columns:

- **File 1 / File 2:** The two files being compared
- **Plagiarism Detected:** Indicates if plagiarism was flagged
  - Warning icon: Plagiarism detected
  - Checkmark: No plagiarism detected
- **Confidence Score:** Numerical confidence (0.0-1.0)
- **Confidence Level:** Human-readable confidence classification
  - Very High: 90-100% confidence
  - High: 75-89% confidence
  - Medium: 50-74% confidence
  - Low: 25-49% confidence
  - Very Low: 0-24% confidence
- **Token Score:** Lexical similarity (0.0-1.0)
- **AST Score:** Structural similarity (0.0-1.0)
- **Hash Score:** Fingerprint similarity (0.0-1.0)

**Interpreting Confidence Levels:**

- **Very High (90-100%):** Strong evidence of plagiarism. All detectors agree.
- **High (75-89%):** Significant similarity detected. Manual review recommended.
- **Medium (50-74%):** Moderate similarity. Could be legitimate or plagiarism.
- **Low (25-49%):** Minor similarities, likely coincidental.
- **Very Low (0-24%):** No significant similarity detected.

**Understanding Detector Scores:**

1. **Token Detector (Weight: 1.0x)**
   - Measures lexical similarity (exact token matching)
   - High score: Direct copying with minimal changes
   - Defeated by: Variable renaming, code restructuring
   - Threshold: 0.70

2. **AST Detector (Weight: 2.0x)**
   - Measures structural similarity (code structure)
   - High score: Same algorithms and control flow
   - Defeated by: Completely different algorithms
   - Threshold: 0.80
   - Most reliable indicator (highest weight)

3. **Hash Detector (Weight: 1.5x)**
   - Measures partial and scattered copying
   - High score: Copied code fragments
   - Defeated by: Heavy obfuscation
   - Threshold: 0.60

**Summary Statistics:**

Below the results table, view:
- Total pairs analyzed
- Plagiarism cases detected
- Average confidence score
- Average detector scores
- Detector agreement analysis

### 4. Adjust Thresholds (Advanced)

The sidebar contains expandable sections for advanced configuration.

**Detection Thresholds Expander:**

Adjust when each detector triggers a plagiarism vote:

- **Token Threshold (0.5-0.9):** Default 0.70
  - Lower: More sensitive to token similarity
  - Higher: Requires more exact token matches

- **AST Threshold (0.6-0.95):** Default 0.80
  - Lower: More sensitive to structural similarity
  - Higher: Requires more exact structural matches

- **Hash Threshold (0.4-0.8):** Default 0.60
  - Lower: More sensitive to partial copying
  - Higher: Requires more substantial copying

**Detector Weights Expander:**

Adjust the relative importance of each detector:

- **Token Weight (0.5-2.0):** Default 1.0
- **AST Weight (1.0-3.0):** Default 2.0 (highest reliability)
- **Hash Weight (0.5-2.5):** Default 1.5

Total possible votes = sum of weights (default: 4.5)

**Decision Threshold Slider:**

Adjust the overall plagiarism decision threshold:

- **Range:** 30-70% of total possible votes
- **Default:** 50% (2.25 out of 4.5 weighted votes)
- **Lower:** More pairs flagged as plagiarism (higher recall)
- **Higher:** Fewer pairs flagged as plagiarism (higher precision)

**Reset to Defaults Button:**

Click to restore all thresholds and weights to their default values.

**When to Adjust Settings:**

1. **Too many false positives?**
   - Increase detection thresholds
   - Increase decision threshold
   - Increase AST weight (most reliable)

2. **Missing obvious plagiarism?**
   - Decrease detection thresholds
   - Decrease decision threshold
   - Check if specific detector is missing cases

3. **Different assignment types?**
   - Simple algorithms: Use default settings
   - Open-ended projects: Increase thresholds
   - Templates provided: Increase AST weight

### 5. Export Results

**CSV Export:**

1. After analysis completes, locate the "Download Results as CSV" button
2. Click to download a CSV file containing all comparison results
3. Default filename: `plagiarism_results_<timestamp>.csv`

**CSV Contents:**

The exported CSV includes:
- File 1 and File 2 names
- Plagiarism detection result (True/False)
- Confidence score and level
- Individual detector scores (Token, AST, Hash)
- Weighted votes
- Timestamp of analysis

**Opening in Excel/Google Sheets:**

1. Open Excel or Google Sheets
2. Import or open the downloaded CSV file
3. Data will be organized in columns for easy sorting and filtering
4. Use Excel filters to find specific patterns or high-confidence matches

**Tips for Analysis:**

- Sort by Confidence Score (descending) to review highest-risk pairs first
- Filter by Plagiarism Detected = True to see only flagged pairs
- Group by Confidence Level to batch review similar cases
- Look for patterns (e.g., one file matching many others)

### 6. View Analysis History

**Accessing History:**

1. Click the "History" tab in the main navigation
2. View list of all previous analyses
3. Each entry shows:
   - Job ID (unique identifier)
   - Timestamp of analysis
   - Number of files analyzed
   - Number of comparisons performed
   - Number of plagiarism cases detected

**Re-accessing Past Results:**

1. Browse the history list
2. Click on a specific analysis entry to view its full results
3. All results, scores, and configurations are preserved
4. Download CSV for any past analysis

**History Retention:**

- Analysis results are stored indefinitely in the SQLite database
- Located at: `data/codeguard.db`
- Can be backed up by copying the database file

## Troubleshooting

### Common Issues

**Issue: "File too large" error**
- **Solution:** Files must be under 16MB. Compress or split large files.

**Issue: "Invalid file format" error**
- **Solution:** Only .py files are accepted. Ensure files have .py extension.

**Issue: Analysis takes too long**
- **Solution:** Reduce number of files. 100 files create 4,950 comparisons.

**Issue: All results show "Very Low" confidence**
- **Solution:** Check that files contain substantial code (not just imports/comments).

**Issue: Too many false positives**
- **Solution:** Increase detection thresholds in sidebar, especially AST threshold.

**Issue: Database connection error**
- **Solution:** Ensure write permissions in the data/ directory.

### Getting Help

For additional support:
1. Check the main [README.md](../../README.md) for detailed information
2. Review the [How It Works](how-it-works.md) guide for algorithm details
3. Consult the [Technical Decisions Log](../../technicalDecisionsLog.md)
4. Open an issue on the GitHub repository

## Best Practices

### For Educators

1. **Establish Baselines:** Run analysis on legitimate diverse submissions to understand typical similarity ranges for your assignments

2. **Use Confidence Levels:** Focus manual review on "High" and "Very High" confidence cases first

3. **Consider Context:** High structural similarity (AST) is more concerning than high token similarity alone

4. **Review Clusters:** If one file matches many others, investigate that file as a potential source

5. **Combine with Judgment:** Use CodeGuard as a tool to assist, not replace, your professional judgment

6. **Document Settings:** Record threshold settings used for each assignment for consistency

### For Analysis

1. **Batch Similar Assignments:** Analyze all submissions for one assignment together

2. **Export and Archive:** Download CSV results for record-keeping

3. **Review Detector Agreement:** Cases where all three detectors agree are most reliable

4. **Watch for Patterns:**
   - All detectors high: Direct copying
   - AST high, others low: Variable renaming
   - Token high, AST low: Coincidental similarity

5. **Use "How It Works" Tab:** Educate students about detection methods to encourage original work

## Next Steps

- Explore the "How It Works" tab to understand detection algorithms
- Experiment with threshold adjustments on sample data
- Review the [ACCURACY_REPORT.md](../ACCURACY_REPORT.md) for validation results
- Check [project_status.md](../../project_status.md) for current development status

## Additional Resources

- [Main Documentation](../../README.md)
- [Algorithm Details](../algorithms/)
- [Developer Guide](../../CLAUDE.md)
- [Architecture Documentation](../../APP_ARCHITECTURE.md)
- [Technical Decisions](../../technicalDecisionsLog.md)
