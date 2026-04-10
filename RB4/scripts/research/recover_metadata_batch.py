import sys
import glob
import os
import re

def process_arks(ark_paths, target_ids):
    results = {}
    for ark_path in ark_paths:
        try:
            with open(ark_path, 'rb') as f:
                content = f.read()
                for tid in target_ids:
                    pos = content.find(tid)
                    if pos != -1:
                        start = max(0, pos - 512)
                        end = min(len(content), pos + 1024)
                        chunk = content[start:end]
                        strings = re.findall(b'[a-zA-Z0-9 \.,\'\(\)-]{3,50}', chunk)
                        cleaned = []
                        for s in strings:
                            decoded = s.decode('ascii', errors='ignore').strip()
                            if decoded.lower() != tid.decode().lower() and len(decoded) > 2:
                                if not any(term in decoded.lower() for term in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]):
                                    cleaned.append(decoded)
                        results[tid.decode()] = cleaned
        except: pass
    return results

if __name__ == "__main__":
    with open('/workspace/RB4/output/truly_new_ids.txt', 'r') as f:
        target_ids = {line.strip().encode('ascii') for line in f}
    
    ark_paths = sys.argv[1:]
    found = process_arks(ark_paths, target_ids)
    
    with open('/workspace/RB4/output/recovered_metadata_batch.txt', 'a') as f:
        for song_id, meta in found.items():
            f.write(f"{song_id}: {', '.join(meta)}\n")
