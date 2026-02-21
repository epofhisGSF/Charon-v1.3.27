# CHARON - Wormhole Intelligence System for EVE Online

**Advanced drifter wormhole tracking and routing for EVE Online null-sec operations.**

CHARON is a desktop application that tracks drifter wormhole connections, calculates optimal routes using wormholes + stargates + jumpbridges, and provides fleet mass analysis for wormhole jumps.

![CHARON Version](https://img.shields.io/badge/version-1.3.23-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)

---

## 🎯 **Features**

### **📡 Wormhole Scanner**
- Scan and track drifter wormhole connections
- Records: system, hole type, life status, mass status, and timestamp
- Auto-cleanup of expired wormholes (16h/24h/48h lifetimes)
- Export/import scan data (CSV format)
- Discord integration for fleet coordination

### **🗺️ Advanced Routing**
- **Hybrid routing**: Combines stargates, wormholes, and jumpbridges
- **Multi-hop wormhole chains** (heavily penalized for realism)
- **Jumpbridge integration**: Import your alliance's JB network (112 Imperium JBs pre-configured)
- **Smart pathfinding**: Uses Dijkstra with weighted costs (gates=1.0, JBs=0.3)
- **Route quality scoring**: Accounts for wormhole stability, mass, and operational risks

### **⚖️ Fleet Mass Calculator**
- Calculate total fleet mass for wormhole jumps
- Supports 188+ ship types (including special edition/AT ships)
- Wormhole compatibility analysis (Fresh/Destabilizing/Critical)
- Bulk import from EVE fleet window
- Detects if fleet can safely jump through wormholes

---

## 🚀 **Quick Start**

### **Option 1: Download EXE (Recommended for Users)**

1. **Download** the latest release: [CHARON-v1.3.23.exe](https://github.com/YOUR_USERNAME/charon/releases/latest)
2. **Run** `CHARON.exe` (Windows only)
3. **First-time setup**: Auto-downloads EVE SDE data (~2 minutes)
4. **Done!** Start scanning wormholes

### **Option 2: Run from Source (For Developers)**

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/charon.git
cd charon

# Install dependencies
pip install -r requirements.txt

# Run application
python drifter_tracker.py
```

**Requirements:**
- Python 3.10+
- PyQt6
- See `requirements.txt` for full list

---

## 📖 **Usage Guide**

### **1. Scanner Tab - Track Wormholes**

**Scan a wormhole:**
1. Paste system name (e.g., `C-J6MT`)
2. Select connected system
3. Enter hole details (type, life, mass)
4. Click **ADD SCAN**

**Export to Discord:**
```
Click "EXPORT TO DISCORD" → paste in your fleet channel
Format: Ready for Discord markdown formatting
```

### **2. Routing Tab - Find Routes**

**Simple Mode (Region → Region):**
1. Select destination region from dropdown
2. View routes from home regions (Scalding Pass, Wicked Creek, Insmother)

**Advanced Mode (Any System → Any System):**
1. Enter origin system (e.g., `C-J6MT`)
2. Enter destination system (e.g., `PF-QHK`)
3. Click **FIND ROUTES**
4. See hybrid routes with gates + JBs + wormholes

**Route Display Example:**
```
#1 [OK] Route (Score: 12.0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
► C-J6MT
    ↓ 2 stargates + 2 JBs
● 8-OZU1
    ↓ [Redoubt Wormhole] ↓
● 92K-H2
    ↓ 8 stargates + 1 JB
► PF-QHK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 10 gates + 3 JBs + 1 wormhole
💡 Saves 12 gates vs direct route (22 gates)
```

### **3. Mass Tab - Fleet Mass Analysis**

**Calculate fleet mass:**
1. Click **BULK IMPORT LIST**
2. Paste fleet composition from EVE
3. See total mass and wormhole compatibility

**Wormhole Compatibility:**
- ✅ **Fresh (750M kg)**: Full fleet can jump
- ⚠️ **Destabilizing (375M kg)**: Reduced capacity
- ❌ **Critical (75M kg)**: Fleet too heavy

---

## ⚙️ **Configuration**

### **Jumpbridge Network**

Edit `jumpbridges.py` to add your alliance's jumpbridges:

```python
JUMPBRIDGES = [
    ('1DQ1-A', 'T5ZI-S', 'GSF'),
    ('PUIG-F', 'HY-RWO', 'GSF'),
    # Add your jumpbridges here
]
```

**Pre-configured:** 112 Imperium/Goonswarm jumpbridges already included!

### **Special Edition Ships**

Edit `special_ships.py` to add missing ships:

```python
SPECIAL_EDITION_SHIPS = {
    'Metamorphosis': 1_000_000,  # AT prize frigate
    'Your Ship': 1_500_000,      # Add custom ships
}
```

---

## 🏗️ **Building from Source**

### **Windows EXE**

```cmd
# Install PyInstaller
pip install pyinstaller

# Build executable
build_exe.bat

# Output: dist/CHARON.exe
```

### **Linux/Mac**

```bash
chmod +x build_exe.sh
./build_exe.sh

# Output: dist/CHARON (binary)
```

---

## 🔒 **Security**

CHARON is open-source for transparency and security auditing.

**Security Features:**
- ✅ Input validation on all user data
- ✅ HTTPS-only downloads with SSL verification
- ✅ Path traversal protection
- ✅ CSV injection prevention
- ✅ Rate limiting on downloads
- ✅ No telemetry or data collection
- ✅ 100% local operation (no cloud servers)

**Code Review:**
- All source code is available in this repository
- No obfuscation or hidden functionality
- Uses standard Python libraries (PyQt6, requests)
- SDE data downloaded directly from CCP's official sources

**What CHARON Does NOT Do:**
- ❌ Does not interact with EVE game client
- ❌ Does not read game memory
- ❌ Does not automate gameplay
- ❌ Does not send data to external servers
- ❌ Does not contain ads or tracking

---

## 📊 **Technical Details**

### **Architecture**

```
CHARON/
├── drifter_tracker.py      # Main application (PyQt6 GUI)
├── eve_sde_loader.py       # EVE SDE data processing
├── security_utils.py       # Input validation & sanitization
├── jumpbridges.py          # Jumpbridge network configuration
├── special_ships.py        # Special edition ship database
├── jove_systems.py         # Drifter region definitions
├── sde_data/               # EVE static data (auto-downloaded)
│   ├── invTypes.csv
│   └── invGroups.csv
└── build_exe.bat           # Windows build script
```

### **Data Sources**

- **EVE SDE**: Downloaded from [Fuzzwork SDE](https://www.fuzzwork.co.uk/dump/)
- **Ship masses**: From invTypes.csv + special_ships.py supplement
- **Jumpbridges**: User-configured (Imperium network pre-loaded)
- **Wormhole scans**: User input only (local storage)

### **Routing Algorithm**

**Weighted Dijkstra pathfinding:**
- Stargate jump: **1.0 cost**
- Jumpbridge: **0.3 cost** (70% faster)
- Wormhole: Bridges K-space regions

**Multi-hop penalties:**
- Burn time: **+15 score**
- NPC danger: **+10 score**
- Complexity: **+5 score**
- Result: Multi-hop only used for 30+ gate savings

### **Performance**

- **Startup time**: ~2 seconds (after initial setup)
- **Route calculation**: 1-3 seconds for 5,000+ routes
- **Memory usage**: ~100 MB
- **Database**: 8,437 K-space systems, 188 ship types, 112 JBs

---

## 🤝 **Contributing**

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Areas for Contribution**

- 🌍 Additional jumpbridge networks (other alliances/coalitions)
- 🚀 More special edition ships
- 🐛 Bug fixes and improvements
- 📝 Documentation improvements
- 🎨 UI/UX enhancements

---

## 🐛 **Known Issues**

- **Icon may not embed** on some Windows builds (see `ICON_TROUBLESHOOTING.md`)
- **Null-sec systems only**: J-space wormhole systems not in routing database
- **Jumpbridges**: Only works for K-space systems

---

## 📜 **License**

MIT License - see [LICENSE](LICENSE) file for details

**Summary:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ✅ No warranty provided
- ✅ Attribution appreciated but not required

---

## 🙏 **Credits**

**Created by:** [Your Name/Corp]  
**Special Thanks:**
- CCP Games for EVE Online
- Fuzzwork for SDE data dumps
- The Imperium for jumpbridge network data
- EVE community for feedback and testing

---

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/charon/issues)
- **Discord**: [Your Alliance Discord]
- **In-game**: [Your Character Name]

---

## 🎮 **EVE Online**

CHARON is a third-party tool for EVE Online.

EVE Online and all related materials are property of CCP Games.  
This tool is not affiliated with or endorsed by CCP Games.

**CCP Copyright Notice:**  
EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide.

---

## 📈 **Version History**

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version: v1.3.23**
- ✅ Jumpbridge routing integration
- ✅ Multi-hop deprioritization 
- ✅ Special edition ships support
- ✅ Fleet mass calculator
- ✅ UI improvements & progress indicators

---

**Made with ❤️ for the EVE Online community**

*Fly safe! o7*
