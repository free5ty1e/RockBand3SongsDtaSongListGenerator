import glob
import re

def extract_songs_from_ark(ark_path):
    songs = set()
    try:
        with open(ark_path, 'rb') as f:
            # Read in chunks to avoid memory issues
            while True:
                chunk = f.read(10 * 1024 * 1024)
                if not chunk:
                    break
                
                # Look for "short_name" followed by a null or some length
                # Based on the previous discovery: b'short_name\x00aintmessinround\x00'
                matches = re.finditer(b'short_name\x00([a-zA-Z0-9_]+)\x00', chunk)
                for match in matches:
                    songs.add(match.group(1).decode('ascii', errors='ignore'))
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return songs

all_songs = set()
ark_files = glob.glob('/workspace/rb4_temp/**/*.ark', recursive=True)
for ark_path in ark_files:
    songs = extract_songs_from_ark(ark_path)
    all_songs.update(songs)
    if songs:
        print(f"Found {len(songs)} songs in {ark_path}")

print(f"Total unique songs found: {len(all_songs)}")
with open('/workspace/RB4/output/extracted_short_names.txt', 'w') as f:
    for song in sorted(list(all_songs)):
        f.write(f"{song}\n")
