#!/usr/bin/env python3
"""
Debug restaurant categorization
"""

import sys
import os
sys.path.append('src')

from src.baseline_order_parser import BaselineOrderParser

def debug_restaurant_categorization():
    print("🔍 Debugging Restaurant Item Categorization")
    print("=" * 60)
    
    parser = BaselineOrderParser()
    
    # Check how items are categorized
    print("Restaurant to Items mapping:")
    for restaurant, items in parser.restaurant_to_items.items():
        print(f"\n{restaurant}: ({len(items)} items)")
        for item in items[:5]:  # Show first 5 items
            print(f"  - {item.name}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    
    # Check specific items we're looking for
    search_items = ["McChicken", "McDonald's Fries", "McDonald's Sprite"]
    print(f"\nSearching for specific items:")
    for search_item in search_items:
        found_in = None
        for restaurant, items in parser.restaurant_to_items.items():
            for item in items:
                if search_item.lower() in item.name.lower():
                    found_in = restaurant
                    break
            if found_in:
                break
        print(f"  '{search_item}' -> {found_in}")

if __name__ == "__main__":
    debug_restaurant_categorization()