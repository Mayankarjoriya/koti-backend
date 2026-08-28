import logging
from typing import Tuple
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from config import settings

logger = logging.getLogger(__name__)


def _configure_cloudinary():
    """Configure Cloudinary with credentials from settings."""
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise ValueError("CLOUDINARY_CLOUD_NAME is not configured in .env")
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_project_image(file: UploadFile, folder: str = "projects") -> Tuple[str, str]:
    """
    Upload an image file to Cloudinary.

    Returns:
        Tuple of (secure_url, public_id)
    """
    _configure_cloudinary()

    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Allowed: JPEG, PNG, WebP, GIF."
        )

    try:
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},  # max size
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ]
        )
        secure_url: str = result["secure_url"]
        public_id: str = result["public_id"]
        logger.info(f"[cloudinary] Uploaded image: {public_id}")
        return secure_url, public_id
    except Exception as exc:
        logger.error(f"[cloudinary] Upload failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image upload to Cloudinary failed. Check your credentials."
        )


def delete_project_image(public_id: str) -> None:
    """Delete an image from Cloudinary by its public_id."""
    if not public_id:
        return
    try:
        _configure_cloudinary()
        cloudinary.uploader.destroy(public_id)
        logger.info(f"[cloudinary] Deleted image: {public_id}")
    except Exception as exc:
        logger.warning(f"[cloudinary] Failed to delete image {public_id}: {exc}")
