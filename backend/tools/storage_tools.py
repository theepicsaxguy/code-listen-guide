"""Storage utilities for interacting with S3."""

from __future__ import annotations

import logging
from pathlib import Path

from backend.config import get_settings


logger = logging.getLogger(__name__)

_CONTENT_TYPE_MAP = {
    ".mp3": "audio/mpeg",
    ".json": "application/json",
    ".txt": "text/plain",
    ".zip": "application/zip",
}


def _placeholder_url(bucket: str, region: str, key: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def upload_to_s3(local_path: str, s3_key: str) -> str:
    """Upload a file to S3 and return the public URL."""

    settings = get_settings()
    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")
    bucket = settings.s3_bucket_name
    region = settings.s3_region
    fallback_url = _placeholder_url(bucket, region, s3_key)
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        if not settings.aws_access_key_id or settings.aws_access_key_id == "aws-access-key":
            logger.warning("AWS credentials not configured; returning placeholder URL")
            return fallback_url
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=region,
        )
        content_type = _CONTENT_TYPE_MAP.get(path.suffix.lower(), "application/octet-stream")
        extra_args = {"ContentType": content_type, "ACL": "public-read"}
        s3_client.upload_file(str(path), bucket, s3_key, ExtraArgs=extra_args)
        url = _placeholder_url(bucket, region, s3_key)
        logger.info("Uploaded %s to %s", local_path, url)
        return url
    except (NoCredentialsError, ClientError) as exc:
        logger.error("Failed to upload to S3: %s", exc)
        return fallback_url
    except ImportError as exc:
        logger.error("boto3 not available: %s", exc)
        return fallback_url
    except Exception as exc:
        logger.error("Unexpected error during S3 upload: %s", exc)
        return fallback_url
