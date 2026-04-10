import os

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

    potential_new = set()
    with open('/workspace/RB4/output/all_strings_base.txt', 'r') as f:
        for line in f:
            # Strip filename if present
            if ':' in line:
                s = line.split(':', 1)[1].strip()
            else:
                s = line.strip()
            if s not in known_ids and s not in blacklist:
                if any(char.isdigit() for char in s) or '_' in s:
                    potential_new.add(s)
    
    print(f"Found {len(potential_new)} potential new IDs from base game")
    with open('/workspace/RB4/output/potential_new_ids_base.txt', 'w') as f:
        for s in sorted(list(potential_new)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
