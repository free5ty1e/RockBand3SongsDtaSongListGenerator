import glob
import os
import re

def main():
    all_strings = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d): continue
        arks = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in arks:
            print(f"Scanning {os.path.basename(ark_path)}...", end='\r')
            try:
                with open(ark_path, 'rb') as f:
                    content = f.read()
                    # Find all ASCII strings 5-30 chars long
                    matches = re.findall(b'[a-zA-Z0-9_]{5,30}', content)
                    for m in matches:
                        all_strings.add(m.decode('ascii', errors='ignore'))
            except: pass
            
    with open('/workspace/RB4/output/all_ark_strings.txt', 'w') as f:
        for s in sorted(list(all_strings)):
            f.write(f"{s}\n")
    print(f"\nExtracted {len(all_strings)} unique strings")

if __name__ == "__main__":
    main()
