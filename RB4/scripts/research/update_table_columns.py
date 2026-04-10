import re

def main():
    with open('/workspace/RB4/missing_songs_investigation.md', 'r') as f:
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
            # Current format: | Song ID | Probable Title | Source | Archive | Status |
            # New format: | Song ID | Song Name | Artist | Album | Source | PKG Filename | Location | Status |
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                song_id = parts[0]
                title = parts[1]
                source = parts[2]
                archive = parts[3]
                status = parts[4]
                
                # We don't have Artist/Album/PKG yet, so use '?'
                new_row = f'| {song_id} | {title} | ? | ? | {source} | ? | {archive} | {status} |\n'
                new_lines.append(new_row)
            else:
                new_lines.append(line)
        else:
            if not line.startswith('|'):
                in_table = False
            new_lines.append(line)

    with open('/workspace/RB4/missing_songs_investigation.md', 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    main()
