#!/usr/bin/env bash
# =============================================================================
# start_ollama.sh — Idempotent Ollama server startup
# =============================================================================

set +e

echo "=========================================="
echo "🚀 Starting Ollama Server"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install with:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Check if Ollama is already running
if ollama list &> /dev/null; then
    echo "✅ Ollama server already running"
    exit 0
fi

# Start the server in background
echo "Starting Ollama server..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..30}; do
    if ollama list &> /dev/null; then
        echo "✅ Ollama server started (PID: $OLLAMA_PID)"
        exit 0
    fi
    sleep 1
done

echo "❌ Ollama server failed to start"
echo "Check logs: /tmp/ollama.log"
exit 1