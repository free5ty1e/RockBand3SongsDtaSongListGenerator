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
echo "   Onyx: $(xvfb-run -a onyx 2>&1 | tail -1)"
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

# 5. Initialize PS4 PKG investigation tools
echo ""
echo "🛠️ Setting up PS4 PKG tools..."
cd /workspace
if [ ! -d "ps4_pkg_tool" ]; then
    echo "   - Cloning ps4_pkg_tool..."
    git clone --depth 1 https://github.com/mc-17/ps4_pkg_tool.git ps4_pkg_tool 2>/dev/null || true
fi
if [ ! -d "PkgToolBox" ]; then
    echo "   - Cloning PkgToolBox..."
    git clone --depth 1 https://github.com/seregonwar/PkgToolBox.git 2>/dev/null || true
fi
if [ ! -d "shadPS4Plus" ]; then
    echo "   - Cloning shadPS4Plus..."
    git clone --depth 1 --branch PKG_EXTRACTOR_1_1 https://github.com/AzaharPlus/shadPS4Plus.git 2>/dev/null || true
fi
echo "   ✅ PS4 tools ready"

# 6. Initialize Rock Band 4 Deluxe tools (THE KEY TO SONG EXTRACTION!)
echo ""
echo "🎸 Setting up RB4 extraction tools..."
cd /workspace
if [ ! -d "LibForge" ]; then
    echo "   - Cloning LibForge (RB4 file extraction)..."
    git clone --depth 1 https://github.com/mtolly/LibForge.git LibForge 2>/dev/null || true
fi
if [ ! -d "rb4dx_repo" ]; then
    echo "   - Cloning Rock Band 4 Deluxe source..."
    git clone --depth 1 https://github.com/hmxmilohax/Rock-Band-4-Deluxe.git rb4dx_repo 2>/dev/null || true
fi
echo "   ✅ RB4 tools ready"

# 7. Install .NET SDK for building tools
echo ""
echo "📦 Installing .NET SDK..."
export HOME_DIR="/home/vscode"
if [ ! -d "$HOME_DIR/dotnet" ]; then
    echo "   - Downloading .NET 8.0 SDK..."
    wget -q https://dot.net/v1/dotnet-install.sh -O /tmp/dotnet-install.sh
    chmod +x /tmp/dotnet-install.sh
    mkdir -p $HOME_DIR/dotnet
    /tmp/dotnet-install.sh --install-dir $HOME_DIR/dotnet --channel 8.0 2>&1 | tail -3
    echo, "   - .NET SDK installed"
fi
export PATH="$HOME_DIR/dotnet:$PATH"
echo "   - .NET $(dotnet --version 2>/dev/null || echo 'available')"

# 8. Copy pre-built ForgeTool binaries for easy access
echo ""
echo "🛠️ Copying pre-built binaries..."
mkdir -p /workspace/binaries
if [ -f "/workspace/rb4dx_repo/dependencies/ForgeTool/ForgeTool.exe" ]; then
    cp /workspace/rb4dx_repo/dependencies/ForgeTool/ForgeTool.exe /workspace/binaries/
    echo "   - ForgeTool.exe copied to /workspace/binaries/"
fi
echo "   ✅ Binaries ready"

echo ""
echo "=========================================="
echo "✅ Dev container ready!"
echo "=========================================="
echo ""
echo "To resume your session:"
echo "   Press Ctrl+Shift+P → 'Tasks: Run Task' → 'Opencode: Resume Last Session'"
echo ""
