#!/usr/bin/env bash
# =============================================================================
# mount_rb4_dlc.sh — Mount RB4 DLC SMB share with graceful fallback
# 
# Custom Configuration:
#   Create a gitignored file at .devcontainer/rb4_dlc_config.sh with:
#     SMB_SHARE="//your-server/your-share"
#     MOUNT_POINT="/your/custom/mount/point"
#   This will be sourced first, allowing custom paths per system.
# =============================================================================

set +e  # Don't exit on error

# Load custom config if it exists (gitignored per .gitignore)
if [ -f "$(dirname "$0")/rb4_dlc_config.sh" ]; then
    source "$(dirname "$0")/rb4_dlc_config.sh"
fi

# Default paths to check (can be overridden via arguments or config file)
SMB_SHARE="${SMB_SHARE:-//incoming/temp/Rb4Dlc}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/rb4dlc}"
SMB_USER="${SMB_USER:-${USERNAME}}"

# Try to create mount point (may fail if doesn't exist)
mkdir -p "$MOUNT_POINT" 2>/dev/null || true

# Check if already mounted
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "✅ RB4 DLC already mounted at $MOUNT_POINT"
    exit 0
fi

# Try to mount SMB share
echo "Attempting to mount SMB share: $SMB_SHARE"

# Try various common mount approaches
if mount -t cifs "$SMB_SHARE" "$MOUNT_POINT" -o guest,vers=3.0 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (guest)"
elif mount -t cifs "$SMB_SHARE" "$MOUNT_POINT" -o guest,vers=2.0 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (guest, vers=2.0)"
elif mount -t smbfs "$SMB_SHARE" "$MOUNT_POINT" -o guest 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (smbfs)"
else
    # Check for local alternatives
    if [ -d "/Volumes/incoming/temp/Rb4Dlc" ]; then
        # macOS: try to bind mount
        mount --bind "/Volumes/incoming/temp/Rb4Dlc" "$MOUNT_POINT" 2>/dev/null && \
            echo "✅ RB4 DLC bound from /Volumes/incoming/temp/Rb4Dlc" || \
            echo "⚠️ Could not bind mount /Volumes/incoming/temp/Rb4Dlc"
    elif [ -d "$HOME/RB4Dlc" ]; then
        mount --bind "$HOME/RB4Dlc" "$MOUNT_POINT" 2>/dev/null && \
            echo "✅ RB4 DLC bound from $HOME/RB4Dlc" || \
            echo "⚠️ Could not bind mount $HOME/RB4Dlc"
    else
        echo "⚠️ RB4 DLC share not available at $SMB_SHARE"
        echo "   Expected locations:"
        echo "     - SMB: $SMB_SHARE"
        echo "     - macOS: /Volumes/incoming/temp/Rb4Dlc"
        echo "     - Local: $HOME/RB4Dlc"
        echo "   You can manually mount with: mount -t cifs $SMB_SHARE $MOUNT_POINT -o guest"
    fi
fi

# Verify mount - only if mount point exists and is not empty
if [ -d "$MOUNT_POINT" ] && [ "$(ls -A "$MOUNT_POINT" 2>/dev/null)" ]; then
    echo "✅ RB4 DLC ready at $MOUNT_POINT"
else
    # Mount point doesn't exist or is empty - that's OK, we fail gracefully
    if [ ! -d "$MOUNT_POINT" ]; then
        echo "⚠️ Mount point $MOUNT_POINT not created (permission issue)"
    else
        echo "⚠️ $MOUNT_POINT is empty - no PKG files found"
    fi
    echo "   You can manually mount your SMB share with:"
    echo "   mount -t cifs //server/share /mnt/rb4dlc -o guest"
    echo "   Or copy PKG files to /workspace/pkgs/"
    # Don't exit with error - this is expected on systems without the share
fi
