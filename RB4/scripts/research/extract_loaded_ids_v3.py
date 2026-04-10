import glob
import os
import struct
import mmap
import re

def extract_value(mm, pos, key_bytes):
    # Pattern: [Key] [BlockLength: uint32] [ValueLength: uint32] [Value: bytes]
    offset = pos + len(key_bytes)
    if offset + 4 <= len(mm):
        block_length = struct.unpack('<I', mm[offset:offset+4])[0]
        if 4 <= block_length <= 1024:
            val_start = offset + 4
            if val_start + 4 <= len(mm):
                val_length = struct.unpack('<I', mm[val_start:val_start+4])[0]
                if 0 <= val_length <= block_length:
                    val_bytes = mm[val_start+4 : val_start+4+val_length]
                    try:
                        return val_bytes.decode('ascii', errors='ignore')
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
                            val = extract_value(mm, pos, key_bytes)
                            if val:
                                # Song IDs: lowercase, underscores, 5-30 chars
                                if re.match(r'^[a-z0-9_]{5,30}$', val) and '_' in val:
                                    found_ids.add(val)
                            pos = mm.find(key_bytes, pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nFound {len(found_ids)} IDs associated with {target_key}")
    with open('/workspace/RB4/output/loaded_song_ids_final.txt', 'w') as f:
        for s in sorted(list(found_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
