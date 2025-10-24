import logging

logger = logging.getLogger(__name__)


def broadcast(channel: str, message: str) -> None:
    logger.debug("ws broadcast", extra={"channel": channel, "message": message})
