#!/bin/bash

echo "====================================="
echo "Drifter Tracker for EVE Online"
echo "====================================="
echo ""

# Try python3 first, fall back to python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed!"
    echo ""
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

echo "Found: $($PYTHON_CMD --version)"
echo ""

# Check for PyQt6
echo "Checking dependencies..."
$PYTHON_CMD -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to install dependencies!"
        echo "Try: pip3 install --user -r requirements.txt"
        exit 1
    fi
fi

echo ""
echo "Starting Drifter Tracker..."
echo ""
$PYTHON_CMD drifter_tracker.py
