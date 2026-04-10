import glob
import os
import json
import subprocess

def main():
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    output_file = '/workspace/RB4/output/all_ark_discoveries.jsonl'
    progress_file = '/workspace/RB4/output/scan_progress.txt'
    
    # Load progress
    processed_arks = set()
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as pf:
            processed_arks = set(line.strip() for line in pf)
    
    # Gather all ARKs
    all_arks = []
    for d in ark_dirs:
        if os.path.exists(d):
            all_arks.extend(glob.glob(os.path.join(d, '*.ark')))
    
    print(f"Total ARKs to scan: {len(all_arks)}")
    
    with open(output_file, 'a') as out_f, open(progress_file, 'a') as pf:
        for ark in all_arks:
            if ark in processed_arks:
                continue
                
            print(f"Scanning {ark}...", end=' ', flush=True)
            try:
                result = subprocess.run(
                    ['python3', '/workspace/RB4/scripts/research/scan_single_ark_v2.py', ark],
                    capture_output=True,
                    text=True,
                    check=True
                )
                for line in result.stdout.splitlines():
                    if line.strip():
                        out_f.write(line + '\n')
                
                pf.write(ark + '\n')
                print("Done")
            except Exception as e:
                print(f"Error: {e}")
                
    print("Batch scan complete.")

if __name__ == "__main__":
    main()
