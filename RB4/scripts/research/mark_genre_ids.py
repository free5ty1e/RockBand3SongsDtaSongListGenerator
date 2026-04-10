import re

def main():
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    
    markers = {
        'request_60s': '60s Genre Marker',
        'request_70s': '70s Genre Marker',
        'request_80s': '80s Genre Marker',
        'request_90s': '90s Genre Marker',
        'request_alternative': 'Alternative Genre Marker',
        'request_classic': 'Classic Genre Marker',
        'request_country': 'Country Genre Marker',
        'request_current': 'Current Request Marker',
        'request_grunge': 'Grunge Genre Marker',
        'request_newwave': 'New Wave Genre Marker',
        'request_pop': 'Pop Genre Marker',
        'request_punk': 'Punk Genre Marker',
        'request_rnd_float': 'Random Request Marker',
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
                
                if song_id in markers:
                    parts[1] = f"`{markers[song_id]}`"
                    parts[2] = "N/A"
                    parts[3] = "N/A"
                    parts[7] = "Confirmed (Marker)"
                    
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
