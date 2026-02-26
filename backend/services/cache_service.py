"""Redis cache service for caching PDF chunks, embeddings, and QA results."""
import json
import redis
from functools import wraps
from typing import Any, Optional, Callable
from backend.config import get_settings


class CacheService:
    """Redis cache service with JSON serialization and TTL support."""

    def __init__(self):
        """Initialize Redis connection."""
        settings = get_settings()
        self.redis = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True
        )

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 1 hour)
        """
        serialized = json.dumps(value)
        self.redis.setex(key, ttl, serialized)

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized value or None if not found
        """
        value = self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)

    def delete(self, key: str) -> None:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete
        """
        self.redis.delete(key)

    def clear_pattern(self, pattern: str) -> None:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Redis pattern (e.g., "pdf:123:*")
        """
        keys = self.redis.keys(pattern)
        if keys:
            for key in keys:
                self.redis.delete(key)

    def _make_cache_key(self, prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generate cache key from function name and arguments.

        Args:
            prefix: Prefix for the cache key
            func_name: Function name
            args: Function positional arguments
            kwargs: Function keyword arguments

        Returns:
            Cache key string
        """
        # Create a simple key from function name and args
        args_str = "_".join(str(arg) for arg in args)
        kwargs_str = "_".join(f"{k}_{v}" for k, v in sorted(kwargs.items()))
        parts = [prefix, func_name, args_str, kwargs_str]
        return ":".join(filter(None, parts))


# Global singleton instance
_cache_service_instance: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance (singleton pattern).

    Returns:
        CacheService instance
    """
    global _cache_service_instance
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
