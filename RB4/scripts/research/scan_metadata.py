import glob
import os

ark_files = glob.glob('/workspace/rb4_temp/**/*.ark', recursive=True)
for ark_path in ark_files:
    with open(ark_path, 'rb') as f:
        content = f.read()
        pos = content.find(b"RBSongMetadata")
        while pos != -1:
            # Extract a chunk of data following the marker
            chunk = content[pos:pos+200]
            print(f"{ark_path} at {pos}: {chunk}")
            pos = content.find(b"RBSongMetadata", pos + 1)
