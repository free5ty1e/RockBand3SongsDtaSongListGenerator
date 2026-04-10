import glob
import os

ark_files = glob.glob('/workspace/rb4_temp/update_extract/*.ark')
for ark_path in ark_files:
    count = 0
    with open(ark_path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            count += chunk.count(b"RBSongMetadata")
    if count > 0:
        print(f"{ark_path}: {count}")
