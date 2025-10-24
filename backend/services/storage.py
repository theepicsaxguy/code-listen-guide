"""
S3 storage service for file uploads and downloads.

TODO: Implementation steps:
1. Initialize boto3 S3 client
2. Implement upload_file() method
3. Implement generate_presigned_url() method
4. Implement delete_file() method
5. Add error handling for S3 operations
6. Add progress callbacks for large files
"""

import boto3
from pathlib import Path
from typing import Optional
from botocore.exceptions import ClientError

# from backend.config import get_settings


class S3Storage:
    """
    Handles file storage operations with AWS S3.

    TODO:
    - Implement all S3 operations
    - Add error handling
    - Add retry logic
    """

    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize S3 client.

        TODO:
        - Initialize boto3 client
        - Set up bucket name
        """
        self.bucket_name = bucket_name
        self.region = region
        # TODO: Initialize S3 client
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

        TODO:
        1. Upload file to S3
        2. Set appropriate metadata
        3. Return public URL
        4. Add error handling
        """
        # TODO: Implement
        pass

    async def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate pre-signed URL for temporary access.

        TODO:
        - Generate pre-signed URL with expiration
        - Return URL string
        """
        pass

    async def delete_file(self, s3_key: str):
        """
        Delete file from S3.

        TODO:
        - Delete object from S3
        - Handle errors gracefully
        """
        pass

    async def list_files(self, prefix: str) -> list:
        """
        List files with given prefix.

        TODO:
        - List objects in bucket
        - Filter by prefix
        - Return list of keys
        """
        pass
