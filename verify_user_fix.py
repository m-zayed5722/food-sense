#!/usr/bin/env python3
"""Final verification of the exact user-reported issue"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.order_processor import OrderProcessor

def test_exact_user_case():
    """Test the exact case reported by the user"""
    processor = OrderProcessor()
    
    # The exact text the user reported as problematic
    text = "big mac no pickles with large fires extra salt"
    
    print(f"🧪 Testing User-Reported Issue")
    print(f"Input: '{text}'")
    print("="*60)
    
    # Process the order (LLM disabled by default)
    result = processor.process_order_text(text)
    
    print("\n🛒 FINAL CHECKOUT:")
    order = result.baseline_order
    for i, item in enumerate(order.items, 1):
        print(f"  {i}. {item.quantity}x {item.name}")
        if item.size:
            size_val = item.size.value if hasattr(item.size, 'value') else str(item.size)
            print(f"     Size: {size_val}")
        if item.modifications:
            print(f"     Modifications ({len(item.modifications)}):")
            for mod in item.modifications:
                mod_type = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                print(f"       • {mod_type.title()}: {mod.item}")
        print(f"     Price: ${item.total_price:.2f}")
    
    print(f"\n💰 TOTAL: ${order.total_amount:.2f}")
    
    # Check if "no pickles" was detected
    big_mac_mods = []
    for item in order.items:
        if "big mac" in item.name.lower():
            big_mac_mods = item.modifications
            break
    
    pickles_removed = any(
        mod.item.lower() == "pickles" and 
        (mod.type.value if hasattr(mod.type, 'value') else str(mod.type)) == "remove"
        for mod in big_mac_mods
    )
    
    print(f"\n🔍 VERIFICATION:")
    print(f"✅ Big Mac found: {any('big mac' in item.name.lower() for item in order.items)}")
    print(f"✅ 'No pickles' detected: {pickles_removed}")
    
    if pickles_removed:
        print("\n🎉 SUCCESS: The user-reported issue is FIXED!")
        print("   'big mac no pickles' correctly detects 'remove: pickles'")
    else:
        print("\n❌ ISSUE: 'no pickles' still not being detected")

if __name__ == "__main__":
    test_exact_user_case()