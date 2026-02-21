# Changelog

All notable changes to CHARON will be documented in this file.

## [1.3.23] - 2026-02-15

### Fixed
- Ship masses now load correctly during first-time SDE setup
- Mass calculator properly recognizes all 188 ships including special editions
- Bulk fleet import now works with Metamorphosis, Nemesis, and other special ships

### Technical
- Added `_load_ship_masses()` call to `process_sde_data()` function

---

## [1.3.22] - 2026-02-15

### Added
- "Calculating routes..." progress indicator when finding routes
- Jumpbridge counts displayed in route details (e.g., "10 gates + 3 JBs")

### Fixed
- Progress indicator now shows immediately when clicking "FIND ROUTES"
- Jumpbridge usage now visible in hybrid route displays
- Removed duplicate code in route display function

### Changed
- Route format now shows: "X gates + Y JBs + Z wormholes"
- Entry and exit legs show individual JB counts

---

## [1.3.21] - 2026-02-15

### Added
- Jumpbridge counting function for route analysis
- Visual feedback during route calculations

### Changed
- Routes now display jumpbridge usage separately from gates
- Updated route display format to show JB breakdown

---

## [1.3.20] - 2026-02-15

### Fixed
- Jumpbridges now load correctly during SDE processing
- Added debug output for jumpbridge loading failures

### Changed
- Region routing limited to single-hop only (removed multi-hop chains)
- Multi-hop wormholes only in hybrid system-to-system mode

---

## [1.3.19] - 2026-02-15

### Added
- **Imperium Jumpbridge Network**: 112 pre-configured jumpbridges
- Covers: Cache, Catch, Detorid, Esoteria, Feythabolis, Immensea, Impass, Insmother, Paragon Soul, Period Basis, Scalding Pass, Tenerifis, Wicked Creek

### Changed
- Jumpbridges now loaded from static configuration file
- Updated `jumpbridges.py` with real network data

---

## [1.3.18] - 2026-02-15

### Added
- **Jumpbridge routing integration**: JBs cost 0.3 vs gates at 1.0
- Weighted Dijkstra pathfinding replaces simple BFS
- `jumpbridges.py` configuration file

### Changed
- **Multi-hop wormholes heavily penalized**: +30 score penalty
  - Burn time penalty: +15
  - NPC danger penalty: +10
  - Complexity penalty: +5
- Multi-hop only worth it for 30+ gate savings

### Technical
- Replaced BFS with weighted Dijkstra algorithm
- Added jumpbridge graph integration to pathfinding
- Updated scoring system for realistic operational costs

---

## [1.3.17] - 2026-02-15

### Added
- **Special Edition Ships Database**: 48 ships added
  - Alliance Tournament prizes (Metamorphosis, Cambion, Malice, etc.)
  - Limited edition ships (Gold/Silver Magnate)
  - Pirate faction ships (Worm, Astero, Stratios, Nestor)
- `special_ships.py` module with mass data

### Fixed
- Metamorphosis now recognized in mass calculator
- All AT prize ships now supported

---

## [1.3.16] - 2026-02-15

### Fixed
- Fleet bulk import parser working correctly
- Mass calculator displays all wormhole stages (Fresh, Destabilizing, Critical)
- Removed debug output from production build

### Changed
- Parser validated with 15-ship fleet test
- Unknown ships generate warnings instead of crashes

---

## [1.3.15] - 2026-02-15

### Added
- Enhanced debug output for fleet parser
- Line-by-line parsing feedback

---

## [1.3.3 - 1.3.14] - 2026-02-15

### Added
- Fleet bulk import from EVE fleet window
- Custom CHARON application icon
- Icon embedding tools and documentation
- Mass calculator wormhole compatibility analysis

### Fixed
- Parser syntax errors
- WORMHOLE_MASS_LIMITS ImportError
- Icon embedding in Windows builds

### Documentation
- `ICON_TROUBLESHOOTING.md` - 6 solutions for icon issues
- `ICON_README.md` - Icon design guide
- `build_exe_with_icon.bat` - Alternative build method

---

## [1.3.0] - 2026-02-14

### Added
- **Hybrid routing mode**: Any system → Any system
- Combines stargates + wormholes for optimal routes
- EVE SDE integration (8,437 K-space systems)
- Automatic SDE download and processing
- Route quality scoring system

### Changed
- Refactored routing architecture
- Added security validation to all inputs

---

## [1.2.0] - 2026-02-13

### Added
- Region-to-region routing
- Discord export formatting
- Auto-cleanup of expired wormholes

### Changed
- Improved UI styling
- Better scan data organization

---

## [1.1.0] - 2026-02-12

### Added
- CSV export/import functionality
- Wormhole scan tracking
- Basic routing between home regions

---

## [1.0.0] - 2026-02-11

### Added
- Initial release
- Wormhole scanner interface
- Basic data persistence
- PyQt6 GUI

---

## Release Notes Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
