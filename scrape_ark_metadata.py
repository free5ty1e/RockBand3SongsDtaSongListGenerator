import os
import struct
import re

def scrape_ark(ark_path):
    songs = []
    with open(ark_path, 'rb') as f:
        content = f.read()
        
    # Search for "RBSongMetadata"
    offsets = []
    pos = content.find(b"RBSongMetadata")
    while pos != -1:
        offsets.append(pos)
        pos = content.find(b"RBSongMetadata", pos + 1)
    
    print(f"Found {len(offsets)} RBSongMetadata markers in {ark_path}")
    
    for offset in offsets:
        # Look around the marker for strings
        # We'll look 1024 bytes after the marker
        chunk = content[offset:offset+1024]
        
        # Try to find sequences that look like [length][string]
        # Looking for strings of length 3-100
        for i in range(len(chunk) - 4):
            length = struct.unpack('<I', chunk[i:i+4])[0]
            if 3 <= length <= 100:
                try:
                    s = chunk[i+4:i+4+length].decode('utf-8')
                    if any(keyword in s.lower() for keyword in ['artist', 'title', 'song']):
                        songs.append(s)
                except:
                    pass
    return songs

if __name__ == '__main__':
    ark_dir = "/workspace/rb4_temp/base_game_extract"
    all_found = []
    for f in os.listdir(ark_dir):
        if f.endswith('.ark'):
            all_found.extend(scrape_ark(os.path.join(ark_dir, f)))
    
    print("\nPotential metadata found:")
    for s in sorted(set(all_found)):
        print(s)
