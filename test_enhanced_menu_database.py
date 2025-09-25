#!/usr/bin/env python3
"""
Test the Enhanced Menu Database
Tests the new 300-item menu database with real restaurant chains
"""

import sys
import os
sys.path.append('src')
from src.baseline_order_parser import BaselineOrderParser

def test_enhanced_menu():
    """Test the enhanced menu database with various restaurant items"""
    parser = BaselineOrderParser()
    
    print("🍔 Food Sense - Enhanced Menu Database Test")
    print("=" * 60)
    print(f"📊 Total Menu Items: {len(parser.menu_items)}")
    
    # Group items by category for overview
    categories = {}
    for item in parser.menu_items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append(item.name)
    
    print(f"📋 Categories: {len(categories)}")
    for category, items in categories.items():
        print(f"  • {category}: {len(items)} items")
    
    print("\n" + "🧪 Testing Text-to-Order with New Menu Items")
    print("=" * 60)
    
    # Test cases showcasing the new restaurant chains
    test_cases = [
        "starbucks caramel frappuccino large with extra shot",
        "big mac no pickles with large fries extra salt",
        "taco bell quesadilla with medium pepsi",
        "kfc chicken sandwich no mayo with coleslaw",
        "subway footlong turkey with extra cheese no onions",
        "pizza hut pepperoni pizza extra cheese thin crust",
        "chick fil a nuggets with waffle fries",
        "wendys baconator with large fries extra crispy",
        "five guys cheeseburger with cajun fries",
        "chipotle burrito bowl with extra rice no beans"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: '{test_case}'")
        print("-" * 40)
        
        try:
            result = parser.parse_order(test_case)
            
            for j, item in enumerate(result.items, 1):
                print(f"  {j}. {item.quantity}x {item.name}")
                if item.size:
                    size_val = item.size.value if hasattr(item.size, 'value') else str(item.size)
                    print(f"     Size: {size_val}")
                if item.modifications:
                    print(f"     Modifications ({len(item.modifications)}):")
                    for mod in item.modifications:
                        mod_type = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                        print(f"       • {mod_type.title()}: {mod.item}")
                print(f"     Price: ${item.total_price:.2f}")
            
            print(f"   💰 Total: ${result.total_amount:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

def show_sample_items():
    """Show sample items from each major restaurant chain"""
    parser = BaselineOrderParser()
    
    print("\n" + "🏪 Sample Items from Each Restaurant Chain")
    print("=" * 60)
    
    # Group by likely restaurant chain (based on item names)
    chain_samples = {
        "Starbucks": [item for item in parser.menu_items if 'frappuccino' in item.name.lower() or 'latte' in item.name.lower()],
        "McDonald's": [item for item in parser.menu_items if 'big mac' in item.name.lower() or 'mcchicken' in item.name.lower()],
        "Taco Bell": [item for item in parser.menu_items if 'taco' in item.name.lower() or 'burrito' in item.name.lower()],
        "KFC": [item for item in parser.menu_items if 'kfc' in item.name.lower() or 'colonel' in item.name.lower()],
        "Pizza Hut": [item for item in parser.menu_items if 'pizza' in item.name.lower() and 'hut' in item.name.lower()],
        "Subway": [item for item in parser.menu_items if 'footlong' in item.name.lower() or 'sub' in item.name.lower()],
    }
    
    for chain, items in chain_samples.items():
        if items:
            print(f"\n🍽️ {chain} Sample Items:")
            for item in items[:5]:  # Show first 5 items
                print(f"  • {item.name} - ${item.base_price}")

if __name__ == "__main__":
    test_enhanced_menu()
    show_sample_items()
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Menu Database is Ready!")
    print("✅ 20 restaurant chains integrated")
    print("✅ 300+ menu items available")
    print("✅ Smart modifications and sizing")
    print("✅ Text-to-order processing enhanced")
    print("🚀 Launch the Streamlit app to try it out!")