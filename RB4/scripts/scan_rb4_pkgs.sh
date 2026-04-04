#!/usr/bin/env bash
# =============================================================================
# scan_rb4_pkgs.sh — Recursively scan a directory for RB4 song .pkg files
#                    and output a JSON array of song metadata via Onyx CLI.
#
# Usage:
#   ./scan_rb4_pkgs.sh [OPTIONS]
#
# Options:
#   --dir  <path>   Directory to scan for .pkg files (default: /pkgs)
#   --out  <file>   Output JSON file path (default: ./rb4_custom_songs.json)
#   --onyx <path>   Path to onyx binary (default: onyx, assumed on $PATH)
#   -v, --verbose   Print each PKG being processed
#   -h, --help      Show this help
#
# Notes:
#   - Scans RECURSIVELY through subdirectories (handles Samba share layouts)
#   - Skips .pkg files that are not song packages (game discs, patches, etc.)
#     by checking if Onyx metadata output contains an 'artist' or 'title' field
#   - Writes a valid JSON array even if 0 songs are found
#   - Any Onyx errors are written to stderr; the scan continues regardless
# =============================================================================

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
PKG_DIR="/pkgs"
OUT_FILE="./rb4_custom_songs.json"
ONYX_BIN="onyx"
VERBOSE=false

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir)   PKG_DIR="$2"; shift 2 ;;
        --out)   OUT_FILE="$2"; shift 2 ;;
        --onyx)  ONYX_BIN="$2"; shift 2 ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -h|--help)
            sed -n '/^# Usage:/,/^# ===*/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ── Validate ──────────────────────────────────────────────────────────────────
if [[ ! -d "$PKG_DIR" ]]; then
    echo "ERROR: PKG directory not found: $PKG_DIR" >&2
    echo "  Hint: mount your Samba share first, or set --dir to the correct path" >&2
    exit 1
fi

if ! command -v "$ONYX_BIN" &>/dev/null; then
    echo "ERROR: onyx not found on PATH. Install it or pass --onyx /path/to/onyx" >&2
    exit 1
fi

# ── Scan ──────────────────────────────────────────────────────────────────────
echo "▶ Scanning for .pkg files in: $PKG_DIR" >&2
echo "  (This may take a while for large Samba shares)" >&2

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

SONG_COUNT=0
SKIP_COUNT=0
FAIL_COUNT=0
INDEX=0

# Find all .pkg files recursively, sorted for deterministic output
mapfile -d $'\0' PKG_FILES < <(find "$PKG_DIR" -type f -iname "*.pkg" -print0 | sort -z)

TOTAL="${#PKG_FILES[@]}"
echo "  Found $TOTAL .pkg file(s) to inspect" >&2

for PKG_FILE in "${PKG_FILES[@]}"; do
    INDEX=$((INDEX + 1))
    PKG_BASENAME=$(basename "$PKG_FILE")

    $VERBOSE && echo "  [$INDEX/$TOTAL] Checking: $PKG_FILE" >&2

    # Run onyx metadata; capture output and exit code separately
    METADATA_JSON=""
    if METADATA_JSON=$(xvfb-run -a "$ONYX_BIN" metadata "$PKG_FILE" --json 2>/tmp/onyx_err_$$.txt); then
        : # success
    else
        ONYX_ERR=$(cat /tmp/onyx_err_$$.txt 2>/dev/null || true)
        echo "  ⚠  Onyx failed on: $PKG_BASENAME" >&2
        [[ -n "$ONYX_ERR" ]] && echo "     $ONYX_ERR" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Determine if this looks like a song PKG by checking for artist or title fields.
    # Onyx returns an empty object or different structure for game/patch PKGs.
    HAS_SONG_DATA=false
    if echo "$METADATA_JSON" | jq -e '
        (type == "array" and length > 0 and (.[0] | has("artist") or has("title") or has("name") or has("song_name"))) or
        (type == "object" and (has("artist") or has("title") or has("name") or has("song_name")))
    ' &>/dev/null; then
        HAS_SONG_DATA=true
    fi

    if ! $HAS_SONG_DATA; then
        $VERBOSE && echo "     ↷ Skipping (no song metadata): $PKG_BASENAME" >&2
        SKIP_COUNT=$((SKIP_COUNT + 1))
        continue
    fi

    # Add source_pkg field to each song object in the output
    ANNOTATED=$(echo "$METADATA_JSON" | jq --arg pkg "$PKG_BASENAME" --arg fullpath "$PKG_FILE" '
        if type == "array" then
            map(. + {"source_pkg": $pkg, "source_pkg_path": $fullpath})
        else
            [. + {"source_pkg": $pkg, "source_pkg_path": $fullpath}]
        end
    ')

    # Write each song to a temp file (one file per PKG for easy concatenation)
    echo "$ANNOTATED" > "$TMP_DIR/songs_$(printf '%06d' $INDEX).json"

    SONG_PKG_COUNT=$(echo "$ANNOTATED" | jq 'length')
    SONG_COUNT=$((SONG_COUNT + SONG_PKG_COUNT))
    echo "  ✓  $PKG_BASENAME → $SONG_PKG_COUNT song(s)" >&2
done

# ── Combine all temp JSON files into a single array ───────────────────────────
SONG_FILES=("$TMP_DIR"/songs_*.json)

if [[ ${#SONG_FILES[@]} -eq 0 ]] || [[ ! -f "${SONG_FILES[0]}" ]]; then
    echo "[]" > "$OUT_FILE"
else
    jq -s 'add // []' "${SONG_FILES[@]}" > "$OUT_FILE"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
rm -f /tmp/onyx_err_$$.txt
echo "" >&2
echo "═══════════════════════════════════════════════" >&2
echo " Scan complete" >&2
echo "   PKGs scanned  : $TOTAL" >&2
echo "   Song PKGs     : $((TOTAL - SKIP_COUNT - FAIL_COUNT))" >&2
echo "   Songs found   : $SONG_COUNT" >&2
echo "   Non-song PKGs : $SKIP_COUNT (skipped)" >&2
echo "   Onyx failures : $FAIL_COUNT (see warnings above)" >&2
echo "   Output        : $OUT_FILE" >&2
echo "═══════════════════════════════════════════════" >&2
