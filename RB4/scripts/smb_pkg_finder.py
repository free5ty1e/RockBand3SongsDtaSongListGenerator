#!/usr/bin/env python3
"""
SMB Package Finder - uses smbclient to list/access PKG files without kernel mount
"""
import subprocess
import os
import tempfile
import shutil

SMB_SERVER = os.environ.get('SMB_SERVER', '192.168.100.135')
# Use just "incoming" - we'll cd to temp/Rb4Dlc in the command
SMB_SHARE = os.environ.get('SMB_SHARE', 'incoming')

def list_pkgs():
    """List PKG files from SMB share"""
    # Navigate through incoming -> temp/Rb4Dlc
    cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "cd temp/Rb4Dlc; ls"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    pkgs = []
    for line in result.stdout.split('\n'):
        # Match lines like: "  UP8802-...-V0100.pkg      A 2853699584"
        if 'UP8802-' in line and '.pkg' in line and not line.startswith('  ._'):
            parts = line.split()
            if parts:
                pkgs.append(parts[0])
    
    # If still no PKGs, try the temp/Rb4Dlc path directly
    if not pkgs:
        cmd2 = f'smbclient //{SMB_SERVER}/incoming/temp/Rb4Dlc -N -c "ls"'
        result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        for line in result2.stdout.split('\n'):
            if 'UP8802-' in line and '.pkg' in line and not line.startswith('  ._'):
                parts = line.split()
                if parts:
                    pkgs.append(parts[0])
    
    return pkgs

def get_pkg_file(pkg_name, dest_dir):
    """Copy a single PKG file from SMB share"""
    cmd = f'smbclient //{SMB_SERVER}/{SMB_SHARE} -N -c "cd temp/Rb4Dlc; get {pkg_name} {dest_dir}/{pkg_name}"'
    return subprocess.run(cmd, shell=True).returncode == 0

if __name__ == '__main__':
    print("=== SMB PKG Files ===")
    pkgs = list_pkgs()
    print(f"Found {len(pkgs)} PKG files:")
    for p in pkgs[:10]:
        print(f"  {p}")
    if len(pkgs) > 10:
        print(f"  ... and {len(pkgs) - 10} more")
