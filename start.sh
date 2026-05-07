#!/usr/bin/env bash
# Hermes Agent WebUI - 启动脚本 (macOS/Linux)
# Usage: ./start.sh [port]

PORT=${1:-8686}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "  Hermes Agent WebUI"
echo "  Starting on http://localhost:${PORT}"
echo "=================================================="

# Auto-detect Python
PYTHON=""
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        PYTHON="$py"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Error: Python not found. Please install Python 3.10+"
    exit 1
fi

# Install deps if needed
$PYTHON -m pip install -r requirements.txt -q 2>/dev/null

export WEBUI_PORT=$PORT
exec $PYTHON app.py
