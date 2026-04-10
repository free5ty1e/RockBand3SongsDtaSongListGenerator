import os
import struct

def extract_strings(data, start_offset, max_len=5000):
    strings = []
    i = start_offset
    while i < start_offset + max_len and i < len(data):
        if i + 4 > len(data):
            break
        
        length = struct.unpack('<I', data[i:i+4])[0]
        if 1 <= length <= 256:
            try:
                s = data[i+4:i+4+length].decode('utf-8')
                strings.append(s)
                i += 4 + length
            except:
                i += 1
        else:
            i += 1
    return strings

def main():
    ark_dir = "/workspace/rb4_temp/base_game_extract"
    all_songs = []
    
    for f in os.listdir(ark_dir):
        if f.endswith('.ark'):
            path = os.path.join(ark_dir, f)
            with open(path, 'rb') as file:
                content = file.read()
                
            pos = content.find(b"RBSongMetadata")
            while pos != -1:
                # Extract strings around this marker
                found_strings = extract_strings(content, pos)
                all_songs.extend(found_strings)
                pos = content.find(b"RBSongMetadata", pos + 1)
    
    # Filter for likely song names (length > 3, contains letters)
    results = set()
    for s in all_songs:
        if len(s) > 3 and any(c.isalpha() for c in s):
            results.add(s)
            
    for r in sorted(results):
        print(r)

if __name__ == '__main__':
    main()
