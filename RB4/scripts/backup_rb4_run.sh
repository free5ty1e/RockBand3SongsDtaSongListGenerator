#!/bin/bash
# RB4 Backup Script - Archives intermediate files from most recent run
# Usage: Run from RB4 folder
#   cd RB4
#   bash scripts/backup_rb4_run.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="rb4_temp/rb4_backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# Output song lists and HTML
cp output/*.txt "$BACKUP_DIR/" 2>/dev/null || true
cp output/*.html "$BACKUP_DIR/" 2>/dev/null || true

# Intermediate files in rb4_temp
cp rb4_temp/rb4_custom_songs.json "$BACKUP_DIR/" 2>/dev/null || true
cp rb4_temp/processed_pkgs.json "$BACKUP_DIR/" 2>/dev/null || true
cp rb4_temp/pipeline_errors.json "$BACKUP_DIR/" 2>/dev/null || true
cp rb4_temp/update_history.json "$BACKUP_DIR/" 2>/dev/null || true

# Most recent run log
LOG_FILE=$(ls -t rb4_temp/rb4_extract_*.log 2>/dev/null | head -1)
if [ -n "$LOG_FILE" ]; then
    cp "$LOG_FILE" "$BACKUP_DIR/"
fi

# Create 7z archive with max compression
cd rb4_temp
7z a -mx=9 "rb4_backup_$TIMESTAMP.7z" "rb4_backup_$TIMESTAMP"
rm -rf "rb4_backup_$TIMESTAMP"

echo "Backed up to: rb4_temp/rb4_backup_$TIMESTAMP.7z"