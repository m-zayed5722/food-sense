#!/usr/bin/env python3
"""Test the full system with complete debugging to find where modifications are lost"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.baseline_order_parser import BaselineOrderParser

def test_full_system_debug():
    parser = BaselineOrderParser()
    
    # Test the exact case that's failing
    text = "big mac no pickles with large fires extra salt"
    
    print(f"Testing: '{text}'")
    print("="*60)
    
    # Parse with full debugging
    result = parser.parse_order(text)
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print(f"Total items: {len(result.items)}")
    
    for i, item in enumerate(result.items):
        print(f"\nItem {i+1}: {item.name} (${item.total_price:.2f})")
        print(f"  Size: {item.size}")
        print(f"  Quantity: {item.quantity}")
        print(f"  Modifications: {len(item.modifications)}")
        for mod in item.modifications:
            mod_type = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
            print(f"    - {mod_type}: {mod.item}")
    
    print(f"\nOrder subtotal: ${result.subtotal:.2f}")
    print(f"Order total: ${result.total_amount:.2f}")

if __name__ == "__main__":
    test_full_system_debug()