#!/usr/bin/env python3
import re
import json

html_file = "/home/vscode/.local/share/opencode/tool-output/tool_dad86a2d0001aR9u70Lx2J9M4Q"

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

def strip_tags(text):
    text = re.sub(r'<sup[^>]*>.*?</sup>', '', text)
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text)
    text = re.sub(r'<i>(.*?)</i>', r'\1', text)
    text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[#a-zA-Z]+;', ' ', text)
    text = text.replace('"', '"').replace('"', '"')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_one_section(content):
    songs = []
    rows = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL)
    header_skip = True
    for row in rows:
        if header_skip:
            header_skip = False
            continue
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) >= 5:
            title = strip_tags(cells[0])
            artist = strip_tags(cells[1])
            year_str = strip_tags(cells[2])
            genre = strip_tags(cells[3])
            pack = strip_tags(cells[4]) if len(cells) > 4 else ""
            
            year = None
            try:
                year = int(year_str)
            except:
                pass
            
            if title and artist and not title.startswith('&nbsp;'):
                title = title.strip().strip('"').strip()
                title = re.sub(r'\s*\(Cover Version\)\s*', '', title)
                title = title.strip('"').strip()
                songs.append({
                    "title": title,
                    "artist": artist,
                    "year": year,
                    "genre": genre,
                    "pack": pack
                })
    return songs

patterns = [
    ('all_games', r'<h3[^>]*id="Playable_in_all_games_in_the_Rock_Band_series"[^>]*>.*?<table class="wikitable[^>]*>(.*?)</table>'),
    ('rb3_onwards', r'<h3[^>]*id="Playable_in_Rock_Band_3_onwards_only"[^>]*>.*?<table class="wikitable[^>]*>(.*?)</table>'),
    ('rb4_only', r'<h3[^>]*id="Playable_in_Rock_Band_4_only"[^>]*>.*?<table class="wikitable[^>]*>(.*?)</table>')
]

songs_by_section = {'all_games': [], 'rb3_onwards': [], 'rb4_only': []}

for section_key, pattern in patterns:
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if match:
        table_content = match.group(1)
        songs = parse_one_section(table_content)
        songs_by_section[section_key] = songs
        print(f"{section_key}: {len(songs)} songs")

filenames = {
    'all_games': '/workspace/RB4/docs/research/song_lists/dlc_rb_all_games.json',
    'rb3_onwards': '/workspace/RB4/docs/research/song_lists/dlc_rb3_onwards.json',
    'rb4_only': '/workspace/RB4/docs/research/song_lists/dlc_rb4_only.json'
}

for section_key in ['all_games', 'rb3_onwards', 'rb4_only']:
    filename = filenames[section_key]
    output = {
        "game": "Rock Band DLC",
        "year": 2007,
        "type": "dlc",
        "songs": songs_by_section[section_key]
    }
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written {filename}")