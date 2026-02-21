"""
EVE Online SDE Data Loader (Security Hardened)
Downloads and parses Static Data Export for routing and mass calculations
"""

import csv
import json
import os
import requests
from pathlib import Path
from security_utils import SecurityValidator, get_rate_limiter


# Drifter Wormhole Mass Limits (for mass calculator)
WORMHOLE_MASS_LIMITS = {
    'Fresh': {
        'total_mass': 750_000_000,  # 750M kg total (drifter wormholes)
        'individual_mass': 375_000_000  # 375M kg per jump (drifter limit)
    },
    'Destabilizing': {
        'total_mass': 375_000_000,  # 50% remaining
        'individual_mass': 375_000_000
    },
    'Critical': {
        'total_mass': 75_000_000,  # < 10% remaining
        'individual_mass': 375_000_000
    }
}


class EVESDELoader:
    """Load and parse EVE Online Static Data Export (Security Hardened)"""
    
    # Security limits
    MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50 MB max per file
    DOWNLOAD_TIMEOUT = 60  # seconds
    
    def __init__(self, data_dir='sde_data'):
        # Validate and sanitize data directory
        self.data_dir = Path(data_dir)
        
        # Ensure data_dir is safe
        if '..' in str(data_dir) or '/' in str(data_dir).replace(data_dir, ''):
            raise ValueError("Invalid data directory path")
        
        self.data_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.systems = {}  # {system_id: {name, region_id, security, ...}}
        self.regions = {}  # {region_id: name}
        self.system_jumps = {}  # {from_system_id: [to_system_id, ...]}
        self.ship_masses = {}  # {type_name: mass_kg}
        self.jumpbridges = {}  # {system_id: [connected_system_id, ...]}
        
        # Name lookups for convenience
        self.system_name_to_id = {}
        self.system_id_to_name = {}
        self.region_name_to_id = {}
        
        # Rate limiter
        self.rate_limiter = get_rate_limiter()
    
    def download_sde_data(self):
        """Download SDE CSV files from Fuzzwork (Security Hardened)"""
        base_url = "https://www.fuzzwork.co.uk/dump/latest/"
        
        files = {
            'mapSolarSystems.csv': 'Solar systems',
            'mapRegions.csv': 'Regions',
            'mapSolarSystemJumps.csv': 'Stargate connections',
            'invTypes.csv': 'Ship types and masses',
            'invGroups.csv': 'Ship groups'
        }
        
        print("Downloading EVE SDE data...")
        
        for filename, description in files.items():
            # Sanitize filename
            safe_filename = SecurityValidator.sanitize_filename(filename)
            if not safe_filename:
                print(f"✗ Invalid filename: {filename}")
                return False
            
            filepath = self.data_dir / safe_filename
            
            if filepath.exists():
                print(f"✓ {description} already downloaded")
                continue
            
            try:
                url = base_url + safe_filename
                
                # Validate URL domain
                if not SecurityValidator.validate_url_domain(url):
                    print(f"✗ Invalid or untrusted URL: {url}")
                    return False
                
                # Check rate limit
                if not self.rate_limiter.can_download(url, cooldown_seconds=3600):
                    print(f"⚠ Rate limit: Please wait before re-downloading {safe_filename}")
                    continue
                
                print(f"  Downloading {description}...")
                
                # Download with security checks
                if not self._secure_download(url, filepath):
                    print(f"✗ Failed to download {safe_filename}")
                    return False
                
                # Record successful download
                self.rate_limiter.record_download(url)
                print(f"✓ Downloaded {safe_filename}")
                
            except Exception as e:
                print(f"✗ Failed to download {safe_filename}: {e}")
                return False
        
        print("✓ All SDE data downloaded")
        return True
    
    def _secure_download(self, url: str, filepath: Path) -> bool:
        """
        Securely download file with size limits and HTTPS enforcement
        """
        try:
            # HTTPS-only with certificate verification
            response = requests.get(
                url,
                timeout=self.DOWNLOAD_TIMEOUT,
                verify=True,  # Enforce SSL certificate validation
                stream=True
            )
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('Content-Length')
            if content_length:
                size = int(content_length)
                if size > self.MAX_DOWNLOAD_SIZE:
                    print(f"  ✗ File too large: {size / 1024 / 1024:.1f} MB (max: {self.MAX_DOWNLOAD_SIZE / 1024 / 1024:.1f} MB)")
                    return False
            
            # Download with size checking
            downloaded = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        
                        # Enforce max size during download
                        if downloaded > self.MAX_DOWNLOAD_SIZE:
                            print(f"  ✗ Download exceeded size limit")
                            filepath.unlink(missing_ok=True)
                            return False
                        
                        f.write(chunk)
            
            # Display download size
            size_mb = downloaded / 1024 / 1024
            print(f"  Downloaded {size_mb:.1f} MB")
            
            return True
            
        except requests.exceptions.SSLError as e:
            print(f"  ✗ SSL certificate validation failed: {e}")
            return False
        except requests.exceptions.Timeout:
            print(f"  ✗ Download timeout")
            return False
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Download error: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            return False
    
    def load_processed_data(self):
        """Load preprocessed data if available"""
        processed_files = {
            'systems_processed.csv': self._load_systems_processed,
            'jumps_processed.csv': self._load_jumps_processed,
        }
        
        for filename, loader_func in processed_files.items():
            # Sanitize filename
            safe_filename = SecurityValidator.sanitize_filename(filename)
            if not safe_filename:
                continue
            
            filepath = self.data_dir / safe_filename
            
            if not filepath.exists():
                return False
            
            # Validate path is within data_dir
            safe_path = SecurityValidator.sanitize_path(filepath, self.data_dir)
            if not safe_path:
                print(f"⚠ Invalid path: {filepath}")
                return False
            
            try:
                loader_func(safe_path)
            except Exception as e:
                print(f"⚠ Failed to load {safe_filename}: {e}")
                return False
        
        # Load ship masses from invTypes.csv
        if not self._load_ship_masses():
            print("⚠ Ship mass data not available. Mass calculator will be limited.")
            print("   Ship data is loaded during SDE processing.")
        
        # Load jumpbridge network (optional)
        self.load_jumpbridges()
        
        return len(self.systems) > 0
    
    def _load_systems_processed(self, filepath):
        """Load processed systems data with validation"""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Validate and sanitize system_id
                    system_id = SecurityValidator.validate_integer(
                        row['system_id'],
                        min_val=30000000,
                        max_val=33000000
                    )
                    if not system_id:
                        continue
                    
                    # Validate system name
                    system_name = SecurityValidator.validate_system_name(row['system_name'])
                    if not system_name:
                        continue
                    
                    # Validate region_id
                    region_id = SecurityValidator.validate_integer(
                        row['region_id'],
                        min_val=10000000,
                        max_val=11000000
                    )
                    if not region_id:
                        continue
                    
                    # Validate security (can be negative)
                    security = SecurityValidator.validate_float(
                        row['security'],
                        min_val=-1.0,
                        max_val=1.0
                    )
                    if security is None:
                        security = 0.0
                    
                    self.systems[system_id] = {
                        'name': system_name,
                        'region_id': region_id,
                        'security': security
                    }
                    
                    self.system_name_to_id[system_name] = system_id
                    self.system_id_to_name[system_id] = system_name
                    
                except (KeyError, ValueError) as e:
                    # Skip malformed rows
                    continue
    
    def _load_jumps_processed(self, filepath):
        """Load processed jumps data with validation"""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Validate system IDs
                    from_system = SecurityValidator.validate_integer(
                        row['from_system'],
                        min_val=30000000,
                        max_val=33000000
                    )
                    to_system = SecurityValidator.validate_integer(
                        row['to_system'],
                        min_val=30000000,
                        max_val=33000000
                    )
                    
                    if not from_system or not to_system:
                        continue
                    
                    if from_system not in self.system_jumps:
                        self.system_jumps[from_system] = []
                    
                    self.system_jumps[from_system].append(to_system)
                    
                except (KeyError, ValueError):
                    continue
    
    def _load_ship_masses(self):
        """Load ship masses from invTypes.csv with validation"""
        types_file = self.data_dir / 'invTypes.csv'
        groups_file = self.data_dir / 'invGroups.csv'
        
        if not types_file.exists() or not groups_file.exists():
            return False
        
        # Validate paths
        safe_types = SecurityValidator.sanitize_path(types_file, self.data_dir)
        safe_groups = SecurityValidator.sanitize_path(groups_file, self.data_dir)
        
        if not safe_types or not safe_groups:
            return False
        
        # Load ship group IDs
        ship_groups = set()
        try:
            with open(safe_groups, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Category 6 = Ships
                        category_id = SecurityValidator.validate_integer(row.get('categoryID'))
                        group_id = SecurityValidator.validate_integer(row.get('groupID'))
                        
                        if category_id == 6 and group_id:
                            ship_groups.add(group_id)
                    except (KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"⚠ Failed to load ship groups: {e}")
            return False
        
        # Load ship types and masses
        try:
            with open(safe_types, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        group_id = SecurityValidator.validate_integer(row.get('groupID'))
                        
                        if group_id not in ship_groups:
                            continue
                        
                        # Validate mass (must be positive)
                        mass = SecurityValidator.validate_float(
                            row.get('mass', '0'),
                            min_val=0,
                            max_val=10_000_000_000  # 10 billion kg max
                        )
                        
                        if not mass or mass == 0:
                            continue
                        
                        # Filter: Only subcapital ships (< 1 billion kg)
                        if mass >= 1_000_000_000:
                            continue
                        
                        # Validate type name
                        type_name = row.get('typeName', '').strip()
                        if not type_name or len(type_name) > 100:
                            continue
                        
                        self.ship_masses[type_name] = mass
                        
                    except (KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"⚠ Failed to load ship masses: {e}")
            return False
        
        # Add special edition ships (AT prizes, limited edition, etc.)
        try:
            from special_ships import SPECIAL_EDITION_SHIPS
            for ship_name, mass in SPECIAL_EDITION_SHIPS.items():
                # Only add subcapital special ships (< 1 billion kg)
                if mass < 1_000_000_000:
                    self.ship_masses[ship_name] = mass
            print(f"✓ Loaded {len(SPECIAL_EDITION_SHIPS)} special edition ships")
        except ImportError:
            # special_ships.py not available - that's okay
            pass
        
        return len(self.ship_masses) > 0
    
    def load_jumpbridges(self):
        """Load jumpbridge network and integrate into routing"""
        try:
            from jumpbridges import JUMPBRIDGES, JB_GATE_COMPARISON
            
            jb_count = 0
            skipped = 0
            for system1, system2, alliance in JUMPBRIDGES:
                # Get system IDs
                sys1_id = self.system_name_to_id.get(system1)
                sys2_id = self.system_name_to_id.get(system2)
                
                if not sys1_id or not sys2_id:
                    # System not in database - might be invalid name
                    skipped += 1
                    if skipped <= 3:  # Show first few for debugging
                        if not sys1_id:
                            print(f"  ⚠ JB system not found: {system1}")
                        if not sys2_id:
                            print(f"  ⚠ JB system not found: {system2}")
                    continue
                
                # Add bidirectional jumpbridge connections
                # JBs are added to jumpbridges dict separately from gates
                if sys1_id not in self.jumpbridges:
                    self.jumpbridges[sys1_id] = []
                if sys2_id not in self.jumpbridges:
                    self.jumpbridges[sys2_id] = []
                
                # Bidirectional
                if sys2_id not in self.jumpbridges[sys1_id]:
                    self.jumpbridges[sys1_id].append(sys2_id)
                if sys1_id not in self.jumpbridges[sys2_id]:
                    self.jumpbridges[sys2_id].append(sys1_id)
                
                jb_count += 1
            
            if jb_count > 0:
                print(f"✓ Loaded {jb_count} jumpbridge connections")
                if skipped > 0:
                    print(f"  (Skipped {skipped} JBs - systems not in K-space database)")
                return True
            elif skipped > 0:
                print(f"⚠ All {skipped} jumpbridge systems not found in database")
                print(f"  JBs are only for K-space systems, not wormholes")
            
        except ImportError:
            # jumpbridges.py not available - that's okay
            pass
        
        return False
    
    def process_sde_data(self):
        """Process raw SDE files into optimized format"""
        print("\nProcessing SDE data...")
        
        if not self._process_systems():
            return False
        
        if not self._process_jumps():
            return False
        
        # Load ship masses from invTypes.csv
        if not self._load_ship_masses():
            print("⚠ Failed to load ship masses")
        
        print(f"✓ Processed {len(self.systems):,} solar systems")
        print(f"✓ Processed {len(self.system_jumps):,} stargate connections")
        print(f"✓ Processed {len(self.ship_masses):,} ship types")
        
        # Load jumpbridge network (optional)
        self.load_jumpbridges()
        
        return True
    
    def _process_systems(self):
        """Process solar systems and regions from raw CSV"""
        systems_file = self.data_dir / 'mapSolarSystems.csv'
        regions_file = self.data_dir / 'mapRegions.csv'
        
        if not systems_file.exists() or not regions_file.exists():
            print("✗ Missing required CSV files")
            return False
        
        # Validate paths
        safe_systems = SecurityValidator.sanitize_path(systems_file, self.data_dir)
        safe_regions = SecurityValidator.sanitize_path(regions_file, self.data_dir)
        
        if not safe_systems or not safe_regions:
            print("✗ Invalid file paths")
            return False
        
        # Load regions first
        try:
            with open(safe_regions, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        region_id = SecurityValidator.validate_integer(row.get('regionID'))
                        region_name = SecurityValidator.validate_region_name(row.get('regionName', ''))
                        
                        if region_id and region_name:
                            self.regions[region_id] = region_name
                            self.region_name_to_id[region_name] = region_id
                    except (KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"✗ Failed to process regions: {e}")
            return False
        
        # Load systems
        try:
            with open(safe_systems, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                output_file = self.data_dir / 'systems_processed.csv'
                with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
                    writer = csv.writer(out_f)
                    writer.writerow(['system_id', 'system_name', 'region_id', 'security'])
                    
                    for row in reader:
                        try:
                            system_id = SecurityValidator.validate_integer(row.get('solarSystemID'))
                            region_id = SecurityValidator.validate_integer(row.get('regionID'))
                            system_name = SecurityValidator.validate_system_name(row.get('solarSystemName', ''))
                            security = SecurityValidator.validate_float(row.get('security', '0'))
                            
                            if not system_id or not region_id or not system_name:
                                continue
                            
                            if security is None:
                                security = 0.0
                            
                            self.systems[system_id] = {
                                'name': system_name,
                                'region_id': region_id,
                                'security': security
                            }
                            
                            self.system_name_to_id[system_name] = system_id
                            self.system_id_to_name[system_id] = system_name
                            
                            writer.writerow([system_id, system_name, region_id, security])
                            
                        except (KeyError, ValueError):
                            continue
        except Exception as e:
            print(f"✗ Failed to process systems: {e}")
            return False
        
        return True
    
    def _process_jumps(self):
        """Process stargate jumps from raw CSV"""
        jumps_file = self.data_dir / 'mapSolarSystemJumps.csv'
        
        if not jumps_file.exists():
            print("✗ Missing jumps CSV file")
            return False
        
        # Validate path
        safe_jumps = SecurityValidator.sanitize_path(jumps_file, self.data_dir)
        if not safe_jumps:
            print("✗ Invalid file path")
            return False
        
        try:
            with open(safe_jumps, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                output_file = self.data_dir / 'jumps_processed.csv'
                with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
                    writer = csv.writer(out_f)
                    writer.writerow(['from_system', 'to_system'])
                    
                    for row in reader:
                        try:
                            from_system = SecurityValidator.validate_integer(row.get('fromSolarSystemID'))
                            to_system = SecurityValidator.validate_integer(row.get('toSolarSystemID'))
                            
                            if not from_system or not to_system:
                                continue
                            
                            if from_system not in self.system_jumps:
                                self.system_jumps[from_system] = []
                            
                            self.system_jumps[from_system].append(to_system)
                            
                            writer.writerow([from_system, to_system])
                            
                        except (KeyError, ValueError):
                            continue
        except Exception as e:
            print(f"✗ Failed to process jumps: {e}")
            return False
        
        return True
    
    def get_system_region(self, system_name: str) -> str:
        """Get region name for a system"""
        # Validate input
        system_name = SecurityValidator.validate_system_name(system_name)
        if not system_name:
            return "Unknown"
        
        system_id = self.system_name_to_id.get(system_name)
        if not system_id:
            return "Unknown"
        
        system_data = self.systems.get(system_id)
        if not system_data:
            return "Unknown"
        
        region_id = system_data.get('region_id')
        return self.regions.get(region_id, "Unknown")
    
    def find_path(self, start_system: str, end_system: str, max_jumps: int = 30, use_jumpbridges: bool = True):
        """
        Find shortest path between two systems using weighted pathfinding
        
        Args:
            start_system: Starting system name
            end_system: Destination system name
            max_jumps: Maximum gate jumps allowed
            use_jumpbridges: Whether to include jumpbridge network
        
        Returns:
            List of system names, or None if no path found
        
        Costs:
            - Standard gate: 1.0
            - Jumpbridge: 0.3 (much faster, instant travel)
        """
        import heapq
        
        # Validate inputs
        start_system = SecurityValidator.validate_system_name(start_system)
        end_system = SecurityValidator.validate_system_name(end_system)
        max_jumps = SecurityValidator.validate_integer(str(max_jumps), min_val=1, max_val=100)
        
        if not start_system or not end_system or not max_jumps:
            return None
        
        start_id = self.system_name_to_id.get(start_system)
        end_id = self.system_name_to_id.get(end_system)
        
        if not start_id or not end_id:
            return None
        
        if start_id == end_id:
            return [start_system]
        
        # Dijkstra's algorithm with weighted edges
        # Priority queue: (cost, current_id, path)
        pq = [(0, start_id, [start_id])]
        visited = {}  # {system_id: min_cost}
        
        while pq:
            cost, current_id, path = heapq.heappop(pq)
            
            # Skip if we've seen this system with lower cost
            if current_id in visited and visited[current_id] <= cost:
                continue
            
            visited[current_id] = cost
            
            # Found destination
            if current_id == end_id:
                return [self.system_id_to_name[sid] for sid in path]
            
            # Exceeded max jumps (approximate - jumpbridges count as 0.3)
            if len(path) > max_jumps * 2:  # Allow more steps for JB routes
                continue
            
            # Explore standard gate connections (cost: 1.0)
            if current_id in self.system_jumps:
                for next_id in self.system_jumps[current_id]:
                    new_cost = cost + 1.0
                    if next_id not in visited or visited.get(next_id, float('inf')) > new_cost:
                        heapq.heappush(pq, (new_cost, next_id, path + [next_id]))
            
            # Explore jumpbridge connections (cost: 0.3)
            if use_jumpbridges and current_id in self.jumpbridges:
                for next_id in self.jumpbridges[current_id]:
                    new_cost = cost + 0.3  # JBs are MUCH faster
                    if next_id not in visited or visited.get(next_id, float('inf')) > new_cost:
                        heapq.heappush(pq, (new_cost, next_id, path + [next_id]))
        
        return None
