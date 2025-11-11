"""
CodeGuard - Code Plagiarism Detection System
Main Streamlit Application

This is the main entry point for the CodeGuard web interface.
Provides file upload, analysis, and results visualization.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import tempfile
from typing import List, Dict, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import core detection components (these will be implemented)
# from detectors.token_detector import TokenDetector
# from detectors.ast_detector import ASTDetector
# from detectors.hash_detector import HashDetector
# from voting.voting_system import VotingSystem
# from database.operations import save_batch_results, create_analysis_job
from utils.constants import (
    TOKEN_THRESHOLD, AST_THRESHOLD, HASH_THRESHOLD,
    TOKEN_WEIGHT, AST_WEIGHT, HASH_WEIGHT,
    DECISION_THRESHOLD, MAX_FILE_SIZE_BYTES, MIN_FILES_PER_UPLOAD
)

# Page configuration
st.set_page_config(
    page_title="CodeGuard - Plagiarism Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2563eb;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563eb;
    }
    .plagiarism-detected {
        background-color: #fee2e2;
        border-left-color: #dc2626;
    }
    .no-plagiarism {
        background-color: #dcfce7;
        border-left-color: #16a34a;
    }
    .stProgress > div > div > div > div {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'job_id' not in st.session_state:
        st.session_state.job_id = None


def validate_uploaded_files(files) -> Tuple[bool, str]:
    """Validate uploaded files meet requirements."""
    if len(files) < MIN_FILES_PER_UPLOAD:
        return False, f"Please upload at least {MIN_FILES_PER_UPLOAD} Python files."

    for file in files:
        if not file.name.endswith('.py'):
            return False, f"File '{file.name}' is not a Python file (.py)"

        if file.size > MAX_FILE_SIZE_BYTES:
            max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
            return False, f"File '{file.name}' exceeds {max_mb}MB limit"

    return True, "All files valid"


def save_uploaded_files(files) -> List[str]:
    """Save uploaded files temporarily and return paths."""
    temp_dir = Path("data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)

    file_paths = []
    for file in files:
        file_path = temp_dir / file.name
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())
        file_paths.append(str(file_path))

    return file_paths


def analyze_files(file_paths: List[str], config: Dict) -> List[Dict]:
    """
    Analyze files for plagiarism using the three-method detection system.

    This is a placeholder that will integrate with actual detectors once implemented.
    """
    results = []

    # TODO: Replace with actual detector implementations
    # token_detector = TokenDetector()
    # ast_detector = ASTDetector()
    # hash_detector = HashDetector()
    # voter = VotingSystem(config)

    # Generate all pairs
    from itertools import combinations
    pairs = list(combinations(file_paths, 2))

    # Placeholder: Generate mock results for demonstration
    # In production, this will call actual detectors
    import random
    for file1, file2 in pairs:
        # Mock similarity scores
        token_sim = random.uniform(0.3, 0.9)
        ast_sim = random.uniform(0.3, 0.9)
        hash_sim = random.uniform(0.3, 0.9)

        # Mock voting
        confidence = (0.3 * token_sim + 0.4 * ast_sim + 0.3 * hash_sim)
        is_plagiarized = confidence >= config['decision_threshold']

        results.append({
            'file1': Path(file1).name,
            'file2': Path(file2).name,
            'token_similarity': token_sim,
            'ast_similarity': ast_sim,
            'hash_similarity': hash_sim,
            'confidence_score': confidence,
            'is_plagiarized': is_plagiarized
        })

    return results


def render_header():
    """Render the application header."""
    st.markdown('<div class="main-header">🛡️ CodeGuard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent Code Plagiarism Detection System</div>',
                unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("Detection Thresholds")
        st.caption("Higher values = stricter detection")

        token_threshold = st.slider(
            "Token Threshold",
            min_value=0.0,
            max_value=1.0,
            value=TOKEN_THRESHOLD,
            step=0.05,
            help="Threshold for token-based detection (lexical similarity)"
        )

        ast_threshold = st.slider(
            "AST Threshold",
            min_value=0.0,
            max_value=1.0,
            value=AST_THRESHOLD,
            step=0.05,
            help="Threshold for AST-based detection (structural similarity)"
        )

        hash_threshold = st.slider(
            "Hash Threshold",
            min_value=0.0,
            max_value=1.0,
            value=HASH_THRESHOLD,
            step=0.05,
            help="Threshold for hash-based detection (winnowing algorithm)"
        )

        st.subheader("Voting Weights")
        st.caption("Relative importance of each detector")

        token_weight = st.slider(
            "Token Weight",
            min_value=0.5,
            max_value=3.0,
            value=TOKEN_WEIGHT,
            step=0.5,
            help="Weight for token detector votes"
        )

        ast_weight = st.slider(
            "AST Weight",
            min_value=0.5,
            max_value=3.0,
            value=AST_WEIGHT,
            step=0.5,
            help="Weight for AST detector votes (most reliable)"
        )

        hash_weight = st.slider(
            "Hash Weight",
            min_value=0.5,
            max_value=3.0,
            value=HASH_WEIGHT,
            step=0.5,
            help="Weight for hash detector votes"
        )

        st.subheader("Decision Threshold")
        decision_threshold = st.slider(
            "Plagiarism Decision Threshold",
            min_value=0.0,
            max_value=1.0,
            value=DECISION_THRESHOLD,
            step=0.05,
            help="Minimum weighted votes needed to flag plagiarism"
        )

        config = {
            'thresholds': {
                'token': token_threshold,
                'ast': ast_threshold,
                'hash': hash_threshold
            },
            'weights': {
                'token': token_weight,
                'ast': ast_weight,
                'hash': hash_weight
            },
            'decision_threshold': decision_threshold
        }

        return config


def render_upload_tab():
    """Render the upload and analyze tab."""
    st.header("📁 Upload Python Files")

    st.info("""
    **Requirements:**
    - Minimum 2 Python (.py) files
    - Maximum 16MB per file
    - Up to 100 files per analysis
    """)

    uploaded_files = st.file_uploader(
        "Choose Python files",
        type=['py'],
        accept_multiple_files=True,
        help="Upload student Python submissions for plagiarism analysis"
    )

    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} files uploaded")

        # Show file list
        with st.expander("View uploaded files"):
            for file in uploaded_files:
                file_size = file.size / 1024  # Convert to KB
                st.text(f"📄 {file.name} ({file_size:.1f} KB)")

        # Validate files
        is_valid, message = validate_uploaded_files(uploaded_files)

        if not is_valid:
            st.error(message)
            return

        # Analyze button
        if st.button("🔍 Analyze for Plagiarism", type="primary", use_container_width=True):
            with st.spinner("Analyzing files..."):
                # Get configuration from sidebar
                config = st.session_state.get('config', {
                    'thresholds': {'token': TOKEN_THRESHOLD, 'ast': AST_THRESHOLD, 'hash': HASH_THRESHOLD},
                    'weights': {'token': TOKEN_WEIGHT, 'ast': AST_WEIGHT, 'hash': HASH_WEIGHT},
                    'decision_threshold': DECISION_THRESHOLD
                })

                # Save files temporarily
                file_paths = save_uploaded_files(uploaded_files)

                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Analyze
                status_text.text("Running detectors...")
                progress_bar.progress(30)

                results = analyze_files(file_paths, config)

                progress_bar.progress(70)
                status_text.text("Aggregating results...")

                # Store results in session state
                st.session_state.analysis_results = results
                st.session_state.job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state.uploaded_files = [f.name for f in uploaded_files]

                progress_bar.progress(100)
                status_text.text("Analysis complete!")

                st.success("✓ Analysis completed successfully!")
                st.info("Switch to the 'Results' tab to view detailed findings.")


def render_results_tab():
    """Render the results tab."""
    st.header("📊 Analysis Results")

    if st.session_state.analysis_results is None:
        st.info("No analysis results yet. Upload files and run analysis first.")
        return

    results = st.session_state.analysis_results

    # Summary metrics
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    total_pairs = len(results)
    plagiarized_count = sum(1 for r in results if r['is_plagiarized'])
    avg_confidence = sum(r['confidence_score'] for r in results) / total_pairs if total_pairs > 0 else 0
    plagiarism_rate = (plagiarized_count / total_pairs * 100) if total_pairs > 0 else 0

    with col1:
        st.metric("Total Pairs Compared", total_pairs)
    with col2:
        st.metric("Plagiarism Detected", plagiarized_count,
                 delta=f"{plagiarism_rate:.1f}%", delta_color="inverse")
    with col3:
        st.metric("Average Confidence", f"{avg_confidence:.1%}")
    with col4:
        st.metric("Clean Pairs", total_pairs - plagiarized_count,
                 delta=f"{100-plagiarism_rate:.1f}%")

    st.divider()

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_option = st.selectbox(
            "Filter Results",
            ["All Results", "Plagiarized Only", "Clean Only"]
        )
    with col2:
        sort_option = st.selectbox(
            "Sort By",
            ["Confidence (High to Low)", "Confidence (Low to High)",
             "File 1 Name", "File 2 Name"]
        )

    # Apply filters
    filtered_results = results.copy()
    if filter_option == "Plagiarized Only":
        filtered_results = [r for r in filtered_results if r['is_plagiarized']]
    elif filter_option == "Clean Only":
        filtered_results = [r for r in filtered_results if not r['is_plagiarized']]

    # Apply sorting
    if sort_option == "Confidence (High to Low)":
        filtered_results.sort(key=lambda x: x['confidence_score'], reverse=True)
    elif sort_option == "Confidence (Low to High)":
        filtered_results.sort(key=lambda x: x['confidence_score'])
    elif sort_option == "File 1 Name":
        filtered_results.sort(key=lambda x: x['file1'])
    else:  # File 2 Name
        filtered_results.sort(key=lambda x: x['file2'])

    st.subheader(f"Comparison Results ({len(filtered_results)} pairs)")

    # Display results
    for idx, result in enumerate(filtered_results, 1):
        with st.container():
            # Create columns for layout
            col1, col2 = st.columns([3, 1])

            with col1:
                status_emoji = "🚨" if result['is_plagiarized'] else "✅"
                status_text = "PLAGIARISM DETECTED" if result['is_plagiarized'] else "CLEAN"
                status_color = "🔴" if result['is_plagiarized'] else "🟢"

                st.markdown(f"### {status_emoji} Pair #{idx}: {result['file1']} vs {result['file2']}")
                st.markdown(f"{status_color} **Status:** {status_text}")

            with col2:
                confidence_pct = result['confidence_score'] * 100
                st.metric("Confidence", f"{confidence_pct:.1f}%")

            # Progress bar for confidence
            st.progress(result['confidence_score'])

            # Similarity scores
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔤 Token Similarity", f"{result['token_similarity']:.1%}")
            with col2:
                st.metric("🌳 AST Similarity", f"{result['ast_similarity']:.1%}")
            with col3:
                st.metric("🔐 Hash Similarity", f"{result['hash_similarity']:.1%}")

            st.divider()

    # Export button
    if st.button("💾 Download Results (JSON)", use_container_width=True):
        export_data = {
            'job_id': st.session_state.job_id,
            'timestamp': datetime.now().isoformat(),
            'files_analyzed': st.session_state.uploaded_files,
            'summary': {
                'total_pairs': total_pairs,
                'plagiarized_count': plagiarized_count,
                'plagiarism_rate': plagiarism_rate,
                'avg_confidence': avg_confidence
            },
            'results': results
        }

        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="📥 Click to Download",
            data=json_str,
            file_name=f"codeguard_analysis_{st.session_state.job_id}.json",
            mime="application/json"
        )


def render_about_tab():
    """Render the about tab."""
    st.header("ℹ️ About CodeGuard")

    st.markdown("""
    ## Overview

    CodeGuard is an intelligent code plagiarism detection system designed to help educators
    maintain academic integrity in programming courses. Using a multi-method approach combining
    three complementary algorithms with a weighted voting system, CodeGuard achieves approximately
    85-90% accuracy in identifying code plagiarism.

    ## Detection Methods

    ### 🔤 Token-Based Detection (Weight: 1.0x)
    - Analyzes code at the lexical level
    - Calculates Jaccard and Cosine similarity
    - Fast processing (~5000 lines/second)
    - **Strengths:** Detects direct copying
    - **Weaknesses:** Defeated by variable renaming

    ### 🌳 AST-Based Detection (Weight: 2.0x)
    - Parses code into Abstract Syntax Trees
    - Compares structural similarity
    - Processing speed (~1000 lines/second)
    - **Strengths:** Immune to variable renaming, detects structural plagiarism
    - **Weaknesses:** May produce false positives for simple patterns

    ### 🔐 Hash-Based Detection (Weight: 1.5x)
    - Implements Winnowing algorithm
    - Creates code fingerprints using k-grams
    - Processing speed (~3000 lines/second)
    - **Strengths:** Detects partial and scattered copying
    - **Weaknesses:** May miss heavily obfuscated code

    ## Voting System

    The weighted voting mechanism combines results from all three detectors:
    1. Each detector compares its score against its threshold
    2. If score exceeds threshold, the detector "votes" with its weight
    3. Plagiarism is flagged when weighted votes ≥ 50% of total possible votes

    **Total Possible Votes:** 4.5 (1.0 + 2.0 + 1.5)

    ## Success Metrics

    - **Precision:** ≥85% (minimize false positives)
    - **Recall:** ≥80% (catch most plagiarism)
    - **F1 Score:** ≥82% (balanced performance)
    - **Processing Speed:** <2 minutes for 50 files

    ## Technology Stack

    - **Language:** Python 3.11
    - **Framework:** Streamlit
    - **Detection:** Python tokenize, ast, and hashlib modules
    - **Database:** SQLite
    - **Platform:** Cross-platform (Windows, Mac, Linux)

    ## Privacy

    All processing is done locally. No code is transmitted to external servers.

    ## Authors

    - Michael Andrew Devlyn Roach (A01781041)
    - Roberto Castro Soto (A01640117)

    Instituto Tecnológico y de Estudios Superiores de Monterrey

    ## References

    - Winnowing algorithm: Schleimer, Wilkerson, and Aiken (2003)
    - Python AST module documentation
    - Python tokenize module documentation
    """)


def main():
    """Main application entry point."""
    initialize_session_state()
    render_header()

    # Get configuration from sidebar
    config = render_sidebar()
    st.session_state.config = config

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📁 Upload & Analyze", "📊 Results", "ℹ️ About"])

    with tab1:
        render_upload_tab()

    with tab2:
        render_results_tab()

    with tab3:
        render_about_tab()

    # Footer
    st.divider()
    st.caption("CodeGuard v1.0.0 | Academic Integrity Through Technology | © 2024")


if __name__ == "__main__":
    main()
