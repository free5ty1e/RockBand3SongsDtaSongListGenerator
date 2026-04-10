import os
import re

def load_song_list(path):
    song_map = {}
    with open(path, 'r') as f:
        for line in f:
            # Format: Artist (Album) - Title (Year / Duration) - Game
            match = re.match(r'^(.*?) \((.*?)\) - (.*?) \(.*?\)', line)
            if match:
                artist = match.group(1)
                album = match.group(2)
                title = match.group(3)
                
                # Create a normalized version of the title to use as a key
                # e.g., "Caught Up in You" -> "caughtupinyou"
                norm_title = re.sub(r'[^a-z0-9]', '', title.lower())
                song_map[norm_title] = {
                    'artist': artist,
                    'album': album,
                    'title': title
                }
    return song_map

def resolve_songs(investigation_path, song_list_path):
    song_map = load_song_list(song_list_path)
    
    with open(investigation_path, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    in_table = False
    
    for line in lines:
        if line.startswith('| Song ID'):
            new_lines.append(line)
            in_table = True
            continue
        if line.startswith('| :---'):
            new_lines.append(line)
            continue
            
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 8:
                song_id = parts[0].replace('`', '')
                # Handle request_ prefix
                search_id = song_id.replace('request_', '')
                
                if search_id in song_map:
                    data = song_map[search_id]
                    # New format: | Song ID | Song Name | Artist | Album | Source | PKG Filename | Location | Status |
                    # parts[1] is Song Name, parts[2] is Artist, parts[3] is Album
                    
                    # Update values
                    parts[1] = f"`{data['title']}`"
                    parts[2] = f"`{data['artist']}`"
                    parts[3] = f"`{data['album']}`"
                    
                    # Update status to Confirmed if we found it in the official list
                    parts[7] = "Confirmed"
                    
                    new_row = '| ' + ' | '.join(parts) + ' |\n'
                    new_lines.append(new_row)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            if not line.startswith('|'):
                in_table = False
            new_lines.append(line)
            
    with open(investigation_path, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    resolve_songs('/workspace/RB4/missing_songs_investigation.md', '/workspace/RB4/rb4songlistWithRivals.txt')
