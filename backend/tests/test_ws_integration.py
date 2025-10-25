from __future__ import annotations

import asyncio

import fakeredis
import fakeredis.aioredis
import pytest

from backend.api.ws import WebSocketManager


class _StubWebSocket:
    def __init__(self) -> None:
        self.accepted = asyncio.Event()
        self.messages: asyncio.Queue[str] = asyncio.Queue()

    async def accept(self) -> None:
        self.accepted.set()

    async def send_text(self, message: str) -> None:
        await self.messages.put(message)


@pytest.mark.asyncio
async def test_cross_worker_broadcast_reaches_remote_listener() -> None:
    server = fakeredis.FakeServer()
    redis_a = fakeredis.aioredis.FakeRedis(
        server=server, decode_responses=True, retry_on_timeout=False
    )
    redis_b = fakeredis.aioredis.FakeRedis(
        server=server, decode_responses=True, retry_on_timeout=False
    )

    manager_a = WebSocketManager(redis=redis_a)
    manager_b = WebSocketManager(redis=redis_b)

    socket = _StubWebSocket()
    await manager_b.connect("job-123", socket)
    await asyncio.wait_for(socket.accepted.wait(), timeout=1)

    await manager_a.publish("job-123", "payload")

    delivered = await asyncio.wait_for(socket.messages.get(), timeout=1)
    assert delivered == "payload"

    await manager_b.disconnect("job-123", socket)
    await manager_a.shutdown()
    await manager_b.shutdown()
