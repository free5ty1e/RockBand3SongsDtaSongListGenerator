import json
import os
import re

def load_known_ids():
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
    results_path = '/workspace/RB4/output/all_ark_discoveries_raw.jsonl'
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    known_ids = load_known_ids()
    
    if not os.path.exists(results_path):
        print(f"Results file not found: {results_path}")
        return

    # Read discoveries
    discoveries = []
    with open(results_path, 'r') as f:
        for line in f:
            try:
                discoveries.append(json.loads(line))
            except: continue
    
    # Filter for actual song IDs (not SNGPKG_HEADER)
    song_ids = set()
    for d in discoveries:
        if d['type'] == 'metadata':
            song_ids.add(d['id'])
            
    # Cross-reference with investigation doc
    with open(investigation_path, 'r') as f:
        lines = f.readlines()
        
    current_ids = set()
    for line in lines:
        match = re.search(r'\| `([^`]+)`', line)
        if match:
            current_ids.add(match.group(1))
            
    new_ids = song_ids - current_ids - known_ids
    print(f"Found {len(new_ids)} new potential song IDs.")
    
    if not new_ids:
        return

    # For each new ID, find its offset and ARK
    id_info = {}
    for d in discoveries:
        if d['type'] == 'metadata' and d['id'] in new_ids:
            id_info[d['id']] = {
                'ark': d['ark'],
                'offset': d['offset']
            }
            
    # Add to table
    new_rows = []
    for sid in sorted(list(new_ids)):
        info = id_info.get(sid, {'ark': '?', 'offset': '?'})
        
        # Determine source PKG
        pkg = '?'
        if 'update' in info['ark']:
            pkg = "Rock.Band.4_CUSA02084_v2.21_[5.05]_OPOISSO893.pkg"
        elif 'base' in info['ark']:
            pkg = "Rock.Band.4_CUSA02084_v1.00_[2.50]_OPOISSO893.pkg"
            
        # Probable Title
        title = sid.replace('request_', '').replace('_', ' ').title()
        if 'request_' in sid:
            title += " (Crowd Request)"
            
        row = f"| `{sid}` | {title} | ? | ? | Update PKG | {pkg} | {os.path.basename(info['ark'])} @ {info['offset']} | Pending |\n"
        new_rows.append(row)
        
    # Append to investigation doc
    with open(investigation_path, 'a') as f:
        f.write('\n'.join(new_rows))
    
    print(f"Added {len(new_rows)} new entries to investigation document.")

if __name__ == "__main__":
    main()
