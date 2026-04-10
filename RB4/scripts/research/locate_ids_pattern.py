import glob
import os
import struct

def search_for_id(ark_path, target_id):
    id_bytes = target_id.encode('ascii')
    length = len(id_bytes)
    # Pattern: [length: uint32][null][string]
    pattern = struct.pack('<I', length) + b'\x00' + id_bytes
    
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            pos = content.find(pattern)
            if pos != -1:
                return pos
    except: pass
    return -1

def main():
    ids_to_search = ["10000hours", "18andlife", "21her", "24kmagic", "3am"]
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for tid in ids_to_search:
        found = False
        for d in ark_dirs:
            if not os.path.exists(d): continue
            for ark in glob.glob(os.path.join(d, '*.ark')):
                pos = search_for_id(ark, tid)
                if pos != -1:
                    print(f"Found {tid} in {ark} at {pos}")
                    found = True
                    break
            if found: break
        if not found:
            print(f"Not found {tid}")

if __name__ == "__main__":
    main()
