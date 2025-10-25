from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import DefaultDict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._channels: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._channels[channel].add(websocket)
        logger.info(
            "WebSocket connected",
            extra={"channel": channel, "connections": self._count(channel)},
        )

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._channels.get(channel)
            if sockets and websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    self._channels.pop(channel, None)
        logger.info(
            "WebSocket disconnected",
            extra={"channel": channel, "connections": self._count(channel)},
        )

    async def broadcast(self, channel: str, message: str) -> None:
        sockets = list(self._channels.get(channel, set()))
        if not sockets:
            return
        stale: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception:
                stale.append(socket)
        if stale:
            async with self._lock:
                current = self._channels.get(channel)
                if current:
                    for socket in stale:
                        current.discard(socket)
                    if not current:
                        self._channels.pop(channel, None)

    def _count(self, channel: str) -> int:
        sockets = self._channels.get(channel)
        return len(sockets) if sockets else 0


manager = WebSocketManager()
router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def job_updates(websocket: WebSocket, job_id: str) -> None:
    await manager.connect(job_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(job_id, websocket)
    except Exception as exc:  # noqa: BLE001
        logger.warning("WebSocket error", exc_info=exc, extra={"job_id": job_id})
        await manager.disconnect(job_id, websocket)


def broadcast(channel: str, message: str) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning(
            "Dropping WebSocket message, no running loop", extra={"channel": channel}
        )
        return
    loop.create_task(manager.broadcast(channel, message))
