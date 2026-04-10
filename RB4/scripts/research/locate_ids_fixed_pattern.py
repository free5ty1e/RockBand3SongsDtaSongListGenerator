import glob
import os
import struct
import mmap

def main():
    # Use a few baseline IDs
    ids_to_search = ["10000hours", "18andlife", "21her", "24kmagic", "3am"]
    patterns = {}
    for tid in ids_to_search:
        id_bytes = tid.encode('ascii')
        patterns[tid] = struct.pack('<I', len(id_bytes)) + id_bytes
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        for ark_path in glob.glob(os.path.join(d, '*.ark')):
            try:
                with open(ark_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        for tid, pattern in patterns.items():
                            pos = mm.find(pattern)
                            if pos != -1:
                                print(f"Found {tid} in {ark_path} at {pos}")
            except Exception as e:
                print(f"Error reading {ark_path}: {e}")

if __name__ == "__main__":
    main()
