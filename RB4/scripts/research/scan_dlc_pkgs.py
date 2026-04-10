import os
import subprocess
import json
import re
import glob

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

def scan_file_for_ids(file_path, known_ids):
    found = []
    asset_prefixes = {
        'crowd_', 'light_', 'preset_', 'emote_', 'state_', 'cb_', 'floor_', 'stage_', 
        'unlit_', 'positive_', 'player_', 'audio_', 'fmod_', 'game_', 'gig_', 
        'entity_', 'waveform_', 'vocal_', 'rblight_', 'rblighting_', 'big_club_', 
        'small_club_', 'arena_', 'curtain_', 'mesh_', 'default_', 'volumetric_', 
        'sr_', 'flare_', 'strobe_', 'blackout_', 'lightgroup_', 'cam_', 'loop_'
    }
    
    try:
        with open(file_path, 'rb') as f:
            chunk_size = 10 * 1024 * 1024
            overlap = 1024 * 1024
            offset = 0
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Look for RBSongMetadata markers
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
                
                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                    offset += chunk_size - overlap
                else:
                    break
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    return found

def download_pkg(filename, retries=3):
    # Use smbget to download the file to /tmp
    # smbget -N smb://server/share/path/file -o local_path
    cmd = f'smbget -N smb://192.168.100.135/incoming/temp/Rb4Dlc/{filename} -o /tmp/{filename}'
    for i in range(retries):
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            if i == retries - 1:
                print(f"Failed to download {filename} after {retries} attempts: {e}")
                return False
            continue
    return False

def main():
    known = get_known_ids()
    
    # Get list of PKGs from SMB with sizes
    cmd = 'smbclient //192.168.100.135/incoming -N -c "cd temp/Rb4Dlc; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    pkg_data = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith('.') or line.startswith('Sharename') or line.startswith('---------'):
            continue
        
        parts = line.split()
        if not parts:
            continue
            
        filename = parts[0]
        if filename.endswith('.pkg') and not filename.startswith('._'):
            try:
                size = int(parts[2])
                pkg_data.append((filename, size))
            except:
                pass
                
    # Sort PKGs by size (smallest first) to maximize progress
    pkg_data.sort(key=lambda x: x[1])
    pkgs = [p[0] for p in pkg_data]
    
    print(f"Found {len(pkgs)} PKGs to process (sorted by size).")
    
    results = []
    output_path = '/workspace/RB4/output/dlc_pkg_discoveries.json'
    
    # Load existing results if any to resume
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r') as f:
                results = json.load(f)
        except: pass

    # Keep track of failed downloads to avoid retrying them every time
    failed_downloads = set()

    for pkg in pkgs:
        # Skip if already processed or consistently fails
        if any(r['pkg'] == pkg for r in results) or pkg in failed_downloads:
            continue

        print(f"Processing {pkg}...", end=' ', flush=True)
        tmp_path = f"/tmp/{pkg}"
        
        if download_pkg(pkg):
            found = scan_file_for_ids(tmp_path, known)
            for item in found:
                item['pkg'] = pkg
                results.append(item)
            
            # Save incrementally
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Clean up
            os.remove(tmp_path)
            print(f"Done (Found {len(found)})")
        else:
            print("Failed")
            failed_downloads.add(pkg)
            
    print(f"Finished. Total discoveries: {len(results)}")

if __name__ == "__main__":
    main()
