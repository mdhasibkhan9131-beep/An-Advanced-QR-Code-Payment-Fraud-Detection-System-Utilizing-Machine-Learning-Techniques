"""
Abstract state cache interface for rolling sliding window frequency counting.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class StateCacheInterface(ABC):
    """Abstract interface defining required sliding window cache operations."""

    @abstractmethod
    def record_transaction(self, payer_hash: str, timestamp_ms: int, amount: float) -> None:
        """Records a transaction occurrence for sliding window velocity computation."""
        pass

    @abstractmethod
    def get_velocities(self, payer_hash: str, current_time_ms: int) -> Tuple[int, int, int]:
        """
        Calculates transaction frequencies across 3 temporal windows:
        Returns: (count_5min, count_1hour, count_24hour)
        """
        pass

    @abstractmethod
    def get_historical_stats(self, payer_hash: str) -> Tuple[float, float]:
        """
        Returns payer historical monetary baseline:
        Returns: (mean_amount, std_amount)
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Flushes cache state (useful for test isolation)."""
        pass

