#!/bin/bash

echo ""
echo "============================================================"
echo "  HEAP ANALYTICS BUDDY"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment."
    exit 1
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the CLI
echo "Starting Heap Analytics Buddy..."
echo ""

# Check for command line arguments
if [ $# -eq 0 ]; then
    # No arguments - run interactive mode
    heap-buddy generate --interactive
elif [ "$1" == "--help" ]; then
    heap-buddy --help
elif [ "$1" == "setup" ]; then
    heap-buddy setup
elif [ "$1" == "browsers" ]; then
    heap-buddy browsers
else
    # Pass all arguments directly
    heap-buddy "$@"
fi
