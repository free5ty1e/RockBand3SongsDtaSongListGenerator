import glob
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

def main():
    with open('/workspace/RB4/output/truly_new_ids.txt', 'r') as f:
        target_ids = [line.strip() for line in f]
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    all_results = {}
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark in arks:
            print(f"Processing {os.path.basename(ark)}...", end='\r')
            meta = recover_meta_mmap(ark, target_ids)
            all_results.update(meta)
    
    with open('/workspace/RB4/output/final_recovered_metadata.txt', 'w') as f:
        for tid, meta in all_results.items():
            f.write(f"{tid}: {', '.join(meta)}\n")
    
    print(f"\nRecovered metadata for {len(all_results)} IDs")

if __name__ == "__main__":
    main()
