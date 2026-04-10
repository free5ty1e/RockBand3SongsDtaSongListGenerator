import glob
import os
import re
import sys

def extract_context(ark_path, song_id, window=2048):
    try:
        with open(ark_path, 'rb') as f:
            content = f.read()
            # Search for the song_id as a byte string
            target = song_id.encode('ascii', errors='ignore')
            pos = content.find(target)
            if pos == -1:
                return None
            
            start = max(0, pos - window)
            end = min(len(content), pos + window)
            chunk = content[start:end]
            
            # Extract all printable strings of length 4+
            strings = re.findall(b'[a-zA-Z0-9_\s\.\,\'\-]{4,}', chunk)
            return [s.decode('ascii', errors='ignore').strip() for s in strings]
    except Exception as e:
        print(f"Error extracting context for {song_id} in {ark_path}: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_context.py <ark_path> <song_id>")
        sys.exit(1)
    
    ark_path = sys.argv[1]
    song_id = sys.argv[2]
    
    context = extract_context(ark_path, song_id)
    if context:
        print(f"Context for {song_id} in {ark_path}:")
        for s in context:
            print(f"- {s}")
    else:
        print(f"Could not find {song_id} in {ark_path}")

if __name__ == "__main__":
    main()
