"""Redis cache service for caching PDF chunks, embeddings, and QA results."""
import json
import hashlib
import threading
import redis
from functools import wraps
from typing import Any, Optional, Callable
from backend.config import get_settings


class CacheService:
    """Redis cache service with JSON serialization and TTL support."""

    def __init__(self):
        """Initialize Redis connection with error handling and auth support."""
        settings = get_settings()
        try:
            self.redis = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=getattr(settings, 'redis_password', None),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 1 hour)

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            serialized = json.dumps(value)
            self.redis.setex(key, ttl, serialized)
        except redis.RedisError as e:
            raise redis.RedisError(f"Failed to set cache key '{key}': {e}") from e

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized value or None if not found

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            return json.loads(value)
        except redis.RedisError as e:
            raise redis.RedisError(f"Failed to get cache key '{key}': {e}") from e

    def delete(self, key: str) -> None:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            self.redis.delete(key)
        except redis.RedisError as e:
            raise redis.RedisError(f"Failed to delete cache key '{key}': {e}") from e

    def clear_pattern(self, pattern: str) -> None:
        """
        Clear all keys matching a pattern using SCAN (production-safe).

        Args:
            pattern: Redis pattern (e.g., "pdf:123:*")

        Raises:
            redis.RedisError: If Redis operation fails
        """
        try:
            cursor = 0
            keys = []
            # Use SCAN instead of KEYS to avoid blocking Redis
            while True:
                cursor, partial_keys = self.redis.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )
                keys.extend(partial_keys)
                if cursor == 0:
                    break

            # Bulk delete for better performance
            if keys:
                self.redis.delete(*keys)
        except redis.RedisError as e:
            raise redis.RedisError(f"Failed to clear pattern '{pattern}': {e}") from e

    def _make_cache_key(self, prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generate cache key from function name and arguments using JSON + hash.

        Args:
            prefix: Prefix for the cache key
            func_name: Function name
            args: Function positional arguments
            kwargs: Function keyword arguments

        Returns:
            Cache key string with hash to prevent collisions
        """
        # Use JSON serialization + MD5 hash to prevent collisions
        args_dict = {"args": args, "kwargs": kwargs}
        args_json = json.dumps(args_dict, sort_keys=True)
        hash_val = hashlib.md5(args_json.encode()).hexdigest()[:12]
        return f"{prefix}:{func_name}:{hash_val}"


# Global singleton instance with thread-safe initialization
_cache_service_instance: Optional[CacheService] = None
_cache_lock = threading.Lock()


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance (thread-safe singleton pattern).

    Returns:
        CacheService instance
    """
    global _cache_service_instance
    if _cache_service_instance is None:
        with _cache_lock:
            # Double-checked locking for thread safety
            if _cache_service_instance is None:
                _cache_service_instance = CacheService()
    return _cache_service_instance


def cached(ttl: int = 3600, key_prefix: str = "") -> Callable:
    """
    Decorator for automatic caching of function results.

    Args:
        ttl: Time to live in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function with caching

    Example:
        @cached(ttl=300, key_prefix="qa")
        def ask_question(pdf_id: int, question: str):
            # Expensive operation
            return answer
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_service()
            cache_key = cache._make_cache_key(key_prefix, func.__name__, args, kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        return wrapper
    return decorator
