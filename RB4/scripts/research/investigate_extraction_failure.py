#!/usr/bin/env python3
"""
Investigate why certain songdta_ps4 files fail to parse.

This script:
1. Downloads a problematic PKG
2. Extracts specific songdta files
3. Analyzes file sizes and raw bytes
4. Tries to understand why parsing fails
"""

import subprocess
import os
import json
import struct

WORK_DIR = "/workspace/RB4/rb4_temp/investigate_failure"
SMB_SERVER = "192.168.100.135"
SMB_SHARE = "incoming/temp/Rb4Dlc"

def download_pkg(pkg_name):
    """Download a PKG from SMB."""
    os.makedirs(WORK_DIR, exist_ok=True)
    pkg_path = os.path.join(WORK_DIR, pkg_name)
    
    if not os.path.exists(pkg_path):
        print(f"Downloading {pkg_name}...")
        cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "get \\"{pkg_name}\\" \\"{pkg_path}\\""'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"Download failed: {result.stderr[:200]}")
            return None
    return pkg_path

def extract_pfs(pkg_path):
    """Extract PFS from PKG."""
    pfs_file = os.path.join(WORK_DIR, "inner.pfs")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract PkgTool.Core pkg_extractinnerpfs "{pkg_path}" "{pfs_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"PFS extraction failed: {result.stderr[:200]}")
        return None
    return pfs_file

def extract_contents(pfs_file):
    """Extract PFS contents."""
    contents_dir = os.path.join(WORK_DIR, "contents")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract DOTNET_ThreadPool_UnfairSemaphoreSpinLimit=0 DOTNET_ProcessorCount=1 PkgTool.Core pfs_extract "{pfs_file}" "{contents_dir}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"Contents extraction failed: {result.stderr[:200]}")
        return None
    return contents_dir

def analyze_songdta(filepath):
    """Analyze a songdta file in detail."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    result = {
        'file': os.path.basename(filepath),
        'size': len(data),
        'is_truncated': len(data) < 1201,  # Need at least 1201 bytes for all fields
        'has_data_at_offsets': {},
    }
    
    # Check key offsets for data
    offsets_to_check = [
        (0, 4, 'songdta_type'),
        (4, 4, 'song_id'),
        (10, 18, 'game_origin'),
        (36, 256, 'name'),
        (292, 256, 'artist'),
        (548, 256, 'album'),
        (945, 256, 'shortname'),
    ]
    
    for offset, size, name in offsets_to_check:
        if offset + size <= len(data):
            chunk = data[offset:offset + size]
            non_zero = sum(1 for b in chunk if b != 0)
            result['has_data_at_offsets'][name] = {
                'non_zero_bytes': non_zero,
                'total_bytes': size,
                'percentage': 100 * non_zero / size if size > 0 else 0,
            }
            
            # Try to decode string
            if name in ['game_origin', 'name', 'artist', 'album', 'shortname']:
                try:
                    string_val = chunk.split(b'\x00')[0].decode('utf-8', errors='replace').strip()
                    result['has_data_at_offsets'][name]['string_value'] = string_val if string_val else "(empty)"
                except:
                    result['has_data_at_offsets'][name]['string_value'] = "(error)"
        else:
            result['has_data_at_offsets'][name] = {'error': 'out of bounds'}
    
    return result

def main():
    # Test with RBLEGACYDLCPASS3 (largest number of failures)
    pkg_name = "UP8802-CUSA02084_00-RBLEGACYDLCPASS3-A0000-V0100.pkg"
    
    print(f"Investigating: {pkg_name}")
    print("=" * 60)
    
    # Download
    pkg_path = download_pkg(pkg_name)
    if not pkg_path:
        return
    
    # Extract
    pfs_file = extract_pfs(pkg_path)
    if not pfs_file:
        return
    
    contents_dir = extract_contents(pfs_file)
    if not contents_dir:
        return
    
    # Find all songdta files
    songdta_files = []
    for root, dirs, files in os.walk(contents_dir):
        for f in files:
            if f.endswith('.songdta_ps4'):
                songdta_files.append(os.path.join(root, f))
    
    print(f"Found {len(songdta_files)} .songdta_ps4 files\n")
    
    # Analyze a sample of files
    analyze_results = []
    for filepath in songdta_files[:50]:  # First 50
        result = analyze_songdta(filepath)
        analyze_results.append(result)
    
    # Categorize results
    working = []
    failing = []
    truncated = []
    
    for r in analyze_results:
        if r['is_truncated']:
            truncated.append(r)
        elif r['has_data_at_offsets'].get('name', {}).get('string_value') == '(empty)':
            failing.append(r)
        else:
            working.append(r)
    
    print(f"Analysis of first 50 files:")
    print(f"  Working (good data): {len(working)}")
    print(f"  Empty strings: {len(failing)}")
    print(f"  Truncated: {len(truncated)}")
    
    # Show examples
    print("\n" + "=" * 60)
    print("EXAMPLE: Working file")
    print("=" * 60)
    if working:
        r = working[0]
        print(f"File: {r['file']}")
        print(f"Size: {r['size']} bytes")
        for name, info in r['has_data_at_offsets'].items():
            if 'string_value' in info:
                print(f"  {name}: '{info['string_value']}'")
    
    print("\n" + "=" * 60)
    print("EXAMPLE: File with empty strings (FAILING)")
    print("=" * 60)
    if failing:
        r = failing[0]
        print(f"File: {r['file']}")
        print(f"Size: {r['size']} bytes")
        for name, info in r['has_data_at_offsets'].items():
            if 'string_value' in info:
                print(f"  {name}: '{info['string_value']}'")
            elif 'non_zero_bytes' in info:
                print(f"  {name}: {info['non_zero_bytes']}/{info['total_bytes']} non-zero bytes ({info['percentage']:.1f}%)")
        
        # Show raw bytes at key locations
        filepath = None
        for f in songdta_files:
            if os.path.basename(f) == r['file']:
                filepath = f
                break
        
        if filepath:
            with open(filepath, 'rb') as f:
                data = f.read()
            print(f"\nRaw hex at offset 36 (name): {data[36:68].hex()}")
            print(f"Raw hex at offset 292 (artist): {data[292:324].hex()}")
            print(f"Raw hex at offset 945 (shortname): {data[945:977].hex()}")
    
    # Save detailed results
    results_file = os.path.join(WORK_DIR, 'investigation_results.json')
    with open(results_file, 'w') as f:
        json.dump({
            'total_files': len(songdta_files),
            'analyzed': len(analyze_results),
            'working': len(working),
            'failing': len(failing),
            'truncated': len(truncated),
            'results': analyze_results
        }, f, indent=2)
    print(f"\nResults saved to {results_file}")

if __name__ == '__main__':
    main()