"""
CodeGuard - Task 4.1: Streamlit App with Database Integration

This is an enhanced Streamlit application that integrates the TokenDetector
with persistent database storage for analysis history.

Features:
- File upload widget (2-100 Python files)
- TokenDetector integration
- Progress bar during analysis
- Results display with interactive table
- JSON export functionality
- Session state management
- Database integration for persistent storage
- Analysis history tab with past results
- Enhanced metrics and statistics

Author: CodeGuard Team
Date: 2024-11-12
Version: 2.0 (Database Integration)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from src.detectors.token_detector import TokenDetector
from src.database.connection import init_db
from src.database.operations import (
    create_analysis_job,
    save_batch_results,
    update_job_status,
    get_recent_jobs,
    get_job_results,
    get_job_summary,
    get_plagiarism_count
)

# ============================================================================
# CONSTANTS
# ============================================================================

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB in bytes
MIN_FILES = 2
MAX_FILES = 100
ALLOWED_EXTENSIONS = ['.py']
DEFAULT_THRESHOLD = 0.7

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_session_state():
    """
    Initialize session state variables.

    Session state preserves data across Streamlit reruns, ensuring
    uploaded files and analysis results persist during user interaction.
    """
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'detector_threshold' not in st.session_state:
        st.session_state.detector_threshold = DEFAULT_THRESHOLD
    if 'file_contents' not in st.session_state:
        st.session_state.file_contents = {}
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'current_job_id' not in st.session_state:
        st.session_state.current_job_id = None
    if 'selected_job_id' not in st.session_state:
        st.session_state.selected_job_id = None
    if 'view_history_details' not in st.session_state:
        st.session_state.view_history_details = False


# ============================================================================
# FILE VALIDATION
# ============================================================================

def validate_uploaded_files(files) -> Tuple[bool, str]:
    """
    Validate uploaded files meet requirements.

    Args:
        files: List of uploaded file objects from st.file_uploader

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if all files pass validation
            - error_message: Description of validation error, or success message

    Validation checks:
        1. File count (minimum 2, maximum 100)
        2. File extension (.py only)
        3. File size (max 16MB per file)
    """
    # Check file count
    if len(files) < MIN_FILES:
        return False, f"Please upload at least {MIN_FILES} Python files."

    if len(files) > MAX_FILES:
        return False, f"Maximum {MAX_FILES} files allowed. You uploaded {len(files)} files."

    # Check each file
    for file in files:
        # Check file extension
        if not file.name.endswith('.py'):
            return False, f"File '{file.name}' is not a Python file (.py extension required)"

        # Check file size
        if file.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            file_mb = file.size / (1024 * 1024)
            return False, f"File '{file.name}' ({file_mb:.2f}MB) exceeds {max_mb:.0f}MB limit"

    return True, "All files valid"


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

def analyze_files(files, threshold: float) -> pd.DataFrame:
    """
    Analyze all file pairs using TokenDetector.

    This function:
    1. Creates a TokenDetector instance with the specified threshold
    2. Generates all possible file pairs (N*(N-1)/2 combinations)
    3. Analyzes each pair using token-based similarity
    4. Displays progress in real-time
    5. Returns results as a formatted DataFrame

    Args:
        files: List of uploaded file objects
        threshold: Similarity threshold (0.0-1.0) for plagiarism detection

    Returns:
        pd.DataFrame: Results with columns:
            - File 1: First file name
            - File 2: Second file name
            - Jaccard Similarity (%): Jaccard similarity score as percentage
            - Cosine Similarity (%): Cosine similarity score as percentage
            - Combined Similarity (%): Average of Jaccard and Cosine
            - Plagiarized: Check mark (✓) or cross (✗) based on threshold
    """
    # Create detector instance
    detector = TokenDetector(threshold=threshold)
    results = []

    # Generate all file pairs (combinations, not permutations)
    # For N files, this creates N*(N-1)/2 pairs
    pairs = [(files[i], files[j])
             for i in range(len(files))
             for j in range(i+1, len(files))]

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Analyze each pair
    for idx, (file1, file2) in enumerate(pairs):
        # Update progress
        progress = (idx + 1) / len(pairs)
        progress_bar.progress(progress)
        status_text.text(f"Analyzing pair {idx+1}/{len(pairs)}: {file1.name} vs {file2.name}")

        # Read file contents
        # Note: We decode bytes to string for the detector
        code1 = file1.read().decode('utf-8')
        code2 = file2.read().decode('utf-8')

        # Reset file pointers for potential re-reading
        file1.seek(0)
        file2.seek(0)

        # Run detector using compare() method
        # compare() returns the combined similarity score
        # We need to access the detector's internal methods for individual scores
        result = detector.compare(code1, code2)

        # Get individual similarity metrics
        # Tokenize both code strings
        tokens1 = detector._tokenize_code(code1)
        tokens2 = detector._tokenize_code(code2)

        # Calculate individual metrics
        jaccard_sim = detector._calculate_jaccard_similarity(tokens1, tokens2)
        cosine_sim = detector._calculate_cosine_similarity(tokens1, tokens2)

        # Combined similarity (average of Jaccard and Cosine)
        combined_sim = result

        # Determine if plagiarized based on threshold
        is_plagiarized = combined_sim >= threshold

        # Store result
        results.append({
            'File 1': file1.name,
            'File 2': file2.name,
            'Jaccard Similarity (%)': jaccard_sim * 100,
            'Cosine Similarity (%)': cosine_sim * 100,
            'Combined Similarity (%)': combined_sim * 100,
            'Plagiarized': '✓' if is_plagiarized else '✗'
        })

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    return pd.DataFrame(results)


# ============================================================================
# DATABASE INTEGRATION
# ============================================================================

def save_analysis_to_database(uploaded_files, results_df: pd.DataFrame, threshold: float) -> str:
    """
    Save analysis results to database.

    Steps:
    1. Generate unique job_id (e.g., 'job-{timestamp}')
    2. Create AnalysisJob with create_analysis_job(job_id, file_count)
    3. Convert DataFrame results to list of dicts
    4. Save all results with save_batch_results(job_id, results)
    5. Update job status to 'completed' with update_job_status(job_id, 'completed')
    6. Store job_id in st.session_state

    Args:
        uploaded_files: List of uploaded file objects
        results_df: DataFrame with analysis results
        threshold: Detection threshold used

    Returns:
        job_id (str): Generated job identifier

    Raises:
        Exception: If database operations fail
    """
    # Generate job_id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    job_id = f'job-{timestamp}'

    # Create job
    file_count = len(uploaded_files)
    create_analysis_job(job_id, file_count)

    # Prepare results for database
    results_list = []
    for _, row in results_df.iterrows():
        # Map DataFrame columns to database fields
        # Note: token_similarity and ast_similarity both use the token detector scores
        # This is a simplified version - in full system, would use all three detectors
        result = {
            'file1_name': row['File 1'],
            'file2_name': row['File 2'],
            'token_similarity': row['Combined Similarity (%)'] / 100,  # Convert back to 0-1
            'ast_similarity': row['Cosine Similarity (%)'] / 100,
            'hash_similarity': row['Jaccard Similarity (%)'] / 100,
            'is_plagiarized': row['Plagiarized'] == '✓',
            'confidence_score': row['Combined Similarity (%)'] / 100
        }
        results_list.append(result)

    # Save batch
    save_batch_results(job_id, results_list)

    # Update status
    update_job_status(job_id, 'completed')

    return job_id


# ============================================================================
# JSON EXPORT
# ============================================================================

def create_download_json(df: pd.DataFrame, threshold: float, file_count: int, job_id: Optional[str] = None) -> str:
    """
    Create JSON string for download.

    Args:
        df: DataFrame with analysis results
        threshold: Threshold used for detection
        file_count: Number of files analyzed
        job_id: Optional job identifier

    Returns:
        str: JSON-formatted string ready for download

    JSON structure includes:
        - job_id: Job identifier (if provided)
        - analysis_date: ISO timestamp
        - file_count: Number of files analyzed
        - pair_count: Number of pairs compared
        - threshold: Detection threshold used
        - results: List of comparison results
        - summary: Aggregate statistics
    """
    # Convert DataFrame to list of dictionaries
    results_list = []
    for _, row in df.iterrows():
        results_list.append({
            'file1': row['File 1'],
            'file2': row['File 2'],
            'jaccard_similarity': row['Jaccard Similarity (%)'] / 100,
            'cosine_similarity': row['Cosine Similarity (%)'] / 100,
            'combined_similarity': row['Combined Similarity (%)'] / 100,
            'is_plagiarized': row['Plagiarized'] == '✓'
        })

    # Calculate summary statistics
    total_pairs = len(df)
    plagiarized_pairs = (df['Plagiarized'] == '✓').sum()
    clean_pairs = total_pairs - plagiarized_pairs

    # Create export data structure
    export_data = {
        'analysis_date': datetime.now().isoformat(),
        'file_count': file_count,
        'pair_count': total_pairs,
        'threshold': threshold,
        'results': results_list,
        'summary': {
            'total_pairs': total_pairs,
            'plagiarized_pairs': int(plagiarized_pairs),
            'clean_pairs': int(clean_pairs)
        }
    }

    # Add job_id if provided
    if job_id:
        export_data['job_id'] = job_id

    # Convert to JSON string with indentation for readability
    return json.dumps(export_data, indent=2)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_sidebar():
    """
    Render sidebar with app information and configuration.

    Displays:
        - App title and description
        - File upload statistics
        - Detection threshold slider
        - Detector information
        - Database status
        - Instructions
    """
    st.sidebar.title("🔍 CodeGuard")
    st.sidebar.markdown("### Plagiarism Detection System")
    st.sidebar.markdown("---")

    # App description
    st.sidebar.markdown("""
    **Token-Based Detection**

    Analyzes code using lexical similarity:
    - Jaccard similarity (set overlap)
    - Cosine similarity (frequency-based)
    - Combined scoring
    """)

    st.sidebar.markdown("---")

    # Threshold configuration
    st.sidebar.subheader("⚙️ Configuration")

    threshold = st.sidebar.slider(
        "Detection Threshold",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_THRESHOLD,
        step=0.05,
        help="Similarity threshold for plagiarism detection. Higher values = stricter detection."
    )

    st.session_state.detector_threshold = threshold

    # Display current configuration
    st.sidebar.info(f"Current threshold: {threshold:.0%}")

    st.sidebar.markdown("---")

    # File statistics (if files uploaded)
    if st.session_state.uploaded_files:
        file_count = len(st.session_state.uploaded_files)
        pair_count = file_count * (file_count - 1) // 2

        st.sidebar.subheader("📊 Upload Statistics")
        st.sidebar.metric("Files Uploaded", file_count)
        st.sidebar.metric("Pairs to Analyze", pair_count)

    st.sidebar.markdown("---")

    # Database status
    st.sidebar.markdown("### 💾 Database")
    try:
        recent_jobs = get_recent_jobs(limit=1)
        if recent_jobs:
            st.sidebar.success("✓ Database connected")
            st.sidebar.caption(f"Latest: {recent_jobs[0]['created_at'][:19]}")
        else:
            st.sidebar.info("No analyses yet")
    except Exception as e:
        st.sidebar.error("✗ Database error")
        st.sidebar.caption(str(e)[:50])

    st.sidebar.markdown("---")

    # Instructions
    st.sidebar.subheader("📖 How to Use")
    st.sidebar.markdown("""
    1. Upload 2-100 Python files
    2. Adjust detection threshold
    3. Click 'Analyze for Plagiarism'
    4. Review results in table
    5. Download results as JSON
    6. View past analyses in History tab
    """)


def render_main_header():
    """Render main application header."""
    st.title("🔍 CodeGuard - Python Code Plagiarism Detection")
    st.markdown("""
    Upload Python files to detect potential plagiarism using **token-based similarity analysis**.
    The system compares all file pairs using Jaccard and Cosine similarity metrics.
    """)
    st.markdown("---")


def render_file_upload():
    """
    Render file upload widget and handle uploads.

    Returns:
        List of uploaded file objects, or None if no valid upload
    """
    st.header("📁 Upload Python Files")

    # File upload widget
    uploaded_files = st.file_uploader(
        "Choose Python files (.py)",
        type=['py'],
        accept_multiple_files=True,
        help=f"Upload {MIN_FILES}-{MAX_FILES} Python files (max {MAX_FILE_SIZE/(1024*1024):.0f}MB each)"
    )

    if uploaded_files:
        # Validate files
        is_valid, error_msg = validate_uploaded_files(uploaded_files)

        if not is_valid:
            st.error(f"❌ {error_msg}")
            return None

        # Show success and file details
        st.success(f"✓ {len(uploaded_files)} files uploaded successfully")

        # Display uploaded file names in an expander
        with st.expander("📋 View uploaded files"):
            for idx, file in enumerate(uploaded_files, 1):
                file_size_kb = file.size / 1024
                st.text(f"{idx}. {file.name} ({file_size_kb:.1f} KB)")

        # Calculate and display pair count
        pair_count = len(uploaded_files) * (len(uploaded_files) - 1) // 2
        st.info(f"ℹ️ Will analyze **{pair_count}** file pairs")

        return uploaded_files

    else:
        # Show instructions when no files uploaded
        st.info("👆 Upload Python files to get started")

        st.markdown("""
        ### Requirements
        - **Minimum files:** 2
        - **Maximum files:** 100
        - **File type:** Python (.py)
        - **Max file size:** 16MB

        ### How It Works
        1. **Tokenization**: Code is broken down into semantic tokens
        2. **Jaccard Similarity**: Measures unique token overlap
        3. **Cosine Similarity**: Measures token frequency similarity
        4. **Combined Score**: Average of both metrics
        5. **Detection**: Flagged as plagiarism if score ≥ threshold
        """)

        return None


def render_analysis_button(uploaded_files):
    """
    Render analyze button and handle analysis execution.

    Args:
        uploaded_files: List of uploaded file objects
    """
    if st.button("🔍 Analyze for Plagiarism", type="primary", use_container_width=True):
        with st.spinner("Analyzing files..."):
            try:
                # Get threshold from session state
                threshold = st.session_state.detector_threshold

                # Run analysis
                results_df = analyze_files(uploaded_files, threshold)

                # Store results in session state
                st.session_state.analysis_results = results_df
                st.session_state.uploaded_files = uploaded_files
                st.session_state.analysis_completed = True

                # Save to database
                with st.spinner("Saving results to database..."):
                    try:
                        job_id = save_analysis_to_database(uploaded_files, results_df, threshold)
                        st.session_state.current_job_id = job_id
                        st.success(f"✓ Analysis completed! Job ID: {job_id}")
                    except Exception as e:
                        st.error(f"Failed to save to database: {e}")
                        st.warning("Results are still available in this session, but won't be saved to history.")
                        st.success("✓ Analysis completed successfully!")

                st.balloons()

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)


def render_results():
    """
    Render analysis results section.

    Displays:
        - Summary metrics (total pairs, plagiarized, clean, average similarity)
        - Interactive results table
        - Download button for JSON export
    """
    if st.session_state.analysis_results is None:
        return

    st.markdown("---")
    st.header("📊 Analysis Results")

    df = st.session_state.analysis_results

    # Summary metrics
    st.subheader("Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    total_pairs = len(df)
    plagiarized_count = (df['Plagiarized'] == '✓').sum()
    clean_count = total_pairs - plagiarized_count
    avg_similarity = df['Combined Similarity (%)'].mean()

    with col1:
        st.metric(
            label="Total Pairs",
            value=total_pairs,
            help="Total number of file pairs compared"
        )

    with col2:
        st.metric(
            label="Plagiarized",
            value=plagiarized_count,
            delta=f"{(plagiarized_count/total_pairs*100):.1f}%",
            delta_color="inverse",
            help="Pairs flagged as plagiarism"
        )

    with col3:
        st.metric(
            label="Clean",
            value=clean_count,
            delta=f"{(clean_count/total_pairs*100):.1f}%",
            help="Pairs not flagged as plagiarism"
        )

    with col4:
        st.metric(
            label="Avg Similarity",
            value=f"{avg_similarity:.1f}%",
            help="Average similarity across all pairs"
        )

    st.markdown("---")

    # Results table
    st.subheader("Detailed Results")

    # Format DataFrame for display
    # Create a copy to avoid modifying session state
    display_df = df.copy()

    # Format percentage columns to 2 decimal places
    for col in ['Jaccard Similarity (%)', 'Cosine Similarity (%)', 'Combined Similarity (%)']:
        display_df[col] = display_df[col].map('{:.2f}'.format)

    # Display interactive dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "File 1": st.column_config.TextColumn("File 1", width="medium"),
            "File 2": st.column_config.TextColumn("File 2", width="medium"),
            "Jaccard Similarity (%)": st.column_config.TextColumn("Jaccard (%)", width="small"),
            "Cosine Similarity (%)": st.column_config.TextColumn("Cosine (%)", width="small"),
            "Combined Similarity (%)": st.column_config.TextColumn("Combined (%)", width="small"),
            "Plagiarized": st.column_config.TextColumn("Plagiarized?", width="small"),
        }
    )

    # Highlight plagiarized pairs
    plagiarized_df = df[df['Plagiarized'] == '✓']
    if len(plagiarized_df) > 0:
        st.warning(f"⚠️ {len(plagiarized_df)} pair(s) flagged as potential plagiarism")
    else:
        st.success("✅ No plagiarism detected in any pairs")

    # Download button
    st.markdown("---")
    st.subheader("💾 Export Results")

    json_data = create_download_json(
        df,
        st.session_state.detector_threshold,
        len(st.session_state.uploaded_files),
        st.session_state.current_job_id
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"codeguard_results_{timestamp}.json"
    if st.session_state.current_job_id:
        filename = f"{st.session_state.current_job_id}_results.json"

    st.download_button(
        label="📥 Download Results (JSON)",
        data=json_data,
        file_name=filename,
        mime="application/json",
        help="Download analysis results in JSON format",
        use_container_width=True
    )


def render_analysis_history():
    """
    Render analysis history tab showing past analyses.

    Displays:
        - List of recent jobs (up to 10)
        - Job summary statistics
        - Button to view detailed results for each job
        - Detailed results view when job is selected
    """
    st.header("📜 Analysis History")

    # Get recent jobs
    try:
        with st.spinner("Loading analysis history..."):
            recent_jobs = get_recent_jobs(limit=10)
    except Exception as e:
        st.error(f"Failed to load analysis history: {e}")
        return

    if not recent_jobs:
        st.info("No analysis history yet. Run an analysis to get started!")
        return

    # Check if we should show details for a selected job
    if st.session_state.view_history_details and st.session_state.selected_job_id:
        # Show back button
        if st.button("← Back to History List"):
            st.session_state.view_history_details = False
            st.session_state.selected_job_id = None
            st.rerun()

        # Show detailed results for selected job
        render_job_details(st.session_state.selected_job_id)
        return

    # Display list of recent jobs
    st.markdown("### Recent Analyses")
    st.caption("Showing up to 10 most recent analysis jobs")

    for job in recent_jobs:
        with st.expander(f"**{job['id']}** - {job['created_at'][:19].replace('T', ' ')}"):
            col1, col2, col3, col4 = st.columns(4)

            # Basic job info
            col1.metric("Status", job['status'].upper())
            col2.metric("Files", job['file_count'])
            col3.metric("Pairs", job['pair_count'])

            # Get detailed summary
            try:
                summary = get_job_summary(job['id'])
                col4.metric("Plagiarized", summary['plagiarized_count'])

                # Progress bar
                completion = summary['completion_percentage']
                st.progress(completion / 100, text=f"Completion: {completion:.1f}%")

                # Additional stats
                if summary['total_comparisons'] > 0:
                    st.markdown(f"""
                    **Summary:**
                    - Total comparisons: {summary['total_comparisons']}
                    - Plagiarized pairs: {summary['plagiarized_count']}
                    - Clean pairs: {summary['clean_count']}
                    - Average confidence: {summary['average_confidence']:.2%}
                    """)

                # Button to view details
                if st.button("📋 View Details", key=f"view_{job['id']}"):
                    st.session_state.selected_job_id = job['id']
                    st.session_state.view_history_details = True
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to load summary: {e}")


def render_job_details(job_id: str):
    """
    Render detailed results for a specific job.

    Args:
        job_id: Job identifier to display
    """
    st.subheader(f"Results for {job_id}")

    try:
        # Load results from database
        with st.spinner("Loading job results..."):
            results = get_job_results(job_id)
            summary = get_job_summary(job_id)
    except Exception as e:
        st.error(f"Failed to load job results: {e}")
        return

    if not results:
        st.warning("No results found for this job.")
        return

    # Display job summary
    st.markdown("### Job Summary")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Status", summary['status'].upper())
    col2.metric("Files", summary['file_count'])
    col3.metric("Total Pairs", summary['total_comparisons'])
    col4.metric("Plagiarized", summary['plagiarized_count'])

    st.markdown("---")

    # Convert to DataFrame for display
    display_data = []
    for result in results:
        display_data.append({
            'File 1': result['file1_name'],
            'File 2': result['file2_name'],
            'Jaccard Similarity (%)': result['hash_similarity'] * 100,  # Mapped from hash
            'Cosine Similarity (%)': result['ast_similarity'] * 100,   # Mapped from ast
            'Combined Similarity (%)': result['confidence_score'] * 100,
            'Plagiarized': '✓' if result['is_plagiarized'] else '✗'
        })

    df = pd.DataFrame(display_data)

    # Display detailed results
    st.markdown("### Detailed Results")

    # Format DataFrame for display
    display_df = df.copy()
    for col in ['Jaccard Similarity (%)', 'Cosine Similarity (%)', 'Combined Similarity (%)']:
        display_df[col] = display_df[col].map('{:.2f}'.format)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "File 1": st.column_config.TextColumn("File 1", width="medium"),
            "File 2": st.column_config.TextColumn("File 2", width="medium"),
            "Jaccard Similarity (%)": st.column_config.TextColumn("Jaccard (%)", width="small"),
            "Cosine Similarity (%)": st.column_config.TextColumn("Cosine (%)", width="small"),
            "Combined Similarity (%)": st.column_config.TextColumn("Combined (%)", width="small"),
            "Plagiarized": st.column_config.TextColumn("Plagiarized?", width="small"),
        }
    )

    # Highlight plagiarized pairs
    plagiarized_count = (df['Plagiarized'] == '✓').sum()
    if plagiarized_count > 0:
        st.warning(f"⚠️ {plagiarized_count} pair(s) flagged as potential plagiarism")
    else:
        st.success("✅ No plagiarism detected in any pairs")

    # Export button
    st.markdown("---")
    st.subheader("💾 Export Results")

    json_data = create_download_json(
        df,
        0.7,  # Default threshold (actual threshold not stored in current implementation)
        summary['file_count'],
        job_id
    )

    st.download_button(
        label="📥 Download Results (JSON)",
        data=json_data,
        file_name=f"{job_id}_results.json",
        mime="application/json",
        help="Download analysis results in JSON format",
        use_container_width=True
    )


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main Streamlit application entry point.

    Application flow:
    1. Initialize database
    2. Initialize session state
    3. Configure page layout
    4. Render sidebar
    5. Create tabs for New Analysis and History
    6. Handle file upload and analysis in Tab 1
    7. Display analysis history in Tab 2
    """
    # Page configuration
    st.set_page_config(
        page_title="CodeGuard - Plagiarism Detection",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()

    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Render main header
    render_main_header()

    # Create tabs for New Analysis and History
    tab1, tab2 = st.tabs(["🔍 New Analysis", "📜 Analysis History"])

    with tab1:
        # File upload section
        uploaded_files = render_file_upload()

        # Analysis button (only show if files are uploaded)
        if uploaded_files:
            render_analysis_button(uploaded_files)

        # Results section (only show if analysis completed)
        if st.session_state.analysis_completed:
            render_results()

    with tab2:
        # Analysis history section
        render_analysis_history()

    # Footer
    st.markdown("---")
    st.caption("CodeGuard v2.0 - Task 4.1: Database Integration | © 2024")


if __name__ == "__main__":
    main()
