# EVE SDE Integration - Advanced Routing

This module adds professional fleet routing capabilities using EVE Online's Static Data Export (SDE).

## Features

### 🗺️ **Full New Eden Pathfinding**
- Route between ANY solar systems (not just home regions)
- Uses actual stargate connections from EVE database
- Hybrid routing: Stargates → Wormhole → Stargates

### 📊 **Mass Calculator**
- Calculate total fleet mass
- Compare against wormhole limits
- Warnings for holes that can't support your fleet

### 🎯 **Weighted Route Scoring**
1. Direct wormhole (best)
2. < 10 gates each side, safe holes (good)
3. < 10 gates, critical time but safe mass (acceptable)
4. > 10 gates one side, safe holes (long)
5. < 10 gates, critical mass (risky)

## Setup Instructions

### Step 1: Install (First Time Only)

Run the setup script to download EVE SDE data:

```bash
python setup_sde.py
```

This will:
- Download ~50MB of EVE data (regions, systems, gates, ships)
- Process and optimize the data
- Save to `sde_data/processed_sde.json` for fast loading

**Note:** You only need to run this once. The data will be saved locally.

### Step 2: Run Tracker

```bash
python drifter_tracker.py
```

The app will automatically load SDE data if available.

## Data Sources

- **EVE SDE:** https://www.fuzzwork.co.uk/dump/latest/
- **Systems:** ~8,000 solar systems across New Eden
- **Regions:** ~100 regions
- **Gates:** ~15,000 stargate connections
- **Ships:** ~400 subcapital ship types with accurate masses

## Usage

### Advanced Routing Tab

**Select Start/End Systems:**
```
From: Jita (The Forge)
To: Amarr (Domain)
```

**Route Display:**
```
📍 Hybrid Route (15 total jumps):
Jita → [12 gates] → U2-28D (Scalding Pass)
  ↓ [Barbican Wormhole]
I-CUVX (Fountain) → [3 gates] → Amarr
```

### Mass Calculator Tab

**Input Fleet:**
- 10x Hurricane (battlecruisers)
- 5x Guardian (logistics)
- 20x Rifter (frigates)

**Analysis:**
```
Total Fleet Mass: 1,250,000,000 kg

Wormhole Compatibility:
✓ Fresh holes: Can support full fleet
✓ Reduced holes: Can support full fleet
⚠️ Critical holes: TOO HEAVY - Split fleet or avoid
```

## Wormhole Mass Limits

### Total Mass (Lifetime Capacity)
- **Fresh (100% > 50%):** 5,000,000,000 kg
- **Reduced (50% > 10%):** 2,500,000,000 kg
- **Critical (< 10%):** 500,000,000 kg

### Individual Jump Limit
- **All stages:** 1,800,000,000 kg per jump
- Capitals exceed this limit (can't use drifter holes)

## File Structure

```
drifter-tracker-python/
├── eve_sde_loader.py      # SDE parsing and pathfinding
├── setup_sde.py           # One-time setup script
├── sde_data/              # Downloaded data (created on setup)
│   ├── mapSolarSystems.csv
│   ├── mapRegions.csv
│   ├── mapSolarSystemJumps.csv
│   ├── invTypes.csv
│   └── processed_sde.json  # Optimized data for fast loading
└── drifter_tracker.py     # Main app (auto-loads SDE)
```

## Troubleshooting

**"No SDE data found"**
- Run `python setup_sde.py` first

**"Failed to download"**
- Check internet connection
- Try again (Fuzzwork servers might be busy)

**"Pathfinding slow"**
- First run processes data (takes ~10s)
- Subsequent runs use cached `processed_sde.json` (instant)

**"Ship not found"**
- Only subcapital ships included
- Capitals can't use drifter wormholes anyway

## Performance

- **Initial setup:** ~2 minutes (one-time)
- **App startup with SDE:** ~1 second
- **Pathfinding:** < 0.1 seconds per route
- **Memory usage:** ~100MB additional for SDE data

## Updates

To update EVE data (e.g., after expansions):

```bash
rm -rf sde_data/
python setup_sde.py
```

This re-downloads the latest SDE data from CCP.

## Advanced Usage

### Custom Pathfinding

```python
from eve_sde_loader import EVESDELoader

loader = EVESDELoader()
loader.load_processed_data()

# Find route
path = loader.find_path('Jita', 'Amarr', max_jumps=50)
print(f"Route: {' -> '.join(path)}")

# Get system info
region = loader.get_system_region('Jita')
print(f"Jita is in {region}")

# Ship mass lookup
mass = loader.ship_masses.get('Hurricane')
print(f"Hurricane mass: {mass:,} kg")
```

## Credits

- **EVE SDE Data:** CCP Games
- **SDE Dumps:** Fuzzwork (Steve Ronuken)
- **Drifter Tracker:** Community project
