"""
Redis Cache Support - High-performance caching for Screenshot-to-Code
"""
import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional, Union, List
from datetime import timedelta
import redis.asyncio as redis
from contextlib import asynccontextmanager
import pickle
import base64
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    hit_count: int = 0
    last_accessed: float = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

class RedisCache:
    """
    Redis-based caching system with advanced features:
    - Async operations
    - TTL support
    - Cache warming
    - Hit rate tracking
    - Tag-based invalidation
    - Compression for large values
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,  # 1 hour
        key_prefix: str = "screenshot2code:",
        max_connections: int = 50,
        enable_compression: bool = True,
        compression_threshold: int = 1024  # Compress values larger than 1KB
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
    
    async def connect(self):
        """Establish Redis connection"""
        try:
            self._pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=False,  # We'll handle encoding ourselves
                max_connections=max_connections
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Disconnected from Redis")
    
    @asynccontextmanager
    async def connection(self):
        """Context manager for Redis connection"""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()
    
    def _make_key(self, key: str) -> str:
        """Create namespaced key"""
        return f"{self.key_prefix}{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        serialized = pickle.dumps(value)
        
        # Compress if enabled and value is large enough
        if self.enable_compression and len(serialized) > self.compression_threshold:
            import zlib
            compressed = zlib.compress(serialized)
            # Add compression marker
            return b"COMPRESSED:" + compressed
        
        return serialized
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        if data.startswith(b"COMPRESSED:"):
            import zlib
            compressed_data = data[11:]  # Remove marker
            decompressed = zlib.decompress(compressed_data)
            return pickle.loads(decompressed)
        
        return pickle.loads(data)
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        if not self._client:
            logger.warning("Redis client not connected")
            return default
        
        full_key = self._make_key(key)
        
        try:
            data = await self._client.get(full_key)
            
            if data is None:
                self._stats["misses"] += 1
                return default
            
            # Update hit count and last accessed
            await self._update_metadata(key)
            
            self._stats["hits"] += 1
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            self._stats["errors"] += 1
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
            tags: Tags for grouping cache entries
            
        Returns:
            True if successful
        """
        if not self._client:
            logger.warning("Redis client not connected")
            return False
        
        full_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize value
            data = self._serialize(value)
            
            # Set with TTL
            if ttl > 0:
                await self._client.setex(full_key, ttl, data)
            else:
                await self._client.set(full_key, data)
            
            # Store metadata
            await self._store_metadata(key, ttl, tags)
            
            # Update tags index
            if tags:
                await self._update_tags(key, tags)
            
            self._stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            self._stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._client:
            return False
        
        full_key = self._make_key(key)
        
        try:
            # Remove from tags index
            await self._remove_from_tags(key)
            
            # Delete key and metadata
            result = await self._client.delete(full_key, f"{full_key}:meta")
            
            self._stats["deletes"] += 1
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
            self._stats["errors"] += 1
            return False
    
    async def delete_by_tag(self, tag: str) -> int:
        """Delete all keys with a specific tag"""
        if not self._client:
            return 0
        
        tag_key = self._make_key(f"tag:{tag}")
        
        try:
            # Get all keys with this tag
            keys = await self._client.smembers(tag_key)
            
            if not keys:
                return 0
            
            # Delete all keys
            deleted = 0
            for key_bytes in keys:
                key = key_bytes.decode('utf-8')
                if await self.delete(key):
                    deleted += 1
            
            # Clean up tag set
            await self._client.delete(tag_key)
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting by tag {tag}: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        if not self._client:
            return False
        
        try:
            # Get all keys with our prefix
            pattern = f"{self.key_prefix}*"
            keys = []
            
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self._client.delete(*keys)
            
            # Reset stats
            self._stats = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "deletes": 0,
                "errors": 0
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def _store_metadata(self, key: str, ttl: int, tags: Optional[List[str]]):
        """Store metadata for cache entry"""
        meta_key = self._make_key(f"{key}:meta")
        
        metadata = {
            "created_at": time.time(),
            "ttl": ttl,
            "tags": tags or [],
            "hit_count": 0
        }
        
        await self._client.setex(
            meta_key,
            ttl if ttl > 0 else self.default_ttl,
            json.dumps(metadata)
        )
    
    async def _update_metadata(self, key: str):
        """Update metadata when key is accessed"""
        meta_key = self._make_key(f"{key}:meta")
        
        try:
            # Get current metadata
            data = await self._client.get(meta_key)
            if data:
                metadata = json.loads(data)
                metadata["hit_count"] += 1
                metadata["last_accessed"] = time.time()
                
                # Update with same TTL
                ttl = await self._client.ttl(meta_key)
                if ttl > 0:
                    await self._client.setex(meta_key, ttl, json.dumps(metadata))
        except Exception as e:
            logger.debug(f"Error updating metadata for {key}: {e}")
    
    async def _update_tags(self, key: str, tags: List[str]):
        """Update tag index"""
        for tag in tags:
            tag_key = self._make_key(f"tag:{tag}")
            await self._client.sadd(tag_key, key)
    
    async def _remove_from_tags(self, key: str):
        """Remove key from tag index"""
        # Get metadata to find tags
        meta_key = self._make_key(f"{key}:meta")
        
        try:
            data = await self._client.get(meta_key)
            if data:
                metadata = json.loads(data)
                tags = metadata.get("tags", [])
                
                for tag in tags:
                    tag_key = self._make_key(f"tag:{tag}")
                    await self._client.srem(tag_key, key)
        except Exception as e:
            logger.debug(f"Error removing from tags for {key}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate
        }
    
    # Convenience methods for specific use cases
    
    async def cache_screenshot_analysis(
        self,
        image_hash: str,
        analysis: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """Cache screenshot analysis results"""
        key = f"screenshot_analysis:{image_hash}"
        return await self.set(key, analysis, ttl, tags=["screenshot_analysis"])
    
    async def get_screenshot_analysis(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached screenshot analysis"""
        key = f"screenshot_analysis:{image_hash}"
        return await self.get(key)
    
    async def cache_generation_result(
        self,
        prompt_hash: str,
        model: str,
        result: str,
        ttl: int = 3600  # 1 hour
    ) -> bool:
        """Cache code generation result"""
        key = f"generation:{model}:{prompt_hash}"
        return await self.set(key, result, ttl, tags=["generation", f"model:{model}"])
    
    async def get_generation_result(
        self,
        prompt_hash: str,
        model: str
    ) -> Optional[str]:
        """Get cached generation result"""
        key = f"generation:{model}:{prompt_hash}"
        return await self.get(key)

# Global cache instance
cache = RedisCache()

# Decorator for caching function results
def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    tags: Optional[List[str]] = None
):
    """
    Decorator to cache async function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        tags: Tags for cache entry
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl, tags)
            
            return result
        
        return wrapper
    return decorator