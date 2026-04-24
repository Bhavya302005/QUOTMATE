from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


# OCR Request Schemas
class OCRProcessRequest(BaseModel):
    """Request schema for OCR processing"""
    preprocess: bool = Field(default=True, description="Apply image preprocessing")
    deskew: bool = Field(default=True, description="Deskew the image")
    enhance: bool = Field(default=True, description="Enhance contrast")
    language_hints: Optional[List[str]] = Field(default=None, description="Language hints (e.g., ['en', 'hi'])")


class OCRBase64Request(BaseModel):
    """Request schema for OCR processing from base64 image"""
    image_base64: str = Field(..., description="Base64 encoded image")
    preprocess: bool = Field(default=True, description="Apply image preprocessing")
    deskew: bool = Field(default=True, description="Deskew the image")
    enhance: bool = Field(default=True, description="Enhance contrast")
    language_hints: Optional[List[str]] = Field(default=None, description="Language hints")


# OCR Response Schemas
class WordConfidence(BaseModel):
    """Word-level confidence score"""
    word: str
    confidence: float = Field(..., ge=0, le=100, description="Confidence score (0-100)")


class OCRResult(BaseModel):
    """OCR extraction result"""
    text: str = Field(..., description="Extracted text")
    confidence: float = Field(..., ge=0, le=100, description="Overall confidence score (0-100)")
    word_confidences: List[WordConfidence] = Field(default=[], description="Per-word confidence scores")
    language: Optional[str] = Field(None, description="Detected language code")
    word_count: int = Field(..., ge=0, description="Total number of words detected")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class OCRResponse(BaseModel):
    """Response schema for OCR processing"""
    success: bool = Field(..., description="Whether OCR was successful")
    ocr_result: Optional[OCRResult] = Field(None, description="OCR extraction result")
    original_image_url: Optional[str] = Field(None, description="URL of uploaded image")
    preprocessed_image_url: Optional[str] = Field(None, description="URL of preprocessed image")
    error: Optional[str] = Field(None, description="Error message if failed")
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Processing timestamp")


class DocumentBoundingBox(BaseModel):
    """Bounding box for detected text block"""
    text: str = Field(..., description="Text in this block")
    vertices: List[tuple] = Field(..., description="Bounding box vertices [(x, y), ...]")
    confidence: float = Field(..., ge=0, le=100, description="Confidence score for this block")


class OCRBoundsResponse(BaseModel):
    """Response schema for OCR with bounding boxes"""
    success: bool
    bounds: List[DocumentBoundingBox] = Field(default=[], description="Text blocks with bounding boxes")
    image_url: Optional[str] = None
    error: Optional[str] = None


# Document OCR Schemas
class DocumentOCRRequest(BaseModel):
    """Request to process document and save OCR results"""
    document_id: str = Field(..., description="Document ID to update")
    preprocess: bool = Field(default=True, description="Apply preprocessing")
    save_preprocessed: bool = Field(default=False, description="Save preprocessed image")


class DocumentOCRResponse(BaseModel):
    """Response after processing document OCR"""
    success: bool
    document_id: str
    ocr_result: Optional[OCRResult] = None
    document_updated: bool = Field(default=False, description="Whether document was updated in database")
    error: Optional[str] = None
