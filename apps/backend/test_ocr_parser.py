#!/usr/bin/env python3
"""
Test OCR parser with the user's sample data
"""
from app.services.quotation_mapper import quotation_mapper

# Sample OCR text from user
sample_text = """1. 5Ls of white paint for the ceiling and wall under coat K7,200
2. 4 buckets of super sheen washable paint for final walls K7,200
3. 15 ltrs of gloss paint for door frames K1,200
4. 20 pcs of painting brushes K20
5. 2 pails of ceiling K2,000
6. 1 roll of wall paper K900
7. 1 roll of wall paper K900
8. Total K21,000"""

print("🧪 Testing OCR Parser\n")
print("=" * 60)
print("Input Text:")
print("=" * 60)
print(sample_text)
print("\n" + "=" * 60)
print("Parsed Results:")
print("=" * 60 + "\n")

result = quotation_mapper.map_text_to_quotation(sample_text)

print(f"Customer Name: {result['customer_name']}")
print(f"Customer Phone: {result['customer_phone']}")
print(f"Customer Email: {result['customer_email']}")
print(f"Customer Address: {result['customer_address']}")
print(f"Discount: {result['discount_percent']}%")
print(f"\nItems Found: {len(result['items'])}\n")

for i, item in enumerate(result['items'], 1):
    print(f"Item {i}:")
    print(f"  Description: {item['description']}")
    print(f"  Quantity: {item['quantity']} {item['unit']}")
    print(f"  Unit Price: ₹{item['unit_price']}")
    print(f"  Total: ₹{item['quantity'] * item['unit_price']}")
    print()

# Calculate expected total
subtotal = sum(item['quantity'] * item['unit_price'] for item in result['items'])
print(f"Subtotal: ₹{subtotal}")
print(f"Expected Total: K21,000 (₹21,000)")

if result['confidence_flags']:
    print(f"\n⚠️  Fields needing review: {', '.join(result['confidence_flags'])}")
else:
    print("\n✅ All fields extracted successfully!")

print("\n" + "=" * 60)
