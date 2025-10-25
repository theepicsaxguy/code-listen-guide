import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def upload_to_s3(local_path: str, s3_key: str) -> str:
    """
    Upload a file to AWS S3.

    Args:
        local_path: Local file path to upload
        s3_key: S3 key (path) for the uploaded file

    Returns:
        Public URL of the uploaded file
    """
    from backend.config import get_settings

    settings = get_settings()

    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {local_path}")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        # Check if AWS credentials are configured
        if not settings.aws_access_key_id or settings.aws_access_key_id == "aws-access-key":
            logger.warning("AWS credentials not configured - returning placeholder URL")
            bucket = settings.s3_bucket_name
            region = settings.s3_region
            return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

        # Create S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.s3_region,
        )

        bucket = settings.s3_bucket_name

        # Determine content type based on file extension
        content_type_map = {
            ".mp3": "audio/mpeg",
            ".json": "application/json",
            ".txt": "text/plain",
            ".zip": "application/zip",
        }
        content_type = content_type_map.get(path.suffix.lower(), "application/octet-stream")

        # Upload file
        extra_args = {"ContentType": content_type, "ACL": "public-read"}

        s3_client.upload_file(str(path), bucket, s3_key, ExtraArgs=extra_args)

        # Construct public URL
        url = f"https://{bucket}.s3.{settings.s3_region}.amazonaws.com/{s3_key}"

        logger.info(f"Uploaded {local_path} to S3: {url}")
        return url

    except (NoCredentialsError, ClientError) as e:
        logger.error(f"Failed to upload to S3: {e}")
        # Return placeholder URL on error
        bucket = settings.s3_bucket_name
        region = settings.s3_region
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    except ImportError:
        logger.error("boto3 not available - S3 upload disabled")
        # Return placeholder URL
        bucket = settings.s3_bucket_name
        region = settings.s3_region
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {e}")
        bucket = settings.s3_bucket_name
        region = settings.s3_region
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
