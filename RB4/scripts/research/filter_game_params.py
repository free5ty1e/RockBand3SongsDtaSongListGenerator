import re

def main():
    investigation_path = '/workspace/RB4/missing_songs_investigation.md'
    
    # Extended list of game parameter patterns
    game_param_patterns = [
        r'^brow_', r'^bump_', r'^cage_', r'^church_', r'^coda_', 
        r'^defaulttex_', r'^drum_kit_', r'^dynamic_drum_', r'^earth_', 
        r'^eat_', r'^energy_', r'^exp_', r'^fave_', r'^gem_', 
        r'^global_', r'^gtrsolo_', r'^guitar_', r'^icon_', 
        r'^if_', r'^improv_', r'^lights_', r'^loaded_song_', r'^manual_', 
        r'^new_', r'^num_', r'^oat_', r'^omparison_', r'^ox_', 
        r'^part\d+_instrument', r'^roar_', r'^roperty_', r'^silhouettes_', 
        r'^single_call', r'^somp_', r'^test_event', r'^though_', 
        r'^told_', r'^vox_', r'^wet_', r'^basis_', r'^band_fail_',
        r'^current_layout'
    ]
    
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
                
                is_param = any(re.search(pattern, song_id) for pattern in game_param_patterns)
                
                if not is_param:
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
