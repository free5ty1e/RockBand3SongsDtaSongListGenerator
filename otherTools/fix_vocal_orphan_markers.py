#!/usr/bin/env python3
"""
================================================================================
Script Name: fix_vocal_orphan_markers.py
Description: 
    Automates the cleanup and repair of vocal phrase markers in Clone Hero and 
    Onyx .chart files. It parses the [Events] section, tracks lyric phrasing 
    states, and automatically injects missing 'phrase_start' or 'phrase_end' 
    events to resolve formatting errors (such as Onyx's 'Vocal note is outside 
    any phrases' error).

Backup Behavior:
    - If the chart is well-formed, no changes are made and NO backup is created.
    - If repairs are needed, an exact copy of the original file is saved as 
      '<filename>.chart.bak' immediately before overwriting the original file 
      in place. This leaves your song folder ready for immediate reprocessing.

Usage:
    python fix_vocal_orphan_markers.py <path_to_chart>
================================================================================
"""

import sys
import os
import re
import shutil

def print_help():
    print(__doc__)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"Analyzing chart: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_lines = f.read().splitlines()

    in_events = False
    events_header_idx = -1
    bracket_start_idx = -1
    events_end_idx = -1

    # Safely locate the [Events] block and its structural brackets
    for i, line in enumerate(file_lines):
        stripped = line.strip()
        if not in_events:
            if stripped == '[Events]':
                in_events = True
                events_header_idx = i
        else:
            if bracket_start_idx == -1 and stripped == '{':
                bracket_start_idx = i
            elif stripped == '}':
                events_end_idx = i
                break

    if events_header_idx == -1 or bracket_start_idx == -1 or events_end_idx == -1:
        print("Error: Could not locate a valid [Events] section and bounds in the chart.")
        sys.exit(1)

    # Isolate the interior of the block to protect structural brackets
    pre_events = file_lines[:bracket_start_idx + 1]
    events_block = file_lines[bracket_start_idx + 1:events_end_idx]
    post_events = file_lines[events_end_idx:]

    parsed_events = []
    unparsed_lines = [] # For blank lines or unknown syntax inside the block
    event_regex = re.compile(r'^\s*(\d+)\s*=\s*E\s+"([^"]+)"')

    for line in events_block:
        match = event_regex.match(line)
        if match:
            parsed_events.append({
                'tick': int(match.group(1)),
                'val': match.group(2),
                'original_line': line
            })
        else:
            unparsed_lines.append(line)

    output_events = []
    in_phrase = False
    current_phrase_start = 0
    unphrased_lyrics = []
    repairs = 0

    # State machine to track and repair phrase bounds
    for ev in parsed_events:
        tick = ev['tick']
        val = ev['val']
        is_start = (val == 'phrase_start')
        is_end = (val == 'phrase_end')
        is_lyric = val.startswith('lyric ')

        if is_start:
            if in_phrase:
                # Prevent negative or reversed phrase lengths if bounds collide
                end_tick = max(current_phrase_start, tick - 1)
                print(f"  [Repair] Missing phrase_end before tick {tick}. Inserting at {end_tick}.")
                output_events.append({'tick': end_tick, 'val': 'phrase_end', 'generated': True})
                repairs += 1
            elif len(unphrased_lyrics) > 0:
                start_tick = unphrased_lyrics[0]['tick']
                end_tick = max(start_tick, unphrased_lyrics[-1]['tick'] + 1)
                print(f"  [Repair] Found unphrased lyrics. Wrapping starting at {start_tick}.")
                output_events.append({'tick': start_tick, 'val': 'phrase_start', 'generated': True})
                output_events.append({'tick': end_tick, 'val': 'phrase_end', 'generated': True})
                unphrased_lyrics = []
                repairs += 2
            
            in_phrase = True
            current_phrase_start = tick
            output_events.append(ev)
            
        elif is_end:
            if not in_phrase:
                if len(unphrased_lyrics) > 0:
                    start_tick = unphrased_lyrics[0]['tick']
                    print(f"  [Repair] Orphaned phrase_end at {tick}. Wrapping preceding lyrics starting at {start_tick}.")
                    output_events.append({'tick': start_tick, 'val': 'phrase_start', 'generated': True})
                    output_events.append(ev)
                    unphrased_lyrics = []
                    repairs += 1
                else:
                    print(f"  [Repair] Dropping useless orphaned phrase_end at {tick} with no lyrics.")
                    repairs += 1
            else:
                in_phrase = False
                output_events.append(ev)
                
        elif is_lyric:
            if not in_phrase:
                unphrased_lyrics.append(ev)
            output_events.append(ev)
            
        else:
            output_events.append(ev)

    # Clean up trailing logic at the end of the song block
    if in_phrase:
        last_tick = output_events[-1]['tick'] if output_events else 0
        end_tick = max(current_phrase_start, last_tick + 1)
        print(f"  [Repair] Missing final phrase_end. Inserting at {end_tick}.")
        output_events.append({'tick': end_tick, 'val': 'phrase_end', 'generated': True})
        repairs += 1
    elif len(unphrased_lyrics) > 0:
        start_tick = unphrased_lyrics[0]['tick']
        end_tick = unphrased_lyrics[-1]['tick'] + 1
        print(f"  [Repair] Unphrased lyrics at end. Wrapping between {start_tick} and {end_tick}.")
        output_events.append({'tick': start_tick, 'val': 'phrase_start', 'generated': True})
        output_events.append({'tick': end_tick, 'val': 'phrase_end', 'generated': True})
        repairs += 2

    if repairs == 0:
        print("\nResult: No phrase issues detected. The chart is already well-formed.")
        print("No changes were made, and no backup file was created.")
        sys.exit(0)

    # Sort safely to maintain correct chronological and event-type ordering per tick
    def sort_key(e):
        v = e['val']
        if v == 'phrase_start': return 0
        if v.startswith('lyric '): return 2
        if v == 'phrase_end': return 3
        return 1

    output_events.sort(key=lambda x: (x['tick'], sort_key(x)))

    # Reconstruct the block safely keeping any unparsed text exactly where it was
    new_events_block = []
    # Dump any unparsed lines (like comments) back at the top of the block interior
    for line in unparsed_lines:
        new_events_block.append(line)
        
    for ev in output_events:
        if ev.get('generated'):
            new_events_block.append(f"  {ev['tick']} = E \"{ev['val']}\"")
        else:
            new_events_block.append(ev['original_line'])

    # Create backup only when changes are confirmed, right before writing
    backup_path = file_path + '.bak'
    shutil.copy2(file_path, backup_path)
    print(f"\nBackup created successfully: {backup_path}")

    # Overwrite the original chart in place
    final_content = pre_events + new_events_block + post_events
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_content) + '\n')

    print(f"Success! Applied {repairs} repairs and updated: {file_path}")
    print("The song folder is ready to process again without further file manipulation.")

if __name__ == '__main__':
    main()
    