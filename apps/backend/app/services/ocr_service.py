import requests
import os
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO
from PIL import Image
import json
import re
import pytesseract
import numpy as np


class OCRService:
    """Service for extracting text from images using NVIDIA NIMs with Tesseract fallback"""
    
    def __init__(self):
        """Initialize OCR engines"""
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        # Vision model: must be a multimodal model that accepts image input
        # Mistral Large 3 675B is text-only — cannot process images
        self.model = os.getenv("NVIDIA_VISION_MODEL", "meta/llama-3.2-11b-vision-instruct")
        self.use_tesseract_fallback = os.getenv("USE_TESSERACT_FALLBACK", "true").lower() == "true"
        
        if not self.api_key:
            print("⚠️  NVIDIA_API_KEY not configured - using Tesseract only")
            self.client = None
        else:
            self.client = True
            print(f"✅ NVIDIA NIMs OCR service configured with model: {self.model}")
        
        # Check Tesseract availability
        try:
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            print("✅ Tesseract OCR available as fallback")
        except Exception:
            self.tesseract_available = False
            print("⚠️  Tesseract OCR not available")
    
    def extract_text_from_bytes(
        self, 
        image_bytes: bytes, 
        language_hints: List[str] = None,
        engine: str = "auto"
    ) -> Dict[str, Any]:
        """
        Extract text from image bytes using specified or auto-selected engine
        
        Args:
            image_bytes: Raw image bytes
            language_hints: List of language codes (e.g., ['en', 'hi'])
            engine: "auto" (try Llama, fallback to Tesseract), "llama", or "tesseract"
        
        Returns:
            Dictionary containing text, confidence, and metadata
        """
        # Force Tesseract if requested
        if engine == "tesseract":
            if self.tesseract_available:
                return self._extract_text_with_tesseract(image_bytes, language_hints)
            else:
                raise Exception("Tesseract OCR not available")
        
        # Try NVIDIA NIMs Llama first (if available and not explicitly Tesseract)
        if self.client and engine in ["auto", "llama"]:
            try:
                result = self._extract_text_with_llama(image_bytes, language_hints)
                result["engine"] = "llama"
                return result
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️  Llama OCR failed: {error_msg}")
                
                # If Tesseract fallback is enabled and available, try it
                if self.use_tesseract_fallback and self.tesseract_available and engine == "auto":
                    print("🔄 Falling back to Tesseract OCR...")
                    try:
                        return self._extract_text_with_tesseract(image_bytes, language_hints)
                    except Exception as tesseract_error:
                        # Both failed, raise original Llama error
                        raise Exception(f"Llama failed: {error_msg}. Tesseract fallback also failed: {str(tesseract_error)}")
                else:
                    # No fallback available or not in auto mode
                    raise e
        
        # No NVIDIA key and Tesseract available
        if self.tesseract_available:
            return self._extract_text_with_tesseract(image_bytes, language_hints)
        
        raise Exception("No OCR engine available. Configure NVIDIA_API_KEY or install Tesseract.")
    
    def _extract_text_with_llama(
        self,
        image_bytes: bytes,
        language_hints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text using NVIDIA NIMs Llama-3.2-90B-Vision
        """
        if not self.client:
            raise Exception("NVIDIA NIMs API not configured. Set NVIDIA_API_KEY environment variable.")
        
        # Compress image to JPEG before base64 encoding to reduce payload
        # Phone photos as PNG can be 3-5 MB; JPEG at quality 85 is ~200-400 KB
        compressed_bytes = self._compress_for_api(image_bytes)
        image_b64 = base64.b64encode(compressed_bytes).decode()
        
        payload_kb = len(image_b64) / 1024
        print(f"  📦 API payload: {payload_kb:.0f} KB base64")
        
        system_instruction = (
            "You are a precise OCR engine. Output ONLY the text found in the image verbatim. "
            "Do NOT add conversational text. Maintain original layout. Use | for table columns. "
            "Preserve all numbers exactly. Write [illegible] for unclear text."
        )

        user_prompt = (
            "Extract ALL text from this handwritten document image exactly as it appears. "
            "Preserve the layout, numbers, and structure. If it's a table or quotation, "
            "preserve columns using | separators."
        )
        
        if language_hints:
            langs = ", ".join(language_hints)
            user_prompt += f" The text is likely in {langs}."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.1,
            "top_p": 0.1
        }
        
        # Retry logic: 1 retry on timeout with 5s backoff
        import time as _time
        max_attempts = 2
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(self.invoke_url, headers=headers, json=payload, timeout=30)
                
                # Log detailed error if request fails
                if response.status_code != 200:
                    error_detail = response.text[:500] 
                    print(f"❌ NVIDIA API Error {response.status_code}: {error_detail}")
                    response.raise_for_status()
                
                result = response.json()
                
                # Extract text from response
                extracted_text = result["choices"][0]["message"]["content"].strip()
                
                # Clean up common AI response artifacts (double safety)
                extracted_text = self._clean_extracted_text(extracted_text)
                
                # Calculate word-level statistics
                words = extracted_text.split()
                word_count = len(words)
                
                # Since Llama doesn't provide per-word confidence, we estimate based on response quality
                # We cap at 98% and assume decent confidence if we got a valid response
                estimated_confidence = min(98.0, 80.0 + (word_count * 0.1)) if word_count > 0 else 0.0
                
                # Generate word confidence list
                word_confidences = [
                    {
                        "word": word,
                        "confidence": round(estimated_confidence, 2)
                    }
                    for word in words
                ]
                
                # Detect language
                detected_language = self._detect_language(extracted_text)
                
                return {
                    "text": extracted_text,
                    "confidence": round(estimated_confidence, 2),
                    "word_confidences": word_confidences,
                    "language": detected_language
                }
                
            except requests.exceptions.Timeout:
                last_error = "NVIDIA NIMs API request timed out"
                if attempt < max_attempts - 1:
                    print(f"⚠️  Timeout on attempt {attempt + 1}, retrying in 2s...")
                    _time.sleep(2)
                    continue
                raise Exception(last_error)
            except requests.exceptions.RequestException as e:
                raise Exception(f"NVIDIA NIMs API error: {str(e)}")
            except (KeyError, IndexError) as e:
                raise Exception(f"Failed to parse NVIDIA NIMs response: {str(e)}")
    
    def _compress_for_api(self, image_bytes: bytes, max_width: int = 1200, quality: int = 75) -> bytes:
        """
        Compress image to JPEG before sending to the API.
        Reduces payload from 3-5 MB (PNG) to 200-400 KB (JPEG).
        
        Does NOT change the image content — just compression format.
        """
        try:
            img = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB if needed (JPEG doesn't support alpha)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too wide (saves API processing time)
            if img.width > max_width:
                ratio = max_width / img.width
                new_h = int(img.height * ratio)
                img = img.resize((max_width, new_h), Image.LANCZOS)
            
            # Save as JPEG
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=quality)
            compressed = buf.getvalue()
            
            original_kb = len(image_bytes) / 1024
            compressed_kb = len(compressed) / 1024
            if compressed_kb < original_kb * 0.8:  # Only log if meaningful compression
                print(f"  🗜️  Image compressed: {original_kb:.0f} KB → {compressed_kb:.0f} KB")
            
            return compressed
        except Exception:
            # If compression fails for any reason, use original bytes
            return image_bytes
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean up extracted text from common LLM artifacts
        """
        # Remove common prefixes LLMs might add
        prefixes_to_remove = [
            "Here is the text from the image:",
            "The text in the image is:",
            "The image contains:",
            "Text extracted:",
            "Extracted text:",
            "Sure, here is the text:",
        ]
        
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        # Remove markdown code blocks if present
        text = re.sub(r'^```[\w]*\n', '', text)
        text = re.sub(r'\n```$', '', text)
        
        return text.strip()
    
    def _detect_language(self, text: str) -> Optional[str]:
        """
        Simple language detection based on character sets
        """
        if not text:
            return None
        
        # Check for Hindi/Devanagari characters
        if any('\u0900' <= char <= '\u097F' for char in text):
            return 'hi'
        
        # Check for Chinese characters
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return 'zh'
        
        # Default to English
        return 'en'
    
    def _extract_text_with_tesseract(
        self,
        image_bytes: bytes,
        language_hints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text using Tesseract OCR (fallback engine)
        """
        if not self.tesseract_available:
            raise Exception("Tesseract OCR not available")
        
        # Tesseract works better with binary images from full preprocessing
        from app.services.image_preprocessing import image_preprocessor
        
        # Apply full preprocessing (binary) for Tesseract
        processed_bytes = image_preprocessor.preprocess_for_ocr(
            image_bytes,
            deskew_image=True,
            enhance=True,
            light_mode=False  # Use full binary preprocessing for Tesseract
        )
        
        image = Image.open(BytesIO(processed_bytes))
        
        # Prepare language parameter (convert from our format to Tesseract format)
        lang_map = {'en': 'eng', 'hi': 'hin', 'zh': 'chi_sim', 'es': 'spa', 'fr': 'fra'}
        if language_hints:
            tesseract_langs = [lang_map.get(lang, lang) for lang in language_hints]
            lang = '+'.join(tesseract_langs)
        else:
            lang = 'eng'
        
        # Get detailed output with confidence
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        
        # Extract text
        text = pytesseract.image_to_string(image, lang=lang).strip()
        
        # Calculate overall confidence from word-level data
        confidences = [conf for conf in data['conf'] if conf != -1]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Build word confidence list
        word_confidences = []
        for i, word in enumerate(data['text']):
            if word.strip() and data['conf'][i] != -1:
                word_confidences.append({
                    "word": word,
                    "confidence": round(float(data['conf'][i]), 2)
                })
        
        detected_language = self._detect_language(text)
        
        return {
            "text": text,
            "confidence": round(overall_confidence, 2),
            "word_confidences": word_confidences,
            "language": detected_language,
            "engine": "tesseract"
        }
    
    def extract_text_from_file(
        self, 
        file_path: str,
        language_hints: List[str] = None
    ) -> Dict[str, Any]:
        """Extract text from image file"""
        with open(file_path, 'rb') as image_file:
            content = image_file.read()
        return self.extract_text_from_bytes(content, language_hints)
    
    def extract_text_from_base64(
        self,
        base64_string: str,
        language_hints: List[str] = None
    ) -> Dict[str, Any]:
        """Extract text from base64 encoded image"""
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        image_bytes = base64.b64decode(base64_string)
        return self.extract_text_from_bytes(image_bytes, language_hints)
    
    def get_document_bounds(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Get bounding boxes for detected text blocks
        Note: NVIDIA NIMs Llama Vision model doesn't provide bounding boxes.
        """
        return []


# Singleton instance
ocr_service = OCRService()