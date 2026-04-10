import glob
import os
import re

def main():
    with open('/workspace/RB4/output/truly_new_ids.txt', 'r') as f:
        target_ids = {line.strip().encode('ascii') for line in f}
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    results = {}
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    content = f.read()
                    for tid in target_ids:
                        pos = content.find(tid)
                        if pos != -1:
                            start = max(0, pos - 512)
                            end = min(len(content), pos + 1024)
                            chunk = content[start:end]
                            
                            # Fixed the regex escape sequence
                            strings = re.findall(b'[a-zA-Z0-9 \.,\'\(\)-]{3,50}', chunk)
                            cleaned = []
                            for s in strings:
                                decoded = s.decode('ascii', errors='ignore').strip()
                                if decoded.lower() != tid.decode().lower() and len(decoded) > 2:
                                    if not any(term in decoded.lower() for term in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]):
                                        cleaned.append(decoded)
                            results[tid.decode()] = cleaned
            except Exception as e:
                print(f"\nError reading {ark_path}: {e}")
    
    with open('/workspace/RB4/output/recovered_metadata.txt', 'w') as f:
        for song_id, meta in results.items():
            f.write(f"{song_id}: {', '.join(meta)}\n")
    
    print(f"\nRecovered metadata for {len(results)} IDs")

if __name__ == "__main__":
    main()
