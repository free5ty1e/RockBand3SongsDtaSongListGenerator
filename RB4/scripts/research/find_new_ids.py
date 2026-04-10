import glob
import os
import re
import json

def get_known_ids():
    known = set()
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            for item in data:
                if 'short_filename' in item:
                    known.add(item['short_filename'])
    return known

def scan_arks(known_ids):
    new_ids = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    # Pattern: short_name followed by null, then the id, then null
    pattern = re.compile(b'short_name\x00([a-zA-Z0-9_]+)\x00')
    
    for d in ark_dirs:
        if not os.path.exists(d):
            continue
        ark_files = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in ark_files:
            print(f"Processing {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    chunk_size = 10 * 1024 * 1024
                    overlap = 1024
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        for match in pattern.finditer(chunk):
                            song_id = match.group(1).decode('ascii', errors='ignore')
                            if song_id not in known_ids:
                                new_ids.add(song_id)
                        
                        if len(chunk) == chunk_size:
                            f.seek(f.tell() - overlap)
                        else:
                            break
            except Exception as e:
                print(f"\nError reading {ark_path}: {e}")
    
    return new_ids

def main():
    print("Loading known IDs...")
    known = get_known_ids()
    print(f"Loaded {len(known)} known IDs.")
    
    print("Scanning ARK files for new IDs...")
    new_ids = scan_arks(known)
    
    print(f"\nFound {len(new_ids)} new unique IDs!")
    
    with open('/workspace/RB4/output/newly_recovered_ids.txt', 'w') as f:
        for s in sorted(list(new_ids)):
            f.write(f"{s}\n")
    
    print(f"New IDs saved to /workspace/RB4/output/newly_recovered_ids.txt")

if __name__ == "__main__":
    main()
