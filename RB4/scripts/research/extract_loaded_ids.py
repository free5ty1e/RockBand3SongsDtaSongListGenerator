import glob
import os
import struct
import mmap
import re

def extract_value_for_key(mm, pos, key_bytes):
    # Key is found at pos. The value follows.
    # Looking at the binary: RBSongMetadata [length][string] [length][string] ...
    # Or maybe: [key_length][key_string] [value_length][value_string]
    
    # Let's try to find the next [length][string] pattern after the key
    offset = pos + len(key_bytes)
    # The key itself was preceded by its length. 
    # Let's assume the value follows the same [length][string] pattern.
    
    # Try to read length
    if offset + 4 <= len(mm):
        length = struct.unpack('<I', mm[offset:offset+4])[0]
        if 3 <= length <= 64:
            val_bytes = mm[offset+4 : offset+4+length]
            if len(val_bytes) == length:
                try:
                    return val_bytes.decode('ascii')
                except:
                    pass
    return None

def main():
    target_key = "loaded_song_id"
    key_bytes = target_key.encode('ascii')
    found_ids = set()
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        pos = mm.find(key_bytes)
                        while pos != -1:
                            val = extract_value_for_key(mm, pos, key_bytes)
                            if val:
                                # Filter for song-like IDs (lowercase, underscores, 5-30 chars)
                                if re.match(r'^[a-z0-9_]{5,30}$', val) and '_' in val:
                                    found_ids.add(val)
                            pos = mm.find(key_bytes, pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nFound {len(found_ids)} IDs associated with {target_key}")
    with open('/workspace/RB4/output/loaded_song_ids.txt', 'w') as f:
        for s in sorted(list(found_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
