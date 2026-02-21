#!/usr/bin/env python3
"""
EVE SDE Data Setup Script
Run this once to download and process EVE Online static data
"""

from eve_sde_loader import EVESDELoader
import sys

def main(silent=False):
    """
    Download and setup SDE data
    silent: If True, skip prompts and just do it
    """
    if not silent:
        print("=" * 60)
        print("EVE Online Drifter Tracker - SDE Data Setup")
        print("=" * 60)
        print()
        print("This script will download EVE Online static data including:")
        print("  • Solar system information")
        print("  • Region data")
        print("  • Stargate connections")
        print("  • Ship masses")
        print()
        print("This is required for advanced routing features.")
        print("Data source: Fuzzwork SDE dumps")
        print()
        
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print()
    loader = EVESDELoader()
    
    # Check if already processed
    if loader.load_processed_data() and not silent:
        print()
        print("✓ SDE data already loaded!")
        print(f"  • {len(loader.systems):,} solar systems")
        print(f"  • {len(loader.regions)} regions")
        print(f"  • {len(loader.system_jumps):,} stargate connections")
        print(f"  • {len(loader.ship_masses):,} ship types")
        print()
        response = input("Re-download and process? (y/n): ")
        if response.lower() != 'y':
            print("Using existing data.")
            return
    elif loader.load_processed_data() and silent:
        # Already have data in silent mode, skip
        return
    
    print()
    print("Downloading SDE data files...")
    print("(This may take a few minutes)")
    print()
    
    if not loader.download_sde_data():
        print()
        print("✗ Failed to download SDE data")
        print("Please check your internet connection and try again.")
        sys.exit(1)
    
    print()
    print("Processing SDE data...")
    
    if not loader.process_sde_data():
        print()
        print("✗ Failed to process SDE data")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Setup Complete!")
    print("=" * 60)
    print()
    print(f"Loaded data:")
    print(f"  • {len(loader.systems):,} solar systems")
    print(f"  • {len(loader.regions)} regions")
    print(f"  • {len(loader.system_jumps):,} stargate connections")
    print(f"  • {len(loader.ship_masses):,} ship types")
    print()
    print("Advanced routing features are now available!")
    print()
    
    # Quick test
    print("Testing pathfinding...")
    test_paths = [
        ('Jita', 'Amarr'),
        ('Jita', 'Dodixie'),
        ('Hek', 'Rens')
    ]
    
    for start, end in test_paths:
        path = loader.find_path(start, end)
        if path:
            print(f"  ✓ {start} → {end}: {len(path)} jumps")
        else:
            print(f"  ✗ {start} → {end}: No route found")
    
    print()
    print("You can now run the Drifter Tracker with full routing support!")

if __name__ == '__main__':
    main()
