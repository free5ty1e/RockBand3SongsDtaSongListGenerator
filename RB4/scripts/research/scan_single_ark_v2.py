import glob
import os
import re
import json
import sys

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

def scan_ark_chunked(ark_path, known_ids):
    found = []
    asset_prefixes = {
        'crowd_', 'light_', 'preset_', 'emote_', 'state_', 'cb_', 'floor_', 'stage_', 
        'unlit_', 'positive_', 'player_', 'audio_', 'fmod_', 'game_', 'gig_', 
        'entity_', 'waveform_', 'vocal_', 'rblight_', 'rblighting_', 'big_club_', 
        'small_club_', 'arena_', 'curtain_', 'mesh_', 'default_', 'volumetric_', 
        'sr_', 'flare_', 'strobe_', 'blackout_', 'lightgroup_', 'cam_', 'loop_'
    }
    
    chunk_size = 10 * 1024 * 1024 # 10MB
    overlap = 1024 * 1024 # 1MB
    
    try:
        with open(ark_path, 'rb') as f:
            offset = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                pos = chunk.find(b"RBSongMetadata")
                while pos != -1:
                    lookahead_start = max(0, pos - 512)
                    lookahead_end = min(len(chunk), pos + 2048)
                    chunk_slice = chunk[lookahead_start:lookahead_end]
                    
                    matches = re.finditer(b'[a-z0-9_]{5,40}', chunk_slice)
                    for m in matches:
                        s = m.group(0).decode('ascii', errors='ignore')
                        if s not in known_ids and '_' in s:
                            if not any(s.startswith(prefix) for prefix in asset_prefixes):
                                if s not in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]:
                                    found.append({
                                        'id': s,
                                        'offset': offset + lookahead_start + m.start(),
                                        'type': 'metadata'
                                    })
                    pos = chunk.find(b"RBSongMetadata", pos + 1)
                
                pos = chunk.find(b"SNGPKG")
                while pos != -1:
                    found.append({
                        'id': 'SNGPKG_HEADER',
                        'offset': offset + pos,
                        'type': 'sng_header'
                    })
                    pos = chunk.find(b"SNGPKG", pos + 1)
                
                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                    offset += chunk_size - overlap
                else:
                    break
    except Exception as e:
        print(f"Error scanning {ark_path}: {e}")
    return found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scan_single_ark.py <ark_path>")
        sys.exit(1)
        
    ark_path = sys.argv[1]
    known = get_known_ids()
    results = scan_ark_chunked(ark_path, known)
    
    # Output as JSON lines for easy appending
    for r in results:
        r['ark'] = ark_path
        print(json.dumps(r))
