#!/usr/bin/env bash
# =============================================================================
# mount_rb4_dlc.sh — Mount RB4 DLC SMB share with graceful fallback
# 
# Custom Configuration:
#   Create a gitignored file at .devcontainer/rb4_dlc_config.sh with:
#     SMB_SERVER="192.168.100.135"
#     SMB_SHARE="incoming/temp/Rb4Dlc"
#     MOUNT_POINT="/mnt/rb4dlc"
#   This will be sourced first, allowing custom paths per system.
# =============================================================================

set +e  # Don't exit on error

# Load custom config if it exists (gitignored per .gitignore)
if [ -f "$(dirname "$0")/rb4_dlc_config.sh" ]; then
    source "$(dirname "$0")/rb4_dlc_config.sh"
fi

# Default paths - now with known working values for this setup
SMB_SERVER="${SMB_SERVER:-192.168.100.135}"
SMB_SHARE="${SMB_SHARE:-incoming/temp/Rb4Dlc}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/rb4dlc}"

# Build the full SMB URL
SMB_URL="//${SMB_SERVER}/${SMB_SHARE}"

# 1. First check if bind mount already worked (from devcontainer.json)
if [ -d "$MOUNT_POINT" ] && [ "$(ls -A "$MOUNT_POINT" 2>/dev/null)" ]; then
    echo "✅ RB4 DLC already mounted at $MOUNT_POINT (via bind mount)"
    exit 0
fi

# 2. Try to create mount point (may fail if doesn't exist)
mkdir -p "$MOUNT_POINT" 2>/dev/null || true

# 3. Check if already mounted via some other means
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "✅ RB4 DLC already mounted at $MOUNT_POINT"
    exit 0
fi

# 4. Try kernel-level SMB mount (requires CAP_SYS_ADMIN)
echo "Attempting to mount SMB share: $SMB_URL"

if mount -t cifs "$SMB_URL" "$MOUNT_POINT" -o guest,vers=3.0 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (cifs, vers=3.0)"
elif mount -t cifs "$SMB_URL" "$MOUNT_POINT" -o guest,vers=2.0 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (cifs, vers=2.0)"
elif mount -t smbfs "$SMB_URL" "$MOUNT_POINT" -o guest 2>/dev/null; then
    echo "✅ RB4 DLC mounted at $MOUNT_POINT (smbfs)"
else
    # 5. Try smbclient as a workaround - can access SMB without kernel mount
    echo "⚠️ Kernel mount failed (no CAP_SYS_ADMIN), trying smbclient access..."
    
    # Verify SMB is accessible via smbclient
    if smbclient "$SMB_URL" -N -c "ls" 2>/dev/null | head -1 | grep -q "blocks"; then
        echo "✅ SMB share accessible via smbclient"
        echo "   Note: Using smbclient-based access (slower but works without kernel mount)"
        echo "   Files available at: smb://${SMB_SERVER}/${SMB_SHARE}"
        
        # Create a marker file to indicate SMB is accessible
        echo "$SMB_URL" > "$MOUNT_POINT/.smb_url"
    else
        # 6. Check for local alternatives
        if [ -d "$HOME/RB4Dlc" ]; then
            mount --bind "$HOME/RB4Dlc" "$MOUNT_POINT" 2>/dev/null && \
                echo "✅ RB4 DLC bound from $HOME/RB4Dlc" || \
                echo "⚠️ Could not bind mount $HOME/RB4Dlc"
        elif [ -d "/workspace/pkgs" ]; then
            echo "⚠️ Using local /workspace/pkgs as fallback"
        else
            echo "⚠️ RB4 DLC share not available"
            echo "   Tried: $SMB_URL"
            echo "   Expected: $HOME/RB4Dlc or /workspace/pkgs"
        fi
    fi
fi

# Verify mount - only if mount point exists and is not empty
if [ -d "$MOUNT_POINT" ] && [ "$(ls -A "$MOUNT_POINT" 2>/dev/null)" ]; then
    echo "✅ RB4 DLC ready at $MOUNT_POINT ($(ls "$MOUNT_POINT"/*.pkg 2>/dev/null | wc -l) PKG files)"
elif [ -f "$MOUNT_POINT/.smb_url" ]; then
    echo "✅ RB4 DLC accessible via smbclient at $SMB_URL"
else
    if [ ! -d "$MOUNT_POINT" ]; then
        echo "⚠️ Mount point $MOUNT_POINT not created (permission issue)"
    else
        echo "⚠️ $MOUNT_POINT is empty - no PKG files found"
    fi
fi
