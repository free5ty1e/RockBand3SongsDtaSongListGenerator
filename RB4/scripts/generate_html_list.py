from datetime import datetime
import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(__file__))
from html_themes import THEMES, generate_theme_js
from empty_song_processor import load_empty_songs_baseline, get_songs_with_fallback
from settings_defaults import DEFAULT_HTML_PAGE_TITLE

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

def generate_html(metadata_dir, output_file, page_title=None):
    """Generate HTML file from metadata directory."""
    
    if page_title is None:
        page_title = DEFAULT_HTML_PAGE_TITLE
    
    # Get timezone from /etc/localtime (follows devcontainer's configured timezone)
    try:
        tz_link = os.readlink('/etc/localtime')
        tz = tz_link.replace('/usr/share/zoneinfo/', '')
    except:
        tz = 'America/New_York'  # Default fallback
    
    # Get current timestamp in devcontainer's timezone
    import time
    now = datetime.now()
    try:
        import zoneinfo
        tz_obj = zoneinfo.ZoneInfo(tz)
        last_updated = now.astimezone(tz_obj).strftime('%A, %B %d, %Y at %I:%M %p %Z')
    except:
        last_updated = now.strftime('%A, %B %d, %Y at %I:%M %p')
    
    baseline = load_empty_songs_baseline()
    songs = get_songs_with_fallback(metadata_dir, baseline)
    
    # Also load and merge baseline songs (rb4songlistWithRivals.txt)
    baseline_file = '/workspace/RB4/rb4songlistWithRivals.txt'
    baseline_songs = []
    if os.path.exists(baseline_file):
        import re
        with open(baseline_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r'^(.+?) \(([^)]+)\)\s*-\s*(.+?)\s*\((\d+)', line)
                if m:
                    artist = m.group(1).strip()
                    album = m.group(2).strip()
                    title = m.group(3).strip()
                    year = int(m.group(4))
                    # Check if this song already exists in extracted songs
                    key = f"{artist}|{title}".lower()
                    exists = any(f"{s.get('artist','')}|{s.get('title','')}".lower() == key for s in songs)
                    if not exists:
                        baseline_songs.append({
                            'artist': artist,
                            'title': title,
                            'album': album,
                            'year': year,
                            'durationMs': 0,
                            'duration_str': '',
                            'source': 'Rock Band 4',  # Match JS logic for baseline detection
                            'shortName': '',
                            'instruments': '🎸🎸🥁🎤 guitar, bass, drums, vocals',
                            'inferred': '',
                            'from_baseline': True
                        })
    
    # Combine extracted songs + baseline-only songs
    all_songs = songs + baseline_songs
    print(f"Extracted: {len(songs)} songs + Baseline-only: {len(baseline_songs)} = {len(all_songs)} total")
    
    js_songs = []
    for s in all_songs:
        duration_sec = s.get("durationMs", 0) // 1000 if s.get("durationMs") else 0
        duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}" if duration_sec else ""
        
        # Handle baseline songs (from_baseline flag)
        if s.get('from_baseline'):
            instruments_display = "🎸🎸🥁🎤 guitar, bass, drums, vocals"  # emoji + text for filter
        else:
            inst_list = s.get("instrumentList", []) or []
            vocal_parts = s.get("vocalParts", 0)
            if vocal_parts > 1:
                inst_list.append("harmony_1")
            if vocal_parts > 2:
                inst_list.append("harmony_2")
            instruments_text = ", ".join(inst_list) if inst_list else ""
            instruments_icons = ""
            for inst in ['real_guitar', 'real_bass', 'guitar', 'bass', 'drums', 'real_keys', 'keys', 'vocals']:
                if inst in instruments_text.lower():
                    instruments_icons += INSTRUMENT_ICONS.get(inst, '🎵')
            instruments_display = instruments_icons + instruments_text
        
        short_name = s.get("shortName", "")
        debug_file = s.get("_debug_file", "")
        if not short_name and debug_file:
            short_name = debug_file.replace(".songdta_ps4", "")
        
        infer = "✓" if s.get("inferred") else ""
        
        # Normalize year - fix invalid years (greater than current year)
        year = s.get("year", 0) or 0
        current_year = datetime.now().year
        if year > current_year:
            year = current_year
        
        js_songs.append({
            "artist": s.get("artist", ""),
            "title": s.get("title", ""),
            "album": s.get("album", ""),
            "year": year,
            "duration": duration_sec,
            "duration_str": duration_str,
            "source": s.get("source", ""),
            "shortName": short_name,
            "instruments": instruments_display,
            "inferred": infer
        })
    
    js_data = json.dumps(js_songs)
    themes_js = generate_theme_js()
    t = THEMES["dark_blue"]
    
    # Build JS as a regular string to avoid f-string issues
    js_code = '''
        const SONG_DATA = ''' + js_data + ''';
        let col = 0, asc = true; // Default sort: artist (column 0), ascending
        
        function setTheme(themeName) {
            const t = THEMES[themeName];
            document.body.style.background = t.body_bg;
            document.body.style.color = t.text;
            document.querySelectorAll('.controls')[0].style.background = t.panel_bg;
            document.querySelectorAll('table')[0].style.background = t.panel_bg;
            document.querySelectorAll('th').forEach(el => {
                el.style.background = t.header_bg;
                el.style.color = t.accent;
            });
            document.querySelectorAll('tr:nth-child(even)').forEach(el => el.style.background = t.body_bg);
            document.querySelectorAll('tr:hover').forEach(el => el.style.background = t.hover);
            document.querySelectorAll('input, select').forEach(el => el.style.background = t.input_bg);
            document.querySelectorAll('h1')[0].style.color = t.accent;
        }
        
        function init() {
            const srcs = [...new Set(SONG_DATA.map(s => s.source))].sort();
            document.getElementById('source').innerHTML = '<option value="">All</option>' + 
                srcs.map(s => `<option value="${s}">${s}</option>`).join('');
            document.getElementById('totalCount').textContent = `${SONG_DATA.length} total`;
            document.getElementById('filteredCount').textContent = '';
            // Calculate default ranges from data
            const years = SONG_DATA.map(s => s.year).filter(y => y);
            const durs = SONG_DATA.map(s => s.duration).filter(d => d);
            const minYear = Math.min(...years), maxYear = Math.max(...years);
            const minDur = Math.min(...durs), maxDur = Math.max(...durs);
            document.getElementById('yearFrom').value = minYear;
            document.getElementById('yearTo').value = maxYear;
            document.getElementById('durMin').value = minDur;
            document.getElementById('durMax').value = maxDur;
            document.getElementById('yearFrom').placeholder = minYear;
            document.getElementById('yearTo').placeholder = maxYear;
            document.getElementById('durMin').placeholder = minDur;
            document.getElementById('durMax').placeholder = maxDur;
            const instruments = ['guitar', 'bass', 'drums', 'vocals', 'keys', 'real_guitar', 'real_bass', 'real_keys', 'harmony_1', 'harmony_2'];
            const instIcons = {'guitar': '🎸', 'bass': '🎸', 'drums': '🥁', 'vocals': '🎤', 'keys': '🎹', 'real_guitar': '🎸', 'real_bass': '🎸', 'real_keys': '🎹', 'harmony_1': '🎤', 'harmony_2': '🎤'};
            document.getElementById('instFilter').innerHTML = instruments.map(i => 
                `<label style="margin-right:8px"><input type="checkbox" value="${i}" checked onchange="filter()">${instIcons[i] || ''} ${i}</label>`
            ).join('');
            // Store default ranges
            window.DEFAULT_MIN_YEAR = minYear;
            window.DEFAULT_MAX_YEAR = maxYear;
            window.DEFAULT_MIN_DUR = minDur;
            window.DEFAULT_MAX_DUR = maxDur;
            filter();
        }
        
        function filter() {
            const search = document.getElementById('search').value.toLowerCase();
            const yf = document.getElementById('yearFrom').value;
            const yt = document.getElementById('yearTo').value;
            const df = document.getElementById('durMin').value;
            const dt = document.getElementById('durMax').value;
            const yearFrom = yf ? parseInt(yf) : window.DEFAULT_MIN_YEAR || 0;
            const yearTo = yt ? parseInt(yt) : window.DEFAULT_MAX_YEAR || 9999;
            const durMin = df ? parseInt(df) : window.DEFAULT_MIN_DUR || 0;
            const durMax = dt ? parseInt(dt) : window.DEFAULT_MAX_DUR || 99999;
            const src = document.getElementById('source').value;
            const checkedInsts = [...document.querySelectorAll('#instFilter input:checked')].map(i => i.value);
            
            let f = SONG_DATA.filter(s => {
                if (search && !s.artist.toLowerCase().includes(search) && !s.title.toLowerCase().includes(search) && !s.album.toLowerCase().includes(search) && !s.shortName.toLowerCase().includes(search)) return false;
                if (s.year && (s.year < yearFrom || s.year > yearTo)) return false;
                if (s.duration && (s.duration < durMin || s.duration > durMax)) return false;
                if (src && s.source !== src) return false;
                if (checkedInsts.length > 0 && s.instruments) {
                    const instLower = s.instruments.toLowerCase();
                    if (!checkedInsts.some(i => instLower.includes(i))) return false;
                }
                return true;
            });
            const cols = ['artist', 'title', 'album', 'year', 'duration', 'source', 'instruments', 'shortName', 'inferred'];
            f.sort((a, b) => {
                const va = a[cols[col]], vb = b[cols[col]];
                if (typeof va === 'number') return asc ? va - vb : vb - va;
                if (va === undefined || va === '') return asc ? 1 : -1;
                if (vb === undefined || vb === '') return asc ? -1 : 1;
                const av = String(va).toLowerCase(), bv = String(vb).toLowerCase();
                return asc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
            });
            document.getElementById('body').innerHTML = f.map(s => `
                <tr>
                    <td>${s.artist}</td>
                    <td>${s.title}</td>
                    <td>${s.album || ''}</td>
                    <td>${s.year || ''}</td>
                    <td>${s.duration_str || ''}</td>
                    <td><span class="source-${s.source.replace(/\s+/g, '')}">${s.source}</span></td>
                    <td class="instr">${s.instruments || ''}</td>
                    <td style="font-family:monospace;font-size:11px;">${s.shortName || ''}</td>
                    <td class="inferred">${s.inferred || ''}</td>
                </tr>
            `).join('');
            document.getElementById('filteredCount').textContent = f.length !== SONG_DATA.length ? ` (filters: ${f.length})` : '';
            document.getElementById('stats').textContent = `Showing ${f.length} of ${SONG_DATA.length} songs`;
        }
        
        function sort(c) { col = c; asc = !asc; filter(); }
        
        function resetFilters() {
            document.getElementById('search').value = '';
            document.getElementById('yearFrom').value = '';
            document.getElementById('yearTo').value = '';
            document.getElementById('durMin').value = '';
            document.getElementById('durMax').value = '';
            document.getElementById('source').value = '';
            document.querySelectorAll('#instFilter input').forEach(i => i.checked = true);
            filter();
        }
        
        init();
    '''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: {t['body_bg']}; color: {t['text']}; }}
        h1 {{ color: {t['accent']}; margin-bottom: 10px; }}
        .controls {{ display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; padding: 15px; background: {t['panel_bg']}; border-radius: 8px; }}
        .control-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .control-group label {{ font-size: 12px; color: #888; }}
        input, select {{ padding: 8px 12px; border-radius: 4px; border: 1px solid #333; background: {t['input_bg']}; color: {t['text']}; font-size: 14px; }}
        button {{ padding: 8px 12px; border-radius: 4px; border: 1px solid #333; background: {t['input_bg']}; color: {t['text']}; font-size: 14px; cursor: pointer; }}
        button:hover {{ background: {t['header_bg']}; }}
        table {{ width: 100%; border-collapse: collapse; background: {t['panel_bg']}; border-radius: 8px; }}
        th, td {{ padding: 10px 12px; text-align: left; font-size: 13px; }}
        th {{ background: {t['header_bg']}; color: {t['accent']}; cursor: pointer; position: sticky; top: 0; white-space: nowrap; }}
        tr:nth-child(even) {{ background: {t['body_bg']}; }}
        tr:hover {{ background: {t['hover']}; }}
        .source-RB4 {{ background: {t['accent']}; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-Rivals {{ background: #ff6b6b; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-custom {{ background: #feca57; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .source-dlc, .source-DLC {{ background: #48dbfb; color: #000; padding: 2px 6px; border-radius: 8px; font-size: 10px; }}
        .instr {{ font-size: 14px; white-space: nowrap; }}
        .inferred {{ color: #4ade80; font-weight: bold; }}
        .stats {{ margin-top: 15px; color: #888; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>{page_title} <span id="totalCount" style="font-size:16px;color:#888"></span> <span id="filteredCount" style="font-size:14px;color:#48dbfb"></span></h1>
    <p style="color:#888;font-size:12px;margin-top:0;">Last updated: {last_updated}</p>
    <p style="color:#666;font-size:13px;margin-top:0;">💡 Click on any column header to sort by that column</p>
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
            <input type="number" id="yearFrom" onchange="filter()">
        </div>
        <div class="control-group">
            <label>📅 Year To</label>
            <input type="number" id="yearTo" onchange="filter()">
        </div>
        <div class="control-group">
            <label>⏱️ Min Duration (sec)</label>
            <input type="number" id="durMin" onchange="filter()">
        </div>
        <div class="control-group">
            <label>⏱️ Max Duration (sec)</label>
            <input type="number" id="durMax" onchange="filter()">
        </div>
        <div class="control-group">
            <label>💿 Source</label>
            <select id="source" onchange="filter()"><option value="">All</option></select>
        </div>
        <div class="control-group">
            <label>🎸 Instruments</label>
            <div id="instFilter" style="font-size:12px;display:flex;gap:8px;flex-wrap:wrap;"></div>
        </div>
        <div class="control-group">
            <label>&nbsp;</label>
            <button onclick="resetFilters()">Reset Filters</button>
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
                <th onclick="sort(6)">Instruments ⬍</th>
                <th onclick="sort(7)">ShortName ⬍</th>
                <th onclick="sort(8)">Inferred* ⬍</th>
            </tr>
        </thead>
        <tbody id="body"></tbody>
    </table>
    <div class="stats" id="stats"></div>
    <div style="margin-top:10px;font-size:12px;color:#666;">
        * Inferred: Song metadata was empty/unparseable - recovered from baseline using short filename
    </div>
    <script>
        {themes_js}
        {js_code}
    </script>
</body>
</html>'''
    
    with open(output_file, 'w') as f:
        f.write(html)
    print(f"Generated: {output_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate HTML song list')
    parser.add_argument('metadata_dir', help='Directory with metadata JSON files')
    parser.add_argument('output_html', help='Output HTML file')
    parser.add_argument('--title', default=None, help='HTML page title')
    args = parser.parse_args()
    
    # Load config for custom title
    config_path = '/workspace/.devcontainer/rb4_dlc_config.sh'
    title = args.title
    if not title and os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                if line.startswith('HTML_PAGE_TITLE='):
                    title = line.split('=', 1)[1].strip().strip('"')
                    break
    
    generate_html(args.metadata_dir, args.output_html, title)