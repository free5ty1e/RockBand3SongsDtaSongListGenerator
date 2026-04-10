import sys
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
            except: pass
    return known

def scan_single_ark(ark_path, known_ids):
    candidates = set()
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            pos = content.find(b"RBSongMetadata")
            while pos != -1:
                start = max(0, pos - 512)
                end = min(len(content), pos + 2048)
                chunk = content[start:end]
                matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                for m in matches:
                    s = m.decode('ascii', errors='ignore')
                    if s not in known_ids and s not in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]:
                        if '_' in s:
                            candidates.add(s)
                pos = content.find(b"RBSongMetadata", pos + 1)
    except: pass
    return candidates

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    ark_path = sys.argv[1]
    known = get_known_ids()
    found = scan_single_ark(ark_path, known)
    for s in found:
        print(s)
