from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from typing import DefaultDict, Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.client import PubSub

from backend.config import get_settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    @dataclass
    class Subscription:
        task: asyncio.Task
        pubsub: PubSub

    def __init__(
        self,
        redis_url: Optional[str] = None,
        *,
        redis: Optional[AsyncRedis] = None,
    ) -> None:
        if redis is None:
            if not redis_url:
                raise ValueError(
                    "A redis_url is required when redis client is not provided"
                )
            self._redis = AsyncRedis.from_url(redis_url, decode_responses=True)
        else:
            self._redis = redis
        self._channels: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self._subscriptions: Dict[str, WebSocketManager.Subscription] = {}
        self._lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        ensure_subscription = False
        async with self._lock:
            sockets = self._channels[channel]
            if websocket not in sockets:
                sockets.add(websocket)
            if channel not in self._subscriptions:
                ensure_subscription = True
            count = len(sockets)
        if ensure_subscription:
            await self._ensure_subscription(channel)
        logger.info(
            "WebSocket connected",
            extra={"channel": channel, "connections": count},
        )

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        stop_subscription = False
        async with self._lock:
            sockets = self._channels.get(channel)
            if sockets and websocket in sockets:
                sockets.remove(websocket)
                if not sockets:
                    self._channels.pop(channel, None)
                    stop_subscription = True
            count = len(sockets) if sockets else 0
        if stop_subscription:
            await self._stop_subscription(channel)
        logger.info(
            "WebSocket disconnected",
            extra={"channel": channel, "connections": count},
        )

    async def broadcast(self, channel: str, message: str) -> None:
        await self._redis.publish(channel, message)

    async def publish(self, channel: str, message: str) -> None:
        await self.broadcast(channel, message)

    async def shutdown(self) -> None:
        async with self._lock:
            subscriptions = list(self._subscriptions.items())
            self._subscriptions.clear()
        for channel, subscription in subscriptions:
            subscription.task.cancel()
            with suppress(asyncio.CancelledError):
                await subscription.task
        close = getattr(self._redis, "aclose", None)
        if callable(close):
            await close()
        else:
            await self._redis.close()

    async def _ensure_subscription(self, channel: str) -> None:
        async with self._lock:
            if channel in self._subscriptions:
                return
            pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
            await pubsub.subscribe(channel)
            task = asyncio.create_task(self._listen(channel, pubsub))
            self._subscriptions[channel] = WebSocketManager.Subscription(
                task=task, pubsub=pubsub
            )

    async def _stop_subscription(self, channel: str) -> None:
        subscription: Optional[WebSocketManager.Subscription]
        async with self._lock:
            subscription = self._subscriptions.pop(channel, None)
        if subscription:
            subscription.task.cancel()
            with suppress(asyncio.CancelledError):
                await subscription.task

    async def _listen(self, channel: str, pubsub: PubSub) -> None:
        should_restart = False
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                payload = message.get("data")
                if payload is None:
                    continue
                await self._deliver(channel, str(payload))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Redis pubsub listener error",
                exc_info=exc,
                extra={"channel": channel},
            )
            should_restart = True
        finally:
            with suppress(Exception):
                await pubsub.unsubscribe(channel)
                closer = getattr(pubsub, "aclose", None)
                if callable(closer):
                    await closer()
                else:
                    await pubsub.close()
            async with self._lock:
                existing = self._subscriptions.get(channel)
                if existing and existing.task is asyncio.current_task():
                    self._subscriptions.pop(channel, None)
                    has_listeners = bool(self._channels.get(channel))
                else:
                    has_listeners = False
            if should_restart and has_listeners:
                await self._ensure_subscription(channel)

    async def _deliver(self, channel: str, message: str) -> None:
        sockets = list(self._channels.get(channel, set()))
        if not sockets:
            return
        stale: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_text(message)
            except Exception:
                stale.append(socket)
        if not stale:
            return
        stop_subscription = False
        async with self._lock:
            current = self._channels.get(channel)
            if current:
                for socket in stale:
                    current.discard(socket)
                if not current:
                    self._channels.pop(channel, None)
                    stop_subscription = True
        if stop_subscription:
            await self._stop_subscription(channel)


settings = get_settings()
manager = WebSocketManager(redis_url=settings.redis_url)
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
    loop.create_task(manager.publish(channel, message))
