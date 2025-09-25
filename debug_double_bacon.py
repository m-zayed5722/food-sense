#!/usr/bin/env python3
"""
Debug why Double Bacon Quarter Pounder is being matched
"""

import sys
import os
sys.path.append('src')

from src.baseline_order_parser import BaselineOrderParser

def debug_double_bacon_matching():
    print("🔍 Debugging Double Bacon Quarter Pounder Matching")
    print("=" * 60)
    
    parser = BaselineOrderParser()
    
    # Find the Double Bacon Quarter Pounder item
    double_bacon_item = None
    for item in parser.menu_items:
        if "Double Bacon Quarter Pounder" in item.name:
            double_bacon_item = item
            break
    
    # Find ALL Quarter Pounder items and check them
    quarter_pounder_items = []
    for item in parser.menu_items:
        if "quarter pounder" in item.name.lower():
            quarter_pounder_items.append(item)
    
    test_text = "craving a mcchicken with large fries and medium sprite, mayo and ketchup included"
    print(f"Testing against: '{test_text}'")
    print(f"Found {len(quarter_pounder_items)} Quarter Pounder items:\n")
    
    for item in quarter_pounder_items:
        print(f"Item: {item.name}")
        print(f"Keywords: {item.keywords}")
        
        matched_keywords = []
        for keyword in item.keywords:
            if keyword in test_text.lower():
                matched_keywords.append(keyword)
        
        if matched_keywords:
            print(f"❌ Matched keywords: {matched_keywords}")
        else:
            print("✅ No keywords matched!")
        print("-" * 40)

if __name__ == "__main__":
    debug_double_bacon_matching()