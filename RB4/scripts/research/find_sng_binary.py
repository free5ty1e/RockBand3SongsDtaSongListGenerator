import os
import struct

def find_sng_files(root_dir):
    sng_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                with open(full_path, 'rb') as f:
                    header = f.read(6)
                    if header == b"SNGPKG":
                        sng_files.append(full_path)
            except:
                continue
    return sng_files

if __name__ == "__main__":
    root = '/workspace/rb4_temp'
    found = find_sng_files(root)
    print(f"Found {len(found)} SNG files:")
    for f in found:
        print(f)
