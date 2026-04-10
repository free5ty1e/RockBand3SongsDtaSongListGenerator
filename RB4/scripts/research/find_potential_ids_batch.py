import sys
import os
import re

def main():
    # Load expanded known IDs
    known_ids = set()
    with open('/workspace/RB4/output/expanded_known_ids.txt', 'r') as f:
        for line in f:
            known_ids.add(line.strip())
    
    blacklist = {
        "results_header", "spot_vocal", "_bass", "idle_realtime", "spot_guitar", 
        "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity",
        "spot_drums", "_vocals", "game_ended", "_guitar", "color_map",
        "onboarding_guitsolo_tutorial_a", "onboarding_guitsolo_tutorial_b",
        "default_env", "frame_ra", "spot_bass", "idle_real", "lightpreset_keyframe",
        "song_details", "crowd_listens", "_guitar", "player_saved", "arena_standard",
        "_bass", "crowd_last_set", "coda_failure", "player_failed", "gig_request_vote",
        "game_started", "gig_encore_result", "gem_miss", "coda_success", "crowd_cheers",
        "vocal_script_score_complete", "_vocals", "gig_request_result", "crowd_laughs",
        "big_club_standard", "crowd_cheers_more", "vocal_script_start", "energy_phrase_hit",
        "crowd_impatient", "gig_encore_vote", "big_club_industrial", "energy_phrase_miss",
        "size_lo", "game_paused"
    }
    blacklist.update(["solid", "solo", "server", "warning", "vocalist", "needs", "mic", "song", "artist", "fmt", "alt", "number", "complete", "details", "view", "leaderboard", "failed", "information", "info", "cache", "button", "cancel", "corrupt", "overwrite", "create", "cannot", "play"])

    new_ids = set()
    ark_paths = sys.argv[1:]
    
    for ark_path in ark_paths:
        try:
            with open(ark_path, 'rb') as f:
                content = f.read()
                matches = re.findall(b'[a-z0-9]{5,30}', content)
                for m in matches:
                    s = m.decode('ascii', errors='ignore')
                    if s not in known_ids and s not in blacklist:
                        if any(char.isdigit() for char in s) or '_' in s:
                            new_ids.add(s)
        except: pass
        
    with open('/workspace/RB4/output/potential_ids_batch.txt', 'a') as f:
        for s in new_ids:
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
