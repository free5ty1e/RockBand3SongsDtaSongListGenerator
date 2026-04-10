import glob
import os
import json
import subprocess

def main():
    ark_dirs = ['/workspace/rb4_temp/base_game_extract', '/workspace/rb4_temp/update_extract']
    output_file = '/workspace/RB4/output/all_ark_discoveries.jsonl'
    
    with open(output_file, 'w') as out_f:
        for d in ark_dirs:
            if not os.path.exists(d): continue
            arks = glob.glob(os.path.join(d, '*.ark'))
            print(f"Processing {len(arks)} ARKs in {d}...")
            
            for ark in arks:
                print(f"  Scanning {os.path.basename(ark)}...", end=' ', flush=True)
                try:
                    result = subprocess.run(
                        ['python3', '/workspace/RB4/scripts/research/scan_single_ark_v2.py', ark],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    # The output is JSON lines
                    for line in result.stdout.splitlines():
                        if line.strip():
                            out_f.write(line + '\n')
                    print("Done")
                except subprocess.CalledProcessError as e:
                    print(f"Error scanning {ark}: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")

    print(f"All scans complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
