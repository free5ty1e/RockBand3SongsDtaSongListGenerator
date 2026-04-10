import json
import os

def main():
    # 1. Load known IDs from JSON
    known_ids = set()
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    if 'short_filename' in item:
                        known_ids.add(item['short_filename'])
            except: pass
    
    # 2. Filter candidates from all_ids.txt
    # Heuristics for song IDs:
    # - Not in known_ids
    # - Must contain an underscore
    # - Not start with an underscore (usually engine internal)
    # - 5-30 characters long
    # - Not a common engine term
    
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
    
    truly_new = set()
    if os.path.exists('/workspace/RB4/output/all_ids.txt'):
        with open('/workspace/RB4/output/all_ids.txt', 'r') as f:
            for line in f:
                s = line.strip()
                if s not in known_ids and s not in blacklist:
                    if '_' in s and not s.startswith('_') and 5 <= len(s) <= 30:
                        truly_new.add(s)
    
    print(f"Filtered {len(truly_new)} potential song IDs")
    with open('/workspace/RB4/output/potential_song_ids.txt', 'w') as f:
        for s in sorted(list(truly_new)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
