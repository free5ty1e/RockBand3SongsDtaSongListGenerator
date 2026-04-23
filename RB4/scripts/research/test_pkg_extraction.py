#!/usr/bin/env python3
"""
Systematic PKG extraction tester - tests each PKG for empty metadata.
This script helps identify which PKGs have extraction problems.
"""

import subprocess
import json
import os
import sys
import time

SMB_SERVER = "192.168.100.135"
SMB_SHARE = "incoming/temp/Rb4Dlc"
WORK_DIR = "/workspace/RB4/rb4_temp/pkg_test"
METADATA_DIR = "/workspace/RB4/output/PkgMetadataExtracted"

sys.path.insert(0, '/workspace/RB4/scripts')

def get_all_pkgs():
    """Get list of all PKGs from SMB."""
    cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    pkgs = []
    for line in result.stdout.split('\n'):
        if ('UP8802-' in line or 'Rock.Band.4_' in line) and '.pkg' in line and not line.startswith('  ._'):
            parts = line.split()
            if parts:
                pkgs.append(parts[0])
    return pkgs

def extract_pkg_metadata(pkg_name, work_dir):
    """Extract all song metadata from a single PKG."""
    os.makedirs(work_dir, exist_ok=True)
    
    # Download PKG
    cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "get \\"{pkg_name}\\" \\"{work_dir}/{pkg_name}\\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=1800)
    if result.returncode != 0:
        return None, f"Download failed: {result.stderr}"
    
    pkg_path = f"{work_dir}/{pkg_name}"
    if not os.path.exists(pkg_path):
        return None, "PKG file not found after download"
    
    # Extract PFS
    basename = pkg_name.replace('.pkg', '')
    work_subdir = os.path.join(work_dir, basename)
    os.makedirs(work_subdir, exist_ok=True)
    
    pfs_file = os.path.join(work_dir, "inner.pfs")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract PkgTool.Core pkg_extractinnerpfs "{pkg_path}" "{pfs_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        return None, f"PFS extraction failed"
    
    # Extract contents
    pfs_contents = os.path.join(work_dir, "pfs_contents")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract DOTNET_ThreadPool_UnfairSemaphoreSpinLimit=0 DOTNET_ProcessorCount=1 PkgTool.Core pfs_extract "{pfs_file}" "{pfs_contents}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        return None, f"Contents extraction failed"
    
    # Find all .songdta_ps4 files
    songdta_files = []
    for root, dirs, files in os.walk(pfs_contents):
        for f in files:
            if f.endswith('.songdta_ps4'):
                songdta_files.append(os.path.join(root, f))
    
    if not songdta_files:
        return None, "No .songdta_ps4 files found"
    
    # Extract metadata
    output_file = os.path.join(work_dir, f"metadata_{basename}.json")
    files_arg = ' '.join(f'"{f}"' for f in songdta_files)
    cmd = f'python3 /workspace/RB4/scripts/extract_binary_dta.py {files_arg} "{output_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    
    if not os.path.exists(output_file):
        return None, "Metadata extraction failed"
    
    with open(output_file) as f:
        songs = json.load(f)
    
    return songs, None

def analyze_songs(songs):
    """Analyze extracted songs for empty metadata."""
    total = len(songs)
    empty_artist = 0
    empty_title = 0
    empty_shortname = 0
    
    empty_songs = []
    
    for s in songs:
        has_empty = False
        if not s.get('artist') or s.get('artist') == 'Unknown' or s.get('artist') == '':
            empty_artist += 1
            has_empty = True
        if not s.get('title') or s.get('title') == '':
            empty_title += 1
            has_empty = True
        if not s.get('shortName') or s.get('shortName') == '':
            empty_shortname += 1
            has_empty = True
        
        if has_empty:
            empty_songs.append({
                'shortName': s.get('shortName', ''),
                'title': s.get('title', ''),
                'artist': s.get('artist', ''),
                '_debug_file': s.get('_debug_file', '')
            })
    
    return {
        'total': total,
        'empty_artist': empty_artist,
        'empty_title': empty_title,
        'empty_shortname': empty_shortname,
        'empty_songs': empty_songs
    }

def main():
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Get PKGs
    print("Fetching PKG list from SMB...")
    pkgs = get_all_pkgs()
    print(f"Found {len(pkgs)} PKGs\n")
    
    results = []
    
    for i, pkg in enumerate(pkgs, 1):
        print(f"[{i}/{len(pkgs)}] Testing {pkg}...")
        
        pkg_work_dir = os.path.join(WORK_DIR, pkg.replace('.pkg', ''))
        
        songs, error = extract_pkg_metadata(pkg, pkg_work_dir)
        
        if error:
            print(f"  ERROR: {error}")
            results.append({
                'pkg': pkg,
                'status': 'error',
                'error': error
            })
        else:
            analysis = analyze_songs(songs)
            print(f"  Songs: {analysis['total']}, Empty: {analysis['empty_artist']}")
            
            results.append({
                'pkg': pkg,
                'status': 'success',
                'total_songs': analysis['total'],
                'empty_artist': analysis['empty_artist'],
                'empty_title': analysis['empty_title'],
                'empty_shortname': analysis['empty_shortname'],
                'empty_songs': analysis['empty_songs']
            })
        
        # Cleanup
        if os.path.exists(pkg_work_dir):
            subprocess.run(['rm', '-rf', pkg_work_dir], shell=True)
        
        time.sleep(0.5)
    
    # Save results
    output_file = os.path.join(WORK_DIR, 'extraction_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to {output_file}")
    
    # Summary
    total_pkgs = len(results)
    failed = sum(1 for r in results if r['status'] == 'error')
    with_empty = sum(1 for r in results if r.get('empty_artist', 0) > 0)
    total_empty = sum(r.get('empty_artist', 0) for r in results)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total PKGs tested: {total_pkgs}")
    print(f"Failed extractions: {failed}")
    print(f"PKGs with empty metadata: {with_empty}")
    print(f"Total songs with empty metadata: {total_empty}")
    
    # List PKGs with problems
    print(f"\n=== PKGs WITH EMPTY METADATA ===")
    for r in results:
        if r.get('empty_artist', 0) > 0:
            print(f"{r['pkg']}: {r['empty_artist']} empty artist, {r['total_songs']} total")

if __name__ == '__main__':
    main()