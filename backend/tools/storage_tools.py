from pathlib import Path

from backend.config import get_settings


def upload_to_s3(local_path: str, s3_key: str) -> str:
    settings = get_settings()
    bucket = settings.s3_bucket_name
    region = settings.s3_region
    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(local_path)
    return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
