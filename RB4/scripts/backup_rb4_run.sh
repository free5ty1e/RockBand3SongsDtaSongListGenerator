#!/bin/bash
# RB4 Backup Script - Archives intermediate files from most recent run
# Usage: ./scripts/backup_rb4_run.sh
#
# Files managed in /workspace/rb4_temp:
#   - rb4_custom_songs.json     (main extracted song metadata)
#   - processed_pkgs.json    (PKGs already scanned)
#   - pipeline_errors.json (extraction errors/warnings)
#   - update_history.json  (update history log)
#   - songs_by_source.json (legacy - can delete)
#   - empty_songs.json    (temp output from extraction)

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/workspace/rb4_temp/rb4_backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

# Output song lists and HTML
cp /workspace/RB4/output/*.txt "$BACKUP_DIR/"
cp /workspace/RB4/output/*.html "$BACKUP_DIR/" 2>/dev/null || true

# Baseline (keep in RB4 - source of truth)
# cp /workspace/RB4/rb4songlistWithRivals.txt "$BACKUP_DIR/"

# Intermediate files in rb4_temp (move them for backup)
cp /workspace/rb4_temp/rb4_custom_songs.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/rb4_temp/processed_pkgs.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/rb4_temp/pipeline_errors.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/rb4_temp/update_history.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/rb4_temp/songs_by_source.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/rb4_temp/empty_songs.json "$BACKUP_DIR/" 2>/dev/null || true

# Legacy files in RB4 root (back up if present, can be deleted)
cp /workspace/RB4/rb4_custom_songs.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/RB4/processed_pkgs.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/RB4/pipeline_errors.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/RB4/update_history.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/RB4/songs_by_source.json "$BACKUP_DIR/" 2>/dev/null || true
cp /workspace/RB4/empty_songs.json "$BACKUP_DIR/" 2>/dev/null || true

# Most recent run log (highest timestamp)
LOG_FILE=$(ls -t /workspace/rb4_temp/rb4_extract_*.log 2>/dev/null | head -1)
if [ -n "$LOG_FILE" ]; then
    cp "$LOG_FILE" "$BACKUP_DIR/"
fi

# Create 7z archive with max compression
cd /workspace/rb4_temp
7z a -mx=9 "rb4_backup_$TIMESTAMP.7z" "rb4_backup_$TIMESTAMP"
rm -rf "rb4_backup_$TIMESTAMP"

echo "Backed up to: rb4_temp/rb4_backup_$TIMESTAMP.7z"