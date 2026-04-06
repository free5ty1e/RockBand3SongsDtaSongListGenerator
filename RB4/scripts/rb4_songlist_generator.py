#!/usr/bin/env python3
"""
rb4_extract_songs.py — Extract song metadata from Rock Band 4 PKG files.

Usage:
    python3 rb4_extract_songs.py --pkg-dir /path/to/pkgs [--temp-dir /path/to/temp] [--no-incremental]

This script:
1. Scans a directory of PKG files (can be local or network mount)
2. Extracts only .songdta_ps4 metadata files from each PKG (one at a time)
3. Parses binary metadata using exact offsets from LibForge template
4. Generates human-readable song lists
5. Supports incremental mode: tracks processed PKGs and skips already-done ones
"""

import os
import sys
import json
import subprocess
import argparse
import shutil
import re

# Force unbuffered output for real-time feedback - handle non-TTY case
if hasattr(sys.stdout, 'fileno') and sys.stdout.fileno() >= 0:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
if hasattr(sys.stderr, 'fileno') and sys.stderr.fileno() >= 0:
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Default paths
DEFAULT_PKG_DIR = "/workspace/pkgs"
DEFAULT_TEMP_DIR = "/workspace/rb4_temp"
DEFAULT_OUTPUT_JSON = "/workspace/RB4/rb4_custom_songs.json"
DEFAULT_SONGLIST_DIR = "/workspace/RB4/output"
PROCESSED_PKGS_FILE = "/workspace/RB4/processed_pkgs.json"
UPDATE_HISTORY_FILE = "/workspace/RB4/update_history.json"

def load_processed_pkgs():
    """Load list of already-processed PKGs."""
    if os.path.exists(PROCESSED_PKGS_FILE):
        with open(PROCESSED_PKGS_FILE) as f:
            return set(json.load(f))
    return set()

def save_processed_pkgs(processed):
    """Save list of processed PKGs."""
    with open(PROCESSED_PKGS_FILE, 'w') as f:
        json.dump(sorted(processed), f, indent=2)

def load_update_history():
    """Load update history."""
    if os.path.exists(UPDATE_HISTORY_FILE):
        with open(UPDATE_HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_update_history(history):
    """Save update history."""
    with open(UPDATE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def record_update(new_songs, total_songs_count):
    """Record this update in history."""
    history = load_update_history()
    from datetime import datetime
    import os
    # Respect TZ environment variable for local timezone
    tz = os.environ.get('TZ', 'UTC')
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "newSongs": new_songs,
        "totalSongs": total_songs_count,
        "timezone": tz
    }
    history.append(entry)
    # Keep last 10 updates
    if len(history) > 10:
        history = history[-10:]
    save_update_history(history)

# Package source mapping
def get_pkg_source(pkg_path):
    """Extract source name from PKG filename."""
    basename = os.path.basename(pkg_path)
    if "CREQ" in basename:
        return "custom"
    elif "GDRB" in basename or "GREENDAY" in basename:
        return "greenday"
    elif "RB2" in basename:
        return "rb2"
    elif "DELISTED" in basename:
        return "delisted"
    elif "UNRELEASED" in basename or "DLCUNRELEASED" in basename:
        return "unreleased"
    elif "SEASON" in basename:
        return "rb4"
    elif "UNEXPORTABLE" in basename:
        return "unexportable"
    return "unknown"

def run_cmd(cmd, check=True, capture=True, show_output=False):
    """Run command and return output. Use show_output=True for realtime feedback."""
    if show_output:
        return subprocess.run(cmd, shell=True).returncode
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout if capture else ""

def extract_songdta_from_pkg(pkg_path, source_name, temp_dir):
    """Extract only .songdta_ps4 files from a PKG using two-step extraction."""
    pkg_name = os.path.basename(pkg_path)
    print(f"[1/4] Extracting: {pkg_name}")
    sys.stdout.flush()
    
    basename = pkg_name.replace('.pkg', '')
    work_dir = os.path.join(temp_dir, 'pfs_extract_' + basename)
    pfs_file = os.path.join(work_dir, "inner.pfs")
    pfs_extract_dir = os.path.join(work_dir, "pfs_contents")
    
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # Step 1: Extract inner PFS image
        print(f"  [2/4] Extracting PFS image...")
        sys.stdout.flush()
        run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pkg_extractinnerpfs "{pkg_path}" {pfs_file}', show_output=True)
        
        # Step 2: Extract PFS contents
        print(f"  [3/4] Extracting song data from PFS...")
        sys.stdout.flush()
        try:
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}', show_output=True)
        except RuntimeError:
            print("    First attempt failed, retrying...")
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}', show_output=True)
        
        # Find all .songdta_ps4 files
        songdta_files = []
        for root, dirs, files in os.walk(pfs_extract_dir):
            for f in files:
                if f.endswith('.songdta_ps4'):
                    songdta_files.append(os.path.join(root, f))
        
        if not songdta_files:
            print(f"    No songdta files found!")
            return []
        
        # Extract metadata using Python script
        temp_output = os.path.join(temp_dir, f'metadata_{basename}.json')
        files_arg = ' '.join(f'"{f}"' for f in songdta_files)
        run_cmd(f'cd /workspace && python3 RB4/scripts/extract_binary_dta.py {files_arg} {temp_output}', show_output=True)
        
        # Load and tag with source
        with open(temp_output) as f:
            songs = json.load(f)
        
        for song in songs:
            song['source'] = source_name
        
        print(f"    Extracted {len(songs)} songs")
        return songs
        
    finally:
        # Clean up to free disk space
        print(f"  [4/4] Cleaning up extraction files...")
        sys.stdout.flush()
        shutil.rmtree(work_dir, ignore_errors=True)
        print(f"  ✓ Done: {pkg_name}")

def main():
    parser = argparse.ArgumentParser(
        description='Extract song metadata from Rock Band 4 PKG files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Extract from local PKG directory (default paths)
  python3 RB4/scripts/rb4_extract_songs.py

  # Extract from network share mounted locally
  python3 RB4/scripts/rb4_extract_songs.py --pkg-dir /mnt/rb4dlc

  # Force full re-extraction (disable incremental mode)
  python3 RB4/scripts/rb4_extract_songs.py --pkg-dir /mnt/rb4dlc --no-incremental

  # Use custom temp directory
  python3 RB4/scripts/rb4_extract_songs.py --pkg-dir /mnt/rb4dlc --temp-dir /tmp/rb4_extract
'''
    )
    parser.add_argument('--pkg-dir', default=DEFAULT_PKG_DIR,
                        help=f'Directory containing PKG files (default: {DEFAULT_PKG_DIR})')
    parser.add_argument('--temp-dir', default=DEFAULT_TEMP_DIR,
                        help=f'Temporary directory for extraction (default: {DEFAULT_TEMP_DIR})')
    parser.add_argument('--output-json', default=DEFAULT_OUTPUT_JSON,
                        help=f'Output JSON file for custom songs (default: {DEFAULT_OUTPUT_JSON})')
    parser.add_argument('--songlist-dir', default=DEFAULT_SONGLIST_DIR,
                        help=f'Output directory for song lists (default: {DEFAULT_SONGLIST_DIR})')
    parser.add_argument('--baseline', default='/workspace/RB4/rb4songlistWithRivals.txt',
                        help='Baseline song list file')
    parser.add_argument('--incremental', action='store_true', default=True,
                        help='Skip already-processed PKGs (default: enabled)')
    parser.add_argument('--no-incremental', action='store_false', dest='incremental',
                        help='Disable incremental mode - re-process all PKGs')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Create temp directory
    os.makedirs(args.temp_dir, exist_ok=True)
    
    # Reset if --no-incremental (fresh run)
    if not args.incremental:
        print("Full rebuild mode - clearing previous state...")
        for f in [PROCESSED_PKGS_FILE, UPDATE_HISTORY_FILE, args.output_json]:
            if os.path.exists(f):
                os.remove(f)
        # Clear output directory BEFORE generating
        if os.path.exists(args.songlist_dir):
            for f in os.listdir(args.songlist_dir):
                os.remove(os.path.join(args.songlist_dir, f))
    
    # Find all PKG files
    if not os.path.isdir(args.pkg_dir):
        print(f"ERROR: PKG directory not found: {args.pkg_dir}")
        sys.exit(1)
    
    pkg_files = [os.path.join(args.pkg_dir, f) for f in os.listdir(args.pkg_dir) if f.endswith('.pkg')]
    
    if not pkg_files:
        print(f"No .pkg files found in {args.pkg_dir}")
        sys.exit(1)
    
    print(f"Found {len(pkg_files)} PKG files in {args.pkg_dir}")
    
    # Load processed PKGs for incremental mode
    processed = load_processed_pkgs() if args.incremental else set()
    print(f"Incremental mode: {'enabled' if args.incremental else 'disabled'}")
    if processed:
        print(f"  Already processed: {len(processed)} PKGs")
    
    # Filter out already-processed PKGs
    if args.incremental:
        new_pkgs = [p for p in pkg_files if os.path.basename(p) not in processed]
        skipped = len(pkg_files) - len(new_pkgs)
        if skipped > 0:
            print(f"  Skipping {skipped} already-processed PKGs")
        pkg_files = new_pkgs
    
    if not pkg_files:
        print("No new PKGs to process.")
        print("\nGenerating song lists from existing data...")
        run_cmd(f'cd /workspace/RB4 && node generate_rb4_song_list.js --baseline {args.baseline} --custom {args.output_json} --processed {PROCESSED_PKGS_FILE}')
        print("✅ Done!")
        sys.exit(0)
    
    print(f"Processing {len(pkg_files)} new PKGs...")
    
    all_songs = []
    
    for pkg_path in sorted(pkg_files):
        source = get_pkg_source(pkg_path)
        
        try:
            songs = extract_songdta_from_pkg(pkg_path, source, args.temp_dir)
            all_songs.extend(songs)
            
            # Mark as processed
            processed.add(os.path.basename(pkg_path))
            save_processed_pkgs(processed)
            
            print(f"  Running total: {len(all_songs)} songs")
            
        except Exception as e:
            print(f"  ERROR processing {os.path.basename(pkg_path)}: {e}")
            continue
    
    print(f"\nExtracted {len(all_songs)} songs from {len(pkg_files)} PKGs")
    
    # Load existing songs if incremental mode and file exists
    if args.incremental and os.path.exists(args.output_json):
        with open(args.output_json) as f:
            existing = json.load(f)
        # Merge (new songs will override duplicates)
        existing_dict = {(s['artist'], s['title']): s for s in existing}
        for song in all_songs:
            key = (song['artist'], song['title'])
            existing_dict[key] = song
        all_songs = list(existing_dict.values())
        print(f"Merged with existing: {len(all_songs)} total songs")
    
    # Filter out garbage entries
    valid_songs = [s for s in all_songs if s.get('title') or s.get('artist')]
    garbage = len(all_songs) - len(valid_songs)
    if garbage > 0:
        print(f"Filtered out {garbage} garbage entries")
    
    # Record update for history (always, to show in output)
    # Track which songs are new in this run
    existing_set = set()
    if os.path.exists(args.output_json):
        with open(args.output_json) as f:
            existing = json.load(f)
            existing_set = {(s['artist'], s['title']) for s in existing}
    
    new_only = [s for s in valid_songs if (s['artist'], s['title']) not in existing_set]
    if new_only:
        record_update(new_only, len(valid_songs))
        print(f"Recorded {len(new_only)} new songs in update history")
    elif len(all_songs) > 0:
        # Even if no truly new songs, record this run (for --no-incremental)
        record_update(valid_songs, len(valid_songs))
        print(f"Recorded {len(valid_songs)} songs in update history (full rebuild)")

    # Write JSON
    with open(args.output_json, 'w') as f:
        json.dump(valid_songs, f, indent=2)
    print(f"Written: {args.output_json}")
    
    # Check for issues
    zero_dur = [s for s in valid_songs if s.get('durationMs', 0) == 0]
    if zero_dur:
        print(f"\n⚠️  Songs with durationMs=0: {len(zero_dur)}")
    
    # Generate song lists
    print(f"\nGenerating song lists...")
    run_cmd(f'cd /workspace/RB4 && node generate_rb4_song_list.js --baseline {args.baseline} --custom {args.output_json} --processed {PROCESSED_PKGS_FILE}')
    
    print("\n✅ Pipeline complete!")
    print(f"Processed PKGs saved to: {PROCESSED_PKGS_FILE}")

if __name__ == '__main__':
    main()