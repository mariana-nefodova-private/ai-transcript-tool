#!/bin/bash
set -e

echo "==> Setting up AI Transcript Tool..."

# Check Python 3.11
PYTHON=/opt/homebrew/bin/python3.11
if ! command -v "$PYTHON" &>/dev/null; then
  echo "==> Installing Python 3.11..."
  brew install python@3.11
fi

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "==> Installing ffmpeg..."
  brew install ffmpeg
fi

# Create virtual environment
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/venv"

if [ ! -d "$VENV" ]; then
  echo "==> Creating Python virtual environment..."
  "$PYTHON" -m venv "$VENV"
fi

# Install Python dependencies
echo "==> Installing Python packages (Whisper, Flask)..."
"$VENV/bin/pip" install --upgrade pip --quiet
"$VENV/bin/pip" install -r "$SCRIPT_DIR/app/requirements.txt"

echo ""
echo "Setup complete!"
echo ""
echo "To start the app, run:"
echo "  source venv/bin/activate && python app/app.py"
