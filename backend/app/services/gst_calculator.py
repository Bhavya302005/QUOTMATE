"""
GST Calculator for Indian taxation
Supports: CGST+SGST (intra-state) and IGST (inter-state)
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict


class GSTCalculator:
    """
    GST Calculator for Indian taxation
    Supports: CGST+SGST (intra-state) and IGST (inter-state)
    """
    
    @staticmethod
    def calculate(
        items: List[Dict],
        is_igst: bool = False,
        discount_percent: float = 0,
        is_gst_on: bool = True,
        manual_total_amount: float = None
    ) -> Dict:
        """
        Calculate GST for quotation items
        
        Args:
            items: List of dicts with {quantity, unit_price, gst_rate, description}
            is_igst: True for inter-state (IGST only), False for intra-state (CGST+SGST)
            discount_percent: Discount percentage on subtotal
            is_gst_on: If False, sets all GST calculations to 0
            manual_total_amount: If provided, overrides the calculated grand_total
        
        Returns:
            Complete calculation breakdown including item totals and GST breakdown
        """
        subtotal = Decimal('0')
        calculated_items = []
        
        # Calculate each item
        for idx, item in enumerate(items):
            qty = Decimal(str(item['quantity']))
            original_price = Decimal(str(item.get('unit_price', 0)))
            
            # If manual total is provided, use 0 for item calculations
            # but preserve the original unit price in the response
            calc_price = Decimal('0') if manual_total_amount is not None else original_price
                
            gst_rate = Decimal(str(item.get('gst_rate', 18)))
            
            # Item calculations
            item_subtotal = qty * calc_price
            
            if is_gst_on:
                item_gst = (item_subtotal * gst_rate / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                item_gst = Decimal('0')
                
            item_total = item_subtotal + item_gst
            
            subtotal += item_subtotal
            
            calculated_items.append({
                **item,
                'unit_price': float(original_price),  # Preserve original unit price
                'item_order': idx + 1,
                'item_subtotal': float(item_subtotal),
                'gst_amount': float(item_gst),
                'total': float(item_total)
            })
        
        # Apply discount on subtotal
        discount_dec = Decimal(str(discount_percent))
        discount_amount = (subtotal * discount_dec / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        taxable_amount = subtotal - discount_amount
        
        # Calculate total GST using weighted average rate
        total_item_gst = sum(Decimal(str(i['gst_amount'])) for i in calculated_items)
        if subtotal > 0:
            effective_gst_rate = (total_item_gst / subtotal * 100)
        else:
            effective_gst_rate = Decimal('18')
        
        # GST on taxable amount (after discount)
        if is_gst_on:
            total_gst = (taxable_amount * effective_gst_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            total_gst = Decimal('0')
        
        # Split GST based on transaction type
        if is_igst:
            # Inter-state: IGST only
            cgst = Decimal('0')
            sgst = Decimal('0')
            igst = total_gst
        else:
            # Intra-state: CGST + SGST (50-50 split)
            cgst = (total_gst / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            sgst = total_gst - cgst  # Remaining to avoid rounding issues
            igst = Decimal('0')
        
        # Calculate grand total
        if manual_total_amount is not None:
            grand_total = Decimal(str(manual_total_amount)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            grand_total = (taxable_amount + total_gst).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        return {
            'items': calculated_items,
            'subtotal': float(subtotal),
            'discount_percent': float(discount_percent),
            'discount_amount': float(discount_amount),
            'taxable_amount': float(taxable_amount),
            'cgst_rate': float(effective_gst_rate / 2) if not is_igst else 0,
            'cgst_amount': float(cgst),
            'sgst_rate': float(effective_gst_rate / 2) if not is_igst else 0,
            'sgst_amount': float(sgst),
            'igst_rate': float(effective_gst_rate) if is_igst else 0,
            'igst_amount': float(igst),
            'total_gst': float(total_gst),
            'grand_total': float(grand_total),
            'is_igst': is_igst,
            'is_gst_on': is_gst_on,
            'manual_total_amount': float(manual_total_amount) if manual_total_amount is not None else None
        }


# Singleton instance
gst_calculator = GSTCalculator()
