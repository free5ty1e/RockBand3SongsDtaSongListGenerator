import glob
import os
import re

def main():
    # Load expanded known IDs
    known_ids = set()
    with open('/workspace/RB4/output/expanded_known_ids.txt', 'r') as f:
        for line in f:
            known_ids.add(line.strip())
    
    # Blacklist of common game engine strings observed in noise
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
    
    # Also add any string that is just a common word (this is risky, so keep it small)
    blacklist.update(["solid", "solo", "server", "warning", "vocalist", "needs", "mic", "song", "artist", "fmt", "alt", "number", "complete", "details", "view", "leaderboard", "failed", "information", "info", "cache", "button", "cancel", "corrupt", "overwrite", "create", "cannot", "play"])

    all_new = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    content = f.read()
                    # Find all lowercase alphanumeric strings 5-30 chars
                    matches = re.findall(b'[a-z0-9]{5,30}', content)
                    for m in matches:
                        s = m.decode('ascii', errors='ignore')
                        if s not in known_ids and s not in blacklist:
                            # Song IDs often have numbers or underscores
                            if any(char.isdigit() for char in s) or '_' in s:
                                all_new.add(s)
            except: pass
            
    print(f"\nFound {len(all_new)} potential new IDs")
    with open('/workspace/RB4/output/potential_new_ids.txt', 'w') as f:
        for s in sorted(list(all_new)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
