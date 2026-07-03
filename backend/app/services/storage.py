"""S3 storage service — upload URLs, download, and file management."""
import boto3
from botocore.exceptions import ClientError
from app.config import settings


class StorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

    def generate_upload_url(self, bucket: str, key: str, expiry_seconds: int = 900) -> str:
        """Generate a presigned URL for direct S3 upload from the browser."""
        url: str = self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key, "ContentType": "application/octet-stream"},
            ExpiresIn=expiry_seconds,
        )
        return url

    def generate_download_url(self, bucket: str, key: str, expiry_seconds: int = 3600) -> str:
        """Generate a presigned URL for downloading a file."""
        url: str = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiry_seconds,
        )
        return url

    def download_file(self, bucket: str, key: str, local_path: str) -> None:
        """Download a file from S3 to local disk (used in pipeline workers)."""
        self.client.download_file(bucket, key, local_path)

    def download_bytes(self, bucket: str, key: str) -> bytes:
        """Download an object directly into memory (used by the processing pipeline,
        which needs the raw .ibt bytes in hand rather than a path on disk)."""
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    def upload_json(self, bucket: str, key: str, data: str) -> None:
        """Upload a JSON string to S3 (for processed features / debriefs)."""
        self.client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data.encode("utf-8"),
            ContentType="application/json",
        )

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if a key exists in S3."""
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False
