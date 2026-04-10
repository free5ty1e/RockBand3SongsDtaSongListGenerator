import sys
import os
import re
import mmap

def recover_meta_mmap(ark_path, target_ids):
    found = {}
    try:
        with open(ark_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for tid in target_ids:
                    pos = mm.find(tid.encode('ascii'))
                    if pos != -1:
                        start = max(0, pos - 512)
                        end = min(len(mm), pos + 1024)
                        chunk = mm[start:end]
                        strings = re.findall(b'[a-zA-Z0-9 \.,\'\(\)-]{3,50}', chunk)
                        cleaned = []
                        for s in strings:
                            decoded = s.decode('ascii', errors='ignore').strip()
                            if decoded.lower() != tid.lower() and len(decoded) > 2:
                                if not any(term in decoded.lower() for term in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]):
                                    cleaned.append(decoded)
                        found[tid] = cleaned
    except: pass
    return found

if __name__ == "__main__":
    with open('/workspace/RB4/output/truly_new_ids.txt', 'r') as f:
        target_ids = [line.strip() for line in f]
    
    ark_paths = sys.argv[1:]
    found_all = {}
    for ark in ark_paths:
        found_all.update(recover_meta_mmap(ark, target_ids))
    
    with open('/workspace/RB4/output/final_recovered_metadata_batch.txt', 'a') as f:
        for tid, meta in found_all.items():
            f.write(f"{tid}: {', '.join(meta)}\n")
