import glob
import os
import re
import json

def get_known_ids():
    known = set()
    # JSON
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
    candidates = set()
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    for d in ark_dirs:
        if not os.path.exists(d): continue
        for ark_path in glob.glob(os.path.join(d, '*.ark')):
            print(f"Scanning {os.path.basename(ark_path)}...")
            try:
                with open(ark_path, 'rb') as f:
                    content = f.read()
                    # Look for all strings 5-30 chars long that contain a digit or underscore
                    matches = re.findall(b'[a-z0-9_]{5,30}', content)
                    for m in matches:
                        s = m.decode('ascii', errors='ignore')
                        if s not in known and '_' in s and not s.startswith('_'):
                            candidates.add(s)
            except: pass
            
    # Filter out obviously non-song IDs
    blacklist = {"results_header", "spot_vocal", "idle_realtime", "spot_guitar", "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity", "spot_drums", "game_ended", "color_map", "default_env", "frame_ra", "song_details", "crowd_listens", "arena_standard", "coda_failure", "player_failed", "game_started", "coda_success", "crowd_cheers", "gig_request_result", "crowd_laughs", "big_club_standard", "vocal_script_start", "energy_phrase_hit", "crowd_impatient", "big_club_industrial", "energy_phrase_miss", "size_lo", "game_paused", "gtrsolo_tutorial"}
    
    final = {s for s in candidates if s not in blacklist}
    
    print(f"Found {len(final)} candidates")
    with open('/workspace/RB4/output/ark_candidates_v2.txt', 'w') as f:
        for s in sorted(list(final)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
