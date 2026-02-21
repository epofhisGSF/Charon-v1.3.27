"""
CHARON Security Utilities
Input validation, sanitization, and security helpers
"""

import re
import hashlib
from pathlib import Path
from typing import Optional, Union


class SecurityValidator:
    """Input validation and sanitization utilities"""
    
    # Constants
    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 4096
    MAX_DISCORD_ROLE_ID_LENGTH = 20
    MAX_SYSTEM_NAME_LENGTH = 100
    MAX_REGION_NAME_LENGTH = 100
    MAX_INPUT_TEXT_LENGTH = 10000
    
    # Allowed domains for downloads
    ALLOWED_DOWNLOAD_DOMAINS = [
        'www.fuzzwork.co.uk',
        'fuzzwork.co.uk'
    ]
    
    # CSV injection patterns
    CSV_FORMULA_CHARS = ['=', '+', '-', '@', '|', '%']
    
    @staticmethod
    def validate_discord_role_id(role_id: str) -> str:
        """
        Validate Discord role ID (snowflake format)
        Returns sanitized ID or empty string if invalid
        """
        if not role_id:
            return ''
        
        # Discord snowflakes are 17-20 digit numbers
        if not re.match(r'^\d{17,20}$', role_id):
            return ''
        
        return role_id
    
    @staticmethod
    def validate_system_name(system_name: str) -> Optional[str]:
        """
        Validate EVE system name
        Allows: letters, numbers, spaces, hyphens
        """
        if not system_name or len(system_name) > SecurityValidator.MAX_SYSTEM_NAME_LENGTH:
            return None
        
        # EVE system names: alphanumeric + hyphen + space
        if not re.match(r'^[A-Za-z0-9\s\-]+$', system_name):
            return None
        
        return system_name.strip()
    
    @staticmethod
    def validate_region_name(region_name: str) -> Optional[str]:
        """
        Validate EVE region name
        Allows: letters, spaces, apostrophes
        """
        if not region_name or len(region_name) > SecurityValidator.MAX_REGION_NAME_LENGTH:
            return None
        
        # EVE region names: letters, spaces, apostrophes
        if not re.match(r"^[A-Za-z\s']+$", region_name):
            return None
        
        return region_name.strip()
    
    @staticmethod
    def sanitize_path(path: Union[str, Path], base_dir: Path) -> Optional[Path]:
        """
        Sanitize and validate file path to prevent directory traversal
        Returns None if path is invalid or outside base_dir
        """
        try:
            path = Path(path)
            
            # Resolve to absolute path
            abs_path = path.resolve()
            abs_base = base_dir.resolve()
            
            # Check if path is within base directory
            if not str(abs_path).startswith(str(abs_base)):
                return None
            
            # Check path length
            if len(str(abs_path)) > SecurityValidator.MAX_PATH_LENGTH:
                return None
            
            return abs_path
            
        except (ValueError, OSError):
            return None
    
    @staticmethod
    def sanitize_filename(filename: str) -> Optional[str]:
        """
        Sanitize filename to prevent path traversal and invalid characters
        """
        if not filename or len(filename) > SecurityValidator.MAX_FILENAME_LENGTH:
            return None
        
        # Remove path separators and dangerous characters
        filename = filename.replace('/', '').replace('\\', '').replace('..', '')
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
        
        if not filename or filename in ['.', '..']:
            return None
        
        return filename
    
    @staticmethod
    def sanitize_csv_value(value: str) -> str:
        """
        Sanitize CSV value to prevent formula injection
        Prefixes potential formulas with a single quote
        """
        if not value:
            return value
        
        value_str = str(value)
        
        # Check if starts with formula character
        if value_str and value_str[0] in SecurityValidator.CSV_FORMULA_CHARS:
            return "'" + value_str
        
        return value_str
    
    @staticmethod
    def sanitize_discord_markdown(text: str) -> str:
        """
        Escape Discord markdown to prevent formatting injection
        """
        if not text:
            return text
        
        # Escape Discord markdown characters
        text = text.replace('*', '\\*')
        text = text.replace('_', '\\_')
        text = text.replace('~', '\\~')
        text = text.replace('`', '\\`')
        text = text.replace('|', '\\|')
        text = text.replace('>', '\\>')
        
        return text
    
    @staticmethod
    def validate_url_domain(url: str) -> bool:
        """
        Validate that URL is from an allowed domain
        """
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            
            # Must be HTTPS
            if parsed.scheme != 'https':
                return False
            
            # Check domain whitelist
            domain = parsed.netloc.lower()
            if domain not in SecurityValidator.ALLOWED_DOWNLOAD_DOMAINS:
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        """
        Safely parse and validate integer with bounds checking
        """
        try:
            int_val = int(value)
            
            if min_val is not None and int_val < min_val:
                return None
            
            if max_val is not None and int_val > max_val:
                return None
            
            return int_val
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_float(value: str, min_val: float = None, max_val: float = None) -> Optional[float]:
        """
        Safely parse and validate float with bounds checking
        """
        try:
            float_val = float(value)
            
            if min_val is not None and float_val < min_val:
                return None
            
            if max_val is not None and float_val > max_val:
                return None
            
            return float_val
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def truncate_string(text: str, max_length: int) -> str:
        """
        Safely truncate string to maximum length
        """
        if not text:
            return ''
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length]
    
    @staticmethod
    def calculate_file_hash(filepath: Path, algorithm='sha256') -> Optional[str]:
        """
        Calculate cryptographic hash of file
        """
        try:
            hash_func = hashlib.new(algorithm)
            
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception:
            return None
    
    @staticmethod
    def verify_file_hash(filepath: Path, expected_hash: str, algorithm='sha256') -> bool:
        """
        Verify file hash matches expected value
        """
        actual_hash = SecurityValidator.calculate_file_hash(filepath, algorithm)
        
        if not actual_hash:
            return False
        
        return actual_hash.lower() == expected_hash.lower()


class RateLimiter:
    """Simple rate limiter for downloads"""
    
    def __init__(self):
        self.last_download_time = {}
    
    def can_download(self, url: str, cooldown_seconds: int = 3600) -> bool:
        """
        Check if URL can be downloaded (rate limit check)
        cooldown_seconds: Minimum time between downloads (default: 1 hour)
        """
        import time
        
        current_time = time.time()
        last_time = self.last_download_time.get(url, 0)
        
        if current_time - last_time < cooldown_seconds:
            return False
        
        return True
    
    def record_download(self, url: str):
        """Record that a download occurred"""
        import time
        self.last_download_time[url] = time.time()


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter
