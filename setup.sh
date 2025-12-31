#!/bin/bash

echo ""
echo "============================================================"
echo "  HEAP ANALYTICS BUDDY - SETUP"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install Python 3.9+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "[1/5] Python found:"
python3 --version
echo ""

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "[ERROR] Python 3.9+ is required. Found: Python $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "     Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "     Virtual environment created successfully."
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment."
    exit 1
fi
echo "     Virtual environment activated."
echo ""

# Install dependencies
echo "[4/5] Installing dependencies (this may take a few minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies."
    echo "Please check your internet connection and try again."
    exit 1
fi
echo ""

# Install the package in development mode
echo "[5/5] Installing Heap Analytics Buddy..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to install package in development mode."
    echo "You can still run the tool using: python -m heap_buddy.cli"
fi
echo ""

# Create config file if it doesn't exist
if [ ! -f "heap_buddy_config.yaml" ]; then
    echo "Creating configuration file..."
    cp heap_buddy_config.example.yaml heap_buddy_config.yaml 2>/dev/null
    echo "Configuration file created: heap_buddy_config.yaml"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp .env.example .env 2>/dev/null
    echo "Environment file created: .env"
    echo ""
    echo "[IMPORTANT] Edit .env file to add your Heap Analytics credentials:"
    echo "  HEAP_EMAIL=your-email@example.com"
    echo "  HEAP_PASSWORD=your-password"
fi

echo ""
echo "============================================================"
echo "  SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your Heap Analytics credentials"
echo "  2. Run './run.sh' to generate a report"
echo "  3. Or run 'heap-buddy generate' in the activated environment"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo ""
