#!/usr/bin/env python3
"""
RB4 Pipeline Settings and Defaults

All configurable paths and settings for the RB4 song extraction pipeline.
Can be overridden via command-line arguments.

Run from the RB4 folder for relative paths:
    cd RB4
    python3 scripts/rb4_songlist_generator.py
"""

import os

# ── Directory Paths (absolute paths for consistency) ─────────────────────────────
DEFAULT_PKG_DIR = "/workspace/RB4/pkgs"
DEFAULT_TEMP_DIR = "/workspace/RB4/rb4_temp"
DEFAULT_OUTPUT_JSON = "/workspace/docs/songlistdata/rb4_custom_songs.json"
DEFAULT_SONGLIST_DIR = "/workspace/docs"
DEFAULT_METADATA_DIR = "/workspace/output/PkgMetadataExtracted"
DEFAULT_DOCS_DIR = "/workspace/docs"

# ── State File Names (relative to temp_dir) ──────────────────────────────
PROCESSED_PKGS_FILENAME = "processed_pkgs.json"
UPDATE_HISTORY_FILENAME = "update_history.json"
ERROR_LOG_FILENAME = "pipeline_errors.json"

# Use docs/songlistdata as the persistent store for state files
STATE_DIR = "/workspace/docs/songlistdata"

# ── Console Output Settings ─────────────────────────────────────────────────────
DEFAULT_PROGRESS_BAR_LENGTH = 50

# ── HTML Output Settings ─────────────────────────────────────────────────
DEFAULT_HTML_PAGE_TITLE = "🎸 Rock Band 4 Song List"


def get_processed_pkgs_file(temp_dir):
    """Get the processed PKGs file path."""
    return f"{STATE_DIR}/{PROCESSED_PKGS_FILENAME}"

def get_update_history_file(temp_dir):
    """Get the update history file path."""
    return f"{STATE_DIR}/{UPDATE_HISTORY_FILENAME}"

def get_error_log_file(temp_dir):
    """Get the error log file path."""
    return f"{STATE_DIR}/{ERROR_LOG_FILENAME}"
