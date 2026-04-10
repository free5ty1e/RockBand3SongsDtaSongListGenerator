import glob
import os
import mmap
import re

def main():
    # Expanded blacklist of engine terms found in metadata blocks
    blacklist = {
        "rbsongmetadata", "short_name", "tempo", "vocal_tonic_note", "vocal_track", 
        "audio_layers", "main_camera", "results_header", "spot_vocal", "idle_realtime", 
        "spot_guitar", "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity",
        "spot_drums", "game_ended", "color_map", "default_env", "frame_ra", 
        "song_details", "crowd_listens", "arena_standard", "coda_failure", 
        "player_failed", "game_started", "coda_success", "crowd_cheers", 
        "gig_request_result", "crowd_laughs", "big_club_standard", 
        "vocal_script_start", "energy_phrase_hit", "crowd_impatient", 
        "big_club_industrial", "energy_phrase_miss", "size_lo", "game_paused",
        "gtrsolo_tutorial", "part_drums", "part_bass", "part_guitar", "part_vocals",
        "harm1", "harm2", "harm3", "events", "beat", "markup", "root", "editor",
        "capabilities", "entityheader", "copy", "instance", "drives", "parent",
        "static", "polling", "mode", "num", "instances", "meshes", "particles",
        "propanims", "lights", "verts", "faces", "changelist", "icon", "cam",
        "initialized", "near", "far", "xfm", "basis", "translate", "data"
    }
    
    found_songs = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        pos = mm.find(b"RBSongMetadata")
                        while pos != -1:
                            # Scan 512 bytes after the marker
                            chunk = mm[pos : pos + 512]
                            # Find all alphanumeric strings 5-30 chars
                            matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                            for m in matches:
                                s = m.decode('ascii', errors='ignore')
                                # Heuristic: must contain underscore, not start with underscore, not in blacklist
                                if '_' in s and not s.startswith('_') and s.lower() not in blacklist:
                                    found_songs.add(s)
                                    break # Take the first valid ID per marker
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nFound {len(found_songs)} unique song-like IDs from markers")
    with open('/workspace/RB4/output/marker_recovered_ids.txt', 'w') as f:
        for s in sorted(list(found_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
