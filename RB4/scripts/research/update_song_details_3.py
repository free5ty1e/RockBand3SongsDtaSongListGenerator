import re

def main():
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    
    updates = {
        'request_impressionthatiget': {
            'name': 'The Impression That I Get',
            'artist': 'The Mighty Mighty Bosstones',
            'album': 'Let\'s Face It',
            'status': 'Confirmed'
        },
        'request_metropolis': {
            'name': 'Metropolis Part 1: The Miracle And The Sleeper',
            'artist': 'Dream Theater',
            'album': 'Images and Words',
            'status': 'Confirmed'
        }
    }
    
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
                
                if song_id in updates:
                    upd = updates[song_id]
                    parts[1] = f"`{upd['name']}`"
                    parts[2] = f"`{upd['artist']}`"
                    parts[3] = f"`{upd['album']}`"
                    parts[7] = upd['status']
                    
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
    main()
