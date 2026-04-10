import json
import os
import sys

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

def main():
    known = get_known_ids()
    candidates_path = '/workspace/RB4/output/patch_4_candidates.txt'
    if not os.path.exists(candidates_path):
        print(f"Candidates file not found: {candidates_path}")
        return

    with open(candidates_path, 'r') as f:
        candidates = [line.strip() for line in f if line.strip()]

    missing_requests = []
    for c in candidates:
        if c.startswith('request_') and c not in known:
            missing_requests.append(c)

    print(f"Found {len(missing_requests)} missing request songs:")
    for r in sorted(missing_requests):
        print(r)

if __name__ == "__main__":
    main()
