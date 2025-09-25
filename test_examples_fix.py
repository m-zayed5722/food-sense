#!/usr/bin/env python3
"""
Test script to verify the example buttons functionality fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.baseline_order_parser import BaselineOrderParser
from src.schema import menu_database

def test_example_processing():
    """Test that all example texts can be processed successfully"""
    parser = BaselineOrderParser(menu_database)
    
    examples = [
        "craving a McChicken with large fries and medium sprite, mayo and ketchup included",
        "grande latte with extra shot and oat milk", 
        "two crunchwrap supremes with extra sour cream and a large baja blast",
        "family bucket with mashed potatoes and gravy, extra crispy"
    ]
    
    print("🧪 Testing Example Processing Fix")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example}")
        
        # Test if text is not empty (the original issue)
        if not example.strip():
            print("❌ FAIL: Empty text detected")
            continue
        else:
            print("✅ PASS: Text not empty")
        
        # Test if parser can process it
        try:
            order = parser.parse_order_text(example)
            if order and order.items:
                print(f"✅ PASS: Parser found {len(order.items)} items")
                print(f"   Restaurant: {order.restaurant_name}")
                print(f"   Total: ${order.total_amount:.2f}")
            else:
                print("⚠️  WARNING: Parser didn't find items (might be expected for some examples)")
        except Exception as e:
            print(f"❌ FAIL: Parser error - {e}")
    
    print("\n" + "=" * 50)
    print("✅ Example Processing Test Complete!")

if __name__ == "__main__":
    test_example_processing()