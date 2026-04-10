import os
import subprocess
import re
import json

def get_pkg_list():
    cmd = 'smbclient //192.168.100.135/incoming -N -c "cd temp/Rb4Dlc; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    pkgs = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith('.') or line.startswith('Sharename') or line.startswith('---------'):
            continue
        parts = line.split()
        if not parts: continue
        filename = parts[0]
        if filename.endswith('.pkg') and not filename.startswith('._'):
            pkgs.append(filename)
    return pkgs

def extract_title(pkg_name):
    tmp_path = f"/tmp/{pkg_name}"
    cmd = f'smbget -N smb://192.168.100.135/incoming/temp/Rb4Dlc/{pkg_name} -o {tmp_path}'
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        with open(tmp_path, 'rb') as f:
            # Read first 1MB for titles
            content = f.read(1024 * 1024).decode('ascii', errors='ignore')
            
            # Look for "Custom Pack \"...\""
            match = re.search(r'Custom Pack "([^"]+)"', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error processing {pkg_name}: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    return None

def main():
    pkgs = get_pkg_list()
    print(f"Found {len(pkgs)} PKGs. Extracting titles...")
    
    discoveries = []
    for pkg in pkgs:
        print(f"Processing {pkg}...", end=' ', flush=True)
        title = extract_title(pkg)
        if title:
            print(f"Found: {title}")
            discoveries.append({'pkg': pkg, 'title': title})
        else:
            print("Not found")
            
    output_path = '/workspace/RB4/output/dlc_titles.json'
    with open(output_path, 'w') as f:
        json.dump(discoveries, f, indent=2)
    print(f"Finished. Saved {len(discoveries)} titles to {output_path}")

if __name__ == "__main__":
    main()
