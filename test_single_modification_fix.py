#!/usr/bin/env python3
"""
Test Fix for Single Modification Detection
Tests the specific issue with "big mac no pickles with large fries extra salt"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.order_processor import OrderProcessor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_single_modification_fix():
    """Test the fix for single modification detection"""
    
    print("🔧 TESTING SINGLE MODIFICATION FIX")
    print("="*60)
    
    # Initialize processor with LLM disabled
    processor = OrderProcessor(use_llm=False)
    print(f"1️⃣ Initialized order processor")
    
    # Test cases focusing on the reported issue
    test_orders = [
        "big mac no pickles with large fries extra salt",
        "mcchicken no mayo with medium sprite",
        "pizza extra cheese with garlic bread",
        "burger hold onions with fries",
        "chicken wings extra sauce",
        "big mac no pickles no lettuce with large fries extra salt extra ketchup",  # Mixed case
    ]
    
    print(f"2️⃣ Testing {len(test_orders)} modification patterns...\n")
    
    for i, order_text in enumerate(test_orders, 1):
        print("-"*60)
        print(f"🧪 TEST {i}: {order_text}")
        print("-"*60)
        
        try:
            # Process the order
            result = processor.process_order_text(order_text)
            
            if result and result.baseline_order:
                order = result.baseline_order
                
                print("🛒 CHECKOUT RESULT:")
                for j, item in enumerate(order.items, 1):
                    print(f"  {j}. {item.quantity}x {item.name}")
                    
                    if item.size:
                        size_str = item.size.value if hasattr(item.size, 'value') else str(item.size)
                        print(f"     Size: {size_str.title()}")
                    
                    if item.modifications:
                        print(f"     Modifications ({len(item.modifications)}):")
                        for mod in item.modifications:
                            mod_type_str = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                            print(f"       • {mod_type_str.title()}: {mod.item}")
                    else:
                        print(f"     Modifications: None ❌")
                    
                    print(f"     Price: ${item.total_price:.2f}")
                
                # Count modifications
                total_mods = sum(len(item.modifications) for item in order.items)
                print(f"\n📊 ANALYSIS:")
                print(f"  Total Items: {len(order.items)}")
                print(f"  Total Modifications: {total_mods}")
                print(f"  Processing Time: {result.baseline_time:.3f}s")
                print(f"  Total: ${order.total_amount:.2f}")
                
                # Highlight issues
                if i == 1 and total_mods == 0:
                    print(f"  ❌ ISSUE: 'no pickles' not detected!")
                elif i == 1 and total_mods > 0:
                    print(f"  ✅ FIXED: Single modifications working!")
                
            else:
                print("❌ Error processing order")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*60)
    print("🏁 SINGLE MODIFICATION FIX TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_single_modification_fix()