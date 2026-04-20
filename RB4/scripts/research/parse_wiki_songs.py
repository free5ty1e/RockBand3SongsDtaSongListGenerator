#!/usr/bin/env python3
"""
Complete Wikipedia song list parser.
"""
import re
import json
from pathlib import Path

def parse_rb3_html(content):
    """Parse RB3 from HTML file - uses state machine."""
    songs = []
    lines = content.split('\n')
    
    in_track = False
    row = {}
    field_count = 0  # Track which field we're looking for
    
    for line in lines:
        line = line.strip()
        
        # Find start of track listing
        if line == '## Track listing':
            in_track = True
            continue
        
        if not in_track:
            continue
        
        # End of section
        if line == '## Downloadable songs' or line == '## Reception':
            break
            
        if not line:
            continue
        
        # Each song has: Title, Artist, Year, Genre in separate lines
        # Some have extra fields but we only need first 4
        
        if line.startswith('"') and '[/wiki/' in line and 'title' not in row:
            # New title - save previous if complete
            if row and 'title' in row and 'artist' in row and 'year' in row and 'genre' in row:
                songs.append(row.copy())
            row = {'title': line.strip('"').split('"')[0]}
        
        elif row.get('title') and 'artist' not in row:
            if line.startswith('['):
                artist = re.search(r'\[([^\]]+)\]', line)
                if artist:
                    row['artist'] = artist.group(1).split('|')[0]
        
        elif row.get('artist') and 'year' not in row:
            if line.isdigit() and len(line) == 4:
                row['year'] = int(line)
        
        elif row.get('year') and 'genre' not in row:
            if re.match(r'^[A-Za-z][A-Za-z\s/&-]+$', line):
                row['genre'] = line
    
    # Don't forget last one
    if row and 'title' in row and 'artist' in row and 'year' in row and 'genre' in row:
        songs.append(row.copy())
    
    return songs


def parse_green_day_html(content):
    """Parse Green Day - similar to RB3 but uses italics for album links."""
    songs = []
    lines = content.split('\n')
    
    in_track = False
    row = {}
    
    for line in lines:
        line = line.strip()
        
        if '## Main setlist' in line:
            in_track = True
            continue
        
        if not in_track:
            continue
        
        if line == '## Downloadable songs':
            break
        
        if not line:
            continue
        
        # Green Day uses format: "Title" on one line, *[Album]* on next
        if line.startswith('"') and row.get('title') is None:
            title_match = re.search(r'"([^"]+)"', line)
            if title_match:
                row = {'title': title_match.group(1), 'artist': 'Green Day', 'genre': 'Punk'}
        
        elif row.get('title') and 'album' not in row and '*[' in line:
            # Album line - skip
            
            # But next should be year
            continue
        
        elif row.get('title') and row.get('album') is None and line.isdigit() and len(line) == 4:
            row['year'] = int(line)
            songs.append(row.copy())
            row = {}
        
        # Check year after title (might be direct)
        elif row.get('title') and not row.get('year'):
            if line.isdigit() and len(line) == 4:
                row['year'] = int(line)
                # Add album if we haven't captured it yet
                songs.append(row.copy())
                row = {}
    
    # Handle last
    if row and 'title' in row and 'year' in row:
        songs.append(row.copy())
    
    return songs


def parse_rb4_webfetch(content):
    """Parse RB4 from webfetch - easier format."""
    songs = []
    lines = content.split('\n')
    
    in_main = False
    row = {}
    
    for line in lines:
        line = line.strip()
        
        if '## Main soundtrack' in line:
            in_main = True
            continue
        
        if not in_main:
            continue
        
        if line.startswith('## Downloadable content'):
            break
        
        if not line or line.startswith('Song'):
            continue
        
        # Title
        if line.startswith('"'):
            if row and 'title' in row and 'artist' in row and 'year' in row:
                songs.append(row.copy())
            match = re.search(r'"([^"]+)"', line)
            if match:
                row = {'title': match.group(1)}
        
        # Artist
        elif row.get('title') and 'artist' not in row:
            if re.match(r'^[A-Za-z]', line):
                row['artist'] = line
        
        # Year
        elif row.get('artist') and 'year' not in row:
            if line.isdigit() and len(line) == 4:
                row['year'] = int(line)
        
        # Genre
        elif row.get('year') and 'genre' not in row:
            if re.match(r'^[A-Za-z][A-Za-z\s/&-]+$', line):
                row['genre'] = line
    
    if row and 'title' in row:
        songs.append(row.copy())
    
    return songs


def parse_dlc_sections(content):
    """Parse DLC sections."""
    songs_all = []
    songs_rb3 = []
    songs_rb4 = []
    
    lines = content.split('\n')
    section = None
    
    for line in lines:
        line = line.strip()
        
        if '## Playable in all games' in line:
            section = 'all'
            continue
        elif '## Playable in Rock Band 3' in line:
            section = 'rb3'
            continue
        elif '## Playable in Rock Band 4 only' in line:
            section = 'rb4'
            continue
        
        if section is None:
            continue
        
        if line.startswith('##') or not line:
            continue
        
        # Pattern: "Title" [Artist] Year Genre
        if line.startswith('"') and '[' in line:
            match = re.search(r'"([^"]+)"\s*\[([^\]]+)\]\s*(\d{4})\s*([A-Za-z/]+)', line)
            if match:
                song = {
                    'title': match.group(1),
                    'artist': match.group(2).split('|')[0],
                    'year': int(match.group(3)),
                    'genre': match.group(4)
                }
                if section == 'all':
                    songs_all.append(song)
                elif section == 'rb3':
                    songs_rb3.append(song)
                elif section == 'rb4':
                    songs_rb4.append(song)
    
    return songs_all, songs_rb3, songs_rb4


def main():
    output_dir = Path('/workspace/RB4/docs/research/song_lists')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    base = '/home/vscode/.local/share/opencode/tool-output'
    
    print("Parsing files...")
    
    # RB3
    print("  RB3...")
    with open(f'{base}/tool_da9056dc1001cM5MYr3DPu4UoX') as f:
        rb3 = parse_rb3_html(f.read())
    print(f"    Found {len(rb3)}")
    
    # Green Day
    print("  Green Day...")
    with open(f'{base}/tool_da906944b001dDQv5rwXWxrQe6') as f:
        green_day = parse_green_day_html(f.read())
    print(f"    Found {len(green_day)}")
    
    # RB4
    print("  RB4...")
    with open('/workspace/RB4/docs/research/song_lists/rock_band_4_disc.json') as f:
        rb4_data = json.load(f)
    # Use the existing parsed data which has more songs
    rb4 = rb4_data['songs']
    print(f"    Using {len(rb4)}")
    
    # DLC - load existing
    print("  DLC...")
    with open(f'{base}/tool_da90f417c001pNhBGmM5AkMj35') as f:
        dlc_all, dlc_rb3, dlc_rb4 = parse_dlc_sections(f.read())
    print(f"    Found {len(dlc_all)} all, {len(dlc_rb3)} rb3, {len(dlc_rb4)} rb4")
    
    # Write
    print("\nWriting files...")
    
    with open(output_dir / 'rock_band_3_disc.json', 'w') as f:
        json.dump({"game": "Rock Band 3", "type": "disc", "songs": rb3}, f, indent=2)
    
    with open(output_dir / 'green_day_rock_band.json', 'w') as f:
        json.dump({"game": "Green Day: Rock Band", "type": "disc", "songs": green_day}, f, indent=2)
    
    with open(output_dir / 'rock_band_4_disc.json', 'w') as f:
        json.dump({"game": "Rock Band 4", "type": "disc", "songs": rb4}, f, indent=2)
    
    with open(output_dir / 'dlc_rb_all_games.json', 'w') as f:
        json.dump({"game": "Rock Band Series", "type": "dlc", "compatibility": "all_games", "songs": dlc_all}, f, indent=2)
    
    with open(output_dir / 'dlc_rb3_onwards.json', 'w') as f:
        json.dump({"game": "Rock Band Series", "type": "dlc", "compatibility": "rb3_onwards", "songs": dlc_rb3}, f, indent=2)
    
    with open(output_dir / 'dlc_rb4_only.json', 'w') as f:
        json.dump({"game": "Rock Band Series", "type": "dlc", "compatibility": "rb4_only", "songs": dlc_rb4}, f, indent=2)
    
    print("Done!")


if __name__ == '__main__':
    main()