#!/usr/bin/env python3
import re
import json
from pathlib import Path

def parse_rb3_disc_debug(content):
    """Parse with debug output."""
    songs = []
    lines = content.split('\n')
    
    in_track_listing = False
    found_table_start = False
    row_data = {}
    debug_count = 0
    
    for i, line in enumerate(lines[:500]):
        line = line.strip()
        
        # Debug: print first few lines
        if debug_count < 5:
            print(f"Line {i}: {line[:80]}")
            debug_count += 1
        
        if 'Track listing' in line and '##' in line:
            in_track_listing = True
            print(f"  -> Found Track listing, in_track_listing = True")
            continue
            
        if not in_track_listing:
            continue
            
        if line.startswith('## Downloadable') or line.startswith('## Reception'):
            print(f"  -> Found section end")
            break
            
        if 'Song title' in line.lower() or (line.startswith('Song') and 'Artist' in line):
            found_table_start = True
            print(f"  -> Found table start")
            continue
            
        if not found_table_start:
            continue
            
        # Debug: print some candidate lines
        if line.startswith('"') and '](/wiki/' in line:
            title_match = re.search(r'"([^"]+)"', line)
            if title_match:
                print(f"  -> Found song title: {title_match.group(1)}")
    
    return songs

# Run with debugging
files = {
    'rb3': '/home/vscode/.local/share/opencode/tool-output/tool_da9056dc1001cM5MYr3DPu4UoX',
}

with open(files['rb3'], 'r', encoding='utf-8') as f:
    content = f.read()

print("=== PARSING RB3 ===\n")
songs = parse_rb3_disc_debug(content)
print(f"\nTotal songs: {len(songs)}")