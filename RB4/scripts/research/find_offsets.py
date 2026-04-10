import glob
import os
import re
import sys

def find_song_offsets(ark_path, target_ids):
    results = {}
    try:
        with open(ark_path, 'rb') as f:
            chunk_size = 10 * 1024 * 1024
            overlap = 1024 * 10
            offset = 0
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                for song_id in target_ids:
                    target_bytes = song_id.encode('ascii', errors='ignore')
                    pos = chunk.find(target_bytes)
                    while pos != -1:
                        results[song_id] = offset + pos
                        pos = chunk.find(target_bytes, pos + 1)
                
                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                    offset += chunk_size - overlap
                else:
                    break
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 find_offsets.py <ark_path> <id1,id2,...>")
        sys.exit(1)
        
    ark_path = sys.argv[1]
    target_ids = sys.argv[2].split(',')
    
    offsets = find_song_offsets(ark_path, target_ids)
    for sid, off in offsets.items():
        print(f"{sid}:{off}")

if __name__ == "__main__":
    main()
