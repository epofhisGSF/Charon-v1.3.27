#!/bin/bash

echo "========================================"
echo "CHARON - Building Executable"
echo "========================================"
echo ""

# Check if pyinstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
    echo ""
fi

# Build the executable
echo "Building CHARON executable..."
echo "This may take several minutes..."
echo ""

pyinstaller charon.spec --clean

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "BUILD FAILED"
    echo "========================================"
    echo "Check the error messages above."
    exit 1
fi

echo ""
echo "========================================"
echo "BUILD COMPLETE!"
echo "========================================"
echo ""
echo "Your executable is located at:"
echo "  dist/CHARON"
echo ""
echo "You can distribute this single file!"
echo ""
ls -lh dist/CHARON
echo ""
