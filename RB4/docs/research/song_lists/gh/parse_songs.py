#!/usr/bin/env python3
import re
import json

def parse_dj_hero():
    with open('/home/vscode/.local/share/opencode/tool-output/tool_dacc54ec6001Uvv0H826VF3CNW', 'r') as f:
        content = f.read()

    songs = []
    lines = content.split('\n')

    in_table = False
    headers = []

    for i, line in enumerate(lines):
        if 'Song 1 title' in line and 'Artist 1' in line:
            in_table = True
            continue

        if in_table and line.startswith('#') or line.startswith('##'):
            break

        if in_table and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 4 and parts[0] and parts[0][0] == '[':
                try:
                    title1 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[0])
                    artist1 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[1])

                    title2 = ""
                    artist2 = ""
                    if len(parts) > 2 and parts[2]:
                        title2 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[2]) if parts[2] else ""
                        artist2 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[3]) if len(parts) > 3 and parts[3] else ""

                    songs.append({
                        "title": title1,
                        "artist": artist1,
                        "title2": title2,
                        "artist2": artist2,
                        "year": None,
                        "genre": None,
                        "master": True
                    })
                except:
                    pass

    return songs

def parse_dj_hero_2():
    with open('/home/vscode/.local/share/opencode/tool-output/tool_dacc5506f001FVbkyHwZXyfGEw', 'r') as f:
        content = f.read()

    songs = []
    lines = content.split('\n')

    in_table = False

    for line in lines:
        if 'Song 1 title' in line and 'Artist 1' in line and 'Song 2' in line:
            in_table = True
            continue

        if in_table and (line.startswith('#') or line.startswith('## Downloadable')):
            break

        if in_table and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 4 and parts[0] and parts[0][0] == '[':
                try:
                    title1 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[0])
                    artist1 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[1])

                    title2 = ""
                    artist2 = ""
                    if len(parts) > 2 and parts[2]:
                        title2 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[2])
                        artist2 = re.sub(r'\[([^\]]+)\].*', r'\1', parts[3]) if len(parts) > 3 and parts[3] else ""

                    songs.append({
                        "title": title1,
                        "artist": artist1,
                        "title2": title2,
                        "artist2": artist2,
                        "year": None,
                        "genre": None,
                        "master": True
                    })
                except:
                    pass

    return songs

def parse_on_tour():
    with open('/home/vscode/.local/share/opencode/tool-output/tool_dacc54fec0015YG17mtc7wrxMX', 'r') as f:
        content = f.read()

    songs = []
    lines = content.split('\n')

    in_section = False
    in_table = False

    for i, line in enumerate(lines):
        if '*Guitar Hero: On Tour* setlist' in line:
            in_section = True
            in_table = True
            continue

        if in_section and '*Guitar Hero On Tour: Decades* setlist' in line:
            break

        if in_table and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 3 and parts[0].isdigit():
                try:
                    year = int(parts[0])
                    title = re.sub(r'\[([^\]]+)\][^\[]*).*', r'\1', parts[1])
                    title = re.sub(r'\(Cover\)|\(Remix\)', '', title).strip()

                    artist = re.sub(r'\[([^\]]+)\].*', r'\1', parts[2])

                    master = True
                    if '(Cover)' in parts[2]:
                        master = False

                    songs.append({
                        "title": title,
                        "artist": artist,
                        "year": year if year else None,
                        "genre": None,
                        "master": master
                    })
                except Exception as e:
                    pass

    return songs

def remove_duplicates(songs):
    seen = set()
    result = []
    for s in songs:
        key = (s.get('title'), s.get('artist'))
        if key not in seen:
            seen.add(key)
            result.append(s)
    return result

if __name__ == '__main__':
    dj1 = remove_duplicates(parse_dj_hero())
    print(f"DJ Hero: {len(dj1)} songs")

    dj2 = remove_duplicates(parse_dj_hero_2())
    print(f"DJ Hero 2: {len(dj2)} songs")

    ontour = remove_duplicates(parse_on_tour())
    print(f"On Tour: {len(ontour)} songs")