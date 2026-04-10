import glob
import os
import re
import sys

def scan_ark_for_sng(ark_path):
    found_offsets = []
    try:
        with open(ark_path, 'rb') as f:
            chunk_size = 10 * 1024 * 1024
            overlap = 1024 * 10
            offset = 0
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                pos = chunk.find(b"SNGPKG")
                while pos != -1:
                    found_offsets.append(offset + pos)
                    pos = chunk.find(b"SNGPKG", pos + 1)
                
                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                    offset += chunk_size - overlap
                else:
                    break
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return found_offsets

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scan_sng.py <ark_path>")
        sys.exit(1)
    
    ark_path = sys.argv[1]
    offsets = scan_ark_for_sng(ark_path)
    print(f"Found {len(offsets)} SNGPKG headers in {ark_path}:")
    for o in offsets:
        print(o)
