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
                            # Scan for a string that matches the song ID pattern
                            # We'll look at the first 200 bytes and take the first match 
                            # that isn't a known engine keyword.
                            chunk = mm[pos : pos + 200]
                            matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                            
                            blacklist = {"rbsongmetadata", "short_name", "tempo", "vocal_tonic_note", "vocal_track", "audio_layers", "main_camera"}
                            
                            for m in matches:
                                s = m.decode('ascii', errors='ignore')
                                if s not in blacklist and '_' in s and not s.startswith('_'):
                                    found_songs.add(s)
                                    break # Found the song ID for this block
                            
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nFound {len(found_songs)} unique song-like IDs")
    with open('/workspace/RB4/output/ark_recovered_ids_v2.txt', 'w') as f:
        for s in sorted(list(found_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
