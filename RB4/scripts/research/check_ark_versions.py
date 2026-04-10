import glob
import struct

ark_files = glob.glob('/workspace/rb4_temp/base_game_extract/*.ark')
for ark_path in ark_files:
    with open(ark_path, 'rb') as f:
        version = struct.unpack('<I', f.read(4))[0]
        print(f"{ark_path}: {version}")
