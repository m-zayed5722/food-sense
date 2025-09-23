#!/usr/bin/env python3
"""
Test Enhanced Rule-Based Parser - Multiple Modifications
Tests the enhanced parser's ability to detect multiple sequential modifications
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

def test_multiple_modifications():
    """Test multiple modification parsing with complex examples"""
    
    print("🍔 TESTING ENHANCED MULTIPLE MODIFICATIONS PARSER")
    print("="*80)
    
    # Initialize processor with LLM disabled
    processor = OrderProcessor(use_llm=False)
    print(f"1️⃣ Initialized order processor with {len(processor.baseline_parser.menu_items)} menu items")
    print(f"INFO: Available features: ❌ LLM Parser Disabled, ✅ Enhanced Baseline Parser, ✅ Multiple Modification Detection")
    
    # Test cases with multiple modifications
    test_orders = [
        "big mac no pickles no lettuce large fries extra ketchup extra mayo",
        "mcchicken no mayo no onions with cheese add lettuce extra pickles",
        "pepperoni pizza no cheese extra pepperoni extra sauce large sprite no ice",
        "two big macs no onions no pickles extra cheese large fries extra salt",
        "chicken wings extra hot sauce extra ranch no celery",
        "oreo blizzard large no whipped cream extra oreo pieces extra chocolate sauce",
        "beef shawarma plate no tomatoes no onions extra tahini extra hot sauce add rice",
        "cheeseburger hold pickles hold onions add bacon extra cheese with mayo",
        "chicken strip basket no fries add onion rings extra honey mustard extra ranch",
        "falafel wrap no cucumber no lettuce add extra hummus extra tahini hot sauce"
    ]
    
    print(f"2️⃣ Processing {len(test_orders)} complex modification test orders...\n")
    
    for i, order_text in enumerate(test_orders, 1):
        print("="*80)
        print(f"📝 TEST ORDER {i}: {order_text}")
        print("="*80)
        
        try:
            # Process the order
            result = processor.process_order_text(order_text)
            
            if result and result.baseline_order:
                order = result.baseline_order
                
                print("🛒 ENHANCED BASELINE CHECKOUT")
                print("="*50)
                print()
                
                for j, item in enumerate(order.items, 1):
                    print(f"{j}. {item.quantity}x {item.name}")
                    
                    if item.size:
                        size_str = item.size.value if hasattr(item.size, 'value') else str(item.size)
                        print(f"   Size: {size_str.title()}")
                    
                    if item.modifications:
                        print("   Modifications:")
                        for mod in item.modifications:
                            mod_type_str = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                            print(f"     • {mod_type_str.title()}: {mod.item}")
                    
                    print(f"   Price: ${item.total_price:.2f}")
                    print()
                
                print("-"*50)
                print(f"Items: {len(order.items)}")
                print(f"Subtotal: ${order.subtotal:.2f}")
                print(f"Tax (8%): ${order.tax_amount:.2f}")
                print("="*50)
                print(f"TOTAL: ${order.total_amount:.2f}")
                print()
                
                # Count modifications
                total_mods = sum(len(item.modifications) for item in order.items)
                print(f"📊 MODIFICATION ANALYSIS:")
                print(f"Total Items: {len(order.items)}")
                print(f"Total Modifications: {total_mods}")
                print(f"Processing Time: {result.baseline_time:.3f}s")
                
                # Show modification breakdown
                if total_mods > 0:
                    print(f"Modification Details:")
                    for item in order.items:
                        if item.modifications:
                            print(f"  {item.name}: {len(item.modifications)} modifications")
                            for mod in item.modifications:
                                mod_type_str = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                                print(f"    - {mod_type_str.title()}: {mod.item}")
                
            else:
                print("❌ Error processing order: No baseline order generated")
                
        except Exception as e:
            print(f"❌ Exception processing order: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("="*80)
    print("✅ ENHANCED MULTIPLE MODIFICATIONS TESTING COMPLETE!")
    print("🚀 Enhanced features:")
    print("  • Sequential modification detection (no X no Y)")
    print("  • Multiple extra items (extra X extra Y)")
    print("  • Mixed modification patterns")
    print("  • Duplicate prevention")
    print("  • Context-aware parsing")
    print("="*80)

if __name__ == "__main__":
    test_multiple_modifications()