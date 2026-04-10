"""
Unit tests for GSTCalculator service
Tests Indian GST calculation logic: CGST+SGST, IGST, discounts, edge cases
"""

import pytest
from decimal import Decimal
from app.services.gst_calculator import GSTCalculator


@pytest.fixture
def calculator():
    return GSTCalculator()


class TestGSTCalculator:
    """Test suite for GSTCalculator.calculate()"""

    def test_single_item_cgst_sgst(self, calculator):
        """Intra-state: CGST+SGST should split 50-50"""
        items = [{"quantity": 2, "unit_price": 500, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, is_igst=False)

        assert result["subtotal"] == 1000.0
        assert result["cgst_amount"] + result["sgst_amount"] == pytest.approx(180.0, abs=0.01)
        assert result["igst_amount"] == 0
        assert result["grand_total"] == pytest.approx(1180.0, abs=0.01)

    def test_single_item_igst(self, calculator):
        """Inter-state: IGST only, no CGST/SGST"""
        items = [{"quantity": 1, "unit_price": 1000, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, is_igst=True)

        assert result["igst_amount"] == pytest.approx(180.0, abs=0.01)
        assert result["cgst_amount"] == 0
        assert result["sgst_amount"] == 0
        assert result["grand_total"] == pytest.approx(1180.0, abs=0.01)

    def test_discount_applied_before_gst(self, calculator):
        """Discount should apply on subtotal BEFORE GST calculation"""
        items = [{"quantity": 1, "unit_price": 1000, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, is_igst=False, discount_percent=10)

        assert result["subtotal"] == 1000.0
        assert result["discount_amount"] == 100.0
        # Taxable = 900, GST 18% = 162, Total = 900 + 162 = 1062
        assert result["grand_total"] == pytest.approx(1062.0, abs=0.01)

    def test_multiple_items_with_different_rates(self, calculator):
        """Items with different GST rates should calculate correctly"""
        items = [
            {"quantity": 1, "unit_price": 100, "gst_rate": 5, "description": "Food"},
            {"quantity": 1, "unit_price": 100, "gst_rate": 18, "description": "Service"},
        ]
        result = calculator.calculate(items, is_igst=False)

        assert result["subtotal"] == 200.0
        assert len(result["items"]) == 2
        assert result["items"][0]["gst_amount"] == 5.0
        assert result["items"][1]["gst_amount"] == 18.0

    def test_zero_quantity(self, calculator):
        """Zero quantity should result in zero totals"""
        items = [{"quantity": 0, "unit_price": 500, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, is_igst=False)

        assert result["subtotal"] == 0
        assert result["grand_total"] == 0

    def test_empty_items_list(self, calculator):
        """Empty items list should return zero totals"""
        result = calculator.calculate([], is_igst=False)

        assert result["subtotal"] == 0
        assert result["grand_total"] == 0

    def test_item_order_assigned(self, calculator):
        """Each item should get sequential item_order"""
        items = [
            {"quantity": 1, "unit_price": 100, "gst_rate": 18, "description": "A"},
            {"quantity": 1, "unit_price": 200, "gst_rate": 18, "description": "B"},
        ]
        result = calculator.calculate(items)

        assert result["items"][0]["item_order"] == 1
        assert result["items"][1]["item_order"] == 2

    def test_hundred_percent_discount(self, calculator):
        """100% discount should result in zero grand total"""
        items = [{"quantity": 1, "unit_price": 1000, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, discount_percent=100)

        assert result["discount_amount"] == 1000.0
        assert result["grand_total"] == 0

    def test_decimal_precision(self, calculator):
        """Results should be rounded to 2 decimal places"""
        items = [{"quantity": 3, "unit_price": 33.33, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items)

        # Verify no more than 2 decimal places
        assert result["subtotal"] == round(result["subtotal"], 2)
        assert result["grand_total"] == round(result["grand_total"], 2)

    def test_is_gst_on_false(self, calculator):
        """When is_gst_on=False, GST should be 0 and total should be just subtotal minus discount"""
        items = [{"quantity": 2, "unit_price": 500, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, is_gst_on=False)

        assert result["subtotal"] == 1000.0
        assert result["total_gst"] == 0
        assert result["cgst_amount"] == 0
        assert result["sgst_amount"] == 0
        assert result["igst_amount"] == 0
        assert result["grand_total"] == 1000.0
        assert result["items"][0]["gst_amount"] == 0
        assert result["items"][0]["total"] == 1000.0

    def test_manual_total_amount_override(self, calculator):
        """manual_total_amount should override the calculated grand_total and zero out item prices"""
        items = [{"quantity": 2, "unit_price": 500, "gst_rate": 18, "description": "Widget"}]
        result = calculator.calculate(items, manual_total_amount=1500)

        assert result["subtotal"] == 0.0
        assert result["total_gst"] == 0.0
        assert result["items"][0]["unit_price"] == 0.0
        assert result["items"][0]["total"] == 0.0
        
        # Grand total is overridden
        assert result["grand_total"] == 1500.0
