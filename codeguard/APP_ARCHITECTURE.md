# CodeGuard Streamlit App Architecture (Task 3.1)

## Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT APP (app.py)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     1. INITIALIZATION                        │
│  • Set page config (wide layout, title, icon)              │
│  • Initialize session state variables                       │
│  • Render sidebar with configuration                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. FILE UPLOAD WIDGET                     │
│  • st.file_uploader (multiple files, .py only)             │
│  • Validate: count (2-100), extension (.py), size (<16MB)  │
│  • Display: file list, pair count, success/error messages  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  3. ANALYSIS TRIGGER                         │
│  • "Analyze for Plagiarism" button                         │
│  • Get threshold from session state                         │
│  • Call analyze_files() function                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  4. ANALYSIS ENGINE                          │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Create TokenDetector(threshold)                │       │
│  └─────────────────────────────────────────────────┘       │
│                        │                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Generate file pairs: N*(N-1)/2 combinations    │       │
│  └─────────────────────────────────────────────────┘       │
│                        │                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │  For each pair:                                 │       │
│  │    • Read file contents                         │       │
│  │    • detector.compare(code1, code2)            │       │
│  │    • Get jaccard_similarity                     │       │
│  │    • Get cosine_similarity                      │       │
│  │    • Calculate combined score                   │       │
│  │    • Determine is_plagiarized                   │       │
│  │    • Update progress bar                        │       │
│  │    • Store result in list                       │       │
│  └─────────────────────────────────────────────────┘       │
│                        │                                     │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Create DataFrame from results                  │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   5. RESULTS DISPLAY                         │
│  • Summary metrics (3 columns):                             │
│    - Total Pairs                                            │
│    - Plagiarized count (with % delta)                       │
│    - Clean count (with % delta)                             │
│                                                              │
│  • Interactive DataFrame:                                   │
│    - File 1, File 2                                         │
│    - Jaccard %, Cosine %, Combined %                        │
│    - Plagiarized (✓/✗)                                      │
│    - Formatted to 2 decimal places                          │
│    - Sortable columns                                       │
│                                                              │
│  • Warning/Success message based on results                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    6. JSON EXPORT                            │
│  • "Download Results (JSON)" button                         │
│  • Convert DataFrame to JSON structure:                     │
│    {                                                         │
│      "analysis_date": ISO timestamp,                        │
│      "file_count": N,                                       │
│      "pair_count": M,                                       │
│      "threshold": 0.7,                                      │
│      "results": [...],                                      │
│      "summary": {...}                                       │
│    }                                                         │
│  • st.download_button with proper filename                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Session State Variables

```python
st.session_state = {
    'uploaded_files': [],           # List of file objects
    'analysis_results': None,       # DataFrame or None
    'detector_threshold': 0.7,      # Float (0.0-1.0)
    'file_contents': {},            # Dict: filename -> code
    'analysis_completed': False     # Boolean flag
}
```

---

## Function Architecture

```
main()
├── initialize_session_state()
├── render_sidebar()
│   └── st.sidebar.slider() → detector_threshold
├── render_main_header()
├── render_file_upload()
│   ├── st.file_uploader()
│   └── validate_uploaded_files()
│       ├── Check file count (2-100)
│       ├── Check extensions (.py)
│       └── Check file sizes (<16MB)
├── render_analysis_button()
│   └── analyze_files()
│       ├── TokenDetector(threshold)
│       ├── Generate pairs
│       ├── For each pair:
│       │   ├── detector.compare()
│       │   ├── detector._tokenize_code()
│       │   ├── detector._calculate_jaccard_similarity()
│       │   └── detector._calculate_cosine_similarity()
│       ├── Update progress (st.progress, st.empty)
│       └── Return DataFrame
└── render_results()
    ├── Display summary metrics
    ├── Display DataFrame
    └── create_download_json()
        ├── Convert DataFrame to dict
        ├── Add metadata
        ├── Add summary
        └── Return JSON string
```

---

## Data Flow Diagram

```
User Upload
    │
    ▼
[File Validator]
    │
    ├─ Valid ──────┐
    │              │
    └─ Invalid ────┼──> Error Message
                   │
                   ▼
        [Generate File Pairs]
                   │
                   ▼
        ┌──────────────────┐
        │  TokenDetector   │
        │  ┌────────────┐  │
        │  │ Tokenize   │  │
        │  │ Calculate  │  │
        │  │ Jaccard    │  │
        │  │ Cosine     │  │
        │  │ Combined   │  │
        │  └────────────┘  │
        └──────────────────┘
                   │
                   ▼
        [Aggregate Results]
                   │
                   ▼
        ┌──────────────────┐
        │    DataFrame     │
        │  ┌────┬────┬──┐  │
        │  │F1  │F2  │%│  │
        │  │... │... │✓│  │
        │  └────┴────┴──┘  │
        └──────────────────┘
                   │
                   ├──────────┐
                   │          │
                   ▼          ▼
            [UI Display]  [JSON Export]
```

---

## UI Component Hierarchy

```
StreamlitApp
├── Sidebar
│   ├── Title & Description
│   ├── Threshold Slider (0.0-1.0, step 0.05)
│   ├── Upload Statistics
│   │   ├── Files Uploaded (metric)
│   │   └── Pairs to Analyze (metric)
│   └── Instructions
│
└── Main Content
    ├── Header
    │   ├── Title
    │   └── Description
    │
    ├── File Upload Section
    │   ├── st.file_uploader
    │   ├── Validation Messages
    │   ├── File List (expandable)
    │   └── Pair Count Info
    │
    ├── Analysis Section
    │   ├── "Analyze for Plagiarism" Button
    │   ├── Progress Bar (during analysis)
    │   ├── Status Text (dynamic)
    │   └── Success/Error Messages
    │
    ├── Results Section (conditional)
    │   ├── Summary Statistics
    │   │   ├── Total Pairs (metric)
    │   │   ├── Plagiarized (metric + delta)
    │   │   └── Clean (metric + delta)
    │   │
    │   ├── Detailed Results Table
    │   │   └── st.dataframe (interactive)
    │   │
    │   └── Export Section
    │       └── st.download_button
    │
    └── Footer
```

---

## TokenDetector Integration

```python
# Import
from src.detectors.token_detector import TokenDetector

# Instantiate
detector = TokenDetector(threshold=0.7)

# Compare files
combined_score = detector.compare(code1, code2)

# Get individual metrics
tokens1 = detector._tokenize_code(code1)
tokens2 = detector._tokenize_code(code2)
jaccard = detector._calculate_jaccard_similarity(tokens1, tokens2)
cosine = detector._calculate_cosine_similarity(tokens1, tokens2)

# Result structure
{
    'File 1': filename1,
    'File 2': filename2,
    'Jaccard Similarity (%)': jaccard * 100,
    'Cosine Similarity (%)': cosine * 100,
    'Combined Similarity (%)': combined_score * 100,
    'Plagiarized': '✓' if combined_score >= threshold else '✗'
}
```

---

## Error Handling Strategy

```
┌──────────────────┐
│  User Action     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│  Try Block       │────>│  Success Path   │
│  • File upload   │     │  • Show success │
│  • Validation    │     │  • Continue     │
│  • Analysis      │     └─────────────────┘
└────────┬─────────┘
         │
         │ Exception
         ▼
┌──────────────────┐
│  Except Block    │
│  • Catch error   │
│  • st.error()    │
│  • st.exception()│
│  • Return early  │
└──────────────────┘
```

### Error Types Handled
1. **Validation Errors**: User-friendly messages
2. **File Reading Errors**: UTF-8 decoding issues
3. **Analysis Errors**: TokenDetector exceptions
4. **Memory Errors**: Large file/batch handling

---

## Performance Optimization

### Current Implementation
- Sequential processing of file pairs
- Progress bar updates for user feedback
- File pointer reset for re-reading
- Efficient pandas DataFrame operations

### Bottlenecks
1. Tokenization (most expensive operation)
2. File I/O (reading file contents)
3. Similarity calculations (mathematical operations)

### Future Optimizations
```python
# Cache detector instance
@st.cache_resource
def get_detector(threshold):
    return TokenDetector(threshold=threshold)

# Cache file tokenization
@st.cache_data
def tokenize_file(file_content):
    return detector._tokenize_code(file_content)

# Parallel processing
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    results = executor.map(analyze_pair, pairs)
```

---

## File Structure

```
codeguard/
├── app.py                           ← Main Streamlit app (591 lines)
│   ├── Constants
│   ├── Session State Management
│   ├── File Validation
│   ├── Analysis Engine
│   ├── JSON Export
│   ├── UI Components
│   └── Main Function
│
├── test_app_functionality.py        ← Test script (288 lines)
│   ├── Test 1: TokenDetector
│   ├── Test 2: Validation
│   ├── Test 3: Analysis
│   └── Test 4: JSON Export
│
├── TASK_3.1_COMPLETION_SUMMARY.md  ← Documentation (582 lines)
├── TASK_3.1_QUICK_START.md         ← Quick start guide
├── APP_ARCHITECTURE.md              ← This file
│
├── src/
│   └── detectors/
│       └── token_detector.py        ← Detector implementation
│
└── validation-datasets/
    ├── plagiarized/                 ← Test files
    ├── legitimate/                  ← Test files
    └── obfuscated/                  ← Test files
```

---

## Technology Stack

```
┌─────────────────────────────────────┐
│         Streamlit Frontend          │
│  • UI Components                    │
│  • Session State                    │
│  • File Upload                      │
│  • Progress Tracking                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Pandas DataFrame            │
│  • Results Storage                  │
│  • Data Manipulation                │
│  • Table Display                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        TokenDetector API            │
│  • compare(code1, code2)           │
│  • _tokenize_code(code)            │
│  • _calculate_jaccard()            │
│  • _calculate_cosine()             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Python Standard Library        │
│  • tokenize (lexical analysis)     │
│  • collections.Counter              │
│  • json (export)                    │
│  • datetime (timestamps)            │
└─────────────────────────────────────┘
```

---

## State Management

### Streamlit Rerun Behavior
Every user interaction causes a full script rerun. Session state preserves data.

```python
# First run
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None  # Initialize

# After analysis
st.session_state.analysis_results = df  # Store

# On rerun (e.g., slider change)
if st.session_state.analysis_results is not None:
    render_results()  # Data persists!
```

### State Lifecycle
1. **Initial Load**: All state variables initialized to defaults
2. **File Upload**: `uploaded_files` updated
3. **Analysis**: `analysis_results` and `analysis_completed` updated
4. **Threshold Change**: Only `detector_threshold` updated (results persist)
5. **New Upload**: State cleared and reinitialized

---

## Validation Rules

### File Count
```python
MIN_FILES = 2
MAX_FILES = 100
if not (MIN_FILES <= len(files) <= MAX_FILES):
    return error
```

### File Extension
```python
ALLOWED_EXTENSIONS = ['.py']
if not file.name.endswith('.py'):
    return error
```

### File Size
```python
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
if file.size > MAX_FILE_SIZE:
    return error
```

---

## Example User Journey

```
1. User opens app
   → Page loads
   → Session state initialized
   → Sidebar and main content rendered

2. User uploads 3 Python files
   → Files validated (✓ 3 files, ✓ .py, ✓ <16MB)
   → Success message shown
   → Pair count calculated: 3 files = 3 pairs
   → Sidebar updated with statistics

3. User adjusts threshold to 0.8
   → Sidebar slider updates
   → Session state updated
   → Previous results (if any) remain visible

4. User clicks "Analyze for Plagiarism"
   → Progress bar appears
   → For each of 3 pairs:
     - Status: "Analyzing pair 1/3: file1.py vs file2.py"
     - TokenDetector compares files
     - Results stored
     - Progress: 33% → 66% → 100%
   → Progress cleared
   → Success message + balloons
   → Results stored in session state

5. User views results
   → Summary metrics displayed
   → DataFrame with 3 rows shown
   → Interactive table (sortable, scrollable)

6. User downloads JSON
   → Download button clicked
   → JSON generated from DataFrame
   → File saved: codeguard_results_20241112_143045.json

7. User uploads new files
   → File uploader cleared
   → Previous results remain until new analysis
   → Can compare different sets of files
```

---

**Created**: November 12, 2024
**Version**: 1.0.0
**Task**: 3.1 - Basic Streamlit App with TokenDetector Integration
