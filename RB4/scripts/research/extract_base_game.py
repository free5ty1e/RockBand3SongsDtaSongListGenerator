import os
import sys
import json
import subprocess
import shutil

def run_cmd(cmd, timeout=3600):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False, result.stdout
    return True, result.stdout

def main():
    pkg_path = "/workspace/rb4_temp/Rock.Band.4_CUSA02084_v1.00_[2.50]_OPOISSO893.pkg"
    temp_dir = "/workspace/rb4_temp"
    work_dir = os.path.join(temp_dir, "base_game_extract")
    pfs_file = os.path.join(work_dir, "inner.pfs")
    pfs_extract_dir = os.path.join(work_dir, "pfs_contents")
    ark_extract_dir = os.path.join(work_dir, "ark_contents")

    if not os.path.exists(pkg_path):
        print(f"PKG not found: {pkg_path}")
        return

    os.makedirs(work_dir, exist_ok=True)

    # Step 1: Extract PKG (using pkg_makegp4 instead of innerpfs)
    if not os.path.exists(os.path.join(work_dir, "main_ps4_0.ark")):
        print("Extracting PKG via pkg_makegp4...")
        success, _ = run_cmd(f'DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 PkgTool.Core pkg_makegp4 --passcode 00000000000000000000000000000000 "{pkg_path}" {work_dir}')
        if not success:
            print("Failed to extract PKG via pkg_makegp4")
            return
    else:
        print("Base game already extracted, skipping...")

    # Now we search for songs in the extracted directory
    # Note: pkg_makegp4 extracts everything, including .songdta_ps4 and .ark files
    pfs_extract_dir = work_dir # The files are extracted directly here

    # Step 3: Find and extract .ark files
    from ark_extract import extract_ark
    ark_files = []
    for root, dirs, files in os.walk(pfs_extract_dir):
        for f in files:
            if f.endswith('.ark'):
                ark_files.append(os.path.join(root, f))
    
    print(f"Found {len(ark_files)} .ark files. Extracting...")
    for ark in ark_files:
        print(f"Extracting {ark}...")
        try:
            extract_ark(ark, ark_extract_dir)
        except Exception as e:
            print(f"Error extracting {ark}: {e}")

    # Step 4: Find all .songdta_ps4 files
    songdta_files = []
    for root, dirs, files in os.walk(ark_extract_dir):
        for f in files:
            if f.endswith('.songdta_ps4'):
                songdta_files.append(os.path.join(root, f))
    
    print(f"Found {len(songdta_files)} .songdta_ps4 files in .ark archives")

    if not songdta_files:
        print("No songs found in .ark files")
        return

    # Step 5: Extract metadata
    temp_output = os.path.join(temp_dir, "base_game_metadata.json")
    files_arg = ' '.join(f'"{f}"' for f in songdta_files)
    print("Parsing binary metadata...")
    success, _ = run_cmd(f'cd /workspace && python3 RB4/scripts/extract_binary_dta.py {files_arg} {temp_output}')
    
    if success:
        print(f"Successfully extracted metadata to {temp_output}")
        with open(temp_output) as f:
            data = json.load(f)
            print(f"Extracted {len(data)} songs from base game!")
    else:
        print("Failed to parse binary metadata")

if __name__ == '__main__':
    main()
