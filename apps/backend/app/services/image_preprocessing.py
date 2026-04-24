"""
Image preprocessing utilities using OpenCV
Enhances image quality for better OCR results
"""

import numpy as np
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional


class ImagePreprocessor:
    """Preprocess images to improve OCR accuracy"""

    @staticmethod
    def _cv2():
        """
        Lazy import OpenCV so backend startup doesn't crash on incompatible builds.
        """
        import cv2

        return cv2
    
    @staticmethod
    def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
        """Convert image bytes to OpenCV format"""
        cv2 = ImagePreprocessor._cv2()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    
    @staticmethod
    def cv2_to_bytes(img: np.ndarray, format: str = 'PNG', quality: int = 85) -> bytes:
        """Convert OpenCV image to bytes"""
        cv2 = ImagePreprocessor._cv2()
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        img_byte_arr = BytesIO()
        if format.upper() == 'JPEG':
            pil_img.save(img_byte_arr, format=format, quality=quality, optimize=True)
        else:
            pil_img.save(img_byte_arr, format=format)
        return img_byte_arr.getvalue()
    
    @staticmethod
    def resize_image(img: np.ndarray, max_width: int = 2048, max_height: int = 2048) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio.
        Higher resolution for better OCR of handwritten text.
        
        Args:
            img: Input image
            max_width: Maximum width
            max_height: Maximum height
        
        Returns:
            Resized image
        """
        cv2 = ImagePreprocessor._cv2()
        height, width = img.shape[:2]
        
        if width <= max_width and height <= max_height:
            return img
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def convert_to_grayscale(img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        cv2 = ImagePreprocessor._cv2()
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    @staticmethod
    def apply_gaussian_blur(img: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur to reduce noise
        
        Args:
            img: Input image
            kernel_size: Size of Gaussian kernel (must be odd)
        
        Returns:
            Blurred image
        """
        cv2 = ImagePreprocessor._cv2()
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    
    @staticmethod
    def apply_adaptive_threshold(img: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text extraction
        
        Args:
            img: Grayscale input image
        
        Returns:
            Binary image
        """
        cv2 = ImagePreprocessor._cv2()
        return cv2.adaptiveThreshold(
            img,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
    
    @staticmethod
    def apply_otsu_threshold(img: np.ndarray) -> np.ndarray:
        """
        Apply Otsu's thresholding method
        
        Args:
            img: Grayscale input image
        
        Returns:
            Binary image
        """
        cv2 = ImagePreprocessor._cv2()
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    @staticmethod
    def remove_noise(img: np.ndarray) -> np.ndarray:
        """
        Remove noise using morphological operations
        
        Args:
            img: Binary input image
        
        Returns:
            Denoised image
        """
        cv2 = ImagePreprocessor._cv2()
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        return img
    
    @staticmethod
    def deskew(img: np.ndarray) -> np.ndarray:
        """
        Deskew the image by detecting and correcting rotation angle
        
        Args:
            img: Input image
        
        Returns:
            Deskewed image
        """
        cv2 = ImagePreprocessor._cv2()
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Invert image
        binary = cv2.bitwise_not(binary)
        
        # Find coordinates of all white pixels
        coords = np.column_stack(np.where(binary > 0))
        
        if len(coords) == 0:
            return img
        
        # Calculate rotation angle
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotate image if angle is significant
        if abs(angle) > 0.5:  # Only rotate if angle is > 0.5 degrees
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                img,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        
        return img
    
    @staticmethod
    def enhance_contrast(img: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE
        
        Args:
            img: Grayscale input image
        
        Returns:
            Contrast-enhanced image
        """
        cv2 = ImagePreprocessor._cv2()
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(img)
    
    @staticmethod
    def preprocess_for_ocr(
        image_bytes: bytes,
        deskew_image: bool = False,
        enhance: bool = True,
        light_mode: bool = True
    ) -> bytes:
        """
        Complete preprocessing pipeline for OCR
        
        Args:
            image_bytes: Raw image bytes
            deskew_image: Whether to deskew the image
            enhance: Whether to enhance contrast
            light_mode: If True, use lighter preprocessing suitable for vision models
        
        Returns:
            Preprocessed image bytes
        """
        cv2 = ImagePreprocessor._cv2()
        # Convert to OpenCV format
        img = ImagePreprocessor.bytes_to_cv2(image_bytes)
        
        # Resize if too large
        img = ImagePreprocessor.resize_image(img)
        
        if light_mode:
            # Light preprocessing: keep COLOR for handwritten blue/black ink
            # Vision models work better with color images that preserve ink contrast
            # Apply mild contrast and sharpness enhancement on the color image
            from PIL import ImageEnhance as PILEnhance
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            pil_img = PILEnhance.Contrast(pil_img).enhance(1.5)
            pil_img = PILEnhance.Sharpness(pil_img).enhance(1.5)
            img_byte_arr = BytesIO()
            pil_img.save(img_byte_arr, format='JPEG', quality=90)
            return img_byte_arr.getvalue()
        
        # Full preprocessing for traditional OCR
        # Deskew if requested
        if deskew_image:
            img = ImagePreprocessor.deskew(img)
        
        # Convert to grayscale
        gray = ImagePreprocessor.convert_to_grayscale(img)
        
        # Enhance contrast if requested
        if enhance:
            gray = ImagePreprocessor.enhance_contrast(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = ImagePreprocessor.apply_gaussian_blur(gray)
        
        # Apply adaptive threshold
        binary = ImagePreprocessor.apply_adaptive_threshold(blurred)
        
        # Remove noise
        denoised = ImagePreprocessor.remove_noise(binary)
        
        # Convert back to bytes
        return ImagePreprocessor.cv2_to_bytes(denoised)


# Singleton instance
image_preprocessor = ImagePreprocessor()
