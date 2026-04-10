import json
import os

def main():
    # 1. Load baseline IDs
    known_ids = set()
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            for item in data:
                if 'short_filename' in item:
                    known_ids.add(item['short_filename'])
    
    # 2. Load all extracted candidates
    candidates = set()
    cand_path = '/workspace/RB4/output/all_candidates.txt'
    if os.path.exists(cand_path):
        with open(cand_path, 'r') as f:
            for line in f:
                candidates.add(line.strip())
    
    # 3. Find new IDs
    new_ids = candidates - known_ids
    
    print(f"Baseline IDs: {len(known_ids)}")
    print(f"Candidates: {len(candidates)}")
    print(f"Truly New IDs: {len(new_ids)}")
    
    with open('/workspace/RB4/output/truly_new_ids.txt', 'w') as f:
        for s in sorted(list(new_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
