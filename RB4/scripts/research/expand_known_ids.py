import re
import json
import os

def slugify(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def get_all_known_ids():
    known = set()
    
    # 1. From JSON
    json_path = '/workspace/RB4/rb4_empty_songs_full.json'
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    if 'short_filename' in item:
                        known.add(item['short_filename'])
            except: pass
            
    # 2. From Rivals text file (slugify the title)
    rivals_path = '/workspace/RB4/rb4songlistWithRivals.txt'
    if os.path.exists(rivals_path):
        with open(rivals_path, 'r') as f:
            for line in f:
                # Line format: Artist (Album) - Title (Year / Length) - Game
                if ' - ' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 2:
                        title_part = parts[1]
                        # Title is before the '(' for year
                        title = title_part.split(' (')[0]
                        known.add(slugify(title))
                        
    return known

def main():
    known = get_all_known_ids()
    print(f"Total known IDs (including slugified): {len(known)}")
    with open('/workspace/RB4/output/expanded_known_ids.txt', 'w') as f:
        for s in sorted(list(known)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
