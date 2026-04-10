import glob
import re
import os

def extract_songs_from_ark(ark_path):
    songs = set()
    try:
        with open(ark_path, 'rb') as f:
            # Read in smaller chunks and handle overlap
            chunk_size = 1024 * 1024
            overlap = 100
            offset = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                matches = re.finditer(b'short_name\x00([a-zA-Z0-9_]+)\x00', chunk)
                for match in matches:
                    songs.add(match.group(1).decode('ascii', errors='ignore'))
                
                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                else:
                    break
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return songs

all_songs = set()
ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
for d in ark_dirs:
    ark_files = glob.glob(os.path.join(d, '*.ark'))
    for ark_path in ark_files:
        print(f"Processing {ark_path}...", end='\r')
        songs = extract_songs_from_ark(ark_path)
        all_songs.update(songs)

print(f"\nTotal unique songs found: {len(all_songs)}")
with open('/workspace/RB4/output/extracted_short_names.txt', 'w') as f:
    for song in sorted(list(all_songs)):
        f.write(f"{song}\n")
