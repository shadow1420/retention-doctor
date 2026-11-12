import os
import shutil
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_STORAGE_DIR = os.path.join(BASE_DIR, "storage")

UPLOADS_DIR = os.path.join(LOCAL_STORAGE_DIR, "uploads")
EXPORTS_DIR = os.path.join(LOCAL_STORAGE_DIR, "exports")
TEMP_DIR = os.path.join(LOCAL_STORAGE_DIR, "temp")
SFX_DIR = os.path.join(LOCAL_STORAGE_DIR, "sfx")

for d in [LOCAL_STORAGE_DIR, UPLOADS_DIR, EXPORTS_DIR, TEMP_DIR, SFX_DIR]:
    os.makedirs(d, exist_ok=True)

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")  # e.g., for Cloudflare R2 or MinIO
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")


class StorageManager:
    """
    Unified storage manager supporting both local filesystem and S3/R2/Supabase cloud storage.
    Default: local filesystem storage with zero dependencies.
    """
    def __init__(self):
        self.backend = STORAGE_BACKEND
        self._s3_client = None

    def _get_s3(self):
        if self._s3_client is None and self.backend in ["s3", "r2"]:
            import boto3
            client_kwargs = {
                "region_name": S3_REGION,
                "aws_access_key_id": AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": AWS_SECRET_ACCESS_KEY
            }
            if S3_ENDPOINT:
                client_kwargs["endpoint_url"] = S3_ENDPOINT
            self._s3_client = boto3.client("s3", **client_kwargs)
        return self._s3_client

    def get_local_path(self, relative_path: str) -> str:
        """Returns normalized absolute path inside local storage."""
        clean = relative_path.lstrip("/\\")
        return os.path.join(LOCAL_STORAGE_DIR, clean)

    def save_local_file(self, source_path: str, destination_folder: str, filename: str) -> str:
        """Copies or moves a file into the local storage folder."""
        dest_dir = os.path.join(LOCAL_STORAGE_DIR, destination_folder)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, filename)
        shutil.copy2(source_path, dest_path)
        return dest_path

    def upload_to_cloud_if_enabled(self, local_filepath: str, cloud_key: str) -> Optional[str]:
        """Uploads a local file to S3/R2 if cloud storage is configured."""
        if self.backend not in ["s3", "r2"] or not S3_BUCKET:
            return None
        try:
            s3 = self._get_s3()
            if s3:
                s3.upload_file(local_filepath, S3_BUCKET, cloud_key)
                if S3_ENDPOINT:
                    return f"{S3_ENDPOINT}/{S3_BUCKET}/{cloud_key}"
                return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{cloud_key}"
        except Exception:
            pass
        return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """Returns disk usage and storage status."""
        total_size = 0
        file_count = 0
        for root, _, files in os.walk(LOCAL_STORAGE_DIR):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_size += os.path.getsize(fp)
                    file_count += 1
                except OSError:
                    pass
        return {
            "backend": self.backend,
            "local_storage_dir": LOCAL_STORAGE_DIR,
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cloud_enabled": bool(self.backend in ["s3", "r2"] and S3_BUCKET)
        }


storage_manager = StorageManager()
