"""
StorageService: Handles document, preprocessed image, and rasterized page storage.
Supports Firebase Cloud Storage (landlens-ai-56a07.firebasestorage.app) with graceful
fallback to local filesystem storage for local development and offline environments.
"""
import os
import shutil
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import quote_plus

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_FIREBASE_BUCKET = "landlens-ai-56a07.firebasestorage.app"

class StorageService:
    _firebase_bucket = None
    _initialized = False

    @classmethod
    def _init_storage(cls):
        if cls._initialized:
            return
        cls._initialized = True
        # Try initializing Firebase Admin if credentials are provided
        service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if service_account_path and os.path.exists(service_account_path):
            try:
                import firebase_admin
                from firebase_admin import credentials, storage

                if not firebase_admin._apps:
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': getattr(settings, 'STORAGE_BUCKET', DEFAULT_FIREBASE_BUCKET) or DEFAULT_FIREBASE_BUCKET
                    })
                cls._firebase_bucket = storage.bucket()
                logger.info(f"Firebase Storage successfully initialized for bucket: {cls._firebase_bucket.name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase Storage: {e}. Falling back to local storage.")
                cls._firebase_bucket = None
        else:
            logger.info("No Firebase Service Account detected. StorageService running in Local Storage mode.")

    @classmethod
    def get_upload_dir(cls, subfolder: str = "") -> str:
        base_dir = os.path.abspath(settings.UPLOAD_DIR or "uploads")
        if subfolder:
            target_dir = os.path.join(base_dir, subfolder)
        else:
            target_dir = base_dir
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    @classmethod
    def save_file_bytes(
        cls,
        data: bytes,
        filename: str,
        subfolder: str = "",
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Saves raw bytes either to Firebase Storage or local filesystem.
        """
        cls._init_storage()

        # Firebase Cloud Storage path
        if cls._firebase_bucket:
            try:
                blob_name = f"{subfolder}/{filename}".strip("/") if subfolder else filename
                blob = cls._firebase_bucket.blob(blob_name)
                blob.upload_from_string(data, content_type=content_type)
                try:
                    blob.make_public()
                    public_url = blob.public_url
                except Exception:
                    # Alternative public URL format
                    encoded_blob = quote_plus(blob_name)
                    public_url = f"https://firebasestorage.googleapis.com/v0/b/{cls._firebase_bucket.name}/o/{encoded_blob}?alt=media"

                return {
                    "storage_type": "firebase",
                    "bucket": cls._firebase_bucket.name,
                    "file_path": blob_name,
                    "url": public_url,
                    "file_size": len(data)
                }
            except Exception as err:
                logger.error(f"Error uploading to Firebase Storage: {err}. Falling back to local disk.")

        # Local storage fallback
        dest_dir = cls.get_upload_dir(subfolder)
        file_path = os.path.join(dest_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)

        relative_url = f"/uploads/{subfolder}/{filename}".replace("//", "/") if subfolder else f"/uploads/{filename}"

        return {
            "storage_type": "local",
            "bucket": "local",
            "file_path": file_path,
            "url": relative_url,
            "file_size": len(data)
        }

    @classmethod
    def save_file_from_disk(
        cls,
        source_path: str,
        filename: Optional[str] = None,
        subfolder: str = ""
    ) -> Dict[str, Any]:
        """
        Takes an existing file on disk and registers/caches it in storage.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found at {source_path}")

        target_name = filename or os.path.basename(source_path)
        with open(source_path, "rb") as f:
            contents = f.read()

        return cls.save_file_bytes(contents, target_name, subfolder=subfolder)

    @classmethod
    def cache_rasterized_page(
        cls,
        doc_identifier: str,
        page_num: int,
        image_bytes: bytes
    ) -> str:
        """
        Caches rasterized PDF page image, returns web-accessible URL.
        """
        fname = f"raster_{doc_identifier}_page_{page_num}.png"
        res = cls.save_file_bytes(image_bytes, fname, subfolder="raster_cache", content_type="image/png")
        return res["url"]

    @classmethod
    def cache_preprocessed_image(
        cls,
        doc_identifier: str,
        image_bytes: bytes
    ) -> str:
        """
        Caches enhanced preprocessed image, returns web-accessible URL.
        """
        fname = f"preprocessed_{doc_identifier}.png"
        res = cls.save_file_bytes(image_bytes, fname, subfolder="preprocessed", content_type="image/png")
        return res["url"]

    @classmethod
    def get_public_url(cls, stored_path_or_url: str) -> str:
        """
        Normalizes a stored path or URL into a browser-loadable URL.
        """
        if not stored_path_or_url:
            return ""
        if stored_path_or_url.startswith("http://") or stored_path_or_url.startswith("https://"):
            return stored_path_or_url
        if stored_path_or_url.startswith("/uploads/"):
            return stored_path_or_url
        # If absolute local path within uploads
        upload_dir = cls.get_upload_dir()
        if stored_path_or_url.startswith(upload_dir):
            rel = os.path.relpath(stored_path_or_url, upload_dir).replace("\\", "/")
            return f"/uploads/{rel}"
        return f"/uploads/{os.path.basename(stored_path_or_url)}"
