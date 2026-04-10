from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.ocr import (
    OCRBase64Request,
    OCRResponse,
    OCRResult,
    WordConfidence,
    OCRBoundsResponse,
    DocumentBoundingBox
)
from app.utils.auth import get_current_user
from app.utils.file_upload import file_upload_service
from app.services.ocr_service import ocr_service
from app.services.image_preprocessing import image_preprocessor
from app.services.audit_service import log_audit
from app.services.nvidia_nims_service import nvidia_nims_service
from typing import Optional, List
import time
import asyncio
import io
import difflib
from datetime import datetime
from PIL import Image, ImageOps, ImageStat

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

# --- HELPER FUNCTIONS ---

def analyze_image_complexity(image: Image.Image) -> dict:
    """Decides if the image needs tiling based on resolution and aspect ratio."""
    width, height = image.size
    aspect_ratio = height / width
    
    # Check contrast to see if we really need enhancement
    grayscale = ImageOps.grayscale(image)
    stat = ImageStat.Stat(grayscale)
    rms_contrast = stat.stddev[0] 
    
    strategy = {
        "should_tile": False,
        "tile_count": 1,
        "should_enhance": rms_contrast < 40, # Enhance only if low contrast
    }

    # If image is tall (like A4/Receipt), tiling is needed for Llama 3.2
    if height > 1500 or (aspect_ratio > 1.5 and height > 1000):
        strategy["should_tile"] = True
        strategy["tile_count"] = max(2, int(height / 1000) + 1)
    
    return strategy

def slice_image(image: Image.Image, tiles: int, overlap: int = 450) -> List[bytes]:
    """
    Slices image vertically with significant overlap to ensure no text loss.
    Tiles are saved as compressed JPEG and resized to max 1024px width
    to reduce API payload and prevent timeouts.
    """
    width, height = image.size
    slice_height = height // tiles
    slices = []
    
    # Max tile width — vision model doesn't need full phone-camera resolution
    MAX_TILE_WIDTH = 1600
    
    for i in range(tiles):
        top = max(0, (i * slice_height) - overlap)
        if i == tiles - 1:
            bottom = height 
        else:
            bottom = min(height, ((i + 1) * slice_height) + overlap)
            
        box = (0, top, width, bottom)
        cropped_img = image.crop(box)
        
        # Resize tile if wider than MAX_TILE_WIDTH
        if cropped_img.width > MAX_TILE_WIDTH:
            ratio = MAX_TILE_WIDTH / cropped_img.width
            new_h = int(cropped_img.height * ratio)
            cropped_img = cropped_img.resize((MAX_TILE_WIDTH, new_h), Image.LANCZOS)
        
        # Save as JPEG (not PNG!) — reduces 3-5 MB tiles to 200-400 KB
        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='JPEG', quality=85)
        tile_bytes = img_byte_arr.getvalue()
        slices.append(tile_bytes)
        
        tile_kb = len(tile_bytes) / 1024
        print(f"  📐 Tile {i+1}/{tiles}: {cropped_img.width}×{cropped_img.height}px, {tile_kb:.0f} KB")
        
    return slices

def stitch_text(text_blocks: List[str], overlap_length: int = 400, use_ai: bool = True) -> str:
    """
    Intelligently merges text blocks by finding overlapping sentences 
    and removing duplicates.
    
    If use_ai is True, tries AI-powered deduplication first (Mistral Large 3),
    then falls back to difflib-based stitching.
    """
    if not text_blocks:
        return ""
    
    if len(text_blocks) == 1:
        return text_blocks[0]
    
    # Try AI-powered tile merging first (much better for handwritten docs)
    if use_ai:
        try:
            merged = nvidia_nims_service.merge_tiled_ocr_texts(text_blocks)
            if merged and merged.strip():
                print(f"✅ AI tile merge: {len(text_blocks)} tiles → {len(merged)} chars")
                return merged
        except Exception as e:
            print(f"⚠️  AI tile merge failed ({str(e)}), falling back to difflib stitching")
    
    # Fallback: difflib-based stitching
    full_text = text_blocks[0]
    
    for i in range(1, len(text_blocks)):
        current_block = text_blocks[i]
        # Look at the end of the previous block
        prev_block_end = full_text[-overlap_length:] 
        
        # Find the longest matching sequence between the tail of A and head of B
        matcher = difflib.SequenceMatcher(None, prev_block_end, current_block[:overlap_length])
        match = matcher.find_longest_match(0, len(prev_block_end), 0, len(current_block[:overlap_length]))
        
        if match.size > 15: # If overlap is substantial (>15 chars)
            # We found the cut point. Append only the NEW text.
            new_content_start = match.b + match.size
            full_text += current_block[new_content_start:]
        else:
            # No clear overlap found, append with newline
            full_text += "\n" + current_block
            
    return full_text

# --- ROUTER ENDPOINTS ---

@router.post("/extract", response_model=OCRResponse)
async def process_uploaded_image(
    file: UploadFile = File(..., description="Image file to process"),
    preprocess: bool = Form(default=True),
    deskew: bool = Form(default=True),
    enhance: bool = Form(default=True),
    language_hints: Optional[str] = Form(default=None),
    engine: str = Form(default="auto"),
    mode: str = Form(default="accuracy", description="accuracy (smart tiling) or speed (standard)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        start_process_time = time.time()

        # 1. Validate & Read
        is_valid, error_msg = file_upload_service.validate_image_file(file)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
        
        file_path, file_url = await file_upload_service.save_upload_file(file, "images")
        
        await file.seek(0)
        original_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(original_bytes))
        
        # 2. Analyze Strategy
        img_analysis = analyze_image_complexity(pil_image)
        
        # Override preprocessing based on analysis if in accuracy mode
        should_enhance = enhance
        if mode == "accuracy":
            should_enhance = img_analysis["should_enhance"] and enhance

        # 3. Preprocess
        processed_bytes = original_bytes
        if preprocess:
            processed_bytes = image_preprocessor.preprocess_for_ocr(
                original_bytes,
                deskew_image=deskew,
                enhance=should_enhance 
            )
            pil_image = Image.open(io.BytesIO(processed_bytes))

        # 4. Execute Strategy
        final_text = ""
        combined_confidence = 0.0
        lang_hints_list = [l.strip() for l in language_hints.split(",")] if language_hints else None

        # STRATEGY: TILING (Accuracy Mode + Tall Image)
        if mode == "accuracy" and img_analysis["should_tile"] and engine != "tesseract":
            # Slice with overlap
            slices = slice_image(pil_image, tiles=img_analysis["tile_count"], overlap=450)
            
            # Parallel Execution
            tasks = [
                asyncio.to_thread(
                    ocr_service.extract_text_from_bytes, 
                    s_bytes, 
                    lang_hints_list, 
                    engine
                ) for s_bytes in slices
            ]
            results = await asyncio.gather(*tasks)
            
            # Stitch Results
            valid_results = [r for r in results if r and "text" in r]
            text_segments = [r["text"] for r in valid_results]
            final_text = stitch_text(text_segments, overlap_length=400)
            
            # Avg Confidence
            if valid_results:
                combined_confidence = sum(r["confidence"] for r in valid_results) / len(valid_results)
            
            # Collect Word Confidences (Flattening list of lists)
            all_word_confidences = []
            for r in valid_results:
                if "word_confidences" in r:
                    all_word_confidences.extend(r["word_confidences"])

        # STRATEGY: STANDARD (Speed Mode or Small Image)
        else:
            result = ocr_service.extract_text_from_bytes(processed_bytes, lang_hints_list, engine=engine)
            final_text = result["text"]
            combined_confidence = result["confidence"]
            all_word_confidences = result.get("word_confidences", [])

        # 5. Build Response
        processing_time = (time.time() - start_process_time) * 1000
        word_confidences_objs = [WordConfidence(**wc) for wc in all_word_confidences]
        
        ocr_result = OCRResult(
            text=final_text,
            confidence=combined_confidence,
            word_confidences=word_confidences_objs,
            language=lang_hints_list[0] if lang_hints_list else "unknown",
            word_count=len(word_confidences_objs) if word_confidences_objs else len(final_text.split()),
            processing_time_ms=processing_time
        )
        
        log_audit(
            db=db,
            user_id=current_user.id,
            action="ocr_process",
            entity_type="image",
            entity_id=file_url,
            new_value={
                "strategy": "tiled" if (mode == "accuracy" and img_analysis["should_tile"]) else "standard",
                "confidence": ocr_result.confidence
            }
        )
        
        return OCRResponse(
            success=True,
            ocr_result=ocr_result,
            original_image_url=file_url,
            processed_at=datetime.utcnow()
        )

    except Exception as e:
        return OCRResponse(success=False, error=str(e), processed_at=datetime.utcnow())


@router.post("/process-base64", response_model=OCRResponse)
async def process_base64_image(
    request: OCRBase64Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process base64 encoded image and extract text using enhanced OCR with tiling
    
    - **image_base64**: Base64 encoded image string
    - **preprocess**: Apply preprocessing
    - **deskew**: Deskew image
    - **enhance**: Enhance contrast
    - **language_hints**: Optional language codes
    - **mode**: 'accuracy' (with tiling) or 'speed' (standard)
    """
    try:
        import base64
        from PIL import Image
        
        # Decode base64
        if ',' in request.image_base64:
            request.image_base64 = request.image_base64.split(',')[1]
        
        image_bytes = base64.b64decode(request.image_base64)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Analyze image strategy
        img_analysis = analyze_image_complexity(pil_image)
        mode = getattr(request, 'mode', 'accuracy')  # Default to accuracy mode
        
        # Preprocess if requested
        processed_bytes = image_bytes
        if request.preprocess:
            should_enhance = request.enhance if hasattr(request, 'enhance') else True
            if mode == "accuracy" and not img_analysis.get("should_enhance"):
                should_enhance = False
                
            processed_bytes = image_preprocessor.preprocess_for_ocr(
                image_bytes,
                deskew_image=request.deskew if hasattr(request, 'deskew') else True,
                enhance=should_enhance
            )
        
        # Perform OCR with tiling strategy
        start_time = time.time()
        lang_hints_list = request.language_hints if hasattr(request, 'language_hints') else None
        
        if mode == "accuracy" and img_analysis["should_tile"]:
            # Tiling strategy
            pil_image_processed = Image.open(io.BytesIO(processed_bytes))
            slices = slice_image(pil_image_processed, tiles=img_analysis["tile_count"], overlap=450)
            
            tasks = [
                ocr_service.extract_text_from_bytes(slice_bytes, lang_hints_list, engine="auto")
                for slice_bytes in slices
            ]
            slice_results = await asyncio.gather(*[asyncio.to_thread(lambda t=task: t) for task in tasks])
            
            text_segments = [r["text"] for r in slice_results if r.get("text")]
            final_text = stitch_text(text_segments, overlap_length=400)
            
            all_word_confidences = []
            for r in slice_results:
                all_word_confidences.extend(r.get("word_confidences", []))
            
            combined_confidence = sum(r["confidence"] for r in slice_results) / len(slice_results) if slice_results else 0
        else:
            # Standard strategy
            result = ocr_service.extract_text_from_bytes(processed_bytes, lang_hints_list, engine="auto")
            final_text = result["text"]
            combined_confidence = result["confidence"]
            all_word_confidences = result.get("word_confidences", [])
        
        processing_time = (time.time() - start_time) * 1000
        word_confidences_objs = [WordConfidence(**wc) for wc in all_word_confidences]
        
        ocr_result = OCRResult(
            text=final_text,
            confidence=combined_confidence,
            word_confidences=word_confidences_objs,
            language=lang_hints_list[0] if lang_hints_list else "unknown",
            word_count=len(word_confidences_objs) if word_confidences_objs else len(final_text.split()),
            processing_time_ms=processing_time
        )
        
        log_audit(
            db=db,
            user_id=current_user.id,
            action="ocr_process_base64",
            entity_type="image",
            new_value={
                "strategy": "tiled" if (mode == "accuracy" and img_analysis["should_tile"]) else "standard",
                "confidence": ocr_result.confidence
            }
        )
        
        return OCRResponse(
            success=True,
            ocr_result=ocr_result,
            processed_at=datetime.utcnow()
        )
        
    except Exception as e:
        return OCRResponse(
            success=False,
            error=str(e),
            processed_at=datetime.utcnow()
        )


@router.post("/document-bounds", response_model=OCRBoundsResponse)
async def get_document_bounding_boxes(
    file: UploadFile = File(..., description="Image file"),
    current_user: User = Depends(get_current_user)
):
    """
    Get bounding boxes for detected text blocks in document
    
    Useful for understanding document layout and structure
    """
    try:
        # Validate file
        is_valid, error_msg = file_upload_service.validate_image_file(file)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
        
        # Read file
        image_bytes = await file.read()
        
        # Get bounds (if method exists in new service)
        if hasattr(ocr_service, 'get_document_bounds'):
            bounds = ocr_service.get_document_bounds(image_bytes)
            
            # Convert to response model
            bounding_boxes = [
                DocumentBoundingBox(
                    text=bound["text"],
                    vertices=bound["vertices"],
                    confidence=bound["confidence"]
                ) for bound in bounds
            ]
            
            return OCRBoundsResponse(
                success=True,
                bounds=bounding_boxes
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Document bounds detection not implemented in current OCR service"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        return OCRBoundsResponse(
            success=False,
            error=str(e)
        )


@router.get("/health")
async def ocr_health_check():
    """Check OCR service health and configuration"""
    nvidia_nims_configured = ocr_service.client is not None
    tesseract_available = ocr_service.tesseract_available if hasattr(ocr_service, 'tesseract_available') else False
    
    return {
        "ocr_service": "online",
        "nvidia_nims_api": "configured" if nvidia_nims_configured else "not configured",
        "tesseract_fallback": "available" if tesseract_available else "not available",
        "ocr_model": ocr_service.model,
        "ai_parser_model": nvidia_nims_service.primary_model,
        "features": {
            "intelligent_tiling": True,
            "ai_tile_merging": True,
            "ai_quotation_parsing": True,
            "smart_overlap": True,
            "contrast_analysis": True,
            "parallel_processing": True,
            "preprocessing": True
        },
        "modes": ["accuracy", "speed"],
        "supported_formats": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
    }
