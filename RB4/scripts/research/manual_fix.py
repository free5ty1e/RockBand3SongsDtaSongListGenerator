#!/usr/bin/env python3
import re
import json
from pathlib import Path

def parse_with_regex(content, game_name):
    """Use regex to extract song records from various formats."""
    songs = []
    
    patterns = [
        # Pattern 1: "Title" [Artist] Year Genre (multi-line cell format)
        r'"([^"]+)"\s*\n\[([^\]]+)\]\s*\n(\d{4})\s*\n([A-Za-z/]+)',
        # Pattern 2: All on one line
        r'"([^"]+)"\s*\[([^\]]+)\]\s*(\d{4})\s*([A-Za-z/]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for m in matches:
            songs.append({
                'title': m[0].strip(),
                'artist': m[1].strip().replace('&amp;', '&'),
                'year': int(m[2]),
                'genre': m[3].strip()
            })
        if songs:
            break
    
    return songs

# File paths
files = {
    'rb3': '/home/vscode/.local/share/opencode/tool-output/tool_da9056dc1001cM5MYr3DPu4UoX',
    'green_day': '/home/vscode/.local/share/opencode/tool-output/tool_da906944b001dDQv5rwXWxrQe6',
    'dlc': '/home/vscode/.local/share/opencode/tool-output/tool_da90f417c001pNhBGmM5AkMj35',
    'rb4': '/home/vscode/.local/share/opencode/tool-output/tool_da92ef9400012qql6FtecxZKxY',
}

output_dir = Path('/workspace/RB4/docs/research/song_lists')

# Load existing DLC files (they work)
print("Loading existing DLC...")
with open(output_dir / 'dlc_rb_all_games.json', 'r') as f:
    dlc_all = json.load(f)['songs']
with open(output_dir / 'dlc_rb3_onwards.json', 'r') as f:
    dlc_rb3 = json.load(f)['songs']
with open(output_dir / 'dlc_rb4_only.json', 'r') as f:
    dlc_rb4 = json.load(f)['songs']

print(f"  Loaded {len(dlc_all)} all, {len(dlc_rb3)} rb3, {len(dlc_rb4)} rb4")

# Try regex for RB3
print("\nTrying regex for Rock Band 3...")
with open(files['rb3'], 'r') as f:
    content = f.read()
    
# Find track listing section
song_pattern = r'"([^"]+)"\n\[([^\]]+)\]\n(\d{4})\n([A-Za-z/]+)'
matches = re.findall(song_pattern, content)
print(f"  Found {len(matches)} matches")

# For now, use the webfetch data for RB4 (it's already complete)
print("\nLoading RB4 from webfetch...")
with open(files['rb4'], 'r') as f:
    content = f.read()

# Find track listing section  
song_pattern = r'"([^"]+)"\s+([A-Za-z][A-Za-z\s&,\.\']+?)\s+(\d{4})\s+([A-Za-z/]+)'
matches = re.findall(song_pattern, content)
print(f"  Found {len(matches)} matches")
if matches:
    print(f"  Sample: {matches[:3]}")

# RB4: extract manually from what I know about it - 65 songs
# The format: "Title" Artist Year Genre - each on separate lines
rb4_songs = []
lines = content.split('\n')
in_main = False
row = {}

for i, line in enumerate(lines):
    line = line.strip()
    
    if 'Main soundtrack' in line:
        in_main = True
        continue
    
    if not in_main:
        continue
    
    if line.startswith('##'):
        break
    
    if not line:
        continue
        
    # Parse state machine - Title starts with "
    if line.startswith('"'):
        if row and 'title' in row and 'artist' in row and 'year' in row:
            rb4_songs.append(row.copy())
        m = re.search(r'"([^"]+)"', line)
        if m:
            title = m.group(1)
            # Handle nested quotes like Metropolis—Part I: "The Miracle and the Sleeper"
            if '"' in title:
                continue
            row = {'title': title}
    
    elif row.get('title') and 'artist' not in row:
        if re.match(r'^[A-Za-z]', line):
            row['artist'] = line
    
    elif row.get('artist') and 'year' not in row:
        if line.isdigit() and len(line) == 4:
            row['year'] = int(line)
    
    elif row.get('year') and 'genre' not in row:
        if re.match(r'^[A-Za-z][A-Za-z\s/&-]+$', line):
            row['genre'] = line

# Last one
if row and 'title' in row and 'artist' in row and 'year' in row:
    rb4_songs.append(row.copy())

print(f"\nTotal RB4 songs: {len(rb4_songs)}")

# Save
output_dir = Path('/workspace/RB4/docs/research/song_lists')

with open(output_dir / 'rock_band_4_disc.json', 'w') as f:
    json.dump({
        "game": "Rock Band 4", 
        "type": "disc", 
        "songs": rb4_songs
    }, f, indent=2)

print("\nDone!")