#!/usr/bin/env python3
"""
================================================================================
Script Name: fix_vocal_phrase_overlap.py
Description: 
    Automates the repair of vocal phrase overlaps and short phrases in Clone Hero 
    and Onyx .chart files. This resolves errors thrown by Magma/Onyx compilers, 
    specifically:
    "ERROR: MIDI Compiler: (PART VOCALS): Confused by vocal phrase overlap..."

    The error occurs when vocal phrases are shorter than a quarter note 
    (1 Resolution) or when they physically overlap each other in ticks.
    
    This script parses both [Events] (for 'phrase_start' and 'phrase_end') and 
    [PART VOCALS] (for 'N 105' and 'N 106' phrase markers). It ensures every 
    phrase meets the minimum length requirement (based on the chart's Resolution) 
    and seamlessly merges any phrases that end up overlapping.

Backup Behavior:
    - If no short or overlapping phrases are found, NO changes are made and NO 
      backup is created.
    - If repairs are needed, an exact copy of the original file is saved as 
      '<filename>.chart.bak' immediately before overwriting the original file 
      in place. This leaves your song folder ready for immediate reprocessing.

Usage:
    python fix_vocal_phrase_overlap.py <path_to_chart>

Note: 
    It is recommended to run 'fix_vocal_orphan_markers.py' before this script 
    to ensure all phrase brackets are properly paired first!
================================================================================
"""

import sys
import os
import re
import shutil

def print_help():
    print(__doc__)

def extract_tick(line):
    # Extracts the leading tick integer from a standard chart event line
    m = re.match(r'^\s*(\d+)\s*=', line)
    return int(m.group(1)) if m else -1

def process_block(block_name, lines, resolution):
    repairs_made = 0
    unparsed_lines = []
    events = []
    
    if block_name == '[Events]':
        phrase_events = []
        # Separate phrase bounds from standard events (lyrics, sections, etc.)
        for line in lines:
            m = re.match(r'^\s*(\d+)\s*=\s*E\s+"([^"]+)"', line)
            if m:
                tick, val = int(m.group(1)), m.group(2)
                if val in ('phrase_start', 'phrase_end'):
                    phrase_events.append({'tick': tick, 'val': val})
                else:
                    events.append({'tick': tick, 'line': line})
            else:
                if re.match(r'^\s*(\d+)\s*=', line):
                    events.append({'tick': extract_tick(line), 'line': line})
                else:
                    unparsed_lines.append(line)
        
        # Pair up phrase events based on chronological starts and ends
        phrases = []
        curr_start = -1
        for ev in phrase_events:
            if ev['val'] == 'phrase_start':
                curr_start = ev['tick']
            elif ev['val'] == 'phrase_end':
                if curr_start != -1:
                    phrases.append({'start': curr_start, 'end': ev['tick']})
                    curr_start = -1
                    
        # State machine to enforce minimum lengths and merge physical overlaps
        new_phrases = []
        for p in phrases:
            start = p['start']
            end = max(p['end'], start + resolution)
            
            if p['end'] < start + resolution:
                repairs_made += 1
                
            if new_phrases and new_phrases[-1]['end'] >= start:
                new_phrases[-1]['end'] = max(new_phrases[-1]['end'], end)
                repairs_made += 1
            else:
                new_phrases.append({'start': start, 'end': end})
                
        if repairs_made == 0:
            return lines, 0
            
        # Reconstruct the repaired phrase boundaries
        for p in new_phrases:
            events.append({'tick': p['start'], 'line': f"  {p['start']} = E \"phrase_start\"", 'type': 'start'})
            events.append({'tick': p['end'], 'line': f"  {p['end']} = E \"phrase_end\"", 'type': 'end'})
            
        # Sort securely: Phrase Start -> Lyrics/Other -> Phrase End
        def sort_events(e):
            t = e.get('type', '')
            if t == 'start': return 0
            if 'lyric ' in e['line']: return 2
            if t == 'end': return 3
            return 1
            
        events.sort(key=lambda x: (x['tick'], sort_events(x)))
        new_lines = unparsed_lines + [e['line'] for e in events]
        return new_lines, repairs_made

    elif block_name == '[PART VOCALS]':
        notes_105 = [] # Standard vocal phrase markers
        notes_106 = [] # Star power vocal phrase markers
        
        for line in lines:
            m = re.match(r'^\s*(\d+)\s*=\s*N\s+(\d+)\s+(\d+)', line)
            if m:
                tick, pitch, length = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if pitch == 105:
                    notes_105.append({'start': tick, 'end': tick + length})
                elif pitch == 106:
                    notes_106.append({'start': tick, 'end': tick + length})
                else:
                    events.append({'tick': tick, 'line': line})
            else:
                if re.match(r'^\s*(\d+)\s*=', line):
                    events.append({'tick': extract_tick(line), 'line': line})
                else:
                    unparsed_lines.append(line)
                    
        def merge_notes(notes, pitch):
            nonlocal repairs_made
            new_notes = []
            for p in sorted(notes, key=lambda x: x['start']):
                start = p['start']
                end = max(p['end'], start + resolution)
                if p['end'] < start + resolution:
                    repairs_made += 1
                if new_notes and new_notes[-1]['end'] >= start:
                    new_notes[-1]['end'] = max(new_notes[-1]['end'], end)
                    repairs_made += 1
                else:
                    new_notes.append({'start': start, 'end': end})
                    
            for p in new_notes:
                events.append({'tick': p['start'], 'line': f"  {p['start']} = N {pitch} {p['end'] - p['start']}"})
                
        merge_notes(notes_105, 105)
        merge_notes(notes_106, 106)
        
        if repairs_made == 0:
            return lines, 0
            
        events.sort(key=lambda x: x['tick'])
        new_lines = unparsed_lines + [e['line'] for e in events]
        return new_lines, repairs_made
        
    return lines, 0

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"Analyzing chart for phrase overlaps: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_lines = f.read().splitlines()

    # Locate dynamic resolution (1 quarter note duration)
    resolution = 192 
    for line in file_lines:
        m = re.match(r'^\s*Resolution\s*=\s*(\d+)', line)
        if m:
            resolution = int(m.group(1))
            break
    print(f"  Detected Chart Resolution: {resolution} ticks per quarter note.")

    # Pass 1: Lossless structure parsing 
    parsed_file = []
    i = 0
    while i < len(file_lines):
        line = file_lines[i]
        m = re.match(r'^\s*\[(.+)\]\s*$', line)
        if m:
            block_name = f"[{m.group(1)}]"
            header = [line]
            i += 1
            while i < len(file_lines) and file_lines[i].strip() != '{':
                header.append(file_lines[i])
                i += 1
            
            if i < len(file_lines) and file_lines[i].strip() == '{':
                header.append(file_lines[i])
                i += 1
                
                block_lines = []
                while i < len(file_lines) and file_lines[i].strip() != '}':
                    block_lines.append(file_lines[i])
                    i += 1
                    
                footer = []
                if i < len(file_lines) and file_lines[i].strip() == '}':
                    footer.append(file_lines[i])
                    
                parsed_file.append({
                    'type': 'block',
                    'name': block_name,
                    'header': header,
                    'lines': block_lines,
                    'footer': footer
                })
            else:
                parsed_file.append({'type': 'raw', 'lines': header})
                continue
        else:
            parsed_file.append({'type': 'raw', 'lines': [line]})
        i += 1

    # Pass 2: Inspect and fix relevant blocks
    total_repairs = 0
    for section in parsed_file:
        if section['type'] == 'block' and section['name'] in ('[Events]', '[PART VOCALS]'):
            new_lines, repairs = process_block(section['name'], section['lines'], resolution)
            if repairs > 0:
                print(f"  [Repair] Fixed {repairs} phrase issues in {section['name']}.")
            section['lines'] = new_lines
            total_repairs += repairs

    if total_repairs == 0:
        print("\nResult: No short or overlapping phrases detected.")
        print("No changes were made, and no backup file was created.")
        sys.exit(0)

    # Pass 3: Create backup and commit changes
    backup_path = file_path + '.bak'
    shutil.copy2(file_path, backup_path)
    print(f"\nBackup created successfully: {backup_path}")

    final_content = []
    for section in parsed_file:
        if section['type'] == 'block':
            final_content.extend(section['header'])
            final_content.extend(section['lines'])
            final_content.extend(section['footer'])
        else:
            final_content.extend(section['lines'])

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content) + '\n')

    print(f"Success! Applied {total_repairs} phrase extensions/merges and updated: {file_path}")
    print("The song folder is ready to process again in Onyx.")

if __name__ == '__main__':
    main()
    