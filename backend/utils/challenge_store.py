"""
Redis-based challenge store for WebAuthn passkey registration and authentication.

Provides:
- Challenge storage with TTL (time-to-live)
- Challenge retrieval and deletion
- Thread-safe operations for multi-worker deployments
"""

import json
import logging
from typing import Dict, Optional
from redis.asyncio import Redis as AsyncRedis

from backend.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Global Redis client instance
_redis_client: Optional[AsyncRedis] = None


def get_redis_client() -> AsyncRedis:
    """
    Get or create Redis client instance.

    Returns:
        AsyncRedis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = AsyncRedis.from_url(
            settings.redis_url,
            decode_responses=False,  # Store binary data for challenges
        )
    return _redis_client


class ChallengeStore:
    """Redis-based challenge store for WebAuthn challenges."""

    def __init__(self, redis_client: Optional[AsyncRedis] = None):
        """
        Initialize challenge store.

        Args:
            redis_client: Optional Redis client (uses global if not provided)
        """
        self._redis = redis_client or get_redis_client()
        self._key_prefix = "webauthn:challenge:"
        self._ttl_seconds = 300  # 5 minutes TTL for challenges

    async def store(
        self, challenge_key: str, challenge_data: Dict, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store challenge data with TTL.

        Args:
            challenge_key: Unique key for the challenge
            challenge_data: Challenge data dictionary
            ttl_seconds: Optional TTL override (defaults to 300 seconds)
        """
        key = f"{self._key_prefix}{challenge_key}"
        ttl = ttl_seconds or self._ttl_seconds

        try:
            serialized = json.dumps(challenge_data).encode("utf-8")
            await self._redis.setex(key, ttl, serialized)
            logger.debug(f"Stored challenge: {challenge_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Failed to store challenge {challenge_key}: {e}")
            raise

    async def get(self, challenge_key: str) -> Optional[Dict]:
        """
        Retrieve challenge data.

        Args:
            challenge_key: Challenge key to retrieve

        Returns:
            Challenge data dictionary or None if not found/expired
        """
        key = f"{self._key_prefix}{challenge_key}"

        try:
            data = await self._redis.get(key)
            if data is None:
                return None

            challenge_data = json.loads(data.decode("utf-8"))
            logger.debug(f"Retrieved challenge: {challenge_key}")
            return challenge_data
        except Exception as e:
            logger.error(f"Failed to retrieve challenge {challenge_key}: {e}")
            return None

    async def delete(self, challenge_key: str) -> None:
        """
        Delete challenge data.

        Args:
            challenge_key: Challenge key to delete
        """
        key = f"{self._key_prefix}{challenge_key}"

        try:
            await self._redis.delete(key)
            logger.debug(f"Deleted challenge: {challenge_key}")
        except Exception as e:
            logger.error(f"Failed to delete challenge {challenge_key}: {e}")
            # Don't raise - deletion is best-effort

    async def exists(self, challenge_key: str) -> bool:
        """
        Check if challenge exists.

        Args:
            challenge_key: Challenge key to check

        Returns:
            True if challenge exists, False otherwise
        """
        key = f"{self._key_prefix}{challenge_key}"

        try:
            exists = await self._redis.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check challenge {challenge_key}: {e}")
            return False


# Global challenge store instance
challenge_store = ChallengeStore()

