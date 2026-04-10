import glob
import os
import mmap
import re
import json

def load_validation_list():
    # Load Rivals list and slugify titles
    songs = set()
    rivals_path = '/workspace/RB4/rb4songlistWithRivals.txt'
    if os.path.exists(rivals_path):
        with open(rivals_path, 'r') as f:
            for line in f:
                if ' - ' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 2:
                        title = parts[1].split(' (')[0].lower()
                        # Slugify: remove non-alphanumeric
                        slug = re.sub(r'[^a-z0-9]', '', title)
                        songs.add(slug)
    
    # Also load from baseline JSON
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

def is_likely_song(s, validation_list):
    # A string is likely a song if it's in the validation list
    # or if it's a common slug of a known song.
    if s in validation_list:
        return True
    # Check if it's a substring of any known song slug
    for known in validation_list:
        if len(s) >= 5 and (s in known or known in s):
            return True
    return False

def main():
    validation_list = load_validation_list()
    print(f"Loaded {len(validation_list)} songs for validation.")
    
    confirmed_songs = set()
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
                            chunk = mm[pos : pos + 512]
                            # Find all alphanumeric strings 5-30 chars
                            matches = re.findall(b'[a-z0-9]{5,30}', chunk)
                            for m in matches:
                                s = m.decode('ascii', errors='ignore')
                                if is_likely_song(s, validation_list):
                                    confirmed_songs.add(s)
                            pos = mm.find(b"RBSongMetadata", pos + 1)
            except Exception as e:
                print(f"Error scanning {ark_path}: {e}")
    
    print(f"\nConfirmed {len(confirmed_songs)} songs in .ark files")
    with open('/workspace/RB4/output/confirmed_ark_songs.txt', 'w') as f:
        for s in sorted(list(confirmed_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
