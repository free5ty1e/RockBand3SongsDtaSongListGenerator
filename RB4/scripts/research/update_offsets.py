import os

def main():
    offsets_path = '/workspace/RB4/output/song_offsets.txt'
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    
    offsets = {}
    with open(offsets_path, 'r') as f:
        for line in f:
            if ':' in line:
                sid, off = line.strip().split(':')
                offsets[sid] = off
                
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
                
                # Update PKG Filename (approximate) and Location
                # We know these were in patch_main_ps4_4.ark
                parts[5] = "patch_main_ps4_4.pkg"
                
                offset = offsets.get(song_id, "Unknown")
                parts[6] = f"patch_main_ps4_4.ark @ {offset}"
                
                new_row = '| ' + ' | '.join(parts) + ' |\n'
                new_lines.append(new_row)
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
