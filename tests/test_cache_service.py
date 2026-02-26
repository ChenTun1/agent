"""Tests for Redis cache service."""
import pytest
import time
from unittest.mock import MagicMock, patch
from backend.services.cache_service import CacheService, get_cache_service, cached


@pytest.fixture
def cache_service():
    """Create a cache service instance with mocked Redis."""
    with patch('backend.services.cache_service.redis.Redis') as mock_redis:
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        service = CacheService()
        service.redis = mock_client
        yield service


def test_set_and_get(cache_service):
    """Test basic set and get operations."""
    # Arrange
    test_data = {"name": "John", "age": 30}
    cache_service.redis.get.return_value = '{"name": "John", "age": 30}'

    # Act
    cache_service.set("test_key", test_data, ttl=60)
    result = cache_service.get("test_key")

    # Assert
    cache_service.redis.setex.assert_called_once()
    cache_service.redis.get.assert_called_once_with("test_key")
    assert result == test_data


def test_get_nonexistent_key(cache_service):
    """Test getting a non-existent key returns None."""
    # Arrange
    cache_service.redis.get.return_value = None

    # Act
    result = cache_service.get("nonexistent_key")

    # Assert
    assert result is None


def test_ttl_expiration(cache_service):
    """Test TTL expiration (simulate with mock)."""
    # Arrange
    cache_service.redis.get.side_effect = [
        '{"data": "value"}',  # First call returns data
        None  # Second call returns None (expired)
    ]

    # Act
    result1 = cache_service.get("test_key")
    result2 = cache_service.get("test_key")

    # Assert
    assert result1 == {"data": "value"}
    assert result2 is None


def test_delete(cache_service):
    """Test delete operations."""
    # Act
    cache_service.delete("test_key")

    # Assert
    cache_service.redis.delete.assert_called_once_with("test_key")


def test_clear_pattern(cache_service):
    """Test pattern-based cache clearing."""
    # Arrange
    cache_service.redis.keys.return_value = [
        b"pdf:123:chunk:1",
        b"pdf:123:chunk:2",
        b"pdf:123:metadata"
    ]

    # Act
    cache_service.clear_pattern("pdf:123:*")

    # Assert
    cache_service.redis.keys.assert_called_once_with("pdf:123:*")
    assert cache_service.redis.delete.call_count == 3


def test_cache_decorator(cache_service):
    """Test cache decorator functionality."""
    # Create a test function with the decorator
    call_count = {"value": 0}

    @cached(ttl=60, key_prefix="test")
    def expensive_function(x, y):
        call_count["value"] += 1
        return x + y

    # Mock the cache service
    with patch('backend.services.cache_service.get_cache_service', return_value=cache_service):
        # First call - cache miss
        cache_service.redis.get.return_value = None
        result1 = expensive_function(5, 3)

        # Second call - cache hit
        cache_service.redis.get.return_value = '8'
        result2 = expensive_function(5, 3)

    # Assert
    assert result1 == 8
    assert call_count["value"] == 1  # Function called once
    # Note: With cache hit, we'd expect call_count to still be 1


