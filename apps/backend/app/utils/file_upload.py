"""
File upload utilities
Handles image uploads to local storage or cloud providers (Cloudinary/AWS S3)
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
import aiofiles


class FileUploadService:
    """Service for handling file uploads"""
    
    # Maximum upload size: 10 MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024
    
    def __init__(self):
        """Initialize file upload service"""
        self.upload_dir = Path("uploads")
        self.images_dir = self.upload_dir / "images"
        self.documents_dir = self.upload_dir / "documents"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate unique filename preserving extension
        
        Args:
            original_filename: Original filename
        
        Returns:
            Unique filename with UUID
        """
        ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate if uploaded file is a valid image (type + size)
        
        Args:
            file: Uploaded file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
        ext = Path(file.filename).suffix.lower()
        
        if ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        # Check content type
        allowed_content_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/bmp",
            "image/tiff",
            "image/webp"
        }
        
        if file.content_type not in allowed_content_types:
            return False, f"Invalid content type: {file.content_type}"
        
        # Check file size (read size header or peek at content)
        if file.size is not None and file.size > FileUploadService.MAX_IMAGE_SIZE:
            max_mb = FileUploadService.MAX_IMAGE_SIZE / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.0f} MB"
        
        return True, None
    
    async def save_upload_file(
        self,
        file: UploadFile,
        destination: str = "images"
    ) -> Tuple[str, str]:
        """
        Save uploaded file to local storage
        
        Args:
            file: Uploaded file
            destination: Destination folder ("images" or "documents")
        
        Returns:
            Tuple of (file_path, file_url)
        """
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename)
        
        # Determine destination directory
        if destination == "images":
            dest_dir = self.images_dir
        elif destination == "documents":
            dest_dir = self.documents_dir
        else:
            dest_dir = self.upload_dir / destination
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = dest_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Generate URL (for local development, this would be a relative path)
        # In production, this would be a full URL
        file_url = f"/uploads/{destination}/{unique_filename}"
        
        return str(file_path), file_url
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local storage
        
        Args:
            file_path: Path to file
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
        
        Returns:
            File size in bytes or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.stat().st_size
            return None
        except Exception:
            return None


class CloudinaryUploadService:
    """Service for uploading files to Cloudinary (optional)"""
    
    def __init__(self):
        """Initialize Cloudinary if credentials are available"""
        self.cloudinary_configured = False
        
        # Check if Cloudinary is configured
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if cloud_name and api_key and api_secret:
            try:
                import cloudinary
                import cloudinary.uploader
                
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
                self.cloudinary_configured = True
                self.cloudinary = cloudinary
            except ImportError:
                print("⚠️  Cloudinary not installed. Install with: pip install cloudinary")
        else:
            print("⚠️  Cloudinary credentials not configured")
    
    async def upload_image(self, file_bytes: bytes, filename: str) -> Optional[str]:
        """
        Upload image to Cloudinary
        
        Args:
            file_bytes: Image bytes
            filename: Original filename
        
        Returns:
            Public URL of uploaded image or None if failed
        """
        if not self.cloudinary_configured:
            return None
        
        try:
            result = self.cloudinary.uploader.upload(
                file_bytes,
                public_id=f"quotmate/{uuid.uuid4()}",
                resource_type="image"
            )
            return result.get("secure_url")
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None


# Singleton instances
file_upload_service = FileUploadService()
cloudinary_service = CloudinaryUploadService()
