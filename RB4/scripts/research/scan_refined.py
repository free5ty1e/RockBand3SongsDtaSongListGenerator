import glob
import os
import re
import json
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

def scan_ark_for_songs(ark_path, known_ids):
    found_songs = set()
    asset_prefixes = {
        'crowd_', 'light_', 'preset_', 'emote_', 'state_', 'cb_', 'floor_', 'stage_', 
        'unlit_', 'positive_', 'player_', 'audio_', 'fmod_', 'game_', 'gig_', 
        'entity_', 'waveform_', 'vocal_', 'rblight_', 'rblighting_', 'big_club_', 
        'small_club_', 'arena_', 'curtain_', 'mesh_', 'default_', 'volumetric_', 
        'sr_', 'flare_', 'strobe_', 'blackout_', 'lightgroup_', 'cam_', 'loop_'
    }
    
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            pos = content.find(b"RBSongMetadata")
            while pos != -1:
                # Look at the chunk around RBSongMetadata
                start = max(0, pos - 1024)
                end = min(len(content), pos + 4096)
                chunk = content[start:end]
                
                # Find strings that look like song IDs
                matches = re.findall(b'[a-z0-9_]{5,40}', chunk)
                for m in matches:
                    s = m.decode('ascii', errors='ignore')
                    # Filter:
                    # 1. Not in known songs
                    # 2. Contains underscore
                    # 3. Not starting with a known asset prefix
                    # 4. Not a common keyword
                    if s not in known_ids and '_' in s:
                        if not any(s.startswith(prefix) for prefix in asset_prefixes):
                            if s not in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]:
                                found_songs.add(s)
                
                # Find SNGPKG headers
                sng_pos = chunk.find(b"SNGPKG")
                while sng_pos != -1:
                    print(f"Found SNGPKG header at offset {offset + sng_pos} in {ark_path}")
                    sng_pos = chunk.find(b"SNGPKG", sng_pos + 1)

    except Exception as e:
        print(f"Error scanning {ark_path}: {e}")
    return found_songs

def main():
    known = get_known_ids()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    all_new_ids = set()
    for d in ark_dirs:
        if not os.path.exists(d): continue
        for ark_path in glob.glob(os.path.join(d, '*.ark')):
            print(f"Scanning {ark_path}...")
            songs = scan_ark_for_songs(ark_path, known)
            if songs:
                print(f"  Found {len(songs)} candidates")
                all_new_ids.update(songs)
    
    print(f"Total unique new candidates: {len(all_new_ids)}")
    with open('/workspace/RB4/output/refined_candidates.txt', 'w') as f:
        for s in sorted(list(all_new_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
