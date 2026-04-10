import glob
import os
import struct
import mmap
import re

def extract_strings_near_marker(mm, pos):
    # Scan a larger area around the marker for human-readable strings
    start = max(0, pos - 1024)
    end = min(len(mm), pos + 4096)
    chunk = mm[start:end]
    
    # Find all strings of 3-60 chars that look like words
    matches = re.findall(b'[a-zA-Z0-9\s\.,\'\(\)-]{3,60}', chunk)
    return [m.decode('ascii', errors='ignore').strip() for m in matches]

def main():
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    results = {}
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        pos = mm.find(b"RBSongMetadata")
                        while pos != -1:
                            strings = extract_strings_near_marker(mm, pos)
                            # We store the strings found near each marker
                            results[pos] = strings
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    # Now let's try to find commonalities or outliers
    # Since we can't easily print all, let's save to a file
    with open('/workspace/RB4/output/metadata_block_strings.txt', 'w') as f:
        for pos, strings in results.items():
            f.write(f"Pos {pos}: {', '.join(strings)}\n")
    
    print(f"\nExtracted strings from {len(results)} metadata blocks")

if __name__ == "__main__":
    main()
