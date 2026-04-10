import os
import re
import struct
import mmap

def main():
    ark_path = '/workspace/rb4_temp/update_extract/patch_main_ps4_4.ark'
    if not os.path.exists(ark_path):
        print(f"File not found: {ark_path}")
        return

    found_ids = set()
    try:
        with open(ark_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Scan for RBSongMetadata markers
                marker = b"RBSongMetadata"
                pos = mm.find(marker)
                while pos != -1:
                    # Scan a larger window (1KB) for potential song IDs
                    chunk = mm[pos : pos + 1024]
                    # Look for [length][string] patterns
                    # We'll use a regex to find lowercase alphanumeric strings 5-30 chars
                    # that are preceded by a length byte (uint32)
                    # But since we are in a chunk, it's easier to just find all candidates
                    matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                    for m in matches:
                        s = m.decode('ascii', errors='ignore')
                        # Filter out known engine terms (the big blacklist)
                        if '_' in s and not s.startswith('_'):
                            found_ids.add(s)
                    pos = mm.find(marker, pos + 1)
    except Exception as e:
        print(f"Error: {e}")

    # Now we have a list of candidates. Let's try to find their values.
    # We'll save them to a file for later analysis.
    with open('/workspace/RB4/output/patch_4_candidates.txt', 'w') as f:
        for s in sorted(list(found_ids)):
            f.write(f"{s}\n")
    
    print(f"Extracted {len(found_ids)} candidates from {ark_path}")

if __name__ == "__main__":
    main()
