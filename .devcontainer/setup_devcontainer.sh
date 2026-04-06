#!/usr/bin/env bash
# =============================================================================
# setup_devcontainer.sh — Runs on container creation
# =============================================================================

set +e

echo "=========================================="
echo "🚀 Dev Container Setup"
echo "=========================================="

# 1. Show environment info
echo ""
echo "📋 Environment:"
echo "   Onyx: $(onyx | head -1)"
echo "   Node: $(node --version)"
echo "   Python: $(python3 --version)"

# 2. Initialize .ai_working folder structure
echo ""
echo "📁 Initializing .ai_working/..."
bash .devcontainer/setup_ai_working.sh

# 3. Mount RB4 DLC share (if available)
echo ""
echo "📦 Mounting RB4 DLC share..."
bash .devcontainer/mount_rb4_dlc.sh

# 4. Fix permissions for opencode data
echo ""
echo "🔧 Fixing permissions..."
mkdir -p /home/vscode/.local/state /home/vscode/.local/share /home/vscode/.local/config 2>/dev/null || true
sudo chown -R vscode:vscode /home/vscode/.local 2>/dev/null || chown -R vscode:vscode /home/vscode/.local 2>/dev/null || true
echo "   ✅ Permissions fixed"

echo ""
echo "=========================================="
echo "✅ Dev container ready!"
echo "=========================================="
echo ""
echo "To resume your session:"
echo "   Press Ctrl+Shift+P → 'Tasks: Run Task' → 'Opencode: Resume Last Session'"
echo ""
