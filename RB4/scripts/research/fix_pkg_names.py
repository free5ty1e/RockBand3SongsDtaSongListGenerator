import os

def main():
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    
    # Mapping of ARK/Location to Outer PKG
    # Based on folder names in /workspace/rb4_temp/
    # base_game_extract -> Rock.Band.4_CUSA02084_v1.00_[2.50]_OPOISSO893.pkg
    # update_extract -> Rock.Band.4_CUSA02084_v2.21_[5.05]_OPOISSO893.pkg
    
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
                # Update PKG Filename (Column 6 - index 5)
                # Check the Location column (Column 7 - index 6) to determine source
                location = parts[6]
                
                if 'patch_main' in location or 'update' in location:
                    parts[5] = "Rock.Band.4_CUSA02084_v2.21_[5.05]_OPOISSO893.pkg"
                elif 'main_ps4' in location or 'base' in location:
                    parts[5] = "Rock.Band.4_CUSA02084_v1.00_[2.50]_OPOISSO893.pkg"
                
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
