#!/usr/bin/env python3
"""
SMB Package Finder - uses smbclient to list/access PKG files without kernel mount

Reads config from .devcontainer/rb4_dlc_config.sh if available
"""
import subprocess
import os
import tempfile
import shutil

# Load config from rb4_dlc_config.sh if it exists
SMB_SERVER = os.environ.get('SMB_SERVER', '192.168.100.135')
SMB_SHARE = os.environ.get('SMB_SHARE', 'incoming/temp/Rb4Dlc')

# Try to read from config file
config_path = '/workspace/.devcontainer/rb4_dlc_config.sh'
if os.path.exists(config_path):
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('SMB_SERVER='):
                SMB_SERVER = line.split('=')[1].strip('"')
            elif line.startswith('SMB_SHARE='):
                SMB_SHARE = line.split('=')[1].strip('"')

def list_pkgs():
    """List PKG files from SMB share"""
    # Parse SMB_SHARE - could be just "incoming" or "incoming/temp/Rb4Dlc"
    share_parts = SMB_SHARE.split('/')
    base_share = share_parts[0]  # e.g., "incoming"
    sub_path = '/'.join(share_parts[1:]) if len(share_parts) > 1 else ''  # e.g., "temp/Rb4Dlc"
    
    if sub_path:
        cmd = f'smbclient //{SMB_SERVER}/{base_share} -N -c "cd {sub_path}; ls"'
    else:
        cmd = f'smbclient //{SMB_SERVER}/{base_share} -N -c "ls"'
    
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
    # Parse SMB_SHARE - could be just "incoming" or "incoming/temp/Rb4Dlc"
    share_parts = SMB_SHARE.split('/')
    base_share = share_parts[0]  # e.g., "incoming"
    sub_path = '/'.join(share_parts[1:]) if len(share_parts) > 1 else ''  # e.g., "temp/Rb4Dlc"
    
    if sub_path:
        cmd = f'smbclient //{SMB_SERVER}/{base_share} -N -c "cd {sub_path}; get {pkg_name} {dest_dir}/{pkg_name}"'
    else:
        cmd = f'smbclient //{SMB_SERVER}/{base_share} -N -c "get {pkg_name} {dest_dir}/{pkg_name}"'
    
    return subprocess.run(cmd, shell=True).returncode == 0

if __name__ == '__main__':
    print("=== SMB PKG Files ===")
    pkgs = list_pkgs()
    print(f"Found {len(pkgs)} PKG files:")
    for p in pkgs[:10]:
        print(f"  {p}")
    if len(pkgs) > 10:
        print(f"  ... and {len(pkgs) - 10} more")
