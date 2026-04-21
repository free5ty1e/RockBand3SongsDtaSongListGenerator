#!/usr/bin/env python3
import re
import json

# Hardcode data boundaries after eyeballing the file
def parse_dj(filename, game_name):
    with open(filename) as f:
        content = f.read()
    
    # Find table by detecting "Song 1 title" with "Artist 1" nearby
    lines = content.split('\n')
    
    # Find first data start: link cells start after Level header (line 170)
    # Data ends before next ## section (around line 1470)
    
    # Get all link values
    links = []
    in_data = False
    for line in lines:
        if '](' in line:
            m = re.search(r'\[([^\]]+)\]', line)
            if m:
                links.append(m.group(1))
    
    # First 58 sets are the disc songs (58 songs * 7 fields)
    # But we only want first 4 fields per row (title, artist, title2, artist2)
    songs = []
    for i in range(0, 58*7, 7):
        if i+1 < len(links):
            songs.append({
                "title": links[i],
                "artist": links[i+1],
                "title2": links[i+2] if i+2 < len(links) else None,
                "artist2": links[i+3] if i+3 < len(links) else None,
                "year": None,
                "genre": None,
                "master": True
            })
    
    return {"game": game_name, "type": "disc", "songs": songs}

def parse_on_tour(filename, game_name):
    with open(filename) as f:
        lines = f.readlines()
    
    in_section = False
    header_done = False
    songs = []
    
    for line in lines:
        s = line.strip()
        if '*Guitar Hero: On Tour* setlist' in s:
            in_section = True
            continue
        if in_section and '*Guitar Hero On Tour: Decades* setlist' in s:
            break
        if in_section and not header_done:
            if 'Year' in s and 'Song title' in s:
                header_done = True
            continue
        if in_section and header_done:
            if s.startswith('|') and '---' not in s:
                parts = [p.strip() for p in s.split('|') if p.strip()]
                if len(parts) >= 3 and parts[0].isdigit():
                    year = int(parts[0])
                    tm = re.search(r'\[([^\]]+)\]', parts[1])
                    am = re.search(r'\[([^\]]+)\]', parts[2])
                    title = tm.group(1) if tm else parts[1]
                    artist = am.group(1) if am else parts[2]
                    master = True
                    if len(parts) > 3:
                        master = ('Yes' in parts[3])
                    songs.append({
                        "title": title,
                        "artist": artist,
                        "year": year,
                        "genre": None,
                        "master": master
                    })
    
    return {"game": game_name, "type": "disc", "songs": songs}

dj1 = parse_dj('/home/vscode/.local/share/opencode/tool-output/tool_dacc54ec6001Uvv0H826VF3CNW', 'DJ Hero')
print(f"DJ Hero: {len(dj1['songs'])} songs")
if dj1['songs']:
    print(f"  1st: {dj1['songs'][0]['title']} - {dj1['songs'][0]['artist']}")

dj2 = parse_dj('/home/vscode/.local/share/opencode/tool-output/tool_dacc5506f001FVbkyHwZXyfGEw', 'DJ Hero 2')
print(f"DJ Hero 2: {len(dj2['songs'])} songs")

ot = parse_on_tour('/home/vscode/.local/share/opencode/tool-output/tool_dacc54fec0015YG17mtc7wrxMX', 'Guitar Hero: On Tour')
print(f"On Tour: {len(ot['songs'])} songs")

out_dir = '/workspace/RB4/docs/research/song_lists/gh'
json.dump(dj1, open(f'{out_dir}/dj_hero_disc.json', 'w'), indent=2)
json.dump(dj2, open(f'{out_dir}/dj_hero_2_disc.json', 'w'), indent=2)
json.dump(ot, open(f'{out_dir}/guitar_hero_on_tour_disc.json', 'w'), indent=2)
print("Saved!")