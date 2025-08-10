"""
API capability cache to remember which endpoints support multimodal
"""
import json
import os
import time
from typing import Dict, Optional

class APICapabilityCache:
    """Simple cache to remember API capabilities"""
    
    def __init__(self, cache_file: str = "/tmp/api_capabilities.json"):
        self.cache_file = cache_file
        self._cache: Dict[str, Dict] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self._cache = json.load(f)
        except:
            self._cache = {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f)
        except:
            pass
    
    def get_capability(self, service_url: str, model_id: str) -> Optional[Dict]:
        """Get cached capability for an API"""
        key = f"{service_url}:{model_id}"
        return self._cache.get(key)
    
    def set_capability(self, service_url: str, model_id: str, supports_multimodal: bool):
        """Cache capability for an API"""
        key = f"{service_url}:{model_id}"
        self._cache[key] = {
            "supports_multimodal": supports_multimodal,
            "timestamp": time.time()
        }
        self._save_cache()

# Global instance
capability_cache = APICapabilityCache()