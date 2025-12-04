"""
CodeGuard - Task 4.2: Multi-Detector Streamlit App with Database Integration

This is an enhanced Streamlit application that integrates all three plagiarism
detection algorithms (TokenDetector, ASTDetector, HashDetector) with persistent
database storage for analysis history.

Features:
- File upload widget (2-100 Python files)
- Multi-detector integration (Token, AST, Hash)
- Parallel detection with progress tracking
- Results display with all detector metrics
- Sidebar filters for detector results
- JSON export functionality
- Session state management
- Database integration for persistent storage
- Analysis history tab with past results
- Enhanced metrics and statistics

Author: CodeGuard Team
Date: 2024-11-13
Version: 3.0 (Multi-Detector Integration)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
import sys
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from src.detectors.token_detector import TokenDetector
from src.detectors.ast_detector import ASTDetector
from src.detectors.hash_detector import HashDetector
from src.voting.voting_system import VotingSystem
from src.voting.confidence_calculator import get_confidence_level
from src.database.connection import init_db
from src.database.operations import (
    create_analysis_job,
    save_batch_results,
    update_job_status,
    get_recent_jobs,
    get_job_results,
    get_job_summary,
)
from src.core import get_preset_config

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB in bytes
MIN_FILES = 2
MAX_FILES = 100
ALLOWED_EXTENSIONS = [".py"]
DEFAULT_THRESHOLD = 0.7

# Detection thresholds for each detector
TOKEN_THRESHOLD = 0.70
AST_THRESHOLD = 0.80
HASH_THRESHOLD = 0.60

# Winnowing parameters for Hash Detector
HASH_K_GRAM = 5
HASH_WINDOW = 4

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================


def initialize_session_state():
    """
    Initialize session state variables.

    Session state preserves data across Streamlit reruns, ensuring
    uploaded files and analysis results persist during user interaction.

    Also initializes voting system configuration parameters (thresholds,
    weights, decision threshold) with default values.
    """
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "detector_threshold" not in st.session_state:
        st.session_state.detector_threshold = DEFAULT_THRESHOLD
    if "file_contents" not in st.session_state:
        st.session_state.file_contents = {}
    if "analysis_completed" not in st.session_state:
        st.session_state.analysis_completed = False
    if "current_job_id" not in st.session_state:
        st.session_state.current_job_id = None
    if "selected_job_id" not in st.session_state:
        st.session_state.selected_job_id = None
    if "view_history_details" not in st.session_state:
        st.session_state.view_history_details = False
    if "show_token_results" not in st.session_state:
        st.session_state.show_token_results = True
    if "show_ast_results" not in st.session_state:
        st.session_state.show_ast_results = True
    if "show_hash_results" not in st.session_state:
        st.session_state.show_hash_results = True
    if "show_combined_score" not in st.session_state:
        st.session_state.show_combined_score = True

    # Initialize preset selection (default to Standard)
    if "selected_preset" not in st.session_state:
        st.session_state.selected_preset = "Standard ( files > 50 lines)"
    if "previous_preset" not in st.session_state:
        st.session_state.previous_preset = "Standard ( files > 50 lines)"

    # Initialize voting system configuration from preset
    # This ensures initial values match the selected preset
    if "token_threshold" not in st.session_state:
        from src.core import get_preset
        # Get the preset based on the selected preset
        preset_map = {
            "Standard ( files > 50 lines)": "standard",
            "Simple (file < 50 lines)": "simple"
        }
        preset_name = preset_map.get(st.session_state.selected_preset, "standard")
        preset_config = get_preset(preset_name)

        # Initialize all values from the preset
        st.session_state.token_threshold = preset_config['token']['threshold']
        st.session_state.ast_threshold = preset_config['ast']['threshold']
        st.session_state.hash_threshold = preset_config['hash']['threshold']
        st.session_state.token_weight = preset_config['token']['weight']
        st.session_state.ast_weight = preset_config['ast']['weight']
        st.session_state.hash_weight = preset_config['hash']['weight']
        st.session_state.decision_threshold = preset_config.get('decision_threshold', 0.50)
    else:
        # Individual checks for other values in case they're missing
        if "ast_threshold" not in st.session_state:
            st.session_state.ast_threshold = 0.80
        if "hash_threshold" not in st.session_state:
            st.session_state.hash_threshold = 0.60
        if "token_weight" not in st.session_state:
            st.session_state.token_weight = 1.0
        if "ast_weight" not in st.session_state:
            st.session_state.ast_weight = 2.0
        if "hash_weight" not in st.session_state:
            st.session_state.hash_weight = 1.5
        if "decision_threshold" not in st.session_state:
            st.session_state.decision_threshold = 0.50


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
        if not file.name.endswith(".py"):
            return False, f"File '{file.name}' is not a Python file (.py extension required)"

        # Check file size
        if file.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            file_mb = file.size / (1024 * 1024)
            return False, f"File '{file.name}' ({file_mb:.2f}MB) exceeds {max_mb:.0f}MB limit"

    return True, "All files valid"


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate preset configuration has required structure.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If config is invalid or missing required keys

    Example:
        >>> from src.core import get_preset_config
        >>> config = get_preset_config("standard")
        >>> validate_config(config)  # No exception raised
        >>> validate_config({})  # Raises ValueError
    """
    required_keys = ['token', 'ast', 'hash']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Config missing required key: '{key}'")

        detector_config = config[key]
        if 'threshold' not in detector_config:
            raise ValueError(f"Config['{key}'] missing 'threshold'")
        if 'weight' not in detector_config:
            raise ValueError(f"Config['{key}'] missing 'weight'")
        if 'confidence_weight' not in detector_config:
            raise ValueError(f"Config['{key}'] missing 'confidence_weight'")

    # Verify at least one detector is active
    total_weight = sum(config[k]['weight'] for k in required_keys)
    if total_weight <= 0:
        raise ValueError("Config must have at least one active detector (total weight > 0)")

    logger.debug("Config validation passed")


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================


def analyze_files(files, threshold: float, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Analyze all file pairs using all three detectors (Token, AST, Hash) with VotingSystem.

    This function:
    1. Creates instances of TokenDetector, ASTDetector, HashDetector, and VotingSystem
    2. Generates all possible file pairs (N*(N-1)/2 combinations)
    3. Analyzes each pair using all three detection methods (conditionally executes hash)
    4. Uses VotingSystem to make final plagiarism determination
    5. Displays progress in real-time with detector-specific status
    6. Returns results as a formatted DataFrame with voting metrics

    Args:
        files: List of uploaded file objects
        threshold: Base similarity threshold (0.0-1.0) - legacy parameter, not used
        config: Preset configuration dict from get_preset_config().
                If None, uses STANDARD_PRESET as default.

    Returns:
        pd.DataFrame: Results with columns:
            - File 1: First file name
            - File 2: Second file name
            - token_similarity: Token similarity (0.0-1.0)
            - ast_similarity: AST similarity (0.0-1.0)
            - hash_similarity: Hash similarity (0.0-1.0)
            - hash_active: Boolean (True if hash ran, False if skipped)
            - plagiarism_detected: Boolean from voting system
            - confidence_score: Confidence score (0.0-1.0)
            - confidence_level: Level string ('Very High', 'High', etc.)
            - weighted_votes: Weighted votes received
            - token_vote: Boolean - did token detector vote for plagiarism
            - ast_vote: Boolean - did AST detector vote for plagiarism
            - hash_vote: Boolean - did hash detector vote for plagiarism
            - preset_name: String - which preset was used
            - Plus display columns with percentages and verdicts
    """
    # Default to standard preset if not provided
    if config is None:
        config = get_preset_config("standard")
        preset_name = "Standard (Default)"
        logger.info("No config provided, using STANDARD preset as default")
    else:
        preset_name = config.get('name', 'Custom')
        logger.info(f"Using provided config: {preset_name}")

    # Validate configuration
    validate_config(config)

    # Log configuration details
    logger.info(f"Starting plagiarism detection with preset: {preset_name}")
    logger.info(f"Detector weights - Token: {config['token']['weight']:.1f}, "
                f"AST: {config['ast']['weight']:.1f}, Hash: {config['hash']['weight']:.1f}")
    logger.info(f"Total files: {len(files)}")

    # Determine if hash detector is active
    hash_active = config['hash']['weight'] > 0.0
    logger.info(f"Hash detector status: {'ACTIVE' if hash_active else 'DISABLED (weight=0.0)'}")

    # Create detector instances with thresholds from config
    token_detector = TokenDetector(threshold=config['token']['threshold'])
    ast_detector = ASTDetector(threshold=config['ast']['threshold'])

    # Only create hash detector if it will be used
    if hash_active:
        hash_detector = HashDetector(
            threshold=config['hash']['threshold'], k=HASH_K_GRAM, w=HASH_WINDOW
        )
        logger.info(f"Hash detector initialized with threshold={config['hash']['threshold']:.2f}, k={HASH_K_GRAM}, w={HASH_WINDOW}")
    else:
        hash_detector = None
        logger.info("Hash detector initialization SKIPPED (disabled in config)")

    # Create VotingSystem instance with configuration
    voter = VotingSystem(config=config)

    results = []

    # Generate all file pairs (combinations, not permutations)
    # For N files, this creates N*(N-1)/2 pairs
    pairs = [(files[i], files[j]) for i in range(len(files)) for j in range(i + 1, len(files))]

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_pairs = len(pairs)

    # Analyze each pair with all three detectors
    for idx, (file1, file2) in enumerate(pairs):
        # Read file contents once for all detectors
        code1 = file1.read().decode("utf-8")
        code2 = file2.read().decode("utf-8")

        # Reset file pointers for potential re-reading
        file1.seek(0)
        file2.seek(0)

        # Calculate base progress for this pair
        base_progress = idx / total_pairs

        # ===== TOKEN DETECTOR =====
        status_text.text(
            f"Token Detector: Pair {idx + 1}/{total_pairs} - {file1.name} vs {file2.name}"
        )
        progress_bar.progress(base_progress + (0.33 / total_pairs))

        try:
            # Get token detector results
            tokens1 = token_detector._tokenize_code(code1)
            tokens2 = token_detector._tokenize_code(code2)

            jaccard_sim = token_detector._calculate_jaccard_similarity(tokens1, tokens2)
            cosine_sim = token_detector._calculate_cosine_similarity(tokens1, tokens2)
            token_sim = (jaccard_sim + cosine_sim) / 2.0

            token_verdict = "🚨 FLAGGED" if token_sim >= config['token']['threshold'] else "✅ CLEAR"
            logger.debug(f"Token detector: {file1.name} vs {file2.name}, score={token_sim:.3f}")
        except Exception as e:
            st.warning(f"Token Detector error on {file1.name} vs {file2.name}: {str(e)[:50]}")
            jaccard_sim, cosine_sim, token_sim = 0.0, 0.0, 0.0
            token_verdict = "⚠️ ERROR"
            logger.error(f"Token detector error: {str(e)}")

        # ===== AST DETECTOR =====
        status_text.text(f"AST Detector: Pair {idx + 1}/{total_pairs} - {file1.name} vs {file2.name}")
        progress_bar.progress(base_progress + (0.66 / total_pairs))

        try:
            ast_sim = ast_detector.compare(code1, code2)
            ast_verdict = "🚨 FLAGGED" if ast_sim >= config['ast']['threshold'] else "✅ CLEAR"
            logger.debug(f"AST detector: {file1.name} vs {file2.name}, score={ast_sim:.3f}")
        except Exception as e:
            st.warning(f"AST Detector error on {file1.name} vs {file2.name}: {str(e)[:50]}")
            ast_sim = 0.0
            ast_verdict = "⚠️ ERROR"
            logger.error(f"AST detector error: {str(e)}")

        # ===== HASH DETECTOR (CONDITIONAL) =====
        # Performance note: Skipping hash detector on simple problems saves ~30-40% execution time
        # Hash detector uses Winnowing algorithm which is expensive on small files
        # In Simple preset (files <50 lines), hash is ineffective anyway (0% precision)
        if hash_active:
            status_text.text(
                f"Hash Detector: Pair {idx + 1}/{total_pairs} - {file1.name} vs {file2.name}"
            )
            progress_bar.progress(base_progress + (1.0 / total_pairs))

            try:
                hash_sim = hash_detector.compare(code1, code2)
                hash_verdict = "🚨 FLAGGED" if hash_sim >= config['hash']['threshold'] else "✅ CLEAR"
                logger.debug(f"Hash detector executed: {file1.name} vs {file2.name}, score={hash_sim:.3f}")
            except Exception as e:
                st.warning(f"Hash Detector error on {file1.name} vs {file2.name}: {str(e)[:50]}")
                hash_sim = 0.0
                hash_verdict = "⚠️ ERROR"
                logger.error(f"Hash detector error: {str(e)}")
        else:
            # Hash detector SKIPPED - weight is 0.0
            hash_sim = 0.0
            hash_verdict = "⏭️ SKIPPED"
            logger.debug(f"Hash detector SKIPPED (disabled): {file1.name} vs {file2.name}")
            # Update progress to show completion
            progress_bar.progress(base_progress + (1.0 / total_pairs))

        # ===== VOTING SYSTEM =====
        status_text.text(
            f"Voting System: Pair {idx + 1}/{total_pairs} - {file1.name} vs {file2.name}"
        )

        try:
            # Use VotingSystem for unified decision
            voting_result = voter.vote(token_sim=token_sim, ast_sim=ast_sim, hash_sim=hash_sim)

            # DEBUG: Log voting decision for this pair
            logger.info(f"\nPair {idx + 1}: {file1.name} vs {file2.name}")
            logger.info(f"  Token: {token_sim:.3f} {'✓' if voting_result['votes']['token'] > 0 else '✗'}")
            logger.info(f"  AST: {ast_sim:.3f} {'✓' if voting_result['votes']['ast'] > 0 else '✗'}")
            logger.info(f"  Hash: {hash_sim:.3f} {'✓' if voting_result['votes']['hash'] > 0 else '⏭ SKIPPED' if config['hash']['weight'] == 0 else '✗'}")
            logger.info(f"  Result: {'PLAGIARIZED' if voting_result['is_plagiarized'] else 'CLEAR'}")

            # Extract voting information
            is_plagiarized = voting_result["is_plagiarized"]
            confidence_score = voting_result["confidence_score"]
            confidence_level = get_confidence_level(confidence_score)
            votes = voting_result["votes"]  # {'token': bool, 'ast': bool, 'hash': bool}
            weighted_votes = voting_result["weighted_votes"]

            # Create overall status based on voting decision
            if is_plagiarized:
                overall_status = f"⚠️ PLAGIARIZED ({confidence_level})"
            else:
                overall_status = f"✅ CLEAR ({confidence_level})"

            # Log voting decision
            logger.info(
                f"Pair {idx + 1}/{total_pairs}: {file1.name} vs {file2.name} - "
                f"{'PLAGIARISM' if is_plagiarized else 'CLEAR'} "
                f"(confidence={confidence_score:.3f}, weighted_votes={weighted_votes:.2f})"
            )

        except Exception as e:
            st.warning(f"Voting System error on {file1.name} vs {file2.name}: {str(e)[:50]}")
            is_plagiarized = False
            confidence_score = 0.0
            confidence_level = "Very Low"
            votes = {"token": False, "ast": False, "hash": False}
            weighted_votes = 0.0
            overall_status = "⚠️ ERROR"
            logger.error(f"Voting system error: {str(e)}")

        # Store result with all detector metrics and voting information
        results.append(
            {
                # File identifiers
                "File 1": file1.name,
                "File 2": file2.name,
                # Raw similarity scores (0.0-1.0)
                "token_similarity": token_sim,
                "token_jaccard": jaccard_sim,
                "token_cosine": cosine_sim,
                "ast_similarity": ast_sim,
                "hash_similarity": hash_sim,
                "hash_active": hash_active,  # NEW: indicates if hash ran
                # Voting results
                "plagiarism_detected": is_plagiarized,
                "confidence_score": confidence_score,
                "confidence_level": confidence_level,
                "weighted_votes": weighted_votes,
                "token_vote": votes["token"],
                "ast_vote": votes["ast"],
                "hash_vote": votes["hash"],
                "preset_name": preset_name,  # NEW: which preset was used
                # Display columns (percentages)
                "Token Similarity (%)": token_sim * 100,
                "Token Jaccard (%)": jaccard_sim * 100,
                "Token Cosine (%)": cosine_sim * 100,
                "AST Similarity (%)": ast_sim * 100,
                "Hash Similarity (%)": hash_sim * 100,
                "Confidence (%)": confidence_score * 100,
                # Verdict columns
                "Token Verdict": token_verdict,
                "AST Verdict": ast_verdict,
                "Hash Verdict": hash_verdict,
                "Overall Status": overall_status,
            }
        )

    # Final progress update
    progress_bar.progress(1.0)
    status_text.text("✅ Analysis complete!")

    return pd.DataFrame(results)


# ============================================================================
# DATABASE INTEGRATION
# ============================================================================


def save_analysis_to_database(uploaded_files, results_df: pd.DataFrame, threshold: float) -> str:
    """
    Save analysis results to database with all three detector scores.

    Steps:
    1. Generate unique job_id (e.g., 'job-{timestamp}')
    2. Create AnalysisJob with create_analysis_job(job_id, file_count)
    3. Convert DataFrame results to list of dicts with all detector scores
    4. Save all results with save_batch_results(job_id, results)
    5. Update job status to 'completed' with update_job_status(job_id, 'completed')
    6. Store job_id in st.session_state

    Args:
        uploaded_files: List of uploaded file objects
        results_df: DataFrame with analysis results from all detectors
        threshold: Detection threshold used (legacy parameter, kept for compatibility)

    Returns:
        job_id (str): Generated job identifier

    Raises:
        Exception: If database operations fail
    """
    # Generate job_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"job-{timestamp}"

    # Create job
    file_count = len(uploaded_files)
    create_analysis_job(job_id, file_count)

    # Prepare results for database with voting system results
    results_list = []
    for _, row in results_df.iterrows():
        # Map DataFrame columns to database fields
        # Uses voting system's is_plagiarized and confidence_score
        result = {
            "file1_name": row["File 1"],
            "file2_name": row["File 2"],
            "token_similarity": row["token_similarity"],
            "ast_similarity": row["ast_similarity"],
            "hash_similarity": row["hash_similarity"],
            "is_plagiarized": row["plagiarism_detected"],
            "confidence_score": row["confidence_score"],
        }
        results_list.append(result)

    # Save batch
    save_batch_results(job_id, results_list)

    # Update status
    update_job_status(job_id, "completed")

    return job_id


# JSON EXPORT FUNCTIONALITY REMOVED - CSV export is now the primary export format


# ============================================================================
# UI COMPONENTS
# ============================================================================


def render_sidebar():
    """
    Render sidebar with app information and configuration.

    Displays:
        - Detection mode preset selector (NEW)
        - Voting system configuration controls (thresholds, weights, decision threshold)
        - Reset to defaults button
        - Current configuration display
        - Multi-detector information
        - Detection method filters
        - File upload statistics
        - Database status
        - Instructions
    """
    # ========================================
    # DETECTION CONFIGURATION (PRESET SELECTOR)
    # ========================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("Detection Configuration")

    # Use key parameter to bind radio button directly to session state
    detection_mode = st.sidebar.radio(
        "Detection Mode",
        options=["Standard ( files > 50 lines)", "Simple (file < 50 lines)"],
        index=0,  # Default to Standard mode
        key="selected_preset",  # CRITICAL: Bind directly to session state
        help="""
**Standard Mode:**
- For typical assignments (50+ lines)
- Games, data structures, algorithms
- Uses all three detectors (Token, AST, Hash)
- 100% precision on realistic code

**Simple Mode:**
- For short assignments (<50 lines)
- FizzBuzz, factorial, palindrome checks
- Hash detector DISABLED (ineffective on small files)
- Stricter AST threshold to reduce false positives
        """,
    )

    # Handle preset changes
    if st.session_state.selected_preset != st.session_state.get('previous_preset', st.session_state.selected_preset):
        # Preset changed - UPDATE ALL SESSION STATE VALUES TO MATCH NEW PRESET
        st.session_state.previous_preset = st.session_state.selected_preset

        # Get new preset configuration
        preset_map = {
            "Standard ( files > 50 lines)": "standard",
            "Simple (file < 50 lines)": "simple",
        }
        new_preset_name = preset_map[st.session_state.selected_preset]

        from src.core import get_preset
        new_preset_config = get_preset(new_preset_name)

        # CRITICAL FIX: Delete ALL widget keys before setting new values
        # This prevents Streamlit's "cannot modify after widget instantiation" error
        widget_keys = [
            'token_threshold', 'ast_threshold', 'hash_threshold',
            'token_weight', 'ast_weight', 'hash_weight',
            'decision_threshold'
        ]

        logger.info(f"PRESET CHANGE: {st.session_state.previous_preset} → {st.session_state.selected_preset}")
        logger.info(f"Deleting widget keys and resetting to preset defaults...")

        for key in widget_keys:
            if key in st.session_state:
                old_value = st.session_state[key]
                del st.session_state[key]
                logger.debug(f"  Deleted {key} (was {old_value})")

        # Set new preset values in session state
        st.session_state.token_threshold = new_preset_config['token']['threshold']
        st.session_state.ast_threshold = new_preset_config['ast']['threshold']
        st.session_state.hash_threshold = new_preset_config['hash']['threshold']
        st.session_state.token_weight = new_preset_config['token']['weight']
        st.session_state.ast_weight = new_preset_config['ast']['weight']
        st.session_state.hash_weight = new_preset_config['hash']['weight']  # ← CRITICAL: Now updates to 0.0 in Simple mode!
        st.session_state.decision_threshold = new_preset_config.get('decision_threshold', 0.50)

        logger.info(f"AFTER PRESET CHANGE:")
        logger.info(f"  Token: threshold={st.session_state.token_threshold:.2f}, weight={st.session_state.token_weight:.1f}")
        logger.info(f"  AST: threshold={st.session_state.ast_threshold:.2f}, weight={st.session_state.ast_weight:.1f}")
        logger.info(f"  Hash: threshold={st.session_state.hash_threshold:.2f}, weight={st.session_state.hash_weight:.1f}")
        logger.info(f"  Decision threshold: {st.session_state.decision_threshold:.2f}")

        # Clear previous analysis results when preset changes
        if "analysis_results" in st.session_state:
            st.session_state.analysis_results = None
            st.session_state.analysis_completed = False

        # Show success message
        st.sidebar.success(f"Switched to {st.session_state.selected_preset}")
        st.rerun()

    # Show configuration details in expander
    with st.sidebar.expander("View Configuration Details", expanded=False):
        from src.core import get_preset

        # Map display name to preset name
        preset_map = {
            "Standard ( files > 50 lines)": "standard",
            "Simple (file < 50 lines)": "simple",
        }
        preset_name = preset_map[detection_mode]

        # Get and display preset configuration
        preset_config = get_preset(preset_name)

        st.markdown(f"**{preset_config['name']}**")
        st.caption(preset_config["description"])

        st.markdown("**Detector Configuration:**")

        # Token detector
        st.markdown("Token Detector:")
        st.code(
            f"""Threshold: {preset_config['token']['threshold']}
Weight: {preset_config['token']['weight']}
Confidence: {preset_config['token']['confidence_weight']}"""
        )

        # AST detector
        st.markdown("AST Detector:")
        st.code(
            f"""Threshold: {preset_config['ast']['threshold']}
Weight: {preset_config['ast']['weight']}
Confidence: {preset_config['ast']['confidence_weight']}"""
        )

        # Hash detector (highlight if disabled)
        if preset_config["hash"]["weight"] == 0.0:
            st.markdown("Hash Detector: **DISABLED**")
            st.caption("Hash detector is disabled in this mode")
        else:
            st.markdown("Hash Detector: **ACTIVE**")
            st.code(
                f"""Threshold: {preset_config['hash']['threshold']}
Weight: {preset_config['hash']['weight']}
Confidence: {preset_config['hash']['confidence_weight']}"""
            )

        # Decision threshold
        total_votes = (
            preset_config["token"]["weight"]
            + preset_config["ast"]["weight"]
            + preset_config["hash"]["weight"]
        )
        decision_threshold = 0.50 * total_votes
        st.markdown("**Decision Threshold:**")
        st.code(f"{decision_threshold} votes (50% of {total_votes})")

    st.sidebar.markdown("---")

    # ===== VOTING SYSTEM CONFIGURATION =====
    with st.sidebar.expander("Detection Thresholds", expanded=False):
        st.caption("Minimum scores for detectors to vote for plagiarism")

        # Token threshold slider
        # FIX: Remove assignment that overwrites session_state
        # Use key parameter for automatic session_state sync
        st.slider(
            "Token Threshold",
            min_value=0.5,
            max_value=0.9,
            value=st.session_state.token_threshold,
            step=0.05,
            help="Minimum similarity score for Token detector to flag plagiarism. Lower = more sensitive.",
            key="token_threshold",  # Key matches session_state variable name
        )

        # AST threshold slider
        # FIX: Remove assignment that overwrites session_state
        st.slider(
            "AST Threshold",
            min_value=0.6,
            max_value=0.95,
            value=st.session_state.ast_threshold,
            step=0.05,
            help="Minimum similarity score for AST detector to flag plagiarism. AST detects structural similarity.",
            key="ast_threshold",  # Key matches session_state variable name
        )

        # Hash threshold slider (only show if hash detector is enabled)
        if st.session_state.hash_weight > 0:
            st.slider(
                "Hash Threshold",
                min_value=0.4,
                max_value=0.8,
                value=st.session_state.hash_threshold,
                step=0.05,
                help="Minimum similarity score for Hash detector to flag plagiarism. Hash detects partial copying.",
                key="hash_threshold",  # Key matches session_state variable name
            )
        else:
            # Hash disabled - ensure value exists in session_state for when it's re-enabled
            if 'hash_threshold' not in st.session_state:
                from src.core import get_preset
                preset_map = {
                    "Standard ( files > 50 lines)": "standard",
                    "Simple (file < 50 lines)": "simple"
                }
                preset_name = preset_map.get(st.session_state.selected_preset, "standard")
                preset_config = get_preset(preset_name)
                st.session_state.hash_threshold = preset_config['hash']['threshold']
            st.info("Hash detector disabled in Simple Problems mode")

    # ===== VOTING WEIGHTS =====
    with st.sidebar.expander("Detector Weights", expanded=False):
        st.caption("Influence of each detector on final decision")

        # Token weight slider
        # FIX: Remove assignment that overwrites session_state
        st.slider(
            "Token Weight",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.token_weight,
            step=0.1,
            help="Voting weight for Token detector. Higher weight = more influence on final decision.",
            key="token_weight",  # Key matches session_state variable name
        )

        # AST weight slider
        # FIX: Remove assignment that overwrites session_state
        st.slider(
            "AST Weight",
            min_value=1.0,
            max_value=3.0,
            value=st.session_state.ast_weight,
            step=0.1,
            help="Voting weight for AST detector. AST is most reliable, so higher weight is recommended.",
            key="ast_weight",  # Key matches session_state variable name
        )

        # Hash weight slider (only show if hash detector is currently enabled)
        # CRITICAL FIX: Check both hash_weight AND selected preset to prevent slider from re-enabling
        is_simple_mode = "Simple" in st.session_state.selected_preset
        if st.session_state.hash_weight > 0 and not is_simple_mode:
            st.slider(
                "Hash Weight",
                min_value=0.5,
                max_value=2.5,
                value=st.session_state.hash_weight,
                step=0.1,
                help="Voting weight for Hash detector. Good for detecting scattered copying.",
                key="hash_weight",  # Key matches session_state variable name
            )
        else:
            # Hash disabled - show disabled slider with locked value
            st.slider(
                "Hash Weight",
                min_value=0.0,
                max_value=2.5,
                value=0.0,
                step=0.1,
                disabled=True,
                key="hash_weight_disabled",
                help="Hash detector is disabled in Simple Problems mode (ineffective on files <50 lines)"
            )
            # CRITICAL: Ensure hash_weight stays at 0.0 in Simple mode
            if is_simple_mode:
                st.session_state.hash_weight = 0.0

    # ===== DECISION THRESHOLD =====
    st.sidebar.markdown("**Decision Threshold**")
    st.sidebar.caption("% of weighted votes needed to flag plagiarism")

    # FIX: Remove assignment that overwrites session_state
    st.sidebar.slider(
        "Plagiarism Decision Threshold",
        min_value=0.3,
        max_value=0.7,
        value=st.session_state.decision_threshold,
        step=0.05,
        help="Percentage of total weighted votes required to flag plagiarism. 0.50 = 50% of votes needed.",
        label_visibility="collapsed",
        key="decision_threshold",  # Key matches session_state variable name
    )

    st.sidebar.markdown("---")

    # ===== RESET TO DEFAULTS BUTTON =====
    if st.sidebar.button("🔄 Reset to Defaults", help="Reset all configuration to current preset defaults"):
        # Get current preset (determine which preset is currently selected)
        preset_map = {
            "Standard ( files > 50 lines)": "standard",
            "Simple (file < 50 lines)": "simple"
        }
        selected_preset_display = st.session_state.get('selected_preset', 'Standard ( files > 50 lines)')
        preset_name = preset_map[selected_preset_display]

        # Enhanced debug logging
        logger.info("=" * 80)
        logger.info(f"RESET BUTTON CLICKED - Preset: {preset_name}")
        logger.info("=" * 80)

        # Load preset default values
        from src.core import get_preset
        preset_config = get_preset(preset_name)

        # Log current values before reset
        logger.info("BEFORE RESET:")
        logger.info(f"  Token Threshold: {st.session_state.token_threshold:.2f} → {preset_config['token']['threshold']:.2f}")
        logger.info(f"  AST Threshold: {st.session_state.ast_threshold:.2f} → {preset_config['ast']['threshold']:.2f}")
        logger.info(f"  Hash Threshold: {st.session_state.hash_threshold:.2f} → {preset_config['hash']['threshold']:.2f}")
        logger.info(f"  Token Weight: {st.session_state.token_weight:.1f} → {preset_config['token']['weight']:.1f}")
        logger.info(f"  AST Weight: {st.session_state.ast_weight:.1f} → {preset_config['ast']['weight']:.1f}")
        logger.info(f"  Hash Weight: {st.session_state.hash_weight:.1f} → {preset_config['hash']['weight']:.1f}")
        logger.info(f"  Decision Threshold: {st.session_state.decision_threshold:.2f} → {preset_config.get('decision_threshold', 0.50):.2f}")

        # CRITICAL FIX: Delete all widget keys BEFORE setting new values
        # This disconnects them from Streamlit widgets and prevents the
        # "cannot be modified after widget instantiation" error
        widget_keys = [
            'token_threshold',
            'ast_threshold',
            'hash_threshold',
            'token_weight',
            'ast_weight',
            'hash_weight',
            'decision_threshold'
        ]

        logger.info("Deleting widget keys to allow reset...")
        for key in widget_keys:
            if key in st.session_state:
                del st.session_state[key]
                logger.debug(f"  Deleted key: {key}")

        # Now safe to set new values (keys are disconnected from widgets)
        st.session_state.token_threshold = preset_config['token']['threshold']
        st.session_state.ast_threshold = preset_config['ast']['threshold']
        st.session_state.hash_threshold = preset_config['hash']['threshold']

        # Reset all weight values to preset defaults
        st.session_state.token_weight = preset_config['token']['weight']
        st.session_state.ast_weight = preset_config['ast']['weight']
        st.session_state.hash_weight = preset_config['hash']['weight']

        # Reset decision threshold (use percentage directly)
        st.session_state.decision_threshold = preset_config.get('decision_threshold', 0.50)

        # Log values after reset
        logger.info("AFTER RESET:")
        logger.info(f"  Token Threshold: {st.session_state.token_threshold:.2f}")
        logger.info(f"  AST Threshold: {st.session_state.ast_threshold:.2f}")
        logger.info(f"  Hash Threshold: {st.session_state.hash_threshold:.2f}")
        logger.info(f"  Token Weight: {st.session_state.token_weight:.1f}")
        logger.info(f"  AST Weight: {st.session_state.ast_weight:.1f}")
        logger.info(f"  Hash Weight: {st.session_state.hash_weight:.1f}")
        logger.info(f"  Decision Threshold: {st.session_state.decision_threshold:.2f}")
        logger.info("=" * 80)

        # Show success message
        st.sidebar.success(f"✅ Reset to {preset_config['name']} defaults")

        # Force UI refresh to update sliders
        st.rerun()

    st.sidebar.markdown("---")

    # ===== CURRENT CONFIGURATION DISPLAY =====
    with st.sidebar.expander("Current Configuration", expanded=False):
        st.write("**Detection Thresholds:**")
        st.write(f"• Token: {st.session_state.token_threshold:.2f}")
        st.write(f"• AST: {st.session_state.ast_threshold:.2f}")
        if st.session_state.hash_weight > 0:
            st.write(f"• Hash: {st.session_state.hash_threshold:.2f}")
        else:
            st.write(f"• Hash: DISABLED")

        st.write("\n**Voting Weights:**")
        st.write(f"• Token: {st.session_state.token_weight:.1f}x")
        st.write(f"• AST: {st.session_state.ast_weight:.1f}x")
        if st.session_state.hash_weight > 0:
            st.write(f"• Hash: {st.session_state.hash_weight:.1f}x")
        else:
            st.write(f"• Hash: DISABLED (0.0x)")

        # Calculate total possible votes
        total_votes = (
            st.session_state.token_weight
            + st.session_state.ast_weight
            + st.session_state.hash_weight
        )
        required_votes = total_votes * st.session_state.decision_threshold

        st.write("\n**Decision Criteria:**")
        st.write(f"• Total Possible Votes: {total_votes:.1f}")
        st.write(
            f"• Required Votes: {required_votes:.2f} ({st.session_state.decision_threshold:.0%})"
        )
        st.write(f"• Decision: Plagiarism if weighted votes ≥ {required_votes:.2f}")

    # ===== CONFIGURATION STATUS INDICATOR =====
    # Show warning if non-default configuration (compare against current preset)
    preset_map = {
        "Standard ( files > 50 lines)": "standard",
        "Simple (file < 50 lines)": "simple"
    }
    selected_preset_display = st.session_state.get('selected_preset', 'Standard ( files > 50 lines)')
    preset_name = preset_map[selected_preset_display]

    from src.core import get_preset
    current_preset = get_preset(preset_name)

    # Check if current values differ from preset defaults
    expected_decision_threshold = current_preset.get('decision_threshold', 0.50)

    if (
        st.session_state.token_threshold != current_preset['token']['threshold']
        or st.session_state.ast_threshold != current_preset['ast']['threshold']
        or st.session_state.hash_threshold != current_preset['hash']['threshold']
        or st.session_state.token_weight != current_preset['token']['weight']
        or st.session_state.ast_weight != current_preset['ast']['weight']
        or st.session_state.hash_weight != current_preset['hash']['weight']
        or abs(st.session_state.decision_threshold - expected_decision_threshold) > 0.01
    ):
        st.sidebar.info(" Using custom configuration")
    else:
        st.sidebar.success(f" Using {current_preset['name']} defaults")

    st.sidebar.markdown("---")

    st.sidebar.markdown("---")

    # Detection Method Filters
    st.sidebar.subheader("Display Filters")

    st.session_state.show_token_results = st.sidebar.checkbox(
        "Show Token Detector",
        value=st.session_state.show_token_results,
        help="Display Token Detector similarity scores",
    )

    st.session_state.show_ast_results = st.sidebar.checkbox(
        "Show AST Detector",
        value=st.session_state.show_ast_results,
        help="Display AST Detector structural similarity",
    )

    # CRITICAL FIX: Only show hash checkbox if hash detector is active
    # In Simple Problems mode (hash_weight = 0.0), hash detector is disabled
    if st.session_state.hash_weight > 0:
        # BUG FIX: When hash is re-enabled (switching from Simple to Standard),
        # restore show_hash_results to True if it was disabled
        # This ensures hash columns reappear when switching back to Standard mode
        if not st.session_state.show_hash_results:
            st.session_state.show_hash_results = True

        st.session_state.show_hash_results = st.sidebar.checkbox(
            "Show Hash Detector",
            value=st.session_state.show_hash_results,
            help="Display Hash Detector fingerprint similarity",
        )
    else:
        # Hash detector disabled - force checkbox to False and show disabled message
        st.session_state.show_hash_results = False
        st.sidebar.checkbox(
            "Show Hash Detector",
            value=False,
            disabled=True,
            help="Hash Detector is disabled in Simple Problems mode (ineffective on files <50 lines)",
        )

    st.session_state.show_combined_score = st.sidebar.checkbox(
        "Show Combined Score",
        value=st.session_state.show_combined_score,
        help="Display average score across all detectors",
    )

    st.sidebar.markdown("---")

    # File statistics (if files uploaded)
    if st.session_state.uploaded_files:
        file_count = len(st.session_state.uploaded_files)
        pair_count = file_count * (file_count - 1) // 2

        st.sidebar.subheader("Upload Statistics")
        st.sidebar.metric("Files Uploaded", file_count)
        st.sidebar.metric("Pairs to Analyze", pair_count)
        st.sidebar.caption(f"{pair_count * 3} total detector runs")

    st.sidebar.markdown("---")

    # Instructions
    st.sidebar.subheader("How to Use")
    st.sidebar.markdown(
        """
    1. Upload 2-100 Python files
    2. Toggle detection method filters
    3. Click 'Analyze for Plagiarism'
    4. Review results from all detectors
    5. View past analyses in History tab
    """
    )


def render_main_header():
    """Render main application header with professional academic styling."""
    # Custom CSS for professional academic look
    st.markdown(
        """
    <style>
    /* Professional color scheme - Academic blues and grays */
    :root {
        --primary-blue: #1e3a8a;
        --accent-blue: #3b82f6;
        --light-gray: #f8fafc;
        --border-gray: #e2e8f0;
        --text-dark: #1e293b;
    }

    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }

    .header-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-blue);
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }

    .header-tagline {
        font-size: 1rem;
        color: #64748b;
        font-weight: 400;
        margin-top: 0.25rem;
    }

    /* Card-like sections */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid var(--border-gray);
        border-radius: 8px;
        overflow: hidden;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--primary-blue);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--light-gray);
    }

    section[data-testid="stSidebar"] .stSlider {
        padding: 0.5rem 0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid var(--border-gray);
        border-radius: 6px;
        font-weight: 500;
    }

    /* Table row highlighting */
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f9fafb;
    }

    /* Success/Error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 6px;
        padding: 1rem;
    }

    /* Upload section styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed var(--border-gray);
        border-radius: 8px;
        padding: 2rem;
        transition: border-color 0.2s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-blue);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 6px 6px 0 0;
        padding: 0 24px;
        background-color: white;
        border: 1px solid var(--border-gray);
        border-bottom: none;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue);
        color: white;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: var(--accent-blue);
    }

    /* Spacing improvements */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 600;
    }

    h2 {
        border-bottom: 2px solid var(--border-gray);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header with icon and tagline
    st.markdown(
        """
    <div class="main-header">
        <div class="header-icon">🛡️</div>
        <h1 class="header-title">CodeGuard</h1>
        <p class="header-tagline">Academic Code Plagiarism Detection</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    Upload Python files to detect potential plagiarism using **three complementary detection algorithms**
    combined through a **weighted voting system**. The system analyzes all file pairs with Token, AST,
    and Hash detectors, then aggregates results for accurate plagiarism determination with confidence scores.
    """
    )
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
        type=["py"],
        accept_multiple_files=True,
        help=f"Upload {MIN_FILES}-{MAX_FILES} Python files (max {MAX_FILE_SIZE / (1024 * 1024):.0f}MB each)",
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
        st.info(f"Analyzing **{pair_count}** file pairs")

        return uploaded_files

    else:
        # Show instructions when no files uploaded
        st.info("Upload Python files to get started")

        st.markdown(
            """
        ### Requirements
        - **Minimum files:** 2
        - **Maximum files:** 100
        - **File type:** Python (.py)
        - **Max file size:** 16MB

        """
        )

        return None


def render_analysis_button(uploaded_files):
    """
    Render analyze button and handle analysis execution.

    Args:
        uploaded_files: List of uploaded file objects
    """
    if st.button("Analyze for Plagiarism", type="primary", use_container_width=True):
        with st.spinner("Analyzing files..."):
            try:
                # Get threshold from session state
                threshold = st.session_state.detector_threshold

                # Get preset configuration based on selected mode
                preset_map = {
                    "Standard ( files > 50 lines)": "standard",
                    "Simple (file < 50 lines)": "simple",
                }
                selected_preset_name = preset_map[st.session_state.selected_preset]

                # Get preset configuration
                config = get_preset_config(selected_preset_name)

                # CRITICAL FIX: Override preset with sidebar threshold and weight values
                # This ensures user's slider settings are used instead of preset defaults
                config['token']['threshold'] = st.session_state.token_threshold
                config['token']['weight'] = st.session_state.token_weight
                config['ast']['threshold'] = st.session_state.ast_threshold
                config['ast']['weight'] = st.session_state.ast_weight
                config['hash']['threshold'] = st.session_state.hash_threshold
                config['hash']['weight'] = st.session_state.hash_weight
                config['decision_threshold'] = st.session_state.decision_threshold

                # Log the configuration being used
                logger.info("=" * 80)
                logger.info(f"STARTING PLAGIARISM DETECTION")
                logger.info(f"Selected preset: {selected_preset_name}")
                logger.info(f"Configuration after sidebar override:")
                logger.info(f"  Token: threshold={config['token']['threshold']:.2f}, weight={config['token']['weight']:.1f}")
                logger.info(f"  AST: threshold={config['ast']['threshold']:.2f}, weight={config['ast']['weight']:.1f}")
                logger.info(f"  Hash: threshold={config['hash']['threshold']:.2f}, weight={config['hash']['weight']:.1f}")
                logger.info(f"  Decision threshold: {config['decision_threshold']:.2f}")
                logger.info(f"Hash detector status: {'ACTIVE' if config['hash']['weight'] > 0 else 'DISABLED (weight=0.0)'}")
                logger.info("=" * 80)

                # Show configuration debug info in UI
                with st.expander("🔍 Debug: Configuration Used", expanded=True):
                    st.markdown("**Session State Values (from sliders):**")
                    st.code(f"""
Token Threshold: {st.session_state.token_threshold:.2f}
Token Weight: {st.session_state.token_weight:.1f}
AST Threshold: {st.session_state.ast_threshold:.2f}
AST Weight: {st.session_state.ast_weight:.1f}
Hash Threshold: {st.session_state.hash_threshold:.2f}
Hash Weight: {st.session_state.hash_weight:.1f}
Decision Threshold: {st.session_state.decision_threshold:.2f}
                    """)

                    st.markdown("**Config Object (passed to VotingSystem):**")
                    st.code(f"""
Preset: {selected_preset_name}

Token Detector:
  - Threshold: {config['token']['threshold']:.2f}
  - Weight: {config['token']['weight']:.1f}

AST Detector:
  - Threshold: {config['ast']['threshold']:.2f}
  - Weight: {config['ast']['weight']:.1f}

Hash Detector:
  - Threshold: {config['hash']['threshold']:.2f}
  - Weight: {config['hash']['weight']:.1f}
  - Status: {"ACTIVE" if config['hash']['weight'] > 0 else "DISABLED (weight=0.0)"}

Voting Configuration:
  - Total Possible Votes: {config['token']['weight'] + config['ast']['weight'] + config['hash']['weight']:.1f}
  - Decision Threshold: {config['decision_threshold']:.2f} ({config['decision_threshold']*100:.0f}%)
  - Required Votes: {(config['token']['weight'] + config['ast']['weight'] + config['hash']['weight']) * config['decision_threshold']:.2f}
                    """)

                # Run analysis with preset configuration
                results_df = analyze_files(uploaded_files, threshold, config=config)

                # Store results in session state
                st.session_state.analysis_results = results_df
                st.session_state.uploaded_files = uploaded_files
                st.session_state.analysis_completed = True

                # Save to database
                with st.spinner("Saving results to database..."):
                    try:
                        job_id = save_analysis_to_database(uploaded_files, results_df, threshold)
                        st.session_state.current_job_id = job_id
                        st.success(f"Analysis completed! Job ID: {job_id}")
                    except Exception as e:
                        st.error(f"Failed to save to database: {e}")
                        st.warning(
                            "Results are still available in this session, but won't be saved to history."
                        )
                        st.success("Analysis completed successfully!")

                # Professional completion notification
                st.success("Analysis Complete - Results ready for review")

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)


def render_results():
    """
    Render analysis results section with voting system results.

    Displays:
        - Preset indicator showing which mode was used
        - Summary metrics for all detectors and voting system
        - Confidence distribution
        - Detector agreement metrics
        - Interactive results table with filtering
        - Detailed voting breakdown for plagiarized pairs
        - Download button for comprehensive JSON export
    """
    if st.session_state.analysis_results is None:
        return

    st.markdown("---")

    # Display which preset was used
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("Analysis Results")

    with col2:
        # Show preset badge
        preset_name = st.session_state.get("selected_preset", "Standard ( files > 50 lines)")
        if "Simple" in preset_name:
            st.info("Simple Mode")
        else:
            st.success("Standard Mode")

    # If Simple mode, show hash disabled warning
    if "Simple" in st.session_state.get("selected_preset", ""):
        st.warning(
            "Hash detector disabled in Simple Problems mode (ineffective on files <50 lines)"
        )
        st.caption(
            "AST threshold increased to 0.85 to reduce false positives on constrained problems."
        )

    df = st.session_state.analysis_results

    # Check if hash detector is active
    hash_is_active = st.session_state.hash_weight > 0

    # Summary metrics - Show average for each detector
    st.subheader("Detector Performance Summary")

    # CRITICAL FIX: Conditional layout based on whether hash is active
    if hash_is_active:
        # Show all 4 metrics (Token, AST, Hash, Confidence)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Avg Token Similarity",
                value=f"{df['Token Similarity (%)'].mean():.1f}%",
                help="Average Token Detector similarity (Jaccard + Cosine)",
            )

        with col2:
            st.metric(
                label="Avg AST Similarity",
                value=f"{df['AST Similarity (%)'].mean():.1f}%",
                help="Average structural similarity from AST analysis",
            )

        with col3:
            st.metric(
                label="Avg Hash Similarity",
                value=f"{df['Hash Similarity (%)'].mean():.1f}%",
                help="Average fingerprint similarity from Winnowing",
            )

        with col4:
            st.metric(
                label="Avg Confidence",
                value=f"{df['confidence_score'].mean():.2%}",
                help="Average confidence score from voting system",
            )
    else:
        # Hash disabled - only show 3 metrics (Token, AST, Confidence)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Avg Token Similarity",
                value=f"{df['Token Similarity (%)'].mean():.1f}%",
                help="Average Token Detector similarity (Jaccard + Cosine)",
            )

        with col2:
            st.metric(
                label="Avg AST Similarity",
                value=f"{df['AST Similarity (%)'].mean():.1f}%",
                help="Average structural similarity from AST analysis",
            )

        with col3:
            st.metric(
                label="Avg Confidence",
                value=f"{df['confidence_score'].mean():.2%}",
                help="Average confidence score from voting system (Token + AST only)",
            )

    st.markdown("---")

    # Overall status summary with voting metrics
    st.subheader("Voting System Summary")
    col1, col2, col3, col4 = st.columns(4)

    total_pairs = len(df)
    plagiarized_count = df["plagiarism_detected"].sum()
    plagiarized_pct = (plagiarized_count / total_pairs * 100) if total_pairs > 0 else 0
    avg_confidence = df["confidence_score"].mean() if len(df) > 0 else 0.0

    # Confidence breakdown
    high_confidence = len(df[df["confidence_level"].isin(["Very High", "High"])])

    with col1:
        st.metric(
            label="Total Pairs", value=total_pairs, help="Total number of file pairs analyzed"
        )

    with col2:
        st.metric(
            label="Plagiarized",
            value=f"{plagiarized_count} ({plagiarized_pct:.1f}%)",
            delta_color="inverse",
            help="Pairs flagged by voting system",
        )

    with col3:
        st.metric(
            label="Avg Confidence",
            value=f"{avg_confidence:.2%}",
            help="Average confidence across all pairs",
        )

    with col4:
        st.metric(
            label="High Confidence",
            value=high_confidence,
            help="Pairs with High or Very High confidence",
        )

    st.markdown("---")

    # Detector Agreement Metrics
    st.subheader("Detector Agreement")

    # CRITICAL FIX: Calculate agreement based on ACTIVE detectors only
    # In Simple mode, only Token and AST vote (hash is disabled)
    if hash_is_active:
        # All 3 detectors active - check if all 3 agree
        def check_unanimous(row):
            votes = [row["token_vote"], row["ast_vote"], row["hash_vote"]]
            return all(votes) or not any(votes)

        df["unanimous"] = df.apply(check_unanimous, axis=1)
        agreement_rate = df["unanimous"].sum() / len(df) * 100 if len(df) > 0 else 0
        agreement_label = "3-Detector Agreement"
        agreement_help = "Percentage of pairs where all 3 detectors agree (all vote yes or all vote no)"
    else:
        # Only Token and AST active - check if both agree
        def check_unanimous(row):
            votes = [row["token_vote"], row["ast_vote"]]
            return all(votes) or not any(votes)

        df["unanimous"] = df.apply(check_unanimous, axis=1)
        agreement_rate = df["unanimous"].sum() / len(df) * 100 if len(df) > 0 else 0
        agreement_label = "2-Detector Agreement"
        agreement_help = "Percentage of pairs where Token and AST detectors agree (both vote yes or both vote no)"

    # CRITICAL FIX: Conditional layout based on whether hash is active
    if hash_is_active:
        # Show all 3 detector vote counts
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=agreement_label,
                value=f"{agreement_rate:.1f}%",
                help=agreement_help,
            )

        with col2:
            vote_counts = df[["token_vote", "ast_vote", "hash_vote"]].sum()
            st.metric(
                label="Token Votes",
                value=f"{int(vote_counts['token_vote'])}/{total_pairs}",
                help="Pairs where Token detector voted for plagiarism",
            )

        with col3:
            col3a, col3b = st.columns(2)
            with col3a:
                st.metric(
                    label="AST Votes",
                    value=f"{int(vote_counts['ast_vote'])}/{total_pairs}",
                    help="Pairs where AST detector voted for plagiarism",
                )
            with col3b:
                st.metric(
                    label="Hash Votes",
                    value=f"{int(vote_counts['hash_vote'])}/{total_pairs}",
                    help="Pairs where Hash detector voted for plagiarism",
                )
    else:
        # Hash disabled - only show Token and AST vote counts
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=agreement_label,
                value=f"{agreement_rate:.1f}%",
                help=agreement_help,
            )

        with col2:
            vote_counts = df[["token_vote", "ast_vote"]].sum()
            st.metric(
                label="Token Votes",
                value=f"{int(vote_counts['token_vote'])}/{total_pairs}",
                help="Pairs where Token detector voted for plagiarism",
            )

        with col3:
            st.metric(
                label="AST Votes",
                value=f"{int(vote_counts['ast_vote'])}/{total_pairs}",
                help="Pairs where AST detector voted for plagiarism",
            )

    st.markdown("---")

    # Results table with filtering
    st.subheader("Detailed Results by Detector")

    # Check if hash detector is active (weight > 0)
    hash_is_active = st.session_state.hash_weight > 0

    # Create display dataframe based on filters
    display_df = df[["File 1", "File 2"]].copy()

    # Add columns based on sidebar filters
    if st.session_state.show_token_results:
        display_df["Token (%)"] = df["Token Similarity (%)"].map("{:.2f}".format)
        display_df["Jaccard (%)"] = df["Token Jaccard (%)"].map("{:.2f}".format)
        display_df["Cosine (%)"] = df["Token Cosine (%)"].map("{:.2f}".format)
        display_df["Token Verdict"] = df["Token Verdict"]

    if st.session_state.show_ast_results:
        display_df["AST (%)"] = df["AST Similarity (%)"].map("{:.2f}".format)
        display_df["AST Verdict"] = df["AST Verdict"]

    # CRITICAL FIX: Only show hash columns if hash detector is ACTIVE (weight > 0)
    # In Simple Problems mode, hash_weight = 0.0, so hash columns should be hidden
    if st.session_state.show_hash_results and hash_is_active:
        display_df["Hash (%)"] = df["Hash Similarity (%)"].map("{:.2f}".format)
        display_df["Hash Verdict"] = df["Hash Verdict"]

    if st.session_state.show_combined_score:
        display_df["Confidence (%)"] = df["Confidence (%)"].map("{:.2f}".format)
        display_df["Confidence Level"] = df["confidence_level"]

    # Always show overall status
    display_df["Overall Status"] = df["Overall Status"]

    # Configure column display
    column_config = {
        "File 1": st.column_config.TextColumn("File 1", width="medium"),
        "File 2": st.column_config.TextColumn("File 2", width="medium"),
    }

    if st.session_state.show_token_results:
        column_config.update(
            {
                "Token (%)": st.column_config.TextColumn("Token %", width="small"),
                "Jaccard (%)": st.column_config.TextColumn("Jaccard %", width="small"),
                "Cosine (%)": st.column_config.TextColumn("Cosine %", width="small"),
                "Token Verdict": st.column_config.TextColumn("Token", width="small"),
            }
        )

    if st.session_state.show_ast_results:
        column_config.update(
            {
                "AST (%)": st.column_config.TextColumn("AST %", width="small"),
                "AST Verdict": st.column_config.TextColumn("AST", width="small"),
            }
        )

    # CRITICAL FIX: Only show hash column config if hash detector is ACTIVE
    if st.session_state.show_hash_results and hash_is_active:
        column_config.update(
            {
                "Hash (%)": st.column_config.TextColumn("Hash %", width="small"),
                "Hash Verdict": st.column_config.TextColumn("Hash", width="small"),
            }
        )

    if st.session_state.show_combined_score:
        column_config["Confidence (%)"] = st.column_config.TextColumn("Confidence %", width="small")
        column_config["Confidence Level"] = st.column_config.TextColumn("Level", width="small")

    column_config["Overall Status"] = st.column_config.TextColumn("Status", width="medium")

    # Display interactive dataframe
    st.dataframe(display_df, use_container_width=True, hide_index=True, column_config=column_config)

    # Status alerts
    if plagiarized_count > 0:
        st.error(f"{plagiarized_count} pair(s) flagged as PLAGIARIZED by voting system")
    if plagiarized_count == 0:
        st.success("All pairs are CLEAR - no plagiarism detected by voting system")

    st.markdown("---")

    # Detailed Voting Breakdown for Plagiarized Pairs
    if plagiarized_count > 0:
        st.subheader("Detailed Voting Breakdown")
        st.caption(f"Showing details for {plagiarized_count} plagiarized pair(s)")

        plagiarized_pairs = df[df["plagiarism_detected"]]

        for idx, row in plagiarized_pairs.iterrows():
            with st.expander(
                f"{row['File 1']} vs {row['File 2']} - {row['confidence_level']} Confidence"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Individual Detector Scores:**")

                    # Token detector
                    token_vote_icon = "✓ VOTE" if row["token_vote"] else "✗ NO VOTE"
                    token_color = "🟢" if row["token_vote"] else "🔴"
                    st.markdown(
                        f"{token_color} **Token**: {row['token_similarity']:.2%} | {token_vote_icon} (threshold: {st.session_state.token_threshold:.2f})"
                    )

                    # AST detector
                    ast_vote_icon = "✓ VOTE" if row["ast_vote"] else "✗ NO VOTE"
                    ast_color = "🟢" if row["ast_vote"] else "🔴"
                    st.markdown(
                        f"{ast_color} **AST**: {row['ast_similarity']:.2%} | {ast_vote_icon} (threshold: {st.session_state.ast_threshold:.2f})"
                    )

                    # CRITICAL FIX: Only show hash detector if it's active
                    if hash_is_active:
                        # Hash detector
                        hash_vote_icon = "✓ VOTE" if row["hash_vote"] else "✗ NO VOTE"
                        hash_color = "🟢" if row["hash_vote"] else "🔴"
                        st.markdown(
                            f"{hash_color} **Hash**: {row['hash_similarity']:.2%} | {hash_vote_icon} (threshold: {st.session_state.hash_threshold:.2f})"
                        )
                    else:
                        # Hash disabled in Simple Problems mode
                        st.markdown("⏭️ **Hash**: Disabled in Simple Problems mode")

                with col2:
                    st.markdown("**Voting Summary:**")
                    total_votes = (
                        st.session_state.token_weight
                        + st.session_state.ast_weight
                        + st.session_state.hash_weight
                    )
                    st.markdown(
                        f"**Weighted Votes**: {row['weighted_votes']:.2f}/{total_votes:.1f}"
                    )
                    st.markdown(
                        f"**Confidence**: {row['confidence_score']:.2%} ({row['confidence_level']})"
                    )
                    decision_icon = "⚠️" if row["plagiarism_detected"] else "✅"
                    decision_text = "PLAGIARIZED" if row["plagiarism_detected"] else "CLEAR"
                    st.markdown(f"**Decision**: {decision_icon} {decision_text}")

                    st.markdown("")
                    st.markdown("**Vote Weights:**")
                    st.markdown(
                        f"- Token: {st.session_state.token_weight:.1f}x "
                        + ("(counted)" if row["token_vote"] else "")
                    )
                    st.markdown(
                        f"- AST: {st.session_state.ast_weight:.1f}x "
                        + ("(counted)" if row["ast_vote"] else "")
                    )
                    # CRITICAL FIX: Only show hash weight if hash detector is active
                    if hash_is_active:
                        st.markdown(
                            f"- Hash: {st.session_state.hash_weight:.1f}x "
                            + ("(counted)" if row["hash_vote"] else "")
                        )
                    else:
                        st.markdown("- Hash: 0.0x (disabled)")

    # Export Results - CSV Only
    st.markdown("---")
    st.subheader("Export Results")

    # Create CSV export
    csv_df = df[
        [
            "File 1",
            "File 2",
            "Token Similarity (%)",
            "AST Similarity (%)",
            "Hash Similarity (%)",
            "Confidence (%)",
            "confidence_level",
            "Overall Status",
        ]
    ].copy()
    csv_df.columns = [
        "File 1",
        "File 2",
        "Token Similarity (%)",
        "AST Similarity (%)",
        "Hash Similarity (%)",
        "Confidence (%)",
        "Confidence Level",
        "Overall Status",
    ]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"codeguard_results_{timestamp}.csv"
    if st.session_state.current_job_id:
        csv_filename = f"{st.session_state.current_job_id}_results.csv"

    st.download_button(
        label="Download Results (CSV)",
        data=csv_df.to_csv(index=False),
        file_name=csv_filename,
        mime="text/csv",
        help="Download analysis results in CSV format",
        use_container_width=True,
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
            col1.metric("Status", job["status"].upper())
            col2.metric("Files", job["file_count"])
            col3.metric("Pairs", job["pair_count"])

            # Get detailed summary
            try:
                summary = get_job_summary(job["id"])
                col4.metric("Plagiarized", summary["plagiarized_count"])

                # Progress bar
                completion = summary["completion_percentage"]
                st.progress(completion / 100, text=f"Completion: {completion:.1f}%")

                # Additional stats
                if summary["total_comparisons"] > 0:
                    st.markdown(
                        f"""
                    **Summary:**
                    - Total comparisons: {summary['total_comparisons']}
                    - Plagiarized pairs: {summary['plagiarized_count']}
                    - Clean pairs: {summary['clean_count']}
                    - Average confidence: {summary['average_confidence']:.2%}
                    """
                    )

                # Button to view details
                if st.button("📋 View Details", key=f"view_{job['id']}"):
                    st.session_state.selected_job_id = job["id"]
                    st.session_state.view_history_details = True
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to load summary: {e}")


def render_how_it_works():
    """
    Render educational content explaining detection methods and voting system.

    Provides brief, accessible explanations suitable for academic users.
    """
    st.header("How CodeGuard Works")
    st.markdown(
        """
    CodeGuard uses a **multi-detector voting system** to identify potential plagiarism.
    Three complementary algorithms analyze your code, each looking for different types of similarity.
    Their results are combined through a weighted voting mechanism for accurate detection.
    """
    )

    st.markdown("---")

    # Detection Modes Section
    st.subheader("Detection Modes")
    st.markdown(
        """
CodeGuard offers two detection modes optimized for different types of assignments:

**Standard Mode (Recommended):**
- Use for typical programming assignments (50+ lines)
- Examples: Rock-Paper-Scissors, data structures, games, algorithms
- All three detectors active (Token, AST, Hash)
- Proven 100% precision and recall on realistic code
- Hash detector uses Winnowing algorithm for partial match detection

**Simple Problems Mode:**
- Use for short, constrained problems (<50 lines)
- Examples: FizzBuzz, factorial calculator, palindrome checker
- Hash detector automatically disabled (ineffective and slow on small files)
- AST threshold increased (0.80 to 0.85) to reduce false positives
- Optimized for problems with limited solution space

**How to choose:**
- If average file size > 50 lines: Use **Standard Mode**
- If average file size < 50 lines: Use **Simple Problems Mode**
- When in doubt: Use **Standard Mode** (default)
    """
    )

    st.markdown("---")

    # Token Detection
    st.subheader("Token Detection")
    st.markdown(
        """
    **What it does:** Breaks code into semantic tokens (keywords, operators, identifiers) and measures overlap.

    **Strengths:** Fast and effective at catching exact or near-exact copies. Uses both Jaccard (unique tokens)
    and Cosine (token frequency) similarity measures.

    **Weaknesses:** Easily defeated by variable renaming or structural changes. Best for identifying
    superficial copying.

    **Example:** Detects when `calculateSum(x, y)` becomes `computeTotal(a, b)` with identical logic.
    """
    )

    st.markdown("---")

    # AST Detection
    st.subheader("AST Detection (Abstract Syntax Tree)")
    st.markdown(
        """
    **What it does:** Analyzes the structural pattern of code by examining its syntax tree representation.

    **Strengths:** Immune to variable renaming and comment changes. Detects structural plagiarism where
    the algorithm and control flow remain identical despite superficial differences. Most reliable detector.

    **Weaknesses:** Can miss plagiarism when algorithms are fundamentally redesigned or when only small
    code fragments are copied.

    **Example:** Recognizes that two sorting implementations use the same nested loop structure,
    even with different variable names.
    """
    )

    st.markdown("---")

    # Hash Detection
    st.subheader("Hash Detection (Winnowing)")
    st.markdown(
        """
    **What it does:** Creates fingerprints of code sequences using the Winnowing algorithm.
    Detects partial and scattered copying.

    **Strengths:** Excellent at finding copy-pasted fragments within larger programs. Can detect
    when segments of code are rearranged or mixed with original code.

    **Weaknesses:** Less effective against systematic refactoring or algorithmic changes.
    May produce false positives with common coding patterns.

    **Example:** Identifies when several helper functions from one file appear scattered
    throughout another file.
    """
    )

    st.markdown("---")

    # Thresholds
    st.subheader("Detection Thresholds")
    st.markdown(
        """
    **What they control:** Each detector has a threshold (0.0-1.0) that determines when similarity
    is high enough to "vote" for plagiarism.

    - **Token Threshold (default 0.70):** Lower = more sensitive to token overlap
    - **AST Threshold (default 0.80):** Higher because structural similarity is stronger evidence
    - **Hash Threshold (default 0.60):** Lower to catch partial copying

    **Adjusting thresholds:** Use sidebar sliders to customize sensitivity. Lower thresholds increase
    detection (more false positives), higher thresholds reduce false alarms (may miss some cases).
    """
    )

    st.markdown("---")

    # Voting System
    st.subheader("Voting System")
    st.markdown(
        """
    **How results are combined:** Each detector votes for plagiarism if its similarity score exceeds
    its threshold. Votes are weighted based on detector reliability:

    - **Token Weight:** 1.0x (baseline)
    - **AST Weight:** 2.0x (most reliable, gets double weight)
    - **Hash Weight:** 1.5x (good for scattered copying)

    **Final Decision:** If weighted votes exceed 50% of the total possible votes (4.5), the pair
    is flagged as plagiarized. The system also calculates a confidence score (0-100%) indicating
    how certain it is about the decision.

    **Example:** If Token and AST both vote "yes" (1.0 + 2.0 = 3.0 weighted votes), that exceeds
    the 2.25 threshold (50% of 4.5), so plagiarism is detected with high confidence.
    """
    )

    st.markdown("---")

    st.info(
        """
    **Best Practices:** Start with default settings for balanced detection. Adjust thresholds and
    weights in the sidebar if you're getting too many false positives or false negatives. Review
    flagged pairs manually to confirm plagiarism, as no automated system is perfect.
    """
    )


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

    col1.metric("Status", summary["status"].upper())
    col2.metric("Files", summary["file_count"])
    col3.metric("Total Pairs", summary["total_comparisons"])
    col4.metric("Plagiarized", summary["plagiarized_count"])

    st.markdown("---")

    # Convert to DataFrame for display with all detector results
    display_data = []
    for result in results:
        display_data.append(
            {
                "File 1": result["file1_name"],
                "File 2": result["file2_name"],
                "Token Similarity (%)": result["token_similarity"] * 100,
                "AST Similarity (%)": result["ast_similarity"] * 100,
                "Hash Similarity (%)": result["hash_similarity"] * 100,
                "Combined Score (%)": result["confidence_score"] * 100,
                "Plagiarized": "✓" if result["is_plagiarized"] else "✗",
            }
        )

    df = pd.DataFrame(display_data)

    # Display detailed results
    st.markdown("### Detailed Results - All Detectors")

    # Summary metrics for historical data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Token", f"{df['Token Similarity (%)'].mean():.1f}%")
    with col2:
        st.metric("Avg AST", f"{df['AST Similarity (%)'].mean():.1f}%")
    with col3:
        st.metric("Avg Hash", f"{df['Hash Similarity (%)'].mean():.1f}%")
    with col4:
        st.metric("Avg Combined", f"{df['Combined Score (%)'].mean():.1f}%")

    st.markdown("")

    # Format DataFrame for display
    display_df = df.copy()
    for col in [
        "Token Similarity (%)",
        "AST Similarity (%)",
        "Hash Similarity (%)",
        "Combined Score (%)",
    ]:
        display_df[col] = display_df[col].map("{:.2f}".format)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "File 1": st.column_config.TextColumn("File 1", width="medium"),
            "File 2": st.column_config.TextColumn("File 2", width="medium"),
            "Token Similarity (%)": st.column_config.TextColumn("Token %", width="small"),
            "AST Similarity (%)": st.column_config.TextColumn("AST %", width="small"),
            "Hash Similarity (%)": st.column_config.TextColumn("Hash %", width="small"),
            "Combined Score (%)": st.column_config.TextColumn("Combined %", width="small"),
            "Plagiarized": st.column_config.TextColumn("Plagiarized?", width="small"),
        },
    )

    # Highlight plagiarized pairs
    plagiarized_count = (df["Plagiarized"] == "✓").sum()
    if plagiarized_count > 0:
        st.warning(f"⚠️ {plagiarized_count} pair(s) flagged as potential plagiarism")
    else:
        st.success("✅ No plagiarism detected in any pairs")

    # CSV Export is handled in the "Analysis" tab display_plagiarism_results function


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
        initial_sidebar_state="expanded",
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

    # Create tabs for New Analysis, History, and How It Works
    tab1, tab2, tab3 = st.tabs(["New Analysis", "Analysis History", "How It Works"])

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

    with tab3:
        # How It Works educational content
        render_how_it_works()

    # Footer
    st.markdown("---")
    st.caption(
        "CodeGuard v4.0 - Voting System Integration (Token + AST + Hash + Weighted Voting) | © 2024"
    )


if __name__ == "__main__":
    main()
