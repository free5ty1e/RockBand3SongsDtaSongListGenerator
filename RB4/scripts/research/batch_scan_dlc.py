#!/usr/bin/env python3
"""
Batch scan DLC PKGs - download, extract, parse songdta, check for new songs
"""
import subprocess
import os
import json
import glob

SMB_SERVER = "192.168.100.135"
SMB_SHARE = "incoming"
SMB_PATH = "temp/Rb4Dlc"
WORK_DIR = "/workspace/rb4_temp/dlc_batch"

def get_pkg_list():
    cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "cd {SMB_PATH}; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    pkgs = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith('.') or '._' in line:
            continue
        parts = line.split()
        if len(parts) >= 3 and parts[0].endswith('.pkg'):
            try:
                size = int(parts[2])
                pkgs.append((parts[0], size))
            except:
                pass
    return sorted(pkgs, key=lambda x: x[1])

def download_and_extract(pkg_name, max_size_mb=200):
    """Download and extract a PKG if it's small enough"""
    local_path = f"/workspace/rb4_temp/downloads/{pkg_name}"
    extract_dir = os.path.join(WORK_DIR, pkg_name.replace('.pkg', ''))
    os.makedirs("/workspace/rb4_temp/downloads", exist_ok=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)
    
    # Clean previous
    import shutil
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    
    # Download
    cmd = f'smbget -N smb://{SMB_SERVER}/{SMB_SHARE}/{SMB_PATH}/{pkg_name} -o {local_path}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"  Download failed")
        return None
    
    # Extract
    cmd = f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 /usr/local/bin/PkgTool.Core pkg_extract {local_path} {extract_dir}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"  Extract failed")
        return None
    
    # Find songdta files
    songdtas = glob.glob(f"{extract_dir}/**/*.songdta_ps4", recursive=True)
    return songdtas

def parse_songdta(songdtas):
    """Parse songdta files"""
    if not songdtas:
        return []
    
    # Parse each file individually and collect results
    all_songs = []
    for sd in songdtas:
        output = f"/workspace/rb4_temp/parse_{os.path.basename(os.path.dirname(sd))}.json"
        cmd = f'python3 /workspace/RB4/scripts/research/extract_binary_dta.py "{sd}" {output}'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        
        if result.returncode == 0 and os.path.exists(output):
            with open(output) as f:
                songs = json.load(f)
                all_songs.extend(songs)
    
    return all_songs

def check_new(songs):
    """Check if songs are new"""
    with open('/workspace/RB4/rb4_empty_songs_full.json', 'r') as f:
        known = json.load(f)
    known_ids = {item['short_filename'] for item in known if 'short_filename' in item}
    
    new = []
    for s in songs:
        if s['shortName'] not in known_ids:
            new.append(s)
    return new

def main():
    print("Getting PKG list...")
    pkgs = get_pkg_list()
    print(f"Found {len(pkgs)} PKGs")
    
    # Load known IDs for quick check
    with open('/workspace/RB4/rb4_empty_songs_full.json', 'r') as f:
        known = json.load(f)
    known_ids = {item['short_filename'] for item in known if 'short_filename' in item}
    
    all_new = []
    
    # Process small PKGs first (< 100MB)
    small_pkgs = [(n, s) for n, s in pkgs if s < 100 * 1024 * 1024]
    print(f"Processing {len(small_pkgs)} small PKGs...")
    
    for i, (pkg_name, size) in enumerate(small_pkgs):  # Process all small PKGs
        # Skip already extracted
        extracted_name = pkg_name.replace('.pkg', '')
        already_extracted = os.path.exists(os.path.join(WORK_DIR, extracted_name))
        if already_extracted:
            print(f"[{i+1}/{len(small_pkgs)}] {pkg_name} - already extracted, parsing...")
            extract_dir = os.path.join(WORK_DIR, extracted_name)
            songdtas = glob.glob(f"{extract_dir}/**/*.songdta_ps4", recursive=True)
            if songdtas:
                songs = parse_songdta(songdtas)
                new_songs = [s for s in songs if s['shortName'] not in known_ids]
                if new_songs:
                    print(f"  Found {len(new_songs)} new!")
                    all_new.extend(new_songs)
                    for ns in new_songs:
                        print(f"    - {ns['shortName']}: {ns['title']} by {ns['artist']}")
                else:
                    print(f"  {len(songs)} songs, all known")
            continue
            
        print(f"[{i+1}/{len(small_pkgs)}] {pkg_name} ({size/1024/1024:.1f}MB)... ", end='', flush=True)
        
        songdtas = download_and_extract(pkg_name)
        if songdtas:
            songs = parse_songdta(songdtas)
            new_songs = [s for s in songs if s['shortName'] not in known_ids]
            if new_songs:
                print(f"Found {len(new_songs)} new!")
                all_new.extend(new_songs)
                for ns in new_songs:
                    print(f"    - {ns['shortName']}: {ns['title']} by {ns['artist']}")
            else:
                print(f"Found {len(songs)} songs, all known")
        else:
            print("skipped")
        
        # Clean up - keep extracted files for now
        try:
            os.remove(f"/workspace/rb4_temp/downloads/{pkg_name}")
        except: pass
    
    # Save results
    if all_new:
        output = "/workspace/rb4_temp/batch_discoveries.json"
        with open(output, 'w') as f:
            json.dump(all_new, f, indent=2)
        print(f"\nTotal new songs found: {len(all_new)}")
        print(f"Saved to {output}")
    
    return all_new

if __name__ == "__main__":
    main()