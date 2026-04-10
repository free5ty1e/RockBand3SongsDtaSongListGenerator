import os
import struct
import mmap
import glob

def extract_loaded_ids(ark_path):
    key = b"loaded_song_id"
    found_ids = set()
    try:
        with open(ark_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                pos = mm.find(key)
                while pos != -1:
                    # Value starts after the key
                    val_start = pos + len(key)
                    if val_start + 4 <= len(mm):
                        # Read length (uint32)
                        length = struct.unpack('<I', mm[val_start:val_start+4])[0]
                        if 3 <= length <= 64:
                            val_bytes = mm[val_start+4 : val_start+4+length]
                            if len(val_bytes) == length:
                                try:
                                    s = val_bytes.decode('ascii')
                                    # Heuristic: song IDs are usually lowercase alphanumeric with underscores
                                    if '_' in s and not s.startswith('_'):
                                        found_ids.add(s)
                                except:
                                    pass
                    pos = mm.find(key, pos + 1)
    except Exception as e:
        print(f"Error scanning {ark_path}: {e}")
    return found_ids

def main():
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    all_ids = set()
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark in arks:
            print(f"Processing {os.path.basename(ark)}...", end='\r')
            all_ids.update(extract_loaded_ids(ark))
    
    print(f"\nFound {len(all_ids)} IDs associated with 'loaded_song_id'")
    with open('/workspace/RB4/output/loaded_song_ids_final.txt', 'w') as f:
        for s in sorted(list(all_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
