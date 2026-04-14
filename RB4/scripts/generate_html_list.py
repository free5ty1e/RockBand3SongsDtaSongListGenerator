#!/usr/bin/env python3
"""Generate HTML song list from JSON data."""

import json
import sys
import os

# Import modules
sys.path.insert(0, os.path.dirname(__file__))
from html_themes import THEMES, generate_theme_js
from empty_song_processor import apply_empty_song_fallback

def generate_html(metadata_dir, output_file):
    """Generate HTML file from metadata directory."""
    
    # Load and apply fallback
    from empty_song_processor import load_empty_songs_baseline, get_songs_with_fallback
    baseline = load_empty_songs_baseline()
    songs = get_songs_with_fallback(metadata_dir)
    """Generate HTML file from song data."""
    
    # Instrument icon mapping
    INSTRUMENT_ICONS = {
        'guitar': '🎸',
        'bass': '🎸',
        'drums': '🥁',
        'vocals': '🎤',
        'keys': '🎹',
        'real_guitar': '🎸',
        'real_bass': '🎸',
        'real_keys': '🎹',
    }
    
    # Convert to JS array
    js_songs = []
    for s in songs:
        duration_sec = s.get("durationMs", 0) // 1000 if s.get("durationMs") else 0
        duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}" if duration_sec else ""
        
        # Convert instruments string to icons
        instruments_str = s.get("instruments", "")
        instruments_icons = ""
        if instruments_str:
            for inst in ['real_guitar', 'real_bass', 'guitar', 'bass', 'drums', 'real_keys', 'keys', 'vocals']:
                if inst in instruments_str.lower():
                    instruments_icons += INSTRUMENT_ICONS.get(inst, '🎵')
        
        js_songs.append({
            "artist": s.get("artist", ""),
            "title": s.get("title", ""),
            "album": s.get("album", ""),
            "year": s.get("year", 0) or "",
            "duration": duration_sec,
            "duration_str": duration_str,
            "source": s.get("source", ""),
            "shortName": s.get("shortName", ""),
            "instruments": instruments_icons
        })
    
    js_data = json.dumps(js_songs)
    themes_js = generate_theme_js()
    
    # Default theme CSS
    t = THEMES["dark_blue"]
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rock Band 4 Song List</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: {t['body_bg']}; color: {t['text']}; }}
        h1 {{ color: {t['accent']}; margin-bottom: 10px; }}
        .controls {{ display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; padding: 15px; background: {t['panel_bg']}; border-radius: 8px; }}
        .control-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .control-group label {{ font-size: 12px; color: #888; }}
        input, select {{ padding: 8px 12px; border-radius: 4px; border: 1px solid #333; background: {t['input_bg']}; color: {t['text']}; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; background: {t['panel_bg']}; border-radius: 8px; }}
        th, td {{ padding: 10px 12px; text-align: left; font-size: 13px; }}
        th {{ background: {t['header_bg']}; color: {t['accent']}; cursor: pointer; position: sticky; top: 0; white-space: nowrap; }}
        tr:nth-child(even) {{ background: {t['body_bg']}; }}
        tr:hover {{ background: {t['hover']}; }}
        .source-RB4 {{ background: {t['accent']}; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-Rivals {{ background: #ff6b6b; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-custom {{ background: #feca57; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-dlc, .source-DLC {{ background: #48dbfb; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .instr {{ font-size: 14px; }}
        .stats {{ margin-top: 15px; color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>🎸 Rock Band 4 Song List</h1>
    <div class="controls">
        <div class="control-group">
            <label>🎨 Theme</label>
            <select id="theme" onchange="setTheme(this.value)">
                <option value="dark_blue">Dark Blue</option>
                <option value="matrix">Matrix</option>
                <option value="cyberpunk">Cyberpunk</option>
                <option value="sunset">Sunset</option>
                <option value="forest">Forest</option>
                <option value="rose">Rose</option>
                <option value="mono">Monochrome</option>
            </select>
        </div>
        <div class="control-group">
            <label>🔍 Search</label>
            <input type="text" id="search" placeholder="Artist, Title, Album..." onkeyup="filter()">
        </div>
        <div class="control-group">
            <label>📅 Year From</label>
            <input type="number" id="yearFrom" placeholder="1970" onchange="filter()">
        </div>
        <div class="control-group">
            <label>📅 Year To</label>
            <input type="number" id="yearTo" placeholder="2024" onchange="filter()">
        </div>
        <div class="control-group">
            <label>⏱️ Max Duration (sec)</label>
            <input type="number" id="durMax" placeholder="999" onchange="filter()">
        </div>
        <div class="control-group">
            <label>💿 Source</label>
            <select id="source" onchange="filter()"><option value="">All</option></select>
        </div>
    </div>
    <table>
        <thead>
            <tr>
                <th onclick="sort(0)">Artist ⬍</th>
                <th onclick="sort(1)">Title ⬍</th>
                <th onclick="sort(2)">Album ⬍</th>
                <th onclick="sort(3)">Year ⬍</th>
                <th onclick="sort(4)">Duration ⬍</th>
                <th onclick="sort(5)">Source ⬍</th>
                <th onclick="sort(6)">ShortName ⬍</th>
                <th>Instruments</th>
            </tr>
        </thead>
        <tbody id="body"></tbody>
    </table>
    <div class="stats" id="stats"></div>
    <script>
        {themes_js}
        
        const SONG_DATA = {js_data};
        let col = 3, asc = false;
        
        function setTheme(themeName) {{
            const t = THEMES[themeName];
            document.body.style.background = t.body_bg;
            document.body.style.color = t.text;
            document.querySelectorAll('.controls')[0].style.background = t.panel_bg;
            document.querySelectorAll('table')[0].style.background = t.panel_bg;
            document.querySelectorAll('th').forEach(el => {{
                el.style.background = t.header_bg;
                el.style.color = t.accent;
            }});
            document.querySelectorAll('tr:nth-child(even)').forEach(el => el.style.background = t.body_bg);
            document.querySelectorAll('tr:hover').forEach(el => el.style.background = t.hover);
            document.querySelectorAll('input, select').forEach(el => el.style.background = t.input_bg);
            document.querySelectorAll('h1')[0].style.color = t.accent;
        }}
        
        function init() {{
            const srcs = [...new Set(SONG_DATA.map(s => s.source))].sort();
            document.getElementById('source').innerHTML = '<option value="">All</option>' + 
                srcs.map(s => `<option value="${{s}}">${{s}}</option>`).join('');
            filter();
        }}
        
        function filter() {{
            const search = document.getElementById('search').value.toLowerCase();
            const yearFrom = parseInt(document.getElementById('yearFrom').value) || 0;
            const yearTo = parseInt(document.getElementById('yearTo').value) || 9999;
            const durMax = parseInt(document.getElementById('durMax').value) || 99999;
            const src = document.getElementById('source').value;
            
            let f = SONG_DATA.filter(s => {{
                if (search && !s.artist.toLowerCase().includes(search) && !s.title.toLowerCase().includes(search) && !s.album.toLowerCase().includes(search) && !s.shortName.toLowerCase().includes(search)) return false;
                if (s.year && (s.year < yearFrom || s.year > yearTo)) return false;
                if (s.duration > durMax) return false;
                if (src && s.source !== src) return false;
                return true;
            }});
            f.sort((a, b) => {{
                const va = a[Object.keys(a)[col]], vb = b[Object.keys(b)[col]];
                if (typeof va === 'number') return asc ? va - vb : vb - va;
                return asc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
            }});
            document.getElementById('body').innerHTML = f.map(s => `
                <tr>
                    <td>${{s.artist}}</td>
                    <td>${{s.title}}</td>
                    <td>${{s.album || ''}}</td>
                    <td>${{s.year || ''}}</td>
                    <td>${{s.duration_str || ''}}</td>
                    <td><span class="source-${{s.source.replace(/\\s+/g, '')}}">${{s.source}}</span></td>
                    <td style="font-family:monospace;font-size:11px;">${{s.shortName || ''}}</td>
                    <td class="instr">${{s.instruments || ''}}</td>
                </tr>
            `).join('');
            document.getElementById('stats').textContent = `Showing ${{f.length}} of ${{SONG_DATA.length}} songs`;
        }}
        
        function sort(c) {{ col = c; asc = !asc; filter(); }}
        
        init();
    </script>
</body>
</html>'''
    
    with open(output_file, 'w') as f:
        f.write(html)
    print(f"Generated: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: generate_html_list.py <metadata_dir> <output.html>")
        sys.exit(1)
    
    generate_html(sys.argv[1], sys.argv[2])