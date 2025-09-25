#!/usr/bin/env python3
"""
Debug the McDonald's menu items and matching logic
"""

import sys
import os
sys.path.append('src')

from src.baseline_order_parser import BaselineOrderParser
import logging

def debug_mcdonalds_items():
    print("🔍 Debugging McDonald's Menu Items")
    print("=" * 60)
    
    parser = BaselineOrderParser()
    
    # Check what McDonald's items are available
    mcdonalds_items = []
    for item in parser.menu_items:
        if item.restaurant.lower() == "mcdonald's":
            mcdonalds_items.append(item)
    
    print(f"📋 Found {len(mcdonalds_items)} McDonald's items:")
    for item in mcdonalds_items:
        print(f"  - {item.name} (${float(item.base_price):.2f})")
    
    # Test restaurant detection
    test_input = "craving a McChicken with large fries and medium sprite"
    print(f"\n🎯 Testing restaurant detection with: '{test_input}'")
    
    detected = parser.detect_restaurant(test_input)
    print(f"Detected restaurant: {detected}")
    
    # Test individual keyword matching
    print(f"\n🔤 Testing keyword matching:")
    words = test_input.lower().split()
    for word in words:
        matches = []
        for item in mcdonalds_items:
            if word in item.name.lower():
                matches.append(item.name)
        if matches:
            print(f"  '{word}' matches: {matches}")

if __name__ == "__main__":
    debug_mcdonalds_items()