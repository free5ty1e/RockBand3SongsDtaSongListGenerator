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
from datetime import datetime
import logging

# Default paths
DEFAULT_PKG_DIR = "/workspace/pkgs"
DEFAULT_TEMP_DIR = "/workspace/rb4_temp"
DEFAULT_OUTPUT_JSON = "/workspace/rb4_temp/rb4_custom_songs.json"
DEFAULT_SONGLIST_DIR = "/workspace/RB4/output"
DEFAULT_METADATA_DIR = "/workspace/RB4/output/PkgMetadataExtracted"
PROCESSED_PKGS_FILE = "/workspace/rb4_temp/processed_pkgs.json"
UPDATE_HISTORY_FILE = "/workspace/rb4_temp/update_history.json"
ERROR_LOG_FILE = "/workspace/rb4_temp/pipeline_errors.json"

LOG_FILE = None  # Set in main()


def log(msg):
    """Log to both console and file."""
    print(msg)
    if LOG_FILE:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')


def load_empty_songs_baseline():
    """Load the pre-identified empty songs baseline."""
    baseline_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(baseline_path):
        try:
            with open(baseline_path) as f:
                data = json.load(f)
                # Map short_filename -> {title, artist}
                return {s['short_filename']: {'title': s.get('probable_title'), 'artist': s.get('probable_artist')} 
                        for s in data if 'short_filename' in s}
        except Exception as e:
            log(f"Warning: Failed to load empty songs baseline: {e}")
    return {}

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

# Error tracking for pipeline failures
class ErrorTracker:
    def __init__(self):
        self.errors = {
            'pkg_download_failed': [],
            'pfs_image_extract_failed': [],  # Step 1: extracting inner PFS image
            'pfs_contents_extract_failed': [],  # Step 2: extracting PFS contents
            'pfs_extraction_failed': [],
            'songdta_parse_failed': [],
            'empty_song_fallback_used': [],
            'timeout_errors': [],
            'file_lock_errors': [],
            'memory_map_error': [],  # .NET memory mapped file errors
            'pkg_processing_failed': [],  # generic catch-all
        }
        self.warnings = {
            'no_songdta_found': [],
            'empty_metadata': [],
            'unknown_source': [],
        }
    
    def add_error(self, error_type, pkg_name, details=''):
        if error_type in self.errors:
            self.errors[error_type].append({
                'pkg': pkg_name,
                'details': details,
                'timestamp': datetime.now().isoformat()
            })
    
    def add_warning(self, warning_type, pkg_name, details=''):
        if warning_type in self.warnings:
            self.warnings[warning_type].append({
                'pkg': pkg_name,
                'details': details,
                'timestamp': datetime.now().isoformat()
            })
    
    def save(self):
        with open(ERROR_LOG_FILE, 'w') as f:
            json.dump({
                'errors': self.errors,
                'warnings': self.warnings
            }, f, indent=2)
    
    def summary(self):
        total_errors = sum(len(v) for v in self.errors.values())
        total_warnings = sum(len(v) for v in self.warnings.values())
        return f"Errors: {total_errors}, Warnings: {total_warnings}"

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

def run_cmd(cmd, check=True, capture=True, show_output=False, indent="\t\t", timeout=None):
    """Run command and return output. Use show_output=True for realtime feedback with indent."""
    import subprocess
    import threading
    
    if show_output:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=False, bufsize=1)
        
        def stream_output(stream):
            try:
                for line in stream:
                    decoded_line = line.decode('utf-8', errors='replace').rstrip()
                    log(f"{indent}{decoded_line}")
                    sys.stdout.flush()
            except Exception as e:
                log(f"{indent}Error reading output: {e}")
        
        thread = threading.Thread(target=stream_output, args=(process.stdout,))
        thread.daemon = True
        thread.start()
        
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"Command timed out after {timeout} seconds: {cmd}")
            
        thread.join(timeout=5)
        
        if check and process.returncode != 0:
            raise RuntimeError(f"Command failed: {cmd}")
        return ""
    
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout)
    if check and result.returncode != 0:
        log(f"ERROR: {cmd}")
        log(f"stdout: {result.stdout}")
        log(f"stderr: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout if capture else ""

def extract_songdta_from_pkg(pkg_path, source_name, temp_dir, metadata_dir=None, empty_baseline=None, error_tracker=None):
    """Extract only .songdta_ps4 files from a PKG using two-step extraction."""
    pkg_name = os.path.basename(pkg_path)
    log(f"\t\t[1/4] Extracting: {pkg_name}")
    sys.stdout.flush()
    
    basename = pkg_name.replace('.pkg', '')
    work_dir = os.path.join(temp_dir, 'pfs_extract_' + basename)
    pfs_file = os.path.join(work_dir, "inner.pfs")
    pfs_extract_dir = os.path.join(work_dir, "pfs_contents")
    
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # Step 1: Extract inner PFS image
        log(f"\t\t[2/4] Extracting PFS image...")
        sys.stdout.flush()
        run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract PkgTool.Core pkg_extractinnerpfs "{pkg_path}" {pfs_file}', show_output=True, indent="\t\t", timeout=3600)
        
        # Step 2: Extract PFS contents with limited parallelism to avoid file lock errors
        # Using environment variables to limit thread pool size and avoid parallel extraction
        log(f"\t\t[3/4] Extracting song data from PFS...")
        sys.stdout.flush()
        try:
            # Limit to 2 threads to reduce file lock conflicts
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract DOTNET_ThreadPool_UnfairSemaphoreSpinLimit=0 DOTNET_ProcessorCount=2 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}', show_output=True, indent="\t\t\t", timeout=3600)
        except RuntimeError as e:
            if error_tracker:
                error_tracker.add_error('pfs_extraction_failed', pkg_name, str(e))
            log(f"\t\tFirst attempt failed: {e}")
            log("\t\tRetrying with single thread...")
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract DOTNET_ThreadPool_UnfairSemaphoreSpinLimit=0 DOTNET_ProcessorCount=1 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}', show_output=True, indent="\t\t\t", timeout=3600)
        
        # Find all .songdta_ps4 files
        songdta_files = []
        for root, dirs, files in os.walk(pfs_extract_dir):
            for f in files:
                if f.endswith('.songdta_ps4'):
                    songdta_files.append(os.path.join(root, f))
        
        if not songdta_files:
            log(f"\t\tNo songdta files found!")
            return []
        
        # Extract metadata using Python script
        # Write to metadata_dir if provided, otherwise temp_dir
        if metadata_dir:
            os.makedirs(metadata_dir, exist_ok=True)
            temp_output = os.path.join(metadata_dir, f'metadata_{basename}.json')
        else:
            temp_output = os.path.join(temp_dir, f'metadata_{basename}.json')
        files_arg = ' '.join(f'"{f}"' for f in songdta_files)
        run_cmd(f'python3 /workspace/RB4/scripts/extract_binary_dta.py {files_arg} {temp_output}', show_output=True, indent="\t\t", timeout=300)
        
        # Load and tag with source
        with open(temp_output) as f:
            songs = json.load(f)
        
        # Handle empty songs using baseline if provided
        if empty_baseline:
            for song in songs:
                # Use _debug_file (filename) as the key for the baseline mapping
                filename = song.get('_debug_file', '')
                short_name = filename.replace('.songdta_ps4', '')
                
                if not song.get('artist') or song.get('artist') == 'Unknown':
                    if short_name in empty_baseline:
                        baseline_info = empty_baseline[short_name]
                        # Use baseline if current is empty or 'Unknown'
                        current_title = song.get('title')
                        current_artist = song.get('artist')
                        
                        if not current_title or current_title == short_name:
                            song['title'] = baseline_info.get('title') or current_title
                        if not current_artist or current_artist == 'Unknown':
                            song['artist'] = baseline_info.get('artist') or current_artist
                        # Mark as inferred so we know it came from fallback
                        song['inferred'] = True
    
        for song in songs:
            binary_source = song.get('source', '')
            use_pkg_source = (
                source_name not in ('unknown', 'Custom') or 
                binary_source in ('Custom', 'unknown', '')
            )
            if use_pkg_source:
                song['source'] = source_name
        
        log(f"\t\tExtracted {len(songs)} songs")
        return songs
        
    finally:
        # Clean up to free disk space
        log(f"\t\t[4/4] Cleaning up extraction files...")
        sys.stdout.flush()
        shutil.rmtree(work_dir, ignore_errors=True)
        log(f"\t✓ Done: {pkg_name}")


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
    parser.add_argument('--metadata-dir', default=DEFAULT_METADATA_DIR,
                        help=f'Output directory for extracted metadata JSONs (default: {DEFAULT_METADATA_DIR})')
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
    parser.add_argument('--smb', action='store_true',
                        help='PKGs are on SMB share (use smbclient to access)')
    parser.add_argument('--log', default=None,
                        help='Log file path (default: temp_dir/metadata_<timestamp>.log)')

    args = parser.parse_args()

    # Ensure directories exist on fresh checkout
    os.makedirs(args.temp_dir, exist_ok=True)
    os.makedirs(args.metadata_dir, exist_ok=True)
    os.makedirs(args.songlist_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    
    global LOG_FILE
    if args.log:
        LOG_FILE = args.log
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        LOG_FILE = os.path.join(args.temp_dir, f'rb4_extract_{ts}.log')
    log(f"Logging to: {LOG_FILE}")
    log(f"Started at {datetime.now().isoformat()}")
    
    # Initialize error tracker
    error_tracker = ErrorTracker()
    if not args.incremental:
        log("Full rebuild mode - clearing previous state...")
        for f in [PROCESSED_PKGS_FILE, UPDATE_HISTORY_FILE, args.output_json]:
            if os.path.exists(f):
                os.remove(f)
        # Clear output directory BEFORE generating (skip directories)
        if os.path.exists(args.songlist_dir):
            for f in os.listdir(args.songlist_dir):
                fpath = os.path.join(args.songlist_dir, f)
                if os.path.isfile(fpath):
                    os.remove(fpath)
    
    # Find all PKG files
    empty_baseline = load_empty_songs_baseline()
    if empty_baseline:
        log(f"Loaded empty songs baseline with {len(empty_baseline)} entries")

    if args.smb:
        # Use smbclient to list PKGs from SMB share
        log("Accessing PKGs via SMB...")
        sys.path.insert(0, '/workspace/RB4/scripts')
        from smb_pkg_finder import list_pkgs as smb_list_pkgs
        pkg_names = smb_list_pkgs()
        pkg_files = pkg_names  # Store just names, we'll fetch one at a time
    else:
        # Local directory - filter out macOS hidden files (starting with ._)
        if not os.path.isdir(args.pkg_dir):
            log(f"ERROR: PKG directory not found: {args.pkg_dir}")
            sys.exit(1)
        
        pkg_files = [
            os.path.join(args.pkg_dir, f) 
            for f in os.listdir(args.pkg_dir) 
            if f.endswith('.pkg') and not f.startswith('._')
        ]
    
    if not pkg_files:
        log(f"No .pkg files found in {args.pkg_dir}")
        sys.exit(1)
    
    log(f"Found {len(pkg_files)} PKG files in {args.pkg_dir}")
    
    # Load processed PKGs for incremental mode
    processed = load_processed_pkgs() if args.incremental else set()
    log(f"Incremental mode: {'enabled' if args.incremental else 'disabled'}")
    if processed:
        log(f"  Already processed: {len(processed)} PKGs")
    
    # Filter out already-processed PKGs
    if args.incremental:
        new_pkgs = [p for p in pkg_files if os.path.basename(p) not in processed]
        skipped = len(pkg_files) - len(new_pkgs)
        if skipped > 0:
            log(f"  Skipping {skipped} already-processed PKGs")
        pkg_files = new_pkgs
    
    if not pkg_files:
        log("No new PKGs to process.")
        log("\nGenerating song lists from existing data...")
        run_cmd(f'cd /workspace/RB4 && node generate_rb4_song_list.js --baseline {args.baseline} --custom {args.output_json} --processed {PROCESSED_PKGS_FILE}')
        log("✅ Done!")
        sys.exit(0)
    
    log(f"Processing {len(pkg_files)} new PKGs...")
    
    all_songs = []
    total_pkgs = len(pkg_files)
    
    for idx, pkg_path in enumerate(sorted(pkg_files), 1):
        source = get_pkg_source(pkg_path)
        pkg_name = os.path.basename(pkg_path)
        
        # For SMB mode: fetch one file at a time
        if args.smb:
            log(f"[{idx}/{total_pkgs}] Fetching: {pkg_name}")
            sys.stdout.flush()
            
            # Fetch from SMB to temp dir
            sys.path.insert(0, '/workspace/RB4/scripts')
            from smb_pkg_finder import get_pkg_file
            success = get_pkg_file(pkg_name, args.temp_dir)
            
            if not success:
                log(f"  ERROR: Failed to fetch {pkg_name} from SMB")
                continue
            
            # Use the fetched file
            pkg_path = os.path.join(args.temp_dir, pkg_name)
        
        log(f"[{idx}/{total_pkgs}] Processing: {pkg_name}")
        sys.stdout.flush()
        
        try:
            songs = extract_songdta_from_pkg(pkg_path, source, args.temp_dir, args.metadata_dir, empty_baseline, error_tracker)
            all_songs.extend(songs)
            
            # For SMB mode: clean up immediately after processing to free space
            if args.smb and os.path.exists(pkg_path):
                os.remove(pkg_path)
                log(f"\tCleaned up {pkg_name} to free space")
            
            # Mark as processed
            processed.add(pkg_name)
            save_processed_pkgs(processed)
            
            pct = int(idx / total_pkgs * 100)
            log(f"Progress: {pct}% ({idx}/{total_pkgs} PKGs) | Total songs: {len(all_songs)}")
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = str(e)
            # Categorize the error based on what failed
            if 'pkg_extractinnerpfs' in error_msg:
                error_tracker.add_error('pfs_image_extract_failed', pkg_name, error_msg)
            elif 'pfs_extract' in error_msg:
                error_tracker.add_error('pfs_contents_extract_failed', pkg_name, error_msg)
            elif 'UnauthorizedAccessException' in error_msg or 'MemoryMapped' in error_msg:
                error_tracker.add_error('memory_map_error', pkg_name, error_msg)
            else:
                error_tracker.add_error('pkg_processing_failed', pkg_name, error_msg)
            log(f"ERROR processing {pkg_name}: {e}")
            continue
    
    log(f"\nExtracted {len(all_songs)} songs from {len(pkg_files)} PKGs")
    
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
        log(f"Merged with existing: {len(all_songs)} total songs")
    
    # Filter out garbage entries
    valid_songs = [s for s in all_songs if s.get('title') or s.get('artist')]
    garbage = len(all_songs) - len(valid_songs)
    if garbage > 0:
        log(f"Filtered out {garbage} garbage entries")
    
    # NEW: Track empty songs separately (these are REAL songs with unparseable metadata)
    # They have no title/artist because .songdta_ps4 contains only zeros
    empty_songs = [s for s in all_songs if not s.get('title') and not s.get('artist')]
    if empty_songs:
        empty_output = os.path.join(os.path.dirname(args.output_json), 'empty_songs.json')
        with open(empty_output, 'w') as f:
            json.dump(empty_songs, f, indent=2)
        log(f"Saved {len(empty_songs)} empty songs (unparseable metadata) to: {empty_output}")
    
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
        log(f"Recorded {len(new_only)} new songs in update history")
    elif len(all_songs) > 0:
        # Even if no truly new songs, record this run (for --no-incremental)
        record_update(valid_songs, len(valid_songs))
        log(f"Recorded {len(valid_songs)} songs in update history (full rebuild)")
    
    # Write JSON
    with open(args.output_json, 'w') as f:
        json.dump(valid_songs, f, indent=2)
    log(f"Written: {args.output_json}")
    
    # Check for issues
    zero_dur = [s for s in valid_songs if s.get('durationMs', 0) == 0]
    if zero_dur:
        log(f"\n⚠️  Songs with durationMs=0: {len(zero_dur)}")
    
    # Generate song lists
    log(f"\nGenerating song lists...")
    run_cmd(f'cd /workspace/RB4 && node generate_rb4_song_list.js --baseline {args.baseline} --custom {args.output_json} --processed {PROCESSED_PKGS_FILE}')
    
    # Save error tracking report
    error_tracker.save()
    log(f"\n📊 Error Report: {error_tracker.summary()}")
    log(f"   Full report saved to: {ERROR_LOG_FILE}")
    
    log("\n✅ Pipeline complete!")
    log(f"Processed PKGs saved to: {PROCESSED_PKGS_FILE}")


if __name__ == '__main__':
    main()