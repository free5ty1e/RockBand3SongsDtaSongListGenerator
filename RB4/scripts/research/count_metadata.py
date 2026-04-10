import os
import glob

ark_files = glob.glob('/workspace/rb4_temp/base_game_extract/*.ark')
for ark_path in ark_files:
    with open(ark_path, 'rb') as f:
        content = f.read()
        count = content.count(b"RBSongMetadata")
        if count > 0:
            print(f"{ark_path}: {count}")
