#!/bin/bash

# List of PKGs to process
PKGS=(
    "UP8802-CUSA02084_00-RBLEGACYDLCPASS3-A0000-V0100.pkg"
    "UP8802-CUSA02084_00-RBLEGACYDLCPASS1-A0000-V0100.pkg"
    "UP8802-CUSA02084_00-RBLEGACYDLCPASS2-A0000-V0100.pkg"
    "UP8802-CUSA02084_00-RB4PRESEASONPASS-A0000-V0100.pkg"
    "UP8802-CUSA02084_00-RB4RBNRERELEASES-A0000-V0100.pkg"
)

for pkg in "${PKGS[@]}"; do
    echo "Starting download of $pkg..."
    smbget -N smb://192.168.100.135/incoming/temp/Rb4Dlc/"$pkg" -o /tmp/"$pkg"
    
    if [ $? -eq 0 ]; then
        echo "Download of $pkg complete. Scanning..."
        
        # 1. Scan for song IDs (existing logic)
        python3 /workspace/RB4/scripts/research/scan_single_dlc_pkg.py "/tmp/$pkg" "$pkg"
        
        # 2. Extract title from header
        title=$(strings "/tmp/$pkg" | grep "Custom Pack" | head -n 1)
        if [ ! -z "$title" ]; then
            echo "Found Title: $title"
            echo "{\"pkg\": \"$pkg\", \"title\": \"$title\"}" >> /workspace/RB4/output/dlc_titles_raw.jsonl
        fi
        
        echo "Scan of $pkg complete."
        rm /tmp/"$pkg"
    else
        echo "Failed to download $pkg"
    fi
done

echo "All large PKGs processed."
