"""
S3 storage service for file uploads and downloads.

This service provides S3 storage utilities used by the audio_agent and other components.
Implementation pending: Requires AWS credentials and bucket configuration.
"""

import boto3
from pathlib import Path
from typing import Optional
from botocore.exceptions import ClientError


class S3Storage:
    """
    Handles file storage operations with AWS S3.

    Implementation Note: This class requires AWS S3 setup with proper credentials.
    Used by backend/tools/storage_tools.py for agent integration.
    """

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize S3 client.

        Note: Uncomment S3 client initialization when AWS credentials are configured.
        """
        self.bucket_name = bucket_name
        self.region = region
        # Uncomment when AWS credentials are configured:
        # self.s3_client = boto3.client('s3', region_name=region)

    async def upload_file(
        self,
        local_path: Path,
        s3_key: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to S3.

        Args:
            local_path: Path to local file
            s3_key: S3 object key (path in bucket)
            content_type: MIME type

        Returns:
            Public URL of uploaded file
        """
        raise NotImplementedError("Implement S3 upload with boto3 when credentials are configured")

    async def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate pre-signed URL for temporary access.

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Pre-signed URL string
        """
        raise NotImplementedError("Implement presigned URL generation when S3 is configured")

    async def delete_file(self, s3_key: str):
        """
        Delete file from S3.

        Args:
            s3_key: S3 object key to delete
        """
        raise NotImplementedError("Implement S3 delete when configured")

    async def list_files(self, prefix: str) -> list:
        """
        List files with given prefix.

        Args:
            prefix: S3 key prefix to filter by

        Returns:
            List of S3 keys matching the prefix
        """
        raise NotImplementedError("Implement S3 list when configured")
