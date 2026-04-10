import glob
import os
import re

def main():
    # Baseline known IDs
    known_ids = set()
    try:
        import json
        with open('/workspace/RB4/rb4_empty_songs_full.json', 'r') as f:
            data = json.load(f)
            for item in data:
                if 'short_filename' in item:
                    known_ids.add(item['short_filename'])
    except: pass

    blacklist = {
        "results_header", "spot_vocal", "idle_realtime", "spot_guitar", 
        "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity",
        "spot_drums", "game_ended", "color_map", "default_env", "frame_ra",
        "song_details", "crowd_listens", "arena_standard", "coda_failure",
        "player_failed", "game_started", "coda_success", "crowd_cheers",
        "gig_request_result", "crowd_laughs", "big_club_standard",
        "vocal_script_start", "energy_phrase_hit", "crowd_impatient",
        "big_club_industrial", "energy_phrase_miss", "size_lo", "game_paused"
    }

    high_conf_ids = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Processing {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    content = f.read()
                    # Find RBSongMetadata
                    pos = content.find(b"RBSongMetadata")
                    while pos != -1:
                        # Look at the 200 bytes following the marker
                        chunk = content[pos : pos + 200]
                        # Look for [length][string] patterns
                        # We search for strings of 5-30 alphanumeric characters with underscores
                        matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                        for m in matches:
                            s = m.decode('ascii', errors='ignore')
                            if s not in known_ids and s not in blacklist:
                                if '_' in s and not s.startswith('_'):
                                    high_conf_ids.add(s)
                        pos = content.find(b"RBSongMetadata", pos + 1)
            except: pass

    print(f"\nFound {len(high_conf_ids)} high-confidence song IDs")
    with open('/workspace/RB4/output/high_conf_song_ids.txt', 'w') as f:
        for s in sorted(list(high_conf_ids)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
