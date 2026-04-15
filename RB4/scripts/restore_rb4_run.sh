#!/bin/bash
# RB4 Restore Script - Restores intermediate files from a backup 7z file
# Usage: Run from RB4 folder
#   cd RB4
#   bash scripts/restore_rb4_run.sh [backup_file]
#   backup_file - Optional path to 7z file (defaults to most recent in rb4_temp)

set -e

# Find most recent backup if not specified
if [ -z "$1" ]; then
    echo "No backup specified, finding most recent..."
    BACKUP_FILE=$(ls -t rb4_temp/rb4_backup_*.7z 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        echo "Error: No backup found in rb4_temp"
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
EXTRACT_DIR="rb4_temp/rb4_restore_$$"
mkdir -p "$EXTRACT_DIR"

# Extract the backup
echo "Extracting backup..."
7z x -o"$EXTRACT_DIR" "$BACKUP_FILE"

# Find the extracted folder
EXTRACTED_FOLDER=$(ls -d "$EXTRACT_DIR"/rb4_backup_* 2>/dev/null | head -1)
if [ -z "$EXTRACTED_FOLDER" ]; then
    echo "Error: Could not find extracted backup folder"
    rm -rf "$EXTRACT_DIR"
    exit 1
fi

echo "Restoring files..."

# Restore output song lists and HTML
cp "$EXTRACTED_FOLDER"/*.txt output/ 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/*.html output/ 2>/dev/null || true

# Restore intermediate files to rb4_temp
cp "$EXTRACTED_FOLDER"/rb4_custom_songs.json rb4_temp/ 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/processed_pkgs.json rb4_temp/ 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/pipeline_errors.json rb4_temp/ 2>/dev/null || true
cp "$EXTRACTED_FOLDER"/update_history.json rb4_temp/ 2>/dev/null || true

# Restore extracted metadata if present
if [ -d "$EXTRACTED_FOLDER/PkgMetadataExtracted" ]; then
    mkdir -p output/PkgMetadataExtracted
    cp -r "$EXTRACTED_FOLDER/PkgMetadataExtracted"/* output/PkgMetadataExtracted/ 2>/dev/null || true
fi

# Restore run log if present
cp "$EXTRACTED_FOLDER"/rb4_extract_*.log rb4_temp/ 2>/dev/null || true

# Cleanup
rm -rf "$EXTRACT_DIR"

echo "Restore complete!"
echo ""
echo "Restored files:"
echo "  - Output: output/*.txt"
echo "  - Intermediate: rb4_temp/*.json"