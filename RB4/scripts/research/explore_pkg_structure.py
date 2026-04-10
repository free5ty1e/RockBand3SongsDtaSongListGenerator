#!/usr/bin/env python3
"""
Explore PKG structure - list contents without full extraction
"""
import subprocess
import struct

def list_pkg_contents(pkg_path):
    """Read PKG header to find internal files"""
    with open(pkg_path, 'rb') as f:
        # Read PKG header
        magic = f.read(4)
        print(f"Magic: {magic}")
        
        # Skip to entry count (different PKG versions have different offsets)
        f.seek(0x80)  # Common area for entry count
        try:
            data = f.read(32)
            print(f"Header data at 0x80: {data[:16].hex()}")
        except: pass

def scan_for_ark(pkg_path):
    """Search for .ark signatures inside PKG"""
    with open(pkg_path, 'rb') as f:
        data = f.read(100 * 1024 * 1024)  # First 100MB
        
    # Look for ARK magic
    ark_offsets = []
    pos = 0
    while True:
        idx = data.find(b'ARK', pos)
        if idx == -1:
            break
        ark_offsets.append(idx)
        pos = idx + 1
    
    # Look for SNGPKG
    sng_offsets = []
    pos = 0
    while True:
        idx = data.find(b'SNGPKG', pos)
        if idx == -1:
            break
        sng_offsets.append(idx)
        pos = idx + 1
    
    print(f"Found {len(ark_offsets)} ARK signatures")
    print(f"Found {len(sng_offsets)} SNGPKG signatures")
    
    return ark_offsets, sng_offsets

def scan_for_strings(pkg_path):
    """Look for any readable strings that might be song IDs"""
    with open(pkg_path, 'rb') as f:
        # Read first 50MB
        data = f.read(50 * 1024 * 1024)
    
    # Find ASCII strings
    import re
    strings = re.findall(rb'[a-z][a-z0-9_]{4,30}', data)
    unique = set(strings)
    
    print(f"Found {len(unique)} unique potential IDs")
    return unique

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pkg = sys.argv[1]
    else:
        pkg = "/tmp/NINTENDO00000001.pkg"
    
    print(f"=== Exploring {pkg} ===")
    ark_offsets, sng_offsets = scan_for_ark(pkg)
    
    if ark_offsets:
        print(f"ARK offsets: {ark_offsets[:10]}")
    if sng_offsets:
        print(f"SNGPKG offsets: {sng_offsets[:10]}")
        
    # Try strings
    strings = scan_for_strings(pkg)
    # Filter out noise
    noise_prefixes = [b'000', b'111', b'222', b'333', b'444', b'555', b'666', b'777', b'888', b'999']
    filtered = [s for s in strings if not any(s.startswith(p) for p in noise_prefixes)]
    print(f"Filtered unique strings: {list(filtered)[:20]}")