"""Tests for plan cache system."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from promptbim.cache.cache_key import compute_cache_key
from promptbim.cache.store import CacheStore
from promptbim.schemas.land import LandParcel
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture
def land():
    return LandParcel(
        name="Test",
        boundary=[(0, 0), (30, 0), (30, 30), (0, 30)],
        area_sqm=900.0,
    )


@pytest.fixture
def zoning():
    return ZoningRules()


@pytest.fixture
def store(tmp_path):
    return CacheStore(cache_dir=tmp_path / "cache")


class TestCacheKey:
    """Test cache key computation."""

    def test_same_input_same_key(self, land, zoning):
        k1 = compute_cache_key("build a house", land, zoning)
        k2 = compute_cache_key("build a house", land, zoning)
        assert k1 == k2

    def test_different_prompt_different_key(self, land, zoning):
        k1 = compute_cache_key("build a house", land, zoning)
        k2 = compute_cache_key("build a school", land, zoning)
        assert k1 != k2

    def test_case_insensitive(self, land, zoning):
        k1 = compute_cache_key("Build a House", land, zoning)
        k2 = compute_cache_key("build a house", land, zoning)
        assert k1 == k2

    def test_key_is_hex_string(self, land, zoning):
        key = compute_cache_key("test", land, zoning)
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)


class TestCacheStore:
    """Test cache store put/get/invalidate/clear."""

    def test_put_and_get(self, store):
        store.put("testkey123", {"result": "success"})
        data = store.get("testkey123")
        assert data == {"result": "success"}

    def test_get_nonexistent(self, store):
        assert store.get("nonexistent") is None

    def test_invalidate(self, store):
        store.put("key1", {"a": 1})
        assert store.invalidate("key1")
        assert store.get("key1") is None

    def test_invalidate_nonexistent(self, store):
        assert not store.invalidate("nope")

    def test_clear_all(self, store):
        store.put("k1", {"a": 1})
        store.put("k2", {"b": 2})
        count = store.clear_all()
        assert count == 2
        assert store.get("k1") is None

    def test_list_entries(self, store):
        store.put("k1", {"a": 1})
        store.put("k2", {"b": 2})
        entries = store.list_entries()
        assert len(entries) == 2


class TestCacheTTL:
    """Test cache TTL expiration."""

    def test_expired_entry_returns_none(self, store):
        store.put("old", {"data": 1})
        # Manually set creation time to past
        import json

        path = store._key_path("old")
        data = json.loads(path.read_text())
        data["_cache_created"] = time.time() - (8 * 86400)  # 8 days ago
        path.write_text(json.dumps(data))

        assert store.get("old") is None

    def test_fresh_entry_returns_data(self, store):
        store.put("fresh", {"data": 1})
        assert store.get("fresh") == {"data": 1}


class TestCacheVersionMismatch:
    """Test version mismatch invalidation."""

    def test_version_mismatch_invalidates(self, store):
        store.put("versioned", {"data": 1})
        # Change the stored version
        import json

        path = store._key_path("versioned")
        data = json.loads(path.read_text())
        data["_cache_version"] = "0.0.1"
        path.write_text(json.dumps(data))

        assert store.get("versioned") is None


class TestCacheLRU:
    """Test LRU eviction."""

    def test_eviction_when_full(self, tmp_path):
        import promptbim.cache.store as store_mod

        with patch.object(store_mod, "CACHE_MAX_ENTRIES", 3):
            store = CacheStore(cache_dir=tmp_path / "lru_cache")
            store.put("k1", {"a": 1})
            time.sleep(0.01)
            store.put("k2", {"b": 2})
            time.sleep(0.01)
            store.put("k3", {"c": 3})
            time.sleep(0.01)
            # This should evict k1 (oldest)
            store.put("k4", {"d": 4})

            assert store.get("k4") is not None
            # k1 should have been evicted
            entries = store.list_entries()
            assert len(entries) <= 3


class TestCacheConcurrency:
    """Task 8: Concurrent read/write stress tests for cache with LOCK_SH."""

    def test_concurrent_put_get(self, tmp_path):
        """Multiple writers and readers should not corrupt data."""
        import threading

        store = CacheStore(cache_dir=tmp_path / "concurrent_cache")
        errors = []

        def writer(key_suffix):
            try:
                for i in range(10):
                    store.put(f"key_{key_suffix}_{i}", {"val": i, "writer": key_suffix})
            except Exception as e:
                errors.append(e)

        def reader(key_suffix):
            try:
                for i in range(10):
                    result = store.get(f"key_{key_suffix}_{i}")
                    # May be None if writer hasn't written yet — that's fine
                    if result is not None:
                        assert "val" in result
            except Exception as e:
                errors.append(e)

        threads = []
        for t in range(4):
            threads.append(threading.Thread(target=writer, args=(t,)))
            threads.append(threading.Thread(target=reader, args=(t,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent cache errors: {errors}"

    def test_concurrent_read_during_write(self, tmp_path):
        """Reader should get complete JSON or None, never partial data."""
        import threading

        store = CacheStore(cache_dir=tmp_path / "rw_cache")
        store.put("shared", {"initial": True})
        read_results = []

        def continuous_writer():
            for i in range(20):
                store.put("shared", {"iteration": i, "data": "x" * 100})

        def continuous_reader():
            for _ in range(20):
                result = store.get("shared")
                if result is not None:
                    read_results.append(result)

        w = threading.Thread(target=continuous_writer)
        r = threading.Thread(target=continuous_reader)
        w.start()
        r.start()
        w.join()
        r.join()

        # All reads should have valid structure (never partial JSON)
        for result in read_results:
            assert isinstance(result, dict)

    def test_read_lock_does_not_block_other_readers(self, tmp_path):
        """Multiple concurrent readers should not deadlock."""
        import threading

        store = CacheStore(cache_dir=tmp_path / "read_lock_cache")
        store.put("readtest", {"data": "parallel_read"})
        results = []

        def reader():
            val = store.get("readtest")
            results.append(val)

        threads = [threading.Thread(target=reader) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 8
        assert all(r == {"data": "parallel_read"} for r in results)


class TestCacheCLI:
    """Test CLI cache commands."""

    def test_cache_stats(self, tmp_path, capsys):
        from promptbim.cache.store import CacheStore

        store = CacheStore(cache_dir=tmp_path / "cli_cache")
        store.put("test", {"data": 1})
        entries = store.list_entries()
        assert len(entries) == 1
