#!/usr/bin/env python3
import re
import json

def simple_dj_parse(content):
    songs = []
    lines = content.split('\n')
    
    row = {}
    state = 0
    
    in_table = False
    
    for line in lines:
        if 'Song 1 title' in line and 'Artist 1' in line:
            in_table = True
            continue
        
        if in_table and line.startswith('## '):
            in_table = False
            break
        
        if not in_table:
            continue
            
        line_stripped = line.strip()
        
        if state == 0:
            if line_stripped.startswith('[') and '](' in line_stripped:
                match = re.search(r'\[([^\]]+)\]', line_stripped)
                if match:
                    row['title'] = match.group(1)
                    state = 1
                    
        elif state == 1:
            if line_stripped.startswith('[') and '](' in line_stripped:
                match = re.search(r'\[([^\]]+)\]', line_stripped)
                if match:
                    row['artist'] = match.group(1)
                    state = 2
                    
        elif state == 2:
            if line_stripped.startswith('[') and '](' in line_stripped:
                match = re.search(r'\[([^\]]+)\]', line_stripped)
                if match:
                    row['title2'] = match.group(1)
                    state = 3
            elif line_stripped == '' or 'n/a' in line_stripped.lower():
                state = 3
                
        elif state == 3:
            if line_stripped.startswith('[') and '](' in line_stripped:
                match = re.search(r'\[([^\]]+)\]', line_stripped)
                if match:
                    row['artist2'] = match.group(1)
            elif line_stripped and not line_stripped.startswith('|'):
                # Skip to next
                pass
            
            # Save the row
            if 'title' in row and 'artist' in row:
                songs.append({
                    "title": row['title'],
                    "artist": row['artist'],
                    "title2": row.get('title2'),
                    "artist2": row.get('artist2'),
                    "year": None,
                    "genre": None,
                    "master": True
                })
                row = {}
                state = 0
    
    seen = set()
    result = []
    for s in songs:
        key = (s.get('title'), s.get('artist'))
        if key not in seen:
            seen.add(key)
            result.append(s)
    
    return result

def main():
    dj_hero_file = '/home/vscode/.local/share/opencode/tool-output/tool_dacc54ec6001Uvv0H826VF3CNW'
    dj_hero_2_file = '/home/vscode/.local/share/opencode/tool-output/tool_dacc5506f001FVbkyHwZXyfGEw'
    on_tour_file = '/home/vscode/.local/share/opencode/tool-output/tool_dacc54fec0015YG17mtc7wrxMX'
    
    with open(dj_hero_file, 'r') as f:
        dj_content = f.read()
    
    with open(dj_hero_2_file, 'r') as f:
        dj2_content = f.read()
    
    with open(on_tour_file, 'r') as f:
        ot_content = f.read()
    
    dj1_songs = simple_dj_parse(dj_content)
    print(f"DJ Hero: {len(dj1_songs)} songs")
    if dj1_songs:
        print(f"  First: {dj1_songs[0]['title']} - {dj1_songs[0]['artist']}")
    
    dj2_songs = simple_dj_parse(dj2_content)
    print(f"DJ Hero 2: {len(dj2_songs)} songs")
    if dj2_songs:
        print(f"  First: {dj2_songs[0]['title']} - {dj2_songs[0]['artist']}")
    
    # On Tour - simpler single-line format
    songs = []
    lines = ot_content.split('\n')
    in_section = False
    header_found = False
    
    for line in lines:
        if '*Guitar Hero: On Tour* setlist' in line:
            in_section = True
            continue
        
        if in_section and '*Guitar Hero On Tour: Decades* setlist' in line:
            in_section = False
            break
        
        if in_section and not header_found:
            if 'Year' in line and 'Song title' in line:
                header_found = True
            continue
        
        if in_section and header_found:
            if line.strip().startswith('|') and '---' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3 and parts[0].isdigit():
                    year = int(parts[0])
                    title_match = re.search(r'\[([^\]]+)\]', parts[1])
                    title = title_match.group(1) if title_match else parts[1]
                    artist_match = re.search(r'\[([^\]]+)\]', parts[2])
                    artist = artist_match.group(1) if artist_match else parts[2]
                    
                    master = True
                    if len(parts) > 3 and 'No' in parts[3]:
                        master = False
                    
                    songs.append({
                        "title": title,
                        "artist": artist,
                        "year": year,
                        "genre": None,
                        "master": master
                    })
    
    print(f"On Tour: {len(songs)} songs")
    if songs:
        print(f"  First: {songs[0]['title']} - {songs[0]['artist']} ({songs[0]['year']})")
    
    output_dir = '/workspace/RB4/docs/research/song_lists/gh'
    
    dj_hero_data = {"game": "DJ Hero", "type": "disc", "songs": dj1_songs}
    dj_hero_2_data = {"game": "DJ Hero 2", "type": "disc", "songs": dj2_songs}
    on_tour_data = {"game": "Guitar Hero: On Tour", "type": "disc", "songs": songs}
    
    with open(f'{output_dir}/dj_hero_disc.json', 'w') as f:
        json.dump(dj_hero_data, f, indent=2)
    with open(f'{output_dir}/dj_hero_2_disc.json', 'w') as f:
        json.dump(dj_hero_2_data, f, indent=2)
    with open(f'{output_dir}/guitar_hero_on_tour_disc.json', 'w') as f:
        json.dump(on_tour_data, f, indent=2)
    
    print(f"\nSaved to {output_dir}")

if __name__ == '__main__':
    main()