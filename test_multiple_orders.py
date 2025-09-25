#!/usr/bin/env python3
"""
Test multiple McDonald's orders to verify the fix
"""

import sys
import os
sys.path.append('src')

from src.baseline_order_parser import BaselineOrderParser

def test_multiple_cases():
    print("🧪 Testing Multiple McDonald's Order Cases")
    print("=" * 60)
    
    parser = BaselineOrderParser()
    
    test_cases = [
        "craving a McChicken with large fries and medium sprite, mayo and ketchup included",
        "I want two Big Macs with extra cheese and a large coke",
        "can I get a small sprite and chicken nuggets with bbq sauce",
        "just a McChicken no mayo",
        "large fries and mcchicken please"
    ]
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_text}")
        print("-" * 60)
        
        try:
            order = parser.parse_order(test_text)
            summary = parser.get_order_summary(order)
            print(summary)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_multiple_cases()