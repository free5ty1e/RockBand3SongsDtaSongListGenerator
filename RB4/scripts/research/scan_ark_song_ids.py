import glob
import os
import struct
import mmap
import re

def scan_ark_for_songs(ark_path):
    found_ids = set()
    try:
        with open(ark_path, 'rb') as f:
            # Memory map the file for efficiency
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Search for the RBSongMetadata marker
                marker = b"RBSongMetadata"
                pos = mm.find(marker)
                while pos != -1:
                    # Scan the next 4KB for [length: uint32][string] patterns
                    scan_end = min(len(mm), pos + 4096)
                    chunk = mm[pos:scan_end]
                    
                    # We look for length (uint32) followed by the string
                    # The length should be reasonable (e.g., 3-64 bytes)
                    offset = 0
                    while offset < len(chunk) - 5:
                        # Try to read a uint32 length
                        try:
                            length = struct.unpack('<I', chunk[offset:offset+4])[0]
                            if 3 <= length <= 64:
                                # Check if the following bytes are a valid ASCII string
                                string_bytes = chunk[offset+4 : offset+4+length]
                                if len(string_bytes) == length:
                                    try:
                                        s = string_bytes.decode('ascii')
                                        # Heuristic: Song IDs are usually lowercase alphanumeric with underscores
                                        if re.match(r'^[a-z0-9_]+$', s) and '_' in s:
                                            found_ids.add(s)
                                    except UnicodeDecodeError:
                                        pass
                        except:
                            pass
                        offset += 1 # Slide window by 1 byte
                    
                    pos = mm.find(marker, pos + 1)
    except Exception as e:
        print(f"Error scanning {ark_path}: {e}")
    return found_ids

def main():
    all_songs = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    # We'll use a blacklist for known engine strings
    blacklist = {
        "results_header", "spot_vocal", "idle_realtime", "spot_guitar", 
        "song_library", "light_mgr", "mic_int", "gem_miss", "mic_intensity",
        "spot_drums", "game_ended", "color_map", "default_env", "frame_ra",
        "song_details", "crowd_listens", "arena_standard", "coda_failure",
        "player_failed", "game_started", "coda_success", "crowd_cheers",
        "gig_request_result", "crowd_laughs", "big_club_standard",
        "vocal_script_start", "energy_phrase_hit", "crowd_impatient",
        "big_club_industrial", "energy_phrase_miss", "size_lo", "game_paused",
        "gtrsolo_tutorial"
    }
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            ids = scan_ark_for_songs(ark_path)
            all_songs.update(ids)
    
    # Filter by blacklist
    final_songs = {s for s in all_songs if s not in blacklist}
    
    print(f"\nFound {len(final_songs)} potential song IDs")
    with open('/workspace/RB4/output/ark_song_ids.txt', 'w') as f:
        for s in sorted(list(final_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
