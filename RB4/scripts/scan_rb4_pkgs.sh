#!/usr/bin/env bash
# =============================================================================
# scan_rb4_pkgs.sh — Recursively scan a directory for RB4 song .pkg files,
#                    extract them using PkgTool, and parse their binary DTA to JSON.
# =============================================================================

set -euo pipefail

PKG_DIR="/pkgs"
OUT_FILE="rb4_custom_songs.json"
PKG_TOOL="/usr/local/bin/PkgTool.Core"

# Export for PkgTool compatibility in some containers
export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)   PKG_DIR="$2"; shift 2 ;;
        --out)   OUT_FILE="$2"; shift 2 ;;
        -v|--verbose) shift ;;
        -h|--help) exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

echo "▶ Scanning for .pkg files in: $PKG_DIR"

WORKING_DIR="RB4/working_dir"
mkdir -p "$WORKING_DIR"
TMP_DIR=$(mktemp -d -p "$WORKING_DIR" tmp_XXXXXX)
# Cleanup tmp dir on exit
trap 'rm -rf "$TMP_DIR"' EXIT

SONG_COUNT=0
INDEX=0

# Find all PKG files
mapfile -d $'\0' PKG_FILES < <(find "$PKG_DIR" -type f -iname "*.pkg" -print0 | sort -z)
TOTAL="${#PKG_FILES[@]}"
echo "  Found $TOTAL .pkg file(s) to process"

for PKG_FILE in "${PKG_FILES[@]}"; do
    INDEX=$((INDEX + 1))
    PKG_BASENAME=$(basename "$PKG_FILE")
    
    echo "  [$INDEX/$TOTAL] Processing: $PKG_BASENAME"
    
    EXTRACT_DIR="$TMP_DIR/extracted_$INDEX"
    mkdir -p "$EXTRACT_DIR"
    
    # Run PkgTool to extract (zero passcode works for standard fPKGs)
    # Using pkg_makegp4 instead of pkg_extract to ensure multi-partition/songs folders are unpacked
    if "$PKG_TOOL" pkg_makegp4 --passcode 00000000000000000000000000000000 "$PKG_FILE" "$EXTRACT_DIR" > /dev/null 2>&1; then
        
        # Extract the Source Title from PARAM.SFO (if available)
        # NOTE: This is ONLY used as fallback when binary doesn't contain source metadata
        SFO_FILE=$(find "$EXTRACT_DIR" -name "param.sfo" | head -n 1)
        PKG_SOURCE=""  # Empty means "auto-detect from binary"
        if [ -n "$SFO_FILE" ]; then
            SFO_TITLE=$("$PKG_TOOL" sfo_listentries "$SFO_FILE" | grep "TITLE :" | cut -d ':' -f 2- | sed 's/^ *//')
            if [ -n "$SFO_TITLE" ]; then
                # Store SFO title for reference, but don't override binary source
                PKG_SOURCE="$SFO_TITLE"
            fi
        fi

        # Find if any song DTAs exist before running Python
        if find "$EXTRACT_DIR" -name "*.songdta_ps4" | grep -q .; then
            # Run the Python scraper - WITHOUT --source override so binary source is used
            SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            PYTHON_OUT="$TMP_DIR/songs_$(printf '%06d' $INDEX).json"
            
            # Only pass --source if explicitly provided (empty string means auto)
            if [ -n "$PKG_SOURCE" ]; then
                python3 "$SCRIPT_DIR/extract_binary_dta.py" "$EXTRACT_DIR" "$PYTHON_OUT" --source "$PKG_SOURCE"
            else
                python3 "$SCRIPT_DIR/extract_binary_dta.py" "$EXTRACT_DIR" "$PYTHON_OUT"
            fi
            
            if [ -f "$PYTHON_OUT" ]; then
                COUNT=$(jq 'length' "$PYTHON_OUT")
                SONG_COUNT=$((SONG_COUNT + COUNT))
                echo "  ✓ Extracted $COUNT song(s) [Source: $PKG_SOURCE]"
            fi
        else
            echo "  ⚠ No .songdta_ps4 files found in $PKG_BASENAME"
        fi
    else
        echo "  ⚠ Failed to unpack: $PKG_BASENAME"
    fi
    
    # CRITICAL: Delete extraction dir immediately to save disk space
    rm -rf "$EXTRACT_DIR"
done

# Combine all partial JSON files into the final output
if ls "$TMP_DIR"/songs_*.json >/dev/null 2>&1; then
    jq -s 'add' "$TMP_DIR"/songs_*.json > "$OUT_FILE"
else
    echo "[]" > "$OUT_FILE"
fi

echo "═══════════════════════════════════════════════"
echo " Scan complete"
echo "   Songs found   : $SONG_COUNT"
echo "   Output        : $OUT_FILE"
echo "═══════════════════════════════════════════════"
