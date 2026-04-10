import subprocess

def main():
    cmd = 'smbclient //192.168.100.135/incoming -N -c "cd temp/Rb4Dlc; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print("Full output:")
    print(result.stdout)
    print("-" * 20)
    
    pkgs = []
    for line in result.stdout.splitlines():
        print(f"Processing line: {repr(line)}")
        line = line.strip()
        if not line:
            continue
        if line.endswith('.pkg') and not line.startswith('._'):
            parts = line.split()
            if parts:
                print(f"Found PKG: {parts[0]}")
                pkgs.append(parts[0])
            else:
                print("No parts found")
        else:
            print("Skipped")
            
    print("-" * 20)
    print(f"Total found: {len(pkgs)}")

if __name__ == "__main__":
    main()
