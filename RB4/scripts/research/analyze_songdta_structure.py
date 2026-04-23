#!/usr/bin/env python3
"""
Diagnostic script to check songdta_ps4 file structure.
Compares our parsing against expected structure from LibForge.
"""

import struct
import json
import os
import glob
import subprocess

WORK_DIR = "/workspace/RB4/rb4_temp/diagnostic"
os.makedirs(WORK_DIR, exist_ok=True)

# Expected structure from LibForge 010/songdta.bt
EXPECTED_STRUCTURE = [
    ('songdta_type', 0, 4, '<I', 'uint32'),
    ('song_id', 4, 4, '<I', 'uint32'),
    ('version', 8, 2, '<h', 'int16'),
    ('game_origin', 10, 18, 'string', 'char[18]'),
    ('preview_start', 28, 4, '<f', 'float'),
    ('preview_end', 32, 4, '<f', 'float'),
    ('name', 36, 256, 'string', 'char[256]'),
    ('artist', 292, 256, 'string', 'char[256]'),
    ('album_name', 548, 256, 'string', 'char[256]'),
    ('album_track_number', 804, 2, '<h', 'int16'),
    ('album_year', 808, 4, '<I', 'int32'),
    ('original_year', 812, 4, '<I', 'int32'),
    ('genre', 816, 64, 'string', 'char[64]'),
    ('song_length', 880, 4, '<f', 'float'),
    ('guitar', 884, 4, '<f', 'float'),
    ('bass', 888, 4, '<f', 'float'),
    ('vocals', 892, 4, '<f', 'float'),
    ('drum', 896, 4, '<f', 'float'),
    ('band', 900, 4, '<f', 'float'),
    ('keys', 904, 4, '<f', 'float'),
    ('real_keys', 908, 4, '<f', 'float'),
    ('shortname', 945, 256, 'string', 'char[256]'),  # After 'fake' at 944
]

def read_struct_string(data, offset, max_size):
    """Read null-terminated string."""
    if offset + max_size > len(data):
        return ""
    chunk = data[offset:offset + max_size]
    return chunk.split(b'\x00')[0].decode('utf-8', errors='replace').strip()

def read_struct_int(data, offset, size, fmt):
    """Read integer."""
    if offset + size > len(data):
        return 0
    return struct.unpack(fmt, data[offset:offset+size])[0]

def analyze_file(filepath):
    """Analyze a single .songdta_ps4 file."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    result = {
        'file': os.path.basename(filepath),
        'size': len(data),
        'is_valid_size': len(data) >= 1201,  # 945 + 256 minimum
        'fields': {},
        'issues': []
    }
    
    if len(data) < 100:
        result['issues'].append('File too small (< 100 bytes)')
        return result
    
    # Read each field
    for field_name, offset, size, fmt, description in EXPECTED_STRUCTURE:
        if fmt == 'string':
            value = read_struct_string(data, offset, size)
        else:
            value = read_struct_int(data, offset, size, fmt)
        
        result['fields'][field_name] = {
            'offset': offset,
            'value': value,
            'is_empty': value == '' or value == 0
        }
        
        if value == '' or value == 0:
            result['issues'].append(f'{field_name} is empty/zero (offset {offset})')
    
    # Check for data after shortname
    if len(data) > 1201:
        result['fields']['extra_data'] = f'{len(data) - 1201} bytes after shortname'
    
    return result

def download_and_analyze(pkg_name):
    """Download PKG and analyze its songdta files."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {pkg_name}")
    print(f"{'='*80}")
    
    # Download PKG
    pkg_path = os.path.join(WORK_DIR, pkg_name)
    if not os.path.exists(pkg_path):
        print(f"Downloading {pkg_name}...")
        cmd = f'smbclient //192.168.100.135/incoming/temp/Rb4Dlc -N -c "get \\"{pkg_name}\\" \\"{pkg_path}\\""'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            print(f"Download failed: {result.stderr[:200]}")
            return
    
    # Extract PFS
    pfs_file = os.path.join(WORK_DIR, "inner.pfs")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract PkgTool.Core pkg_extractinnerpfs "{pkg_path}" "{pfs_file}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"PFS extraction failed")
        return
    
    # Extract contents
    contents_dir = os.path.join(WORK_DIR, "contents")
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract PkgTool.Core pfs_extract "{pfs_file}" "{contents_dir}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"Contents extraction failed")
        return
    
    # Find songdta files
    songdta_files = []
    for root, dirs, files in os.walk(contents_dir):
        for f in files:
            if f.endswith('.songdta_ps4'):
                songdta_files.append(os.path.join(root, f))
    
    print(f"Found {len(songdta_files)} .songdta_ps4 files")
    
    # Analyze first 5 files
    total_valid = 0
    total_invalid = 0
    all_issues = []
    
    for i, filepath in enumerate(songdta_files[:10]):
        result = analyze_file(filepath)
        
        if result['is_valid_size']:
            total_valid += 1
        else:
            total_invalid += 1
        
        if i < 3:  # Show first 3 in detail
            print(f"\n{os.path.basename(filepath)}:")
            print(f"  Size: {result['size']} bytes (valid: {result['is_valid_size']})")
            for field_name, info in result['fields'].items():
                if field_name not in ['extra_data']:
                    status = "EMPTY" if info['is_empty'] else "OK"
                    val_str = str(info['value'])[:50] if info['value'] else "(empty)"
                    print(f"  {field_name}: {val_str} [{status}]")
    
    print(f"\nSummary: {total_valid} valid size, {total_invalid} invalid size")
    
    # Cleanup
    subprocess.run(['rm', '-rf', contents_dir], shell=True)

def main():
    # Test with top 5 problematic PKGs
    problem_pkgs = [
        "UP8802-CUSA02084_00-RBLEGACYDLCPASS3-A0000-V0100.pkg",  # 156 empty
        "UP8802-CUSA02084_00-RBLEGACYDLCPASS2-A0000-V0100.pkg",  # 140 empty
        "UP8802-CUSA02084_00-RBLEGACYDLCPASS1-A0000-V0100.pkg",  # 118 empty
        "UP8802-CUSA02084_00-RB4SEASON21TOS30-A0000-V0100.pkg",  # 68 empty
        "UP8802-CUSA02084_00-RB4PRESEASONPASS-A0000-V0100.pkg",  # 58 empty
    ]
    
    for pkg in problem_pkgs:
        download_and_analyze(pkg)

if __name__ == '__main__':
    main()