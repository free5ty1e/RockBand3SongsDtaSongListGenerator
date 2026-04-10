import glob
import os
import re

def extract_metadata_for_id(ark_path, target_id):
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            pos = content.find(target_id.encode('ascii'))
            if pos == -1:
                return None
            
            # Scan around the ID for strings that look like Artist or Title
            # Usually metadata is in a block. Let's take 1KB around it.
            start = max(0, pos - 512)
            end = min(len(content), pos + 1024)
            chunk = content[start:end]
            
            # Find all strings of length 3-50
            strings = re.findall(b'[a-zA-Z0-9\s\.,\'\(\)-]{3,50}', chunk)
            # Filter out the ID itself and common metadata terms
            cleaned = []
            for s in strings:
                decoded = s.decode('ascii', errors='ignore').strip()
                if decoded.lower() != target_id.lower() and len(decoded) > 2:
                    if not any(term in decoded.lower() for term in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]):
                        cleaned.append(decoded)
            
            return cleaned
    except:
        return None

def main():
    with open('/workspace/RB4/output/truly_new_ids.txt', 'r') as f:
        new_ids = [line.strip() for line in f]
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    results = {}
    
    for song_id in new_ids:
        print(f"Searching for {song_id}...", end='\r')
        found = False
        for d in ark_dirs:
            if not os.path.exists(d): continue
            for ark in glob.glob(os.path.join(d, '*.ark')):
                meta = extract_metadata_for_id(ark, song_id)
                if meta:
                    results[song_id] = meta
                    found = True
                    break
            if found: break
    
    with open('/workspace/RB4/output/recovered_metadata.txt', 'w') as f:
        for song_id, meta in results.items():
            f.write(f"{song_id}: {', '.join(meta)}\n")
    
    print(f"\nRecovered metadata for {len(results)}/{len(new_ids)} IDs")

if __name__ == "__main__":
    main()
