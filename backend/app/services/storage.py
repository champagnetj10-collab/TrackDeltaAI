"""Storage service — upload URLs, download, and file management.

Backed by Supabase Storage's native REST API (not S3) using the project's
service_role key — this avoids needing a separate S3-compatible credential
pair; the same Supabase project covers auth, database, and file storage.
Public method signatures are unchanged from the original boto3-based
implementation so callers (sessions router, process_session task) don't
need to change.
"""
from __future__ import annotations

import httpx

from app.config import settings


class StorageError(Exception):
    """Raised when a Supabase Storage API call fails unexpectedly."""


class StorageService:
    def __init__(self) -> None:
        self._base_url = settings.supabase_url.rstrip("/") + "/storage/v1"
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
            },
            timeout=30.0,
        )

    def generate_upload_url(self, bucket: str, key: str, expiry_seconds: int = 900) -> str:
        """Generate a signed URL the browser can PUT directly to."""
        response = self._client.post(f"{self._base_url}/object/upload/sign/{bucket}/{key}", json={})
        if response.status_code >= 400:
            raise StorageError(f"Failed to sign upload URL: {response.status_code} {response.text}")
        relative_url = response.json()["url"]
        return f"{self._base_url}{relative_url}"

    def generate_download_url(self, bucket: str, key: str, expiry_seconds: int = 3600) -> str:
        """Generate a signed URL for downloading a file."""
        response = self._client.post(
            f"{self._base_url}/object/sign/{bucket}/{key}",
            json={"expiresIn": expiry_seconds},
        )
        if response.status_code >= 400:
            raise StorageError(f"Failed to sign download URL: {response.status_code} {response.text}")
        relative_url = response.json()["signedURL"]
        return f"{self._base_url}{relative_url}"

    def download_file(self, bucket: str, key: str, local_path: str) -> None:
        """Download a file from storage to local disk (used in pipeline workers)."""
        with open(local_path, "wb") as f:
            f.write(self.download_bytes(bucket, key))

    def download_bytes(self, bucket: str, key: str) -> bytes:
        """Download an object directly into memory (used by the processing
        pipeline, which needs the raw .ibt bytes in hand)."""
        response = self._client.get(f"{self._base_url}/object/{bucket}/{key}")
        if response.status_code >= 400:
            raise StorageError(f"Failed to download {bucket}/{key}: {response.status_code} {response.text}")
        return response.content

    def upload_json(self, bucket: str, key: str, data: str) -> None:
        """Upload a JSON string to storage (for processed features / debriefs)."""
        response = self._client.post(
            f"{self._base_url}/object/{bucket}/{key}",
            content=data.encode("utf-8"),
            headers={"Content-Type": "application/json", "x-upsert": "true"},
        )
        if response.status_code >= 400:
            raise StorageError(f"Failed to upload {bucket}/{key}: {response.status_code} {response.text}")

    def file_exists(self, bucket: str, key: str) -> bool:
        """Check if a key exists in storage."""
        response = self._client.head(f"{self._base_url}/object/{bucket}/{key}")
        return response.status_code == 200

    def get_object_size(self, bucket: str, key: str) -> int | None:
        """Return the size in bytes of a storage object, or None if it doesn't
        exist. Used to validate an upload actually landed (and is within size
        limits) before enqueueing processing — the signed upload URL itself
        can't enforce a max size."""
        response = self._client.head(f"{self._base_url}/object/{bucket}/{key}")
        if response.status_code != 200:
            return None
        content_length = response.headers.get("content-length")
        return int(content_length) if content_length is not None else None
