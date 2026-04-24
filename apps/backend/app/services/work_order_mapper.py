"""
OCR to Work Order Mapper Service
Maps OCR extracted text to work order fields using:
1. AI-powered extraction via Llama 3.3 70B (primary)
2. Pattern matching / regex (fallback)
"""

import re
import json
from typing import Dict, List, Optional


class WorkOrderMapper:
    """
    Maps OCR extracted text to work order fields.
    Targets field-service job cards, service sheets, and handwritten work orders.
    """

    PHONE_PATTERNS = [
        r'(?:phone|mobile|contact|mob|ph|tel|cell)?[:\s]*([6-9]\d{9})',
        r'(?:phone|mobile|contact|mob|ph|tel)?[:\s]*\+91[\s-]?([6-9]\d{9})',
        r'(?:phone|mobile|contact|mob|ph|tel)?[:\s]*0?([6-9]\d{9})',
    ]

    EMAIL_PATTERN = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'

    CLIENT_NAME_PATTERNS = [
        r'(?:customer|client|to|bill\s*to|name|party|buyer|customer\s*name|client\s*name)[:\s]+([A-Za-z][A-Za-z\s\.]+?)(?:\n|phone|mobile|address|email|$)',
        r'(?:M/s|Mr\.|Mrs\.|Ms\.)\s+([A-Za-z][A-Za-z\s\.&]+?)(?:\n|phone|mobile|address|$)',
    ]

    TECHNICIAN_PATTERNS = [
        r'(?:assigned\s*to|technician|engineer|mechanic|worker|staff|by)[:\s]+([A-Za-z][A-Za-z\s\.]+?)(?:\n|date|time|$)',
    ]

    LOCATION_PATTERNS = [
        r'(?:address|location|site|service\s*location|job\s*site|place)[:\s]+(.+?)(?:\n\n|\n(?:[A-Z]|phone|mobile|email|date)|$)',
    ]

    MATERIAL_PATTERNS = [
        # "5 pcs of X @ Rs.100"
        r'(\d+(?:\.\d+)?)\s*(pcs?|pieces?|nos?|units?|kgs?|ltrs?|liters?|rolls?|boxes?|packets?|sets?|bags?)\s+(?:of\s+)?([A-Za-z][A-Za-z0-9\s\-/,\.]+?)\s+[@xX×]\s*(?:Rs\.?|₹|INR)?\s*(\d+(?:[,\.]\d+)?)',
        # "Product name - 5 nos - Rs.100"
        r'([A-Za-z][A-Za-z0-9\s\-\.]{2,40}?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:nos?|pcs?|units?|kg|ltr|piece|box|packet)?\s*[-–@]\s*(?:Rs\.?|₹)?\s*(\d+(?:\.\d+)?)',
        # "5 x Item @ 100"
        r'(\d+(?:\.\d+)?)\s*[xX×]\s*([A-Za-z][A-Za-z0-9\s\-\.]+?)\s*[@]\s*(?:Rs\.?|₹)?\s*(\d+(?:\.\d+)?)',
    ]

    def map_text_to_work_order(self, ocr_text: str, use_ai: bool = True) -> Dict:
        """
        Extract work order fields from OCR text.

        Strategy:
        1. Try AI-powered extraction (Llama 3.3 70B)
        2. Fall back to regex pattern matching

        Args:
            ocr_text: Raw text from OCR service
            use_ai: Whether to try AI extraction first

        Returns:
            Dictionary with extracted fields and confidence flags
        """
        if use_ai:
            try:
                from app.services.nvidia_nims_service import nvidia_nims_service
                ai_result = nvidia_nims_service.parse_work_order_from_ocr(ocr_text)
                if ai_result and not ai_result.get('ai_parse_error'):
                    has_client = ai_result.get('client_name') is not None
                    if has_client:
                        print(f"✅ AI WO extraction succeeded, confidence: {ai_result.get('ai_confidence', 'N/A')}")
                        return ai_result
                print("⚠️  AI WO extraction produced no usable data, falling back to regex")
            except Exception as e:
                print(f"⚠️  AI WO extraction failed ({e}), falling back to regex")

        return self._regex_map(ocr_text)

    def _regex_map(self, ocr_text: str) -> Dict:
        result = {
            'client_name': None,
            'client_phone': None,
            'client_email': None,
            'service_location': None,
            'work_description': None,
            'assigned_to': None,
            'remarks': None,
            'materials': [],
            'confidence_flags': [],
            'raw_text': ocr_text,
        }

        text = ocr_text.strip()

        result['client_name'] = self._extract_client_name(text)
        if not result['client_name']:
            result['confidence_flags'].append('client_name')

        result['client_phone'] = self._extract_phone(text)
        result['client_email'] = self._extract_email(text)
        result['service_location'] = self._extract_location(text)
        result['work_description'] = self._extract_work_description(text)
        result['assigned_to'] = self._extract_technician(text)
        result['materials'] = self._extract_materials(text)

        return result

    def _extract_client_name(self, text: str) -> Optional[str]:
        for pattern in self.CLIENT_NAME_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                name = m.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                if 2 <= len(name) <= 100:
                    return name
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        for pattern in self.PHONE_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE)
            if m and len(m.group(1)) == 10:
                return m.group(1)
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        m = re.search(self.EMAIL_PATTERN, text, re.IGNORECASE)
        return m.group(1) if m else None

    def _extract_location(self, text: str) -> Optional[str]:
        for pattern in self.LOCATION_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if m:
                loc = m.group(1).strip()
                if 3 <= len(loc) <= 300:
                    return loc
        return None

    def _extract_work_description(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:work\s*description|description|service|job\s*description|scope\s*of\s*work|task)[:\s]+(.+?)(?:\n\n|materials?|signature|remarks?|$)',
            r'(?:work\s*to\s*be\s*done|work\s*performed)[:\s]+(.+?)(?:\n\n|materials?|$)',
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if m:
                desc = m.group(1).strip()
                if 3 <= len(desc) <= 1000:
                    return desc
        return None

    def _extract_technician(self, text: str) -> Optional[str]:
        for pattern in self.TECHNICIAN_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                name = m.group(1).strip()
                if 2 <= len(name) <= 100:
                    return name
        return None

    def _extract_materials(self, text: str) -> List[Dict]:
        materials = []
        for pattern in self.MATERIAL_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                groups = m.groups()
                if len(groups) == 4:
                    qty, unit, name, unit_cost = groups
                elif len(groups) == 3:
                    # Check if first group is a number (qty x name @ price) or name
                    try:
                        float(groups[0].replace(',', ''))
                        qty, name, unit_cost = groups
                        unit = None
                    except ValueError:
                        name, qty, unit_cost = groups
                        unit = None
                else:
                    continue

                try:
                    qty_val = float(str(qty).replace(',', '')) if qty else None
                    cost_val = float(str(unit_cost).replace(',', '')) if unit_cost else None
                    total = round(qty_val * cost_val, 2) if qty_val and cost_val else None
                    materials.append({
                        'material_name': str(name).strip(),
                        'quantity': qty_val,
                        'unit': str(unit).strip() if unit else None,
                        'unit_cost': cost_val,
                        'total_cost': total,
                    })
                except (ValueError, TypeError):
                    continue

        # Deduplicate by name
        seen = set()
        unique = []
        for mat in materials:
            if mat['material_name'] not in seen:
                seen.add(mat['material_name'])
                unique.append(mat)
        return unique


work_order_mapper = WorkOrderMapper()
