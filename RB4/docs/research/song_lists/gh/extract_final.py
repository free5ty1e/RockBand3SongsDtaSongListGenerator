#!/usr/bin/env python3
import re
import json

def parse_dj(filename, game_name):
    with open(filename) as f:
        lines = f.readlines()
    
    # Find header row position - table is between Song headers and next ## section
    in_section = False
    song_headers = []
    for i, line in enumerate(lines):
        s = line.strip()
        if 'Song 1 title' in s:
            song_headers.append(i)
        if s.startswith('## ') and in_section:
            song_headers.append(i)
            break
        if 'Song 1 title' in s:
            in_section = True
    
    # If no Level, just get all links between Song 1 and next section
    start = 0
    end = len(lines)
    for i, line in enumerate(lines):
        if 'Song 1 title' in line.strip():
            # find data start (skip header lines that contain titles)
            start = i + 20  # rough data start offset
    
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('## '):
            end = i
            break
    
    # Collect all link cells
    links = []
    for i in range(start, min(end, len(lines))):
        s = lines[i].strip()
        if '](' in s:
            m = re.search(r'\[([^\]]+)\]', s)
            if m:
                links.append(m.group(1))
    
    # Group by 7
    songs = []
    for i in range(0, len(links), 7):
        if i+1 < len(links):
            songs.append({
                "title": links[i],
                "artist": links[i+1],
                "title2": links[i+2] if i+2 < len(links) and links[i+2] != 'n/a' else None,
                "artist2": links[i+3] if i+3 < len(links) and links[i+3] != 'n/a' else None,
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
    print(f"  1st: {dj1['songs'][0]}")

dj2 = parse_dj('/home/vscode/.local/share/opencode/tool-output/tool_dacc5506f001FVbkyHwZXyfGEw', 'DJ Hero 2')
print(f"DJ Hero 2: {len(dj2['songs'])} songs")
if dj2['songs']:
    print(f"  1st: {dj2['songs'][0]}")

ot = parse_on_tour('/home/vscode/.local/share/opencode/tool-output/tool_dacc54fec0015YG17mtc7wrxMX', 'Guitar Hero: On Tour')
print(f"On Tour: {len(ot['songs'])} songs")
if ot['songs']:
    print(f"  1st: {ot['songs'][0]}")

out_dir = '/workspace/RB4/docs/research/song_lists/gh'
json.dump(dj1, open(f'{out_dir}/dj_hero_disc.json', 'w'), indent=2)
json.dump(dj2, open(f'{out_dir}/dj_hero_2_disc.json', 'w'), indent=2)
json.dump(ot, open(f'{out_dir}/guitar_hero_on_tour_disc.json', 'w'), indent=2)
print("Saved!")