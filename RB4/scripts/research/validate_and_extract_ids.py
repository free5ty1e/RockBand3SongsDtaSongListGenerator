import glob
import os
import mmap
import re
import json

def load_validation_list():
    songs = set()
    rivals_path = '/workspace/RB4/rb4songlistWithRivals.txt'
    if os.path.exists(rivals_path):
        with open(rivals_path, 'r') as f:
            for line in f:
                if ' - ' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 2:
                        title = parts[1].split(' (')[0].lower()
                        slug = re.sub(r'[^a-z0-9]', '', title)
                        songs.add(slug)
    
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    if 'short_filename' in item:
                        songs.add(item['short_filename'])
            except: pass
    return songs

def main():
    validation_list = load_validation_list()
    print(f"Loaded {len(validation_list)} songs for validation.")
    
    confirmed_songs = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
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
                            chunk = mm[pos : pos + 512]
                            matches = re.findall(b'[a-z0-9_]{5,30}', chunk)
                            for m in matches:
                                s = m.decode('ascii', errors='ignore')
                                if s.lower() in validation_list:
                                    confirmed_songs.add(s)
                                elif s.lower() not in blacklist and '_' in s and not s.startswith('_'):
                                    # Potential new song
                                    confirmed_songs.add(s)
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nConfirmed/Potential songs found: {len(confirmed_songs)}")
    with open('/workspace/RB4/output/ark_confirmed_songs.txt', 'w') as f:
        for s in sorted(list(confirmed_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
