"""Utilities for storing deliverables in Amazon S3."""

from __future__ import annotations

import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError

from backend.config import get_settings

logger = logging.getLogger(__name__)


class S3Storage:
    """High-level wrapper around the boto3 S3 client."""

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        *,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        default_acl: str = "private",
    ) -> None:
        self.bucket_name = bucket_name
        self.region = region
        self.default_acl = default_acl
        self._client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
        )

    async def upload_file(
        self,
        local_path: Path,
        s3_key: str,
        *,
        content_type: Optional[str] = None,
        acl: Optional[str] = None,
    ) -> str:
        if not local_path.exists():
            raise FileNotFoundError(local_path)

        detected_type, _ = mimetypes.guess_type(str(local_path))
        resolved_content_type = content_type or detected_type or "application/octet-stream"
        resolved_acl = acl or self.default_acl

        def _upload() -> None:
            self._client.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": resolved_content_type,
                    "ACL": resolved_acl,
                },
            )

        try:
            await asyncio.to_thread(_upload)
        except ClientError as exc:
            logger.error("S3 upload failed", exc_info=exc, extra={"key": s3_key})
            raise

        return self._object_url(s3_key)

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        def _generate() -> str:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )

        try:
            return await asyncio.to_thread(_generate)
        except ClientError as exc:
            logger.error("Failed to generate presigned URL", exc_info=exc, extra={"key": s3_key})
            raise

    async def delete_file(self, s3_key: str) -> None:
        def _delete() -> None:
            self._client.delete_object(Bucket=self.bucket_name, Key=s3_key)

        try:
            await asyncio.to_thread(_delete)
        except ClientError as exc:
            logger.error("Failed to delete S3 object", exc_info=exc, extra={"key": s3_key})
            raise

    async def list_files(self, prefix: str) -> list[str]:
        paginator = self._client.get_paginator("list_objects_v2")

        def _collect() -> list[str]:
            keys: list[str] = []
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                contents: Iterable[dict[str, str]] = page.get("Contents", [])
                for entry in contents:
                    key = entry.get("Key")
                    if key:
                        keys.append(key)
            return keys

        return await asyncio.to_thread(_collect)

    def _object_url(self, s3_key: str) -> str:
        quoted_key = quote(s3_key)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{quoted_key}"


_storage_instance: Optional[S3Storage] = None


def get_storage() -> S3Storage:
    global _storage_instance
    if _storage_instance is None:
        settings = get_settings()
        _storage_instance = S3Storage(
            bucket_name=settings.s3_bucket_name,
            region=settings.s3_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
    return _storage_instance


async def upload_audio_file(job_id: str, chapter_number: int, file_path: str) -> str:
    storage = get_storage()
    path = Path(file_path)
    key = f"jobs/{job_id}/audio/chapter_{chapter_number}{path.suffix or '.mp3'}"
    return await storage.upload_file(path, key, content_type="audio/mpeg")


async def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    storage = get_storage()
    return await storage.generate_presigned_url(s3_key, expiration)


async def delete_job_files(job_id: str) -> None:
    storage = get_storage()
    prefix = f"jobs/{job_id}/"
    keys = await storage.list_files(prefix)
    await asyncio.gather(*(storage.delete_file(key) for key in keys))
