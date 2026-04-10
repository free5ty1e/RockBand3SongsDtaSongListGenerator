#!/usr/bin/env python3
import subprocess
import json
import re
import os
import time

def get_pkg_list_with_sizes():
    """Get list of PKGs sorted by size."""
    cmd = 'smbclient //192.168.100.135/incoming -N -c "cd temp/Rb4Dlc; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    pkgs = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith('.') or line.startswith('Sharename') or line.startswith('---------'):
            continue
        
        parts = line.split()
        if not parts or len(parts) < 5:
            continue
            
        filename = parts[0]
        if filename.endswith('.pkg') and not filename.startswith('._'):
            try:
                size = int(parts[2])
                pkgs.append((filename, size))
            except:
                pass
                
    return sorted(pkgs, key=lambda x: x[1])

def scan_pkg_for_ids(pkg_name):
    """Scan a PKG file for RBSongMetadata and return any found IDs."""
    tmp_path = f"/tmp/{pkg_name}"
    
    # Download with timeout
    cmd = f'smbget -N smb://192.168.100.135/incoming/temp/Rb4Dlc/{pkg_name} -o {tmp_path}'
    try:
        # Use subprocess.run with timeout
        subprocess.run(cmd, shell=True, check=True, capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"Timeout downloading {pkg_name}")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {pkg_name}: {e}")
        return []
    
    # Quick scan for metadata
    try:
        with open(tmp_path, 'rb') as f:
            # Read first 100MB maximum
            chunk = f.read(100 * 1024 * 1024)
            if not chunk:
                return []
            
            # Look for RBSongMetadata markers
            ids = []
            pos = 0
            while True:
                idx = chunk.find(b"RBSongMetadata", pos)
                if idx == -1:
                    break
                
                # Look for strings near the marker
                lookahead = chunk[idx:min(idx+2048, len(chunk))]
                matches = re.finditer(b'[a-z0-9_]{5,40}', lookahead)
                
                known_ids = set()
                # Load known IDs
                json_path = '/workspace/RB4/rb4_empty_songs_full.json'
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f_json:
                        data = json.load(f_json)
                        known_ids = {item['short_filename'] for item in data if 'short_filename' in item}
                
                asset_prefixes = {
                    'crowd_', 'light_', 'preset_', 'emote_', 'state_', 'cb_', 'floor_', 'stage_', 
                    'unlit_', 'positive_', 'player_', 'audio_', 'fmod_', 'game_', 'gig_', 
                    'entity_', 'waveform_', 'vocal_', 'rblight_', 'rblighting_', 'big_club_', 
                    'small_club_', 'arena_', 'curtain_', 'mesh_', 'default_', 'volumetric_', 
                    'sr_', 'flare_', 'strobe_', 'blackout_', 'lightgroup_', 'cam_', 'loop_'
                }
                
                for m in matches:
                    s = m.group(0).decode('ascii', errors='ignore')
                    if s not in known_ids and '_' in s:
                        if not any(s.startswith(prefix) for prefix in asset_prefixes):
                            if s not in ["rbsongmetadata", "short_name", "tempo", "vocal_track"]:
                                ids.append({
                                    'id': s,
                                    'pkg': pkg_name,
                                    'type': 'metadata'
                                })
                pos = idx + 1
                
            return ids
    except Exception as e:
        print(f"Error scanning {pkg_name}: {e}")
        return []
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main():
    # Get PKGs sorted by size
    pkgs = get_pkg_list_with_sizes()
    print(f"Found {len(pkgs)} PKGs")
    
    # Process smaller PKGs first
    processed = 0
    all_results = []
    discovery_count = 0
    
    for pkg_name, size in pkgs[:20]:  # Start with first 20 smallest PKGs
        print(f"Processing {pkg_name} ({size:,} bytes)... ")
        
        # Skip if size > 200MB for now
        if size > 200 * 1024 * 1024:
            print(f"Skipping large PKG {pkg_name} ({size:,} bytes)")
            continue
            
        results = scan_pkg_for_ids(pkg_name)
        if results:
            discovery_count += len(results)
            all_results.extend(results)
            print(f"Found {len(results)} new IDs")
        else:
            print("No new IDs found")
        
        processed += 1
        if processed >= 10:  # Limit to first 10 successful scans
            break
    
    # Save results
    output_path = '/workspace/RB4/output/dlc_small_pkg_discoveries.json'
    if all_results:
        with open(output_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Saved {len(all_results)} new IDs to {output_path}")
    else:
        print("No new IDs found in small PKGs")
    
    return all_results

if __name__ == "__main__":
    main()
