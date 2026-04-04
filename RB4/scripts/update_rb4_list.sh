#!/usr/bin/env bash
# =============================================================================
# update_rb4_list.sh — One-click RB4 song list pipeline
#
# Runs the full "Scan PKGs → Generate 4 song lists" pipeline.
#
# Usage (from repo root, inside devcontainer or on the Ubuntu host):
#   ./RB4/scripts/update_rb4_list.sh [OPTIONS]
#
# Options:
#   --pkg-dir  <path>   Samba share / PKG directory to scan (default: /pkgs)
#   --no-scan           Skip the PKG scan step (reuse existing rb4_custom_songs.json)
#   -v, --verbose       Verbose output for both scan and generator
#   -h, --help          Show this help
#
# Outputs (in RB4/output/):
#   RB4SongListSortedByArtist.txt
#   RB4SongListSortedBySongName.txt
#   RB4SongListSortedByArtistClean.txt
#   RB4SongListSortedBySongNameClean.txt
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RB4_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$RB4_DIR/.." && pwd)"

PKG_DIR="/pkgs"
CUSTOM_JSON="$RB4_DIR/rb4_custom_songs.json"
BASELINE="$RB4_DIR/rb4songlistWithRivals.txt"
GENERATOR="$RB4_DIR/generate_rb4_song_list.js"
SCAN_SCRIPT="$SCRIPT_DIR/scan_rb4_pkgs.sh"
DO_SCAN=true
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pkg-dir)  PKG_DIR="$2"; shift 2 ;;
        --no-scan)  DO_SCAN=false; shift ;;
        -v|--verbose) VERBOSE="--verbose"; shift ;;
        -h|--help)
            sed -n '/^# Usage:/,/^# ===*/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

echo ""
echo "════════════════════════════════════════════════"
echo "   RB4 Song List — Full Pipeline"
echo "════════════════════════════════════════════════"
echo ""

# ── Step 1: Scan PKGs ─────────────────────────────────────────────────────────
if $DO_SCAN; then
    echo "▶ Step 1/2 — Scanning .pkg files in: $PKG_DIR"
    echo ""
    bash "$SCAN_SCRIPT" --dir "$PKG_DIR" --out "$CUSTOM_JSON" $VERBOSE
    echo ""
else
    echo "▶ Step 1/2 — Skipping scan (--no-scan); using: $CUSTOM_JSON"
    if [[ ! -f "$CUSTOM_JSON" ]]; then
        echo "  WARNING: $CUSTOM_JSON not found — generator will use baseline only" >&2
    fi
    echo ""
fi

# ── Step 2: Generate song lists ───────────────────────────────────────────────
echo "▶ Step 2/2 — Generating song lists"
echo ""

CUSTOM_ARG=""
if [[ -f "$CUSTOM_JSON" ]]; then
    CUSTOM_ARG="--custom $CUSTOM_JSON"
fi

node "$GENERATOR" \
    --baseline "$BASELINE" \
    $CUSTOM_ARG \
    --outdir "$RB4_DIR/output" \
    $VERBOSE

echo ""
echo "════════════════════════════════════════════════"
echo "  ✅ Pipeline complete!"
echo ""
echo "  Output files are in: $RB4_DIR/output/"
echo ""
echo "  Upload the 4 .txt files to your Google Drive"
echo "  (overwrite existing files to update QR code links)"
echo "════════════════════════════════════════════════"
echo ""
