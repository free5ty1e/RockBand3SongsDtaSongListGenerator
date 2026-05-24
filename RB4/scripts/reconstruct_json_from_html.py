#!/usr/bin/env python3
import re
import json
import os
import argparse

def reconstruct_json(html_path, output_json):
    print(f"Reading HTML from: {html_path}")
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract SONG_DATA array
    match = re.search(r'const SONG_DATA = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print('Error: Could not find SONG_DATA in HTML')
        return False

    songs = json.loads(match.group(1))
    print(f"Found {len(songs)} songs in HTML")

    # Normalize and add dateAdded
    processed_songs = []
    for s in songs:
        # Map HTML data back to the expected format of rb4_custom_songs.json
        entry = {
            'artist': s.get('artist', ''),
            'title': s.get('title', ''),
            'album': s.get('album', ''),
            'year': s.get('year', 0),
            'durationMs': s.get('duration', 0) * 1000,
            'source': s.get('source', ''),
            'shortName': s.get('shortName', ''),
            'instruments': s.get('instruments', ''),
            'inferred': s.get('inferred', ''),
            'pkg': s.get('pkg', ''),
            'dateAdded': '2026.04.18' # Baseline date
        }
        processed_songs.append(entry)

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(processed_songs, f, indent=2)

    print(f"Successfully wrote {len(processed_songs)} songs to {output_json}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reconstruct rb4_custom_songs.json from RB4SongList.html')
    parser.add_argument('--html', default='/workspace/docs/RB4SongList.html', help='Path to the HTML song list')
    parser.add_argument('--json', default='/workspace/docs/songlistdata/rb4_custom_songs.json', help='Path to the output JSON file')
    args = parser.parse_args()
    
    if reconstruct_json(args.html, args.json):
        print("Done!")
    else:
        exit(1)
