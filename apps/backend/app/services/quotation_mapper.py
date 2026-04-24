"""
OCR to Quotation Mapper Service
Maps OCR extracted text to quotation fields using:
1. AI-powered extraction via Mistral Large 3 675B (primary)
2. Pattern matching / regex (fallback)
"""

import re
from typing import Dict, List, Optional


class QuotationMapper:
    """
    Maps OCR extracted text to quotation fields
    Uses pattern matching for common handwritten formats
    """
    
    # Indian phone patterns
    PHONE_PATTERNS = [
        r'(?:phone|mobile|contact|mob|ph|tel|cell)?[:\s]*([6-9]\d{9})',
        r'(?:phone|mobile|contact|mob|ph|tel)?[:\s]*\+91[\s-]?([6-9]\d{9})',
        r'(?:phone|mobile|contact|mob|ph|tel)?[:\s]*0?([6-9]\d{9})',
    ]
    
    # Email patterns
    EMAIL_PATTERN = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    
    # Customer name patterns
    NAME_PATTERNS = [
        r'(?:customer|client|to|bill\s*to|name|party|buyer)[:\s]+([A-Za-z][A-Za-z\s\.]+?)(?:\n|phone|mobile|address|email|$)',
        r'(?:M/s|Mr\.|Mrs\.|Ms\.)\s+([A-Za-z][A-Za-z\s\.&]+?)(?:\n|phone|mobile|address|$)',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})$',
    ]
    
    # Address patterns
    ADDRESS_PATTERNS = [
        r'(?:address|addr)[:\s]+(.+?)(?:phone|mobile|email|pin|gst|$)',
    ]
    
    # Item patterns (description, quantity, price)
    ITEM_PATTERNS = [
        # "1. 5Ls of white paint K7,200" or "2. 4 buckets of paint K1,200"
        # Group 1: qty, Group 2: unit, Group 3: description, Group 4: price
        r'(?:\d+\.?\s*)?(\d+(?:\.\d+)?)\s*(Ls?|ltrs?|liters?|litres?|buckets?|pails?|rolls?|pcs|pieces?|nos?|units?|kgs?|packets?|boxes?)\s+(?:of\s+)?([A-Za-z][A-Za-z\s\-/,\.]+?)\s+[KRs₹]+\.?\s*(\d+(?:[,\.]\d+)*)',
        # "Product name - 5 nos @ Rs.100" or "Product - 5 @ 100"
        r'([A-Za-z][A-Za-z\s\-\.]+?)[\s\-]+(\d+(?:\.\d+)?)\s*(?:nos|pcs|units?|kg|ltr|ltrs?|piece|box|packet)?\s*[@xX×]\s*(?:Rs\.?|₹|INR|K)?\s*(\d+(?:\.\d+)?)',
        # "Product name    5    100" (multiple spaces)
        r'([A-Za-z][A-Za-z\s]{2,40}?)\s{2,}(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
        # "5 x Product @ 100"
        r'(\d+(?:\.\d+)?)\s*[xX×]\s*([A-Za-z][A-Za-z\s\-\.]+?)\s*[@]\s*(?:Rs\.?|₹|K)?\s*(\d+(?:\.\d+)?)',
        # "Product name qty:5 price:100"
        r'([A-Za-z][A-Za-z\s\-\.]+?)\s+(?:qty|quantity)[:\s]+(\d+(?:\.\d+)?)\s+(?:price|rate)[:\s]+(\d+(?:\.\d+)?)',
    ]
    
    # GST number pattern (Indian GST format)
    GST_PATTERN = r'(?:GST(?:IN)?|GSTIN)[:\s]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})'
    
    # Discount pattern
    DISCOUNT_PATTERN = r'(?:discount|disc)[:\s]*(\d+(?:\.\d+)?)\s*%?'
    
    def map_text_to_quotation(self, ocr_text: str, use_ai: bool = True) -> Dict:
        """
        Extract quotation fields from OCR text.
        
        Strategy:
        1. Try AI-powered extraction first (Mistral Large 3 675B)  
        2. Fall back to regex pattern matching if AI is unavailable
        
        Args:
            ocr_text: Raw text from OCR service
            use_ai: Whether to try AI extraction first (default: True)
        
        Returns:
            Dictionary with extracted fields and confidence flags
        """
        # Try AI-powered extraction first
        if use_ai:
            try:
                from app.services.nvidia_nims_service import nvidia_nims_service
                ai_result = nvidia_nims_service.parse_quotation_from_ocr(ocr_text)
                
                # Check if AI produced usable results
                if ai_result and not ai_result.get('ai_parse_error'):
                    has_name = ai_result.get('customer_name') is not None
                    has_items = len(ai_result.get('items', [])) > 0
                    
                    if has_name or has_items:
                        print(f"✅ AI extraction succeeded: {len(ai_result.get('items', []))} items, confidence: {ai_result.get('ai_confidence', 'N/A')}")
                        return ai_result
                
                print("⚠️  AI extraction produced no usable data, falling back to regex")
            except Exception as e:
                print(f"⚠️  AI extraction failed ({str(e)}), falling back to regex")
        
        # Fallback: regex-based extraction
        return self._regex_map_text_to_quotation(ocr_text)
    
    def _regex_map_text_to_quotation(self, ocr_text: str) -> Dict:
        """
        Extract quotation fields from OCR text
        
        Args:
            ocr_text: Raw text from OCR service
        
        Returns:
            Dictionary with extracted fields and confidence flags
        """
        result = {
            'customer_name': None,
            'customer_phone': None,
            'customer_email': None,
            'customer_address': None,
            'customer_gst': None,
            'items': [],
            'discount_percent': 0,
            'confidence_flags': [],  # Fields that need manual review
            'raw_text': ocr_text
        }
        
        text = ocr_text.strip()
        
        # Extract customer name
        result['customer_name'] = self._extract_customer_name(text)
        if not result['customer_name']:
            result['confidence_flags'].append('customer_name')
        
        # Extract phone
        result['customer_phone'] = self._extract_phone(text)
        if not result['customer_phone']:
            result['confidence_flags'].append('customer_phone')
        
        # Extract email
        result['customer_email'] = self._extract_email(text)
        
        # Extract address
        result['customer_address'] = self._extract_address(text)
        
        # Extract GST number
        result['customer_gst'] = self._extract_gst(text)
        
        # Extract discount
        result['discount_percent'] = self._extract_discount(text)
        
        # Extract items
        result['items'] = self._extract_items(text)
        if len(result['items']) == 0:
            result['confidence_flags'].append('items')
        
        return result
    
    def _extract_customer_name(self, text: str) -> Optional[str]:
        """Extract customer name from text"""
        for pattern in self.NAME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Clean up common prefixes/suffixes
                name = re.sub(r'\s+', ' ', name)  # Normalize spaces
                if 3 <= len(name) <= 100:
                    return name
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        for pattern in self.PHONE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = match.group(1)
                # Return 10-digit phone
                if len(phone) == 10:
                    return phone
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text"""
        match = re.search(self.EMAIL_PATTERN, text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address from text"""
        for pattern in self.ADDRESS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                address = match.group(1).strip()
                # Clean up and limit length
                address = re.sub(r'\s+', ' ', address)
                if 5 <= len(address) <= 500:
                    return address
        return None
    
    def _extract_gst(self, text: str) -> Optional[str]:
        """Extract GST number from text"""
        match = re.search(self.GST_PATTERN, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None
    
    def _extract_discount(self, text: str) -> float:
        """Extract discount percentage from text"""
        match = re.search(self.DISCOUNT_PATTERN, text, re.IGNORECASE)
        if match:
            try:
                discount = float(match.group(1))
                if 0 <= discount <= 100:
                    return discount
            except ValueError:
                pass
        return 0.0
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract line items from text"""
        items = []
        seen_descriptions = set()
        
        # Clean the text - remove "Total" line
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not re.match(r'^\s*(?:\d+\.?\s*)?total\s*[KRs₹]', line.strip(), re.IGNORECASE)]
        cleaned_text = '\n'.join(cleaned_lines)
        
        for pattern_idx, pattern in enumerate(self.ITEM_PATTERNS):
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    if len(match) >= 3:
                        # Pattern 0: qty, unit, description, price (numbered list format)
                        # In this format, price is typically TOTAL price, not unit price
                        if pattern_idx == 0 and len(match) == 4:
                            qty, unit, desc, total_price = match[0], match[1], match[2], match[3]
                            # Clean price - remove commas and convert
                            total_price_clean = str(total_price).replace(',', '')
                            
                            # Validate ranges
                            qty_val = float(qty)
                            total_price_val = float(total_price_clean)
                            
                            # Calculate unit price from total
                            unit_price_val = total_price_val / qty_val if qty_val > 0 else total_price_val
                            
                            # Clean description
                            desc = desc.strip()
                            desc = re.sub(r'\s+', ' ', desc)
                            # Remove trailing punctuation
                            desc = re.sub(r'[,\.;]+$', '', desc)
                            
                            if qty_val <= 0 or qty_val > 10000:
                                continue
                            if total_price_val < 0 or total_price_val > 10000000:
                                continue
                            if len(desc) < 2 or len(desc) > 500:
                                continue
                            
                            # Avoid duplicates
                            desc_lower = desc.lower()
                            if desc_lower in seen_descriptions:
                                continue
                            
                            seen_descriptions.add(desc_lower)
                            
                            # Normalize unit
                            unit_str = str(unit).lower()
                            if unit_str in ['l', 'ls', 'ltr', 'ltrs', 'liter', 'liters', 'litre', 'litres']:
                                unit_str = 'ltrs'
                            elif unit_str in ['bucket', 'buckets', 'pail', 'pails']:
                                unit_str = 'pcs'
                            elif unit_str in ['roll', 'rolls']:
                                unit_str = 'rolls'
                            elif unit_str in ['pc', 'pcs', 'piece', 'pieces']:
                                unit_str = 'pcs'
                            else:
                                unit_str = 'nos'
                            
                            item = {
                                'description': desc,
                                'quantity': qty_val,
                                'unit_price': round(unit_price_val, 2),
                                'unit': unit_str,
                                'gst_rate': 18.0,
                                'is_free_text': True
                            }
                            
                            items.append(item)
                            continue
                        
                        # Handle other pattern formats (where price is unit price)
                        if match[0].replace('.', '').replace(',', '').isdigit():
                            # Pattern: qty x product @ price
                            qty, desc, price = match[0], match[1], match[2]
                        else:
                            # Pattern: product qty price
                            desc, qty, price = match[0], match[1], match[2]
                        
                        unit = 'nos'
                        
                        # Clean description
                        desc = desc.strip()
                        desc = re.sub(r'\s+', ' ', desc)
                        # Remove trailing punctuation
                        desc = re.sub(r'[,\.;]+$', '', desc)
                        
                        # Clean price - remove commas and convert
                        price = str(price).replace(',', '')
                        
                        # Validate ranges
                        qty_val = float(qty)
                        price_val = float(price)
                        
                        if qty_val <= 0 or qty_val > 10000:
                            continue
                        if price_val < 0 or price_val > 10000000:
                            continue
                        if len(desc) < 2 or len(desc) > 500:
                            continue
                        
                        # Avoid duplicates
                        desc_lower = desc.lower()
                        if desc_lower in seen_descriptions:
                            continue
                        
                        seen_descriptions.add(desc_lower)
                        
                        item = {
                            'description': desc,
                            'quantity': qty_val,
                            'unit_price': price_val,
                            'unit': unit,
                            'gst_rate': 18.0,
                            'is_free_text': True
                        }
                        
                        items.append(item)
                        
                except (ValueError, IndexError, ZeroDivisionError) as e:
                    continue
        
        return items


# Singleton instance
quotation_mapper = QuotationMapper()
