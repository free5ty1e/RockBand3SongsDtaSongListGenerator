import glob
import os
import re
import json

def get_known_ids():
    known = set()
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    if 'short_filename' in item:
                        known.add(item['short_filename'])
            except Exception as e:
                print(f"Error loading JSON: {e}")
    return known

def scan_ark_for_candidates(ark_path, known_ids):
    candidates = set()
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            
            # Find all occurrences of RBSongMetadata
            pos = content.find(b"RBSongMetadata")
            while pos != -1:
                # Scan 2KB around the marker for strings that look like song IDs
                start = max(0, pos - 512)
                end = min(len(content), pos + 2048)
                chunk = content[start:end]
                
                # Look for strings of lowercase alphanumeric + underscore
                # typically 5-30 chars long
                matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                for m in matches:
                    s = m.decode('ascii', errors='ignore')
                    # Filter out known metadata labels and common words
                    if s not in known_ids and s not in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]:
                        # Heuristic: song IDs usually have at least one underscore
                        if '_' in s:
                            candidates.add(s)
                
                pos = content.find(b"RBSongMetadata", pos + 1)
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return candidates

def main():
    known = get_known_ids()
    all_new = set()
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark in arks:
            print(f"Scanning {os.path.basename(ark)}...")
            found = scan_ark_for_candidates(ark, known)
            all_new.update(found)
            if found:
                print(f"  Found {len(found)} candidates")

    print(f"Total unique candidates: {len(all_new)}")
    with open('/workspace/RB4/output/ark_candidates.txt', 'w') as f:
        for s in sorted(list(all_new)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
