"""
Thread-safe in-memory sliding window TTL cache.
Enables 100% standalone offline velocity computation with sub-millisecond lookups.
"""

import threading
from collections import deque
from typing import Tuple, Dict, Deque
from backend.cache.base import StateCacheInterface


class InMemoryTTLCache(StateCacheInterface):
    """Thread-safe in-memory sliding window cache."""

    def __init__(self):
        self._lock = threading.Lock()
        # Maps payer_hash -> deque of (timestamp_ms, amount)
        self._store: Dict[str, Deque[Tuple[int, float]]] = {}

    def record_transaction(self, payer_hash: str, timestamp_ms: int, amount: float) -> None:
        with self._lock:
            if payer_hash not in self._store:
                self._store[payer_hash] = deque()
            self._store[payer_hash].append((timestamp_ms, amount))
            self._evict_expired(payer_hash, timestamp_ms)

    def _evict_expired(self, payer_hash: str, current_time_ms: int) -> None:
        """Evicts entries older than 24 hours (86,400,000 ms)."""
        cutoff = current_time_ms - 86_400_000
        q = self._store[payer_hash]
        while q and q[0][0] < cutoff:
            q.popleft()

    def get_velocities(self, payer_hash: str, current_time_ms: int) -> Tuple[int, int, int]:
        with self._lock:
            if payer_hash not in self._store:
                return (0, 0, 0)

            self._evict_expired(payer_hash, current_time_ms)
            records = self._store[payer_hash]

            cutoff_5m = current_time_ms - 300_000
            cutoff_1h = current_time_ms - 3_600_000
            cutoff_24h = current_time_ms - 86_400_000

            count_5m = sum(1 for t, _ in records if t >= cutoff_5m)
            count_1h = sum(1 for t, _ in records if t >= cutoff_1h)
            count_24h = sum(1 for t, _ in records if t >= cutoff_24h)

            return (count_5m, count_1h, count_24h)

    def get_historical_stats(self, payer_hash: str) -> Tuple[float, float]:
        with self._lock:
            if payer_hash not in self._store or len(self._store[payer_hash]) < 2:
                # Return default population assumptions if insufficient history
                return (50.0, 30.0)

            amounts = [amt for _, amt in self._store[payer_hash]]
            mean_val = sum(amounts) / len(amounts)
            variance = sum((x - mean_val) ** 2 for x in amounts) / len(amounts)
            std_val = max(variance ** 0.5, 1.0)
            return (float(mean_val), float(std_val))

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Global in-memory cache instance
cache_instance = InMemoryTTLCache()
