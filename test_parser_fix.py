#!/usr/bin/env python3
"""
Direct test of the enhanced baseline parser to verify the fix
"""

import sys
import os
sys.path.append('src')

from src.baseline_order_parser import BaselineOrderParser
import logging

def test_parser_fix():
    print("🔧 Testing Enhanced Baseline Parser Fix")
    print("=" * 60)
    
    # Create parser
    parser = BaselineOrderParser()
    
    # Test the specific problematic case
    test_input = "craving a McChicken with large fries and medium sprite, mayo and ketchup included"
    
    print(f"📝 Input: {test_input}")
    print("-" * 60)
    
    try:
        # Parse the order
        order = parser.parse_order(test_input)
        
        # Get summary
        summary = parser.get_order_summary(order)
        print(summary)
        
        # Show detailed results
        print(f"\nDetailed Results:")
        print(f"Items found: {len(order.items)}")
        print(f"Total: ${order.total_amount:.2f}")
        
        for item in order.items:
            print(f"  - {item.quantity}x {item.name} (${float(item.base_price):.2f})")
            if item.modifications:
                print(f"    Modifications: {', '.join([mod.name for mod in item.modifications])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser_fix()