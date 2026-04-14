#!/bin/bash
# RB4 Restore Script - Restores intermediate files from a backup 7z file
# Usage: ./scripts/restore_rb4_run.sh [backup_file]
#   backup_file - Optional path to 7z file (defaults to most recent in rb4_temp)

set -e

BACKUP_DIR="/workspace/rb4_temp"
DEFAULT_BACKUP_DIR="$BACKUP_DIR"

# Find most recent backup if not specified
if [ -z "$1" ]; then
    echo "No backup specified, finding most recent..."
    BACKUP_FILE=$(ls -t "$DEFAULT_BACKUP_DIR"/rb4_backup_*.7z 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        echo "Error: No backup found in $DEFAULT_BACKUP_DIR"
        exit 1
    fi
    echo "Using: $BACKUP_FILE"
else
    BACKUP_FILE="$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "Error: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

# Create temp extraction dir
EXTRACT_DIR="/workspace/rb4_temp/rb4_restore_$$"
mkdir -p "$EXTRACT_DIR"

# Extract the backup
echo "Extracting backup..."
7z x -o"$EXTRACT_DIR" "$BACKUP_FILE"

# Find the extracted folder (backup is in a subfolder)
EXTRACTED_FOLDER=$(ls -d "$EXTRACT_DIR"/rb4_backup_* 2>/dev/null | head -1)
if [ -z "$EXTRACTED_FOLDER" ]; then
    echo "Error: Could not find extracted backup folder"
    rm -rf "$EXTRACT_DIR"
    exit 1
fi

echo "Restoring files..."

# Restore output song lists and HTML
cp "$EXTRACTED_FOLDER"/*.txt /workspace/RB4/output/ 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/*.html /workspace/RB4/output/ 2>/dev/null || true

# Restore intermediate files to rb4_temp
cp "$EXTRACTED_FOLDER"/rb4_custom_songs.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/processed_pkgs.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/pipeline_errors.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/update_history.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/songs_by_source.json "$BACKUP_DIR/" 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/empty_songs.json "$BACKUP_DIR/" 2>/dev/null || true

# Restore extracted metadata if present
if [ -d "$EXTRACTED_FOLDER/PkgMetadataExtracted" ]; then
    mkdir -p /workspace/RB4/output/PkgMetadataExtracted
    cp -r "$EXTRACTED_FOLDER/PkgMetadataExtracted"/* /workspace/RB4/output/PkgMetadataExtracted/ 2>/dev/null || true
fi

# Restore run log if present
cp "$EXTRACTED_FOLDER"/rb4_extract_*.log "$BACKUP_DIR/" 2>/dev/null || true

# Cleanup
rm -rf "$EXTRACT_DIR"

echo "Restore complete!"
echo ""
echo "Restored files:"
echo "  - Output: /workspace/RB4/output/*.txt"
echo "  - Intermediate: /workspace/rb4_temp/*.json"
if [ -d "/workspace/RB4/output/PkgMetadataExtracted" ]; then
    echo "  - Metadata: /workspace/RB4/output/PkgMetadataExtracted/"
fi