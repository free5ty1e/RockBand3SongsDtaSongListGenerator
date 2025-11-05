#!/usr/bin/env python3
"""
Script to extract commented-out song definitions from songs.dta
and create a clean songs.dta with only active songs.
"""

import os
import sys
import re
from datetime import datetime

def normalize_comment_line(line):
    """Normalize comment lines by removing semicolon prefix and returning content"""
    line = line.strip()
    if line.startswith(';;'):
        return line[2:].strip()
    elif line.startswith(';'):
        return line[1:].strip()
    return line

def is_commented_line(line):
    """Check if a line is commented (starts with ; or ;; )"""
    return line.strip().startswith(';')

def parse_song_metadata(song_lines):
    """Parse song name, artist, and album from commented song lines"""
    song_name = "Unknown"
    artist = "Unknown" 
    album = "Unknown"
    
    # Track if we've already found the main song title
    found_song_title = False
    
    i = 0
    while i < len(song_lines):
        line = song_lines[i].strip()
        if not is_commented_line(line):
            i += 1
            continue
            
        # Remove the comment prefix for parsing (handles both ; and ;;)
        content = normalize_comment_line(line)
        
        # Look for metadata fields that are followed by quoted strings on the next line
        if content == "'name'" and i + 1 < len(song_lines) and not found_song_title:
            next_line = song_lines[i + 1].strip()
            if is_commented_line(next_line) and '"' in next_line:
                # Extract quoted string from next line
                next_content = normalize_comment_line(next_line)
                quote_match = re.search(r'"([^"]*)"', next_content)
                if quote_match:
                    song_name = quote_match.group(1)
                    found_song_title = True  # Don't look for more name fields
        
        elif content == "'artist'" and i + 1 < len(song_lines):
            next_line = song_lines[i + 1].strip()
            if is_commented_line(next_line) and '"' in next_line:
                # Extract quoted string from next line
                next_content = normalize_comment_line(next_line)
                quote_match = re.search(r'"([^"]*)"', next_content)
                if quote_match:
                    artist = quote_match.group(1)
                    
        elif content == "'album_name'" and i + 1 < len(song_lines):
            next_line = song_lines[i + 1].strip()
            if is_commented_line(next_line) and '"' in next_line:
                # Extract quoted string from next line
                next_content = normalize_comment_line(next_line)
                quote_match = re.search(r'"([^"]*)"', next_content)
                if quote_match:
                    album = quote_match.group(1)
        
        i += 1
    
    return song_name, artist, album

def extract_disabled_songs():
    """Extract commented-out song definitions from songs.dta"""
    
    input_file = 'songs.dta'
    output_file = 'songs.dta.tmp'
    disabled_file = 'songs.disabled.dta'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return False
    
    print(f"Processing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    disabled_songs = []
    clean_lines = []
    in_disabled_song = False
    disabled_song_lines = []
    disabled_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n\r')
        
        # Check if we're starting a commented-out song definition
        # Handle multiple formats
        line_stripped = line.strip()
        song_start = False
        song_id = ""
        
        if line_stripped == '; (' or line_stripped == ';; (':
            # Original format: ; ( or ;; ( followed by song ID on next line
            song_start = True
            # Look ahead for song ID
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                song_id_line = normalize_comment_line(next_line)
                if song_id_line.startswith("'") and song_id_line.endswith("'"):
                    song_id = song_id_line.replace("'", "").strip()
        
        elif line_stripped.startswith('; (') and "'" in line_stripped:
            # Single semicolon Cursor format: ; ('song_id' on the same line
            song_start = True
            # Extract song ID from current line
            normalized = normalize_comment_line(line_stripped)
            # Try different extraction methods
            if normalized.startswith("('") and "'" in normalized:
                # Find the content between (' and ')
                start = normalized.find("('") + 2
                end = normalized.find("'", start)
                if end > start:
                    song_id = normalized[start:end]
        
        elif line_stripped.startswith(';; (') and "'" in line_stripped:
            # Double semicolon Cursor format: ;; ('song_id' on the same line
            song_start = True
            # Extract song ID from current line
            normalized = normalize_comment_line(line_stripped)
            # Try different extraction methods
            if normalized.startswith("('") and "'" in normalized:
                # Find the content between (' and ')
                start = normalized.find("('") + 2
                end = normalized.find("'", start)
                if end > start:
                    song_id = normalized[start:end]
        
        elif line_stripped.startswith(';; (') and line_stripped != ';; (' and "'" not in line_stripped:
            # Double semicolon direct format: ;; (song_id (song ID directly after parenthesis)
            song_start = True
            normalized = normalize_comment_line(line_stripped)
            if normalized.startswith('(') and not normalized.startswith("('"):
                # Extract song ID directly after (
                song_id = normalized[1:].strip()  # Remove the opening (
        
        elif line_stripped.startswith('; (') and line_stripped != '; (' and "'" not in line_stripped:
            # Single semicolon direct format: ; (song_id (song ID directly after parenthesis)
            song_start = True
            normalized = normalize_comment_line(line_stripped)
            if normalized.startswith('(') and not normalized.startswith("('"):
                # Extract song ID directly after (
                song_id = normalized[1:].strip()  # Remove the opening (
        
        if song_start and song_id:
            in_disabled_song = True
            disabled_song_lines = [line]  # Start collecting lines
            disabled_count += 1
            i += 1
            continue
        
        if in_disabled_song:
            disabled_song_lines.append(line)
            
            # Check if we're ending a commented-out song definition
            line_stripped = line.strip()
            if line_stripped == '; )' or line_stripped == ';; )':
                # Parse metadata before logging
                song_name, artist, album = parse_song_metadata(disabled_song_lines)
                print(f"Found commented-out song: '{song_name}' by {artist} (Album: {album}) [{song_id}]")
                
                disabled_songs.append(disabled_song_lines)
                in_disabled_song = False
                disabled_song_lines = []
        else:
            clean_lines.append(line)
        
        i += 1
    
    # Write the disabled songs to the file (append if it exists, create if it doesn't)
    if disabled_count > 0:
        print(f"\nWriting {disabled_count} disabled songs to {disabled_file}...")
        
        file_exists = os.path.exists(disabled_file)
        timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        
        with open(disabled_file, 'a', encoding='utf-8') as f:
            if not file_exists:
                # Write header for new file
                f.write("; This file contains song definitions that were commented out\n")
                f.write("; from songs.dta to reduce memory usage on PS3\n")
                f.write(f"; Created: {timestamp}\n")
                f.write(f"; Total disabled songs: {disabled_count}\n\n")
            else:
                # Add separator for appended content
                f.write(f"\n; --- Additional disabled songs added ({disabled_count} songs) - {timestamp} ---\n\n")
            
            for song_lines in disabled_songs:
                for line in song_lines:
                    f.write(line + '\n')
                f.write('\n')  # Add spacing between songs
    else:
        print("No commented-out songs found to extract.")
    
    # Write the clean songs.dta
    print(f"Writing cleaned songs.dta...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in clean_lines:
            f.write(line + '\n')
    
    # Backup original and replace
    backup_file = 'songs.dta.backup'
    if not os.path.exists(backup_file):
        print(f"Creating backup: {backup_file}")
        os.rename(input_file, backup_file)
    else:
        print(f"Backup {backup_file} already exists, not overwriting")
        os.remove(input_file)  # Remove original
    
    os.rename(output_file, input_file)
    
    print("Done!")
    if disabled_count > 0:
        print(f"- {disabled_count} song definitions moved to {disabled_file}")
    print(f"- Original file backed up as {backup_file}")
    
    return True

if __name__ == '__main__':
    success = extract_disabled_songs()
    if not success:
        sys.exit(1)
