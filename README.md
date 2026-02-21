# Drifter Wormhole Tracker - Python Desktop App

A native desktop application for tracking Jove Observatory drifter wormholes across New Eden in EVE Online. Built with Python and PyQt6 for a fast, native GUI experience.

## Features

- **1,003+ Jove Observatory Systems** - Complete database organized by region
- **Paste from EVE Client** - Copy wormhole info directly from game, auto-parses life and mass
- **Discord Export** - Generate formatted intel reports with role mentions and timestamps
- **Persistent Storage** - Your scans are saved automatically using Qt Settings
- **Native Desktop UI** - Fast, responsive interface with dark theme
- **Cross-Platform** - Works on Windows, macOS, and Linux

## Quick Installation

### Prerequisites

Python 3.8 or higher is required. Check your version:
```bash
python --version
# or
python3 --version
```

### Install & Run

**Windows:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python drifter_tracker.py
```

**macOS/Linux:**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the app
python3 drifter_tracker.py
```

## Creating a Standalone Executable

To create a double-clickable application that doesn't require Python:

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build the Executable

**Windows:**
```bash
pyinstaller --onefile --windowed --name "Drifter Tracker" --icon=icon.ico drifter_tracker.py
```

**macOS:**
```bash
pyinstaller --onefile --windowed --name "Drifter Tracker" --icon=icon.icns drifter_tracker.py
```

**Linux:**
```bash
pyinstaller --onefile --windowed --name "Drifter Tracker" drifter_tracker.py
```

The executable will be in the `dist` folder.

## How to Use

1. **Select Region & System** - Choose from the dropdowns
2. **Paste Wormhole Info** - Right-click the wormhole in EVE → Show Info → Copy all text → Paste
3. **Auto-Parse** - The app detects hole type, life, and mass automatically
4. **OR Click "No Hole Found"** - Quick button if system has no wormhole
5. **Export to Discord** - Generate formatted intel report with timestamps

## Supported Wormhole Types

- Vidette
- Redoubt  
- Sentinel
- Barbican
- Conflux
- Unidentified (K162)

## Data Storage

All data is stored locally using Qt Settings:
- **Windows:** Registry (`HKEY_CURRENT_USER\Software\DrifterTracker`)
- **macOS:** `~/Library/Preferences/com.DrifterTracker.plist`
- **Linux:** `~/.config/DrifterTracker/EVEWormholeScanner.conf`

Your scans persist between sessions and are never sent to any server.

## Keyboard Shortcuts

- Right-click on scans to delete individual entries
- Standard copy/paste works in text fields

## Troubleshooting

**ModuleNotFoundError: No module named 'PyQt6':**
```bash
pip install PyQt6
# or
pip3 install PyQt6
```

**App window is too small/large:**
- The window is resizable - drag the edges to resize
- Minimum size is 1000x600, starts at 1400x900

**Data not persisting:**
- Check that you have write permissions in your home directory
- On Linux, ensure `~/.config` directory exists

**PyInstaller build fails:**
```bash
# Try installing the latest PyInstaller
pip install --upgrade pyinstaller

# On Linux, you may need these packages:
sudo apt-get install python3-dev
```

## File Structure

```
drifter-tracker-python/
├── drifter_tracker.py   # Main application
├── jove_systems.py      # Jove Observatory database
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Development

The app uses:
- **PyQt6** - Modern Qt bindings for Python
- **QSettings** - Native platform settings storage
- **QMainWindow** - Professional window with menus
- **Custom Styling** - Dark theme matching EVE aesthetic

## System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows 7+, macOS 10.13+, or any modern Linux
- **RAM:** 256MB minimum
- **Disk:** 50MB for app + dependencies

## Building from Source

1. Clone or download the files
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python drifter_tracker.py`

That's it! No complex build process needed.

## Credits

- Jove Observatory data from the EVE Online community research
- Built with PyQt6 framework
- Designed for EVE Online capsuleers

Fly safe! o7

## License

MIT License - Free to use and modify
