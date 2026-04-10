import glob
import os
import mmap
import re

def main():
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    found_songs = set()
    
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
                            # The song ID seems to be the first significant string 
                            # after the marker, but NOT 'RBSongMetadata' itself.
                            # Let's scan 100 bytes ahead.
                            chunk = mm[pos : pos + 200]
                            # Look for a string that is 5-30 lowercase chars with underscores
                            matches = re.finditer(b'[a-z0-9_]{5,30}', chunk)
                            for match in matches:
                                s = match.group(0).decode('ascii', errors='ignore')
                                if s != "rbsongmetadata" and '_' in s and not s.startswith('_'):
                                    found_songs.add(s)
                                    break # Take only the first one per marker
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nFound {len(found_songs)} unique song-like IDs")
    with open('/workspace/RB4/output/ark_recovered_ids.txt', 'w') as f:
        for s in sorted(list(found_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
