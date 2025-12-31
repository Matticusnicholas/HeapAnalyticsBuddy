#!/bin/bash

echo ""
echo "============================================================"
echo "  HEAP ANALYTICS BUDDY - HEADLESS MODE"
echo "============================================================"
echo ""
echo "Running in headless mode (no browser window)..."
echo "Note: You must have valid credentials in .env file"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run in headless mode with default settings
heap-buddy generate --headless --no-interactive --browser firefox --format pdf --format docx --days 30

echo ""
echo "Report generation complete!"
echo "Check the 'reports' folder for your files."
