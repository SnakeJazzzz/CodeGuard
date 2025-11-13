-- CodeGuard Database Schema
-- SQLite database for plagiarism detection analysis results
-- Version: 1.0
-- Created: 2025-11-12

-- =============================================================================
-- Analysis Jobs Table
-- =============================================================================
-- Stores metadata about each plagiarism analysis job
-- Each job represents a batch analysis of multiple files
CREATE TABLE IF NOT EXISTS analysis_jobs (
    id TEXT PRIMARY KEY,                        -- UUID for job identification
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Job creation time (UTC)
    status TEXT NOT NULL,                       -- Job status: 'pending', 'running', 'completed', 'failed'
    file_count INTEGER NOT NULL,                -- Total number of files analyzed
    pair_count INTEGER NOT NULL,                -- Total number of comparisons performed
    results_path TEXT,                          -- Path to detailed results JSON file
    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    CONSTRAINT valid_file_count CHECK (file_count >= 0),
    CONSTRAINT valid_pair_count CHECK (pair_count >= 0)
);

-- =============================================================================
-- Comparison Results Table
-- =============================================================================
-- Stores individual file pair comparison results
-- Each row represents one pairwise comparison between two files
CREATE TABLE IF NOT EXISTS comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Auto-incrementing result ID
    job_id TEXT NOT NULL,                       -- Foreign key to analysis_jobs
    file1_name TEXT NOT NULL,                   -- Name of first file in comparison
    file2_name TEXT NOT NULL,                   -- Name of second file in comparison
    token_similarity REAL NOT NULL,             -- Token-based similarity score (0.0-1.0)
    ast_similarity REAL NOT NULL,               -- AST-based similarity score (0.0-1.0)
    hash_similarity REAL NOT NULL,              -- Hash-based similarity score (0.0-1.0)
    is_plagiarized BOOLEAN NOT NULL,            -- Final plagiarism verdict (0 or 1)
    confidence_score REAL NOT NULL,             -- Confidence in verdict (0.0-1.0)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Comparison timestamp (UTC)
    FOREIGN KEY (job_id) REFERENCES analysis_jobs(id) ON DELETE CASCADE,
    CONSTRAINT valid_token_similarity CHECK (token_similarity BETWEEN 0.0 AND 1.0),
    CONSTRAINT valid_ast_similarity CHECK (ast_similarity BETWEEN 0.0 AND 1.0),
    CONSTRAINT valid_hash_similarity CHECK (hash_similarity BETWEEN 0.0 AND 1.0),
    CONSTRAINT valid_confidence CHECK (confidence_score BETWEEN 0.0 AND 1.0)
);

-- =============================================================================
-- Configuration Table
-- =============================================================================
-- Stores system configuration key-value pairs
-- Allows runtime configuration without code changes
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,                       -- Configuration key (unique)
    value TEXT NOT NULL,                        -- Configuration value (stored as text)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Last update timestamp (UTC)
);

-- =============================================================================
-- Performance Indexes
-- =============================================================================
-- Index for fast lookup of comparison results by job_id
-- Critical for fetching all results for a specific analysis job
CREATE INDEX IF NOT EXISTS idx_job_id ON comparison_results(job_id);

-- Index for fast lookup of jobs by creation time
-- Useful for dashboard views and chronological queries
CREATE INDEX IF NOT EXISTS idx_created_at ON analysis_jobs(created_at);

-- Index for fast filtering of plagiarized comparisons
-- Enables quick queries for flagged results
CREATE INDEX IF NOT EXISTS idx_plagiarized ON comparison_results(is_plagiarized);

-- Composite index for efficient job-specific plagiarism queries
-- Optimizes queries that filter by both job_id and plagiarism status
CREATE INDEX IF NOT EXISTS idx_job_plagiarized ON comparison_results(job_id, is_plagiarized);

-- =============================================================================
-- Default Configuration Values
-- =============================================================================
-- Insert default system configuration if not already present
INSERT OR IGNORE INTO configuration (key, value) VALUES
    ('similarity_threshold', '0.80'),           -- Threshold for plagiarism detection (80%)
    ('confidence_threshold', '0.75'),           -- Minimum confidence for positive match (75%)
    ('max_file_size_mb', '16'),                 -- Maximum file size in megabytes
    ('database_version', '1.0'),                -- Schema version for migrations
    ('created_at', datetime('now'));            -- Database initialization timestamp
