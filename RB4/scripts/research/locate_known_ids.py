import os
import glob

def find_id_in_arks(target_id):
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    for d in ark_dirs:
        if not os.path.exists(d): continue
        for ark_path in glob.glob(os.path.join(d, '*.ark')):
            try:
                with open(ark_path, 'rb') as f:
                    # Use memory mapping for faster searching and to avoid reading whole file
                    import mmap
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        pos = mm.find(target_id.encode('ascii'))
                        if pos != -1:
                            return ark_path, pos
            except Exception as e:
                pass
    return None, None

if __name__ == "__main__":
    ids_to_search = ["10000hours", "18andlife", "21her", "24kmagic", "3am"]
    for tid in ids_to_search:
        path, pos = find_id_in_arks(tid)
        if path:
            print(f"Found {tid} in {path} at {pos}")
        else:
            print(f"Not found {tid}")
