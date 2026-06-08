"""In-memory Server-Sent Events pub/sub for development.

Production should replace this with Redis pub/sub.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class ScoreEventBus:
    """Per-candidate asyncio queues for streaming score events."""

    def __init__(self) -> None:
        self._queues: dict[str, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)

    def subscribe(self, candidate_id: str) -> asyncio.Queue[dict[str, Any]]:
        """Register a new subscriber queue for a candidate."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._queues[candidate_id].add(queue)
        return queue

    def unsubscribe(self, candidate_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """Remove a subscriber queue when the client disconnects."""
        self._queues[candidate_id].discard(queue)
        if not self._queues[candidate_id]:
            del self._queues[candidate_id]

    async def publish(self, candidate_id: str, event: dict[str, Any]) -> None:
        """Broadcast an event to all subscribers for the candidate."""
        for queue in list(self._queues.get(candidate_id, set())):
            await queue.put(event)


score_event_bus = ScoreEventBus()
