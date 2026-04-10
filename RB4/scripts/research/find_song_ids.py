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
            except: pass
    return known

def scan_for_real_ids(ark_path, known_ids):
    found = set()
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            # We look for the [length][string] pattern
            # Since length is usually small (< 255), we can iterate
            for length in range(3, 64):
                # This is slow, but let's try a more targeted approach
                pass
            
            # Actually, let's use the regex but filter more strictly
            # Song IDs: lowercase, underscores, maybe numbers, 5-30 chars
            matches = re.finditer(b'([a-z0-9_]{5,30})', content)
            for match in matches:
                s = match.group(1).decode('ascii', errors='ignore')
                if s not in known_ids:
                    # Heuristic: must contain at least one underscore AND not be in a common metadata list
                    if '_' in s and not s.startswith('_'):
                        found.add(s)
    except: pass
    return found

def main():
    known = get_known_ids()
    all_found = set()
    
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark in arks:
            print(f"Scanning {os.path.basename(ark)}...")
            all_found.update(scan_for_real_ids(ark, known))

    # Filter out common engine terms
    blacklist = {
        "results_header", "spot_vocal", "idle_realtime", "spot_guitar", 
        "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity",
        "spot_drums", "_vocals", "game_ended", "_guitar", "color_map",
        "onboarding_guitsolo_tutorial_a", "onboarding_guitsolo_tutorial_b",
        "default_env", "frame_ra", "spot_bass", "idle_real", "lightpreset_keyframe",
        "song_details", "crowd_listens", "player_saved", "arena_standard",
        "crowd_last_set", "coda_failure", "player_failed", "gig_request_vote",
        "game_started", "gig_encore_result", "coda_success", "crowd_cheers",
        "vocal_script_score_complete", "gig_request_result", "crowd_laughs",
        "big_club_standard", "crowd_cheers_more", "vocal_script_start", "energy_phrase_hit",
        "crowd_impatient", "gig_encore_vote", "big_club_industrial", "energy_phrase_miss",
        "size_lo", "game_paused"
    }
    
    final = {s for s in all_found if s not in blacklist}
    
    print(f"Found {len(final)} potential song IDs")
    with open('/workspace/RB4/output/potential_song_ids.txt', 'w') as f:
        for s in sorted(list(final)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
