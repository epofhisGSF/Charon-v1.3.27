# Quick Start Guide - Python Version

## Windows Users

**Easy Way:**
1. Double-click `run.bat`
2. The script will check Python and install dependencies automatically
3. App will launch!

**Manual Way:**
```bash
pip install -r requirements.txt
python drifter_tracker.py
```

## Mac/Linux Users

**Easy Way:**
1. Open Terminal in this folder
2. Run: `./run.sh`
3. App will launch!

**Manual Way:**
```bash
pip3 install -r requirements.txt
python3 drifter_tracker.py
```

## First Time Setup

1. **Install Python** (if not already installed)
   - Download from https://python.org/
   - Version 3.8 or higher required
   - On Windows, check "Add Python to PATH" during installation

2. **Run the app**
   - Windows: Double-click `run.bat`
   - Mac/Linux: Run `./run.sh` in terminal

## Creating a Standalone Executable

Want a double-clickable app without Python installed?

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "Drifter Tracker" drifter_tracker.py

# Find your app in the 'dist' folder
```

## Troubleshooting

**"Python is not recognized"** (Windows):
- Reinstall Python and check "Add to PATH"
- Or use full path: `C:\Python39\python.exe drifter_tracker.py`

**"No module named 'PyQt6'":**
```bash
pip install PyQt6
# or
pip3 install PyQt6
```

**Permission denied (Linux/Mac):**
```bash
chmod +x run.sh
./run.sh
```

## Features

✅ Native desktop app - no browser required
✅ 1,003+ Jove Observatory systems
✅ Auto-parse wormhole info from EVE
✅ Discord export with role mentions
✅ Persistent local storage
✅ Cross-platform (Windows, Mac, Linux)

## Usage

1. Select Region → System
2. Paste wormhole info from EVE (Right-click → Show Info)
3. Click "Parse & Add Scan" or "No Hole Found"
4. Export to Discord when ready

Fly safe! o7
