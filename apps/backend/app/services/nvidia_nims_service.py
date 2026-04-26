"""
NVIDIA NIMs AI Service - Text parsing and meeting summarization
Uses Llama 3.3 70B Instruct as the primary model for all AI text tasks:
- OCR text cleanup and tile merging
- Quotation field extraction from raw OCR text
- Meeting notes summarization (MOM)
"""

import os
import requests
import json
import re
from typing import Dict, List, Optional
from datetime import datetime


class NVIDIANIMsService:
    """NVIDIA NIMs AI service for all text AI tasks"""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        # Primary model: Llama 3.3 70B (fast, reliable, ~0.3s response)
        self.primary_model = "meta/llama-3.3-70b-instruct"
        
        # Build model chain: primary → configured → fallbacks
        configured_model = os.getenv("NVIDIA_CHAT_MODEL")
        self.chat_models = [self.primary_model]
        if configured_model and configured_model not in self.chat_models:
            self.chat_models.append(configured_model)
        for fallback in ["meta/llama-3.1-70b-instruct"]:
            if fallback not in self.chat_models:
                self.chat_models.append(fallback)
        
        if not self.api_key:
            print("⚠️  NVIDIA_API_KEY not set. AI features will not work.")
        else:
            print(f"✅ NVIDIA NIMs configured with primary model: {self.primary_model}")
    
    def _call_model(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> Optional[str]:
        """
        Call the AI model with automatic fallback through the model chain.
        
        Returns the raw text response, or None if all models fail.
        """
        if not self.api_key:
            return None
        
        for model in self.chat_models:
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": temperature,
                        "top_p": 1.00,
                        "max_tokens": max_tokens,
                        "frequency_penalty": 0.00,
                        "presence_penalty": 0.00,
                        "stream": False
                    },
                    timeout=180
                )
                
                if response.status_code == 404:
                    print(f"⚠️  Model {model} not found, trying next...")
                    continue
                
                response.raise_for_status()
                result = response.json()
                ai_output = result['choices'][0]['message']['content'].strip()
                print(f"✅ AI response from {model}: {len(ai_output)} chars")
                return ai_output
                
            except requests.exceptions.RequestException as e:
                print(f"❌ NVIDIA NIMs API error ({model}): {str(e)}")
                continue
        
        return None

    # ========================================================================
    # QUOTATION PARSING - Extract structured data from raw OCR text
    # ========================================================================
    
    def parse_quotation_from_ocr(self, raw_ocr_text: str) -> Dict:
        """
        Parse raw OCR text from a handwritten quotation into structured data.
        Uses AI model for accurate extraction with minimal hallucination.
        
        Returns dict compatible with existing QuotationMapper output format:
        {
            customer_name, customer_phone, customer_email, customer_address,
            customer_gst, items[], discount_percent, confidence_flags[], raw_text
        }
        """
        if not raw_ocr_text or not raw_ocr_text.strip():
            return {
                'customer_name': None,
                'customer_phone': None,
                'customer_email': None,
                'customer_address': None,
                'customer_gst': None,
                'items': [],
                'discount_percent': 0,
                'confidence_flags': ['customer_name', 'items'],
                'raw_text': raw_ocr_text or ''
            }
        
        system_prompt = (
            "You are a precise data extraction assistant specialized in reading handwritten "
            "Indian business quotations and construction/contractor estimates. "
            "You NEVER fabricate, guess, or hallucinate any data. "
            "You ONLY extract information that is EXPLICITLY present in the provided OCR text. "
            "When a value is unclear or missing, you use null instead of guessing. "
            "You are familiar with Indian business terms, units (sq ft, nos, ltrs, pcs, sets), "
            "and currency formats (Rs., ₹, commas in lakhs/thousands)."
        )
        
        user_prompt = f"""Extract structured quotation data from this raw OCR text of a handwritten quotation.

CRITICAL RULES:
1. ONLY extract information that is EXPLICITLY present in the text below.
2. NEVER fabricate, invent, or guess any data - not names, not numbers, not descriptions.
3. If a field is unclear, ambiguous, or missing, set it to null.
4. Preserve item descriptions EXACTLY as they appear in the OCR text. Do not rephrase.
5. For quantities - use the EXACT numbers from the text. If it says "106 sq ft", use 106.
6. For rates/prices - only use numbers actually visible in the text.
7. If an item has quantity but no rate, set rate to null. Do NOT invent a rate.
8. If you see "Rate: 45-50/- per sq ft", use the average or first value as rate.
9. Items may not have individual totals - that's OK, set amount to null.

LUMP-SUM TOTAL DETECTION:
10. Check if the quotation has a single overall total/grand total written (instead of per-item prices).
11. If items are listed with descriptions and quantities but NO individual rates/prices, AND there is an overall total written somewhere (like a circled number, bottom total, side total), set "is_lump_sum_total" to true and put that number in "total_amount".
12. Common patterns: a big number written to the side, bottom, or in a "Total" column without per-item breakdowns.
13. If individual rates ARE given for each item, set "is_lump_sum_total" to false.

RAW OCR TEXT:
---
{raw_ocr_text}
---

Return a JSON object with this EXACT structure:
{{
    "quotation_by": {{
        "company_name": "string or null",
        "date": "string exactly as written or null",
        "phone": "string exactly as written or null",
        "email": "string or null"
    }},
    "customer": {{
        "name": "string or null",
        "phone": "string exactly as written or null",
        "address": "string or null"
    }},
    "items": [
        {{
            "sr_no": 1,
            "description": "EXACT description from the text",
            "quantity": null or number,
            "unit": "sqft, Ton, nos, pcs, sets, ltrs, kg, box, etc. or null",
            "rate": null or number (per unit price),
            "amount": null or number (total for this line),
            "notes": "any bracket notes or sub-text for this item, or null"
        }}
    ],
    "total_amount": null or number,
    "is_lump_sum_total": true or false,
    "notes": "any general notes at the bottom, or null",
    "confidence": "HIGH or MEDIUM or LOW"
}}

Return ONLY valid JSON. No explanation text before or after."""
        
        ai_output = self._call_model(system_prompt, user_prompt, temperature=0.1)
        
        if not ai_output:
            # AI unavailable - return empty with flags
            return {
                'customer_name': None,
                'customer_phone': None,
                'customer_email': None,
                'customer_address': None,
                'customer_gst': None,
                'items': [],
                'discount_percent': 0,
                'confidence_flags': ['customer_name', 'items'],
                'raw_text': raw_ocr_text,
                'ai_model': 'fallback'
            }
        
        parsed = self._extract_json_from_response(ai_output)
        if not parsed:
            print(f"❌ Failed to parse AI JSON response: {ai_output[:300]}")
            return {
                'customer_name': None,
                'customer_phone': None,
                'customer_email': None,
                'customer_address': None,
                'customer_gst': None,
                'items': [],
                'discount_percent': 0,
                'confidence_flags': ['customer_name', 'items'],
                'raw_text': raw_ocr_text,
                'ai_parse_error': True
            }
        
        # Convert AI-parsed format to existing QuotationMapper output format
        return self._convert_ai_parsed_to_mapper_format(parsed, raw_ocr_text)
    
    def _convert_ai_parsed_to_mapper_format(self, parsed: Dict, raw_text: str) -> Dict:
        """
        Convert the AI-parsed quotation JSON into the format that the existing
        frontend and quotation router expect (matching QuotationMapper.map_text_to_quotation output).
        """
        customer = parsed.get('customer', {}) or {}
        quotation_by = parsed.get('quotation_by', {}) or {}
        
        confidence_flags = []
        
        # Extract customer fields
        customer_name = customer.get('name')
        if not customer_name:
            confidence_flags.append('customer_name')
        
        customer_phone = customer.get('phone')
        if not customer_phone:
            confidence_flags.append('customer_phone')
        
        customer_address = customer.get('address')
        customer_email = customer.get('email') or quotation_by.get('email')
        
        # Extract items in the format expected by QuotationItemCreate
        items = []
        raw_items = parsed.get('items', []) or []
        
        for item in raw_items:
            description = item.get('description', '')
            if not description or not str(description).strip():
                continue
            
            quantity = self._parse_number(item.get('quantity'))
            rate = self._parse_number(item.get('rate'))
            amount = self._parse_number(item.get('amount'))
            unit = item.get('unit', 'nos') or 'nos'
            
            # Normalize unit
            unit_lower = str(unit).lower().strip()
            unit_map = {
                'sq ft': 'sqft', 'sqft': 'sqft', 'sft': 'sqft', 'square feet': 'sqft', 'sq feet': 'sqft',
                'nos': 'nos', 'no': 'nos', 'no.': 'nos', 'numbers': 'nos',
                'pcs': 'pcs', 'pc': 'pcs', 'piece': 'pcs', 'pieces': 'pcs',
                'set': 'sets', 'sets': 'sets',
                'ltr': 'ltrs', 'ltrs': 'ltrs', 'liters': 'ltrs', 'litres': 'ltrs',
                'kg': 'kg', 'kgs': 'kg',
                'rft': 'rft', 'running feet': 'rft',
                'bag': 'bags', 'bags': 'bags',
                'ton': 'Ton', 'tons': 'Ton', 'tonne': 'Ton', 'tonnes': 'Ton',
                'box': 'box', 'boxes': 'box',
            }
            unit_normalized = unit_map.get(unit_lower, unit_lower)
            
            # Calculate unit_price from rate or from amount/quantity
            unit_price = rate
            if unit_price is None and amount is not None and quantity and quantity > 0:
                unit_price = amount / quantity
            
            # Default quantity to 1 if we have a description but no quantity
            if quantity is None or quantity <= 0:
                quantity = 1
                confidence_flags.append(f'item_{len(items)+1}_quantity')
            
            if unit_price is None:
                unit_price = 0
                confidence_flags.append(f'item_{len(items)+1}_price')
            
            # Add notes to description if present
            notes = item.get('notes')
            if notes:
                description = f"{description} ({notes})"
            
            mapped_item = {
                'description': str(description).strip(),
                'quantity': float(quantity),
                'unit': unit_normalized,
                'unit_price': round(float(unit_price), 2),
                'gst_rate': 18.0,
                'is_free_text': True,
            }
            items.append(mapped_item)
        
        if len(items) == 0:
            confidence_flags.append('items')
        
        # Extract additional metadata
        company_name = quotation_by.get('company_name')
        quotation_date = quotation_by.get('date')
        company_phone = quotation_by.get('phone')
        company_email = quotation_by.get('email')
        notes = parsed.get('notes')
        ai_confidence = parsed.get('confidence', 'LOW')
        
        # Detect lump-sum total
        is_lump_sum = bool(parsed.get('is_lump_sum_total', False))
        total_amount = self._parse_number(parsed.get('total_amount'))
        
        # Auto-detect lump-sum even if AI didn't flag it:
        # If most items have rate=0/null and total_amount is present, it's lump-sum
        if not is_lump_sum and total_amount and total_amount > 0 and len(items) > 0:
            items_with_price = sum(1 for item in items if item.get('unit_price', 0) > 0)
            if items_with_price < len(items) * 0.3:  # Less than 30% have prices
                is_lump_sum = True
                print(f"🔍 Auto-detected lump-sum total: ₹{total_amount:,.0f} ({items_with_price}/{len(items)} items priced)")
        
        if is_lump_sum and total_amount:
            print(f"💰 Lump-sum quotation detected: ₹{total_amount:,.0f} for {len(items)} items")
        
        return {
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'customer_address': customer_address,
            'customer_gst': None,  # Rarely in handwritten quotations
            'items': items,
            'discount_percent': 0,
            'confidence_flags': list(set(confidence_flags)),
            'raw_text': raw_text,
            # Extra fields for display (not in original mapper but useful)
            'company_name': company_name,
            'quotation_date': quotation_date,
            'company_phone': company_phone,
            'company_email': company_email,
            'notes': notes,
            'ai_confidence': ai_confidence,
            'ai_model': self.primary_model,
            # Lump-sum total fields
            'lump_sum_total': total_amount if is_lump_sum else None,
            'is_lump_sum_total': is_lump_sum,
        }
    
    def _parse_number(self, value) -> Optional[float]:
        """Parse a number from various formats (Indian currency, etc.)"""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = re.sub(r'[₹$,\s]', '', value)
            cleaned = re.sub(r'Rs\.?', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'/-$', '', cleaned)
            cleaned = re.sub(r'/\-', '', cleaned)
            cleaned = cleaned.strip()
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None
    
    # ========================================================================
    # TILE MERGING - Deduplicate overlapping OCR tile texts
    # ========================================================================
    
    def merge_tiled_ocr_texts(self, tile_texts: List[str]) -> str:
        """
        Intelligently merge OCR texts from multiple overlapping tiles of the same image.
        Uses Mistral Large 3 to deduplicate and order the text properly.
        
        Falls back to simple stitching if AI is unavailable.
        """
        if not tile_texts:
            return ""
        if len(tile_texts) == 1:
            return tile_texts[0]
        
        combined = ""
        for i, text in enumerate(tile_texts):
            combined += f"\n--- TILE {i+1} of {len(tile_texts)} ---\n{text}\n"
        
        system_prompt = (
            "You merge overlapping OCR tile texts into a single clean document. "
            "You NEVER add, modify, correct, or rephrase any text. "
            "You ONLY remove duplicates from overlapping regions and order the text correctly."
        )
        
        user_prompt = f"""The following text was extracted from {len(tile_texts)} overlapping vertical tiles of ONE handwritten document image.

Because tiles overlap, some lines appear in BOTH adjacent tiles. Your job:
1. Merge all tiles into ONE coherent text, top to bottom.
2. REMOVE duplicate lines that appear in overlapping regions.
3. Do NOT add any text that isn't in the tiles.
4. Do NOT correct spelling, grammar, or OCR errors.
5. Keep the raw OCR text as-is, just deduplicated.
6. Output ONLY the merged text, nothing else (no "Here is..." prefix).

TILE TEXTS:
{combined}

MERGED TEXT:"""
        
        ai_output = self._call_model(system_prompt, user_prompt, temperature=0.05, max_tokens=4096)
        
        if ai_output:
            # Clean any AI preamble
            cleaned = ai_output.strip()
            prefixes = ["Here is the merged text:", "Merged text:", "MERGED TEXT:"]
            for prefix in prefixes:
                if cleaned.lower().startswith(prefix.lower()):
                    cleaned = cleaned[len(prefix):].strip()
            return cleaned
        
        # Fallback: simple concatenation with newlines
        return "\n".join(tile_texts)

    # ========================================================================
    # WORK ORDER PARSING - Extract structured data from raw OCR text
    # ========================================================================

    def parse_work_order_from_ocr(self, raw_ocr_text: str) -> Dict:
        """
        Parse raw OCR text from a handwritten work order / job card into structured data.

        Returns dict compatible with WorkOrderMapper output format:
        {
            client_name, client_phone, client_email, service_location,
            work_description, assigned_to, remarks,
            materials[], confidence_flags[], raw_text, ai_confidence
        }
        """
        if not raw_ocr_text or not raw_ocr_text.strip():
            return {
                'client_name': None,
                'client_phone': None,
                'client_email': None,
                'service_location': None,
                'work_description': None,
                'assigned_to': None,
                'remarks': None,
                'materials': [],
                'confidence_flags': ['client_name'],
                'raw_text': raw_ocr_text or '',
                'ai_confidence': 'LOW',
            }

        system_prompt = (
            "You are a precise data extraction assistant specialized in reading handwritten "
            "Indian field-service job cards, work orders, and service sheets. "
            "You NEVER fabricate, guess, or hallucinate any data. "
            "You ONLY extract information that is EXPLICITLY present in the provided OCR text. "
            "When a value is unclear or missing, you use null instead of guessing."
        )

        user_prompt = f"""Extract structured work order data from this raw OCR text of a handwritten work order or job card.

CRITICAL RULES:
1. ONLY extract information EXPLICITLY present in the text.
2. NEVER fabricate or invent data. If a field is missing, set it to null.
3. Preserve descriptions EXACTLY as they appear.
4. For quantities, use the EXACT numbers from the text.
5. If material has no unit cost, set unit_cost to null.

RAW OCR TEXT:
---
{raw_ocr_text}
---

Return a JSON object with this EXACT structure:
{{
    "client_name": "string or null",
    "client_phone": "string exactly as written or null",
    "client_email": "string or null",
    "service_location": "full address / site location or null",
    "work_description": "description of the work to be performed or null",
    "assigned_to": "technician / engineer name or null",
    "remarks": "any extra notes or remarks or null",
    "materials": [
        {{
            "material_name": "EXACT name from text",
            "quantity": null or number,
            "unit": "pcs, nos, kg, ltr, sqft, Ton, sets, rolls, box, etc. or null",
            "unit_cost": null or number,
            "total_cost": null or number
        }}
    ],
    "confidence": "HIGH or MEDIUM or LOW"
}}

Return ONLY valid JSON. No explanation text before or after."""

        ai_output = self._call_model(system_prompt, user_prompt, temperature=0.1)

        if not ai_output:
            return {
                'client_name': None,
                'client_phone': None,
                'client_email': None,
                'service_location': None,
                'work_description': None,
                'assigned_to': None,
                'remarks': None,
                'materials': [],
                'confidence_flags': ['client_name'],
                'raw_text': raw_ocr_text,
                'ai_model': 'fallback',
            }

        # Parse AI JSON response
        try:
            # Strip markdown code fences if present
            clean = ai_output.strip()
            for fence in ['```json', '```JSON', '```']:
                if clean.startswith(fence):
                    clean = clean[len(fence):]
            if clean.endswith('```'):
                clean = clean[:-3]
            clean = clean.strip()

            parsed = json.loads(clean)

            materials = []
            for m in parsed.get('materials', []):
                materials.append({
                    'material_name': m.get('material_name') or '',
                    'quantity': m.get('quantity'),
                    'unit': m.get('unit'),
                    'unit_cost': m.get('unit_cost'),
                    'total_cost': m.get('total_cost'),
                })

            confidence_flags = []
            if not parsed.get('client_name'):
                confidence_flags.append('client_name')
            if not materials:
                confidence_flags.append('materials')

            return {
                'client_name': parsed.get('client_name'),
                'client_phone': parsed.get('client_phone'),
                'client_email': parsed.get('client_email'),
                'service_location': parsed.get('service_location'),
                'work_description': parsed.get('work_description'),
                'assigned_to': parsed.get('assigned_to'),
                'remarks': parsed.get('remarks'),
                'materials': materials,
                'confidence_flags': confidence_flags,
                'raw_text': raw_ocr_text,
                'ai_confidence': parsed.get('confidence', 'MEDIUM'),
            }

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Work order AI JSON parse error: {e}")
            return {
                'client_name': None,
                'client_phone': None,
                'client_email': None,
                'service_location': None,
                'work_description': None,
                'assigned_to': None,
                'remarks': None,
                'materials': [],
                'confidence_flags': ['client_name'],
                'raw_text': raw_ocr_text,
                'ai_parse_error': str(e),
            }

    # ========================================================================
    # MEETING SUMMARIZATION (MOM) - Existing functionality, now with Mistral
    # ========================================================================

    def summarize_meeting_notes(
        self,
        raw_notes: str,
        meeting_context: Optional[str] = None
    ) -> Dict:
        """
        Summarize meeting notes using Mistral Large 3 675B.
        
        Args:
            raw_notes: Raw meeting notes text
            meeting_context: Optional context about the meeting
        
        Returns:
            Dictionary with summary, key_points, decisions, action_items, next_steps
        """
        if not self.api_key:
            return self._fallback_extraction(raw_notes)

        try:
            prompt = self._build_summarization_prompt(raw_notes, meeting_context)

            system_prompt = (
                "You are an expert meeting summarizer. Extract key information from meeting notes "
                "and format it as structured JSON. Only include information explicitly mentioned "
                "in the notes. Never fabricate attendees, decisions, or action items."
            )
            
            ai_output = self._call_model(system_prompt, prompt, temperature=0.2, max_tokens=2048)
            
            if ai_output:
                parsed = self._parse_ai_output(ai_output)
                parsed['ai_model'] = self.primary_model
                parsed['confidence'] = self._calculate_confidence(parsed)
                return parsed
            
            return self._fallback_extraction(raw_notes)
            
        except Exception as e:
            print(f"❌ Summarization error: {str(e)}")
            return self._fallback_extraction(raw_notes)
    
    def _build_summarization_prompt(
        self,
        raw_notes: str,
        meeting_context: Optional[str] = None
    ) -> str:
        """Build optimized prompt for meeting summarization"""
        
        context_section = f"\n\nMeeting Context: {meeting_context}" if meeting_context else ""
        
        prompt = f"""Analyze the following meeting notes and extract structured information.

Meeting Notes:
{raw_notes}{context_section}

Please provide a JSON response with the following structure:
{{
  "summary": "A concise 2-3 sentence summary of the meeting",
  "key_points": ["Key point 1", "Key point 2", ...],
  "decisions": ["Decision 1", "Decision 2", ...],
  "action_items": [
    {{
      "title": "Action item title",
      "description": "Brief description",
      "assigned_to": "Person name or null",
      "priority": "low|medium|high"
    }}
  ],
  "next_steps": ["Next step 1", "Next step 2", ...]
}}

Extract:
- Key discussion points (5-7 items)
- Clear decisions made (if any)
- Action items with assignees (if mentioned)
- Next steps and follow-ups

Be concise and factual. Only include information explicitly mentioned in the notes."""

        return prompt
    
    def _parse_ai_output(self, ai_output: str) -> Dict:
        """Parse AI JSON response"""
        parsed = self._extract_json_from_response(ai_output)
        if parsed:
            return {
                'summary': parsed.get('summary', ''),
                'key_points': parsed.get('key_points', []),
                'decisions': parsed.get('decisions', []),
                'action_items': parsed.get('action_items', []),
                'next_steps': parsed.get('next_steps', [])
            }
        
        # Fallback: extract from text
        return self._extract_from_text(ai_output)
    
    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """Extract JSON from AI response, handling markdown code blocks and extra text."""
        if not text:
            return None
        
        # Try direct JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try finding raw JSON object
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _extract_from_text(self, text: str) -> Dict:
        """Extract structured data from plain text response"""
        lines = text.strip().split('\n')
        
        result = {
            'summary': '',
            'key_points': [],
            'decisions': [],
            'action_items': [],
            'next_steps': []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'summary' in line.lower() and ':' in line:
                current_section = 'summary'
                if ':' in line:
                    result['summary'] = line.split(':', 1)[1].strip()
            elif 'key point' in line.lower() or 'discussion' in line.lower():
                current_section = 'key_points'
            elif 'decision' in line.lower():
                current_section = 'decisions'
            elif 'action' in line.lower():
                current_section = 'action_items'
            elif 'next step' in line.lower():
                current_section = 'next_steps'
            elif current_section and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # Extract list item
                item = re.sub(r'^[\d\-•\.\)]+\s*', '', line)
                if current_section == 'action_items':
                    result['action_items'].append({
                        'title': item,
                        'description': '',
                        'assigned_to': None,
                        'priority': 'medium'
                    })
                else:
                    result[current_section].append(item)
        
        return result
    
    def _fallback_extraction(self, raw_notes: str) -> Dict:
        """Simple rule-based extraction when AI is unavailable"""
        lines = raw_notes.strip().split('\n')
        
        return {
            'summary': f"Meeting notes containing {len(lines)} lines of discussion.",
            'key_points': self._extract_bullet_points(raw_notes),
            'decisions': [],
            # Keep fallback conservative to avoid low-quality autogenerated actions.
            'action_items': [],
            'next_steps': [],
            'ai_model': 'fallback',
            'confidence': 50
        }
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        points = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith(('-', '•', '*')) or (line and line[0].isdigit() and '.' in line[:3]):
                point = re.sub(r'^[\d\-•\*\.\)]+\s*', '', line)
                if len(point) > 5:
                    points.append(point)
        return points[:10]  # Limit to 10
    
    def _extract_action_items(self, text: str) -> List[Dict]:
        """Extract action items using patterns"""
        action_items = []
        action_patterns = [
            r'action item[:\s]+(.*?)(?:\n|$)',
            r'todo[:\s]+(.*?)(?:\n|$)',
            r'(.*?)\s+(?:should|must|will|needs to)\s+(.*?)(?:\n|\.)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                title = match[0] if isinstance(match, tuple) else match
                if len(title.strip()) > 5:
                    action_items.append({
                        'title': title.strip()[:200],
                        'description': '',
                        'assigned_to': None,
                        'priority': 'medium'
                    })
        
        return action_items[:10]  # Limit to 10
    
    def _calculate_confidence(self, parsed: Dict) -> int:
        """Calculate confidence score based on extracted data"""
        score = 30  # Base score
        
        if parsed.get('summary'):
            score += 20
        if parsed.get('key_points'):
            score += min(len(parsed['key_points']) * 5, 30)
        if parsed.get('decisions'):
            score += 10
        if parsed.get('action_items'):
            score += 10
        
        return min(score, 95)  # Cap at 95


# Singleton instance
nvidia_nims_service = NVIDIANIMsService()
