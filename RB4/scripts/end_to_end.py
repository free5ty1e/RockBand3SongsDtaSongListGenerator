#!/usr/bin/env python3
"""
end_to_end.py — Full pipeline: extract songdta from PKGs → extract metadata → generate lists.
Processes one PKG at a time, extracts only .songdta_ps4, saves metadata, cleans up.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil

def run_cmd(cmd, check=True, capture=True):
    """Run command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout if capture else ""

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

def extract_songdta_from_pkg(pkg_path, source_name):
    """Extract only .songdta_ps4 files from a PKG using two-step extraction."""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(pkg_path)} ({source_name})")
    print(f"{'='*60}")
    
    basename = os.path.basename(pkg_path).replace('.pkg', '')
    work_dir = os.path.join('/workspace', 'pfs_extract_' + basename)
    pfs_file = os.path.join(work_dir, "inner.pfs")
    pfs_extract_dir = os.path.join(work_dir, "pfs_contents")
    
    # Try to extract to /workspace (more stable than /tmp)
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # Step 1: Extract inner PFS image
        print(f"Extracting inner PFS...")
        run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pkg_extractinnerpfs "{pkg_path}" {pfs_file}')
        
        # Step 2: Extract PFS contents (retry once on failure)
        print(f"Extracting PFS contents...")
        try:
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}')
        except RuntimeError:
            print("First attempt failed, retrying...")
            run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pfs_extract {pfs_file} {pfs_extract_dir}')
        
        # Find all .songdta_ps4 files
        songdta_files = []
        for root, dirs, files in os.walk(pfs_extract_dir):
            for f in files:
                if f.endswith('.songdta_ps4'):
                    songdta_files.append(os.path.join(root, f))
        
        print(f"Found {len(songdta_files)} .songdta_ps4 files")
        
        if not songdta_files:
            print("No songdta files found!")
            return []
        
        # Extract metadata
        temp_output = tempfile.mktemp(suffix=".json")
        files_arg = ' '.join(f'"{f}"' for f in songdta_files)
        print(f"Extracting metadata...")
        run_cmd(f'cd /workspace && python3 RB4/scripts/extract_binary_dta.py {files_arg} {temp_output}')
        
        # Load and tag with source
        with open(temp_output) as f:
            songs = json.load(f)
        
        for song in songs:
            song['source'] = source_name
        
        print(f"Extracted {len(songs)} songs")
        return songs
        
    finally:
        # Clean up workspace
        print(f"Cleaning up {work_dir}...")
        shutil.rmtree(work_dir, ignore_errors=True)

def process_pkgs(pkg_dir):
    """Find and process all PKG files in a directory."""
    # Find all PKG files
    pkg_files = []
    for f in os.listdir(pkg_dir):
        if f.endswith('.pkg'):
            pkg_files.append(os.path.join(pkg_dir, f))
    
    if not pkg_files:
        print(f"No .pkg files found in {pkg_dir}")
        return []
    
    print(f"Found {len(pkg_files)} PKG files")
    
    all_songs = []
    for pkg_path in sorted(pkg_files):
        source = get_pkg_source(pkg_path)
        songs = extract_songdta_from_pkg(pkg_path, source)
        all_songs.extend(songs)
        print(f"Running total: {len(all_songs)} songs")
    
    return all_songs

def main():
    # Default to /workspace/pkgs but allow override via argument
    pkg_dir = sys.argv[1] if len(sys.argv) > 1 else "/workspace/pkgs"
    
    print(f"Starting extraction pipeline...")
    print(f"PKG directory: {pkg_dir}")
    
    if not os.path.isdir(pkg_dir):
        print(f"ERROR: {pkg_dir} is not a directory")
        sys.exit(1)
    
    all_songs = process_pkgs(pkg_dir)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_songs)} songs extracted")
    print(f"{'='*60}")
    
    # Filter out garbage entries (songs with no title or artist)
    valid_songs = [s for s in all_songs if s.get('title') or s.get('artist')]
    garbage = len(all_songs) - len(valid_songs)
    if garbage > 0:
        print(f"Filtered out {garbage} garbage entries (no title/artist)")
    
    # Write combined JSON
    output_json = "/workspace/RB4/rb4_custom_songs.json"
    with open(output_json, 'w') as f:
        json.dump(valid_songs, f, indent=2)
    print(f"Written: {output_json}")
    
    # Check for issues
    zero_dur = [s for s in all_songs if s.get('durationMs', 0) == 0]
    if zero_dur:
        print(f"\n⚠️  Songs with durationMs=0: {len(zero_dur)}")
        for s in zero_dur[:5]:
            print(f"   - {s.get('shortName')}: {s.get('title')}")
    
    no_shortname = [s for s in all_songs if not s.get('shortName')]
    if no_shortname:
        print(f"\n⚠️  Songs with empty shortName: {len(no_shortname)}")
    
    # Generate song lists
    print(f"\nGenerating song lists...")
    run_cmd('cd /workspace/RB4 && node generate_rb4_song_list.js --baseline rb4songlistWithRivals.txt --custom rb4_custom_songs.json')
    
    print(f"\n✅ Pipeline complete!")

if __name__ == '__main__':
    main()
