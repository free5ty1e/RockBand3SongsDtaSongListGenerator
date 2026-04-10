import glob
import os
import re

def scan_ark_for_songs(ark_path):
    found_songs = set()
    try:
        with open(ark_path, 'rb') as f:
            # Read in chunks to avoid memory issues
            chunk_size = 10 * 1024 * 1024
            overlap = 1024 * 10
            offset = 0
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Strategy 1: Look for "short_name" pattern
                # Based on observed: b'short_name\x00([a-zA-Z0-9_]+)\x00'
                matches = re.finditer(b'short_name\x00([a-zA-Z0-9_]+)\x00', chunk)
                for match in matches:
                    found_songs.add(match.group(1).decode('ascii', errors='ignore'))
                
                # Strategy 2: Look for RBSongMetadata and then scan nearby for strings
                # This is a fallback if short_name is not explicitly labeled
                meta_pos = chunk.find(b"RBSongMetadata")
                while meta_pos != -1:
                    # Scan 1KB ahead for potential song names
                    lookahead = chunk[meta_pos:meta_pos + 1024]
                    # Look for strings that look like song identifiers (alphanumeric, underscores, 5-30 chars)
                    # This is riskier and might produce noise
                    potential_names = re.findall(b'[a-zA-Z0-9_]{5,30}', lookahead)
                    for name in potential_names:
                        # Filter out common markers
                        decoded = name.decode('ascii', errors='ignore')
                        if decoded not in ["RBSongMetadata", "short_name", "tempo", "vocal_tonic_note"]:
                            # Only add if it looks like a song ID (usually lowercase with underscores)
                            if decoded.islower() and '_' in decoded:
                                found_songs.add(decoded)
                    
                    meta_pos = chunk.find(b"RBSongMetadata", meta_pos + 1)

                if len(chunk) == chunk_size:
                    f.seek(f.tell() - overlap)
                else:
                    break
    except Exception as e:
        print(f"Error reading {ark_path}: {e}")
    return found_songs

def main():
    all_found_songs = set()
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    
    for d in ark_dirs:
        if not os.path.exists(d):
            continue
        ark_files = glob.glob(os.path.join(d, '*.ark'))
        for ark_path in ark_files:
            print(f"Scanning {ark_path}...")
            songs = scan_ark_for_songs(ark_path)
            if songs:
                print(f"  Found {len(songs)} potential songs")
                all_found_songs.update(songs)

    print(f"Total unique identifiers found: {len(all_found_songs)}")
    
    # Save to a file for analysis
    with open('/workspace/RB4/output/ark_extracted_identifiers.txt', 'w') as f:
        for s in sorted(list(all_found_songs)):
            f.write(f"{s}\n")

if __name__ == "__main__":
    main()
