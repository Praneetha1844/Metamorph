"""A small bounded in-memory store for finished runs."""

from __future__ import annotations

from collections import OrderedDict
from threading import Lock

from .models import RunReport


class RunStore:
    """Keeps the most recent `capacity` reports. Reports are lost on restart (see roadmap)."""

    def __init__(self, capacity: int = 200) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self._capacity = capacity
        self._items: OrderedDict[str, RunReport] = OrderedDict()
        self._lock = Lock()

    def add(self, report: RunReport) -> None:
        with self._lock:
            self._items[report.id] = report
            while len(self._items) > self._capacity:
                self._items.popitem(last=False)

    def get(self, run_id: str) -> RunReport | None:
        with self._lock:
            return self._items.get(run_id)

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
