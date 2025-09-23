"""
Test Enhanced Rule-Based Order Parser
"""

import sys
import os
import logging

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from src.order_processor import OrderProcessor


def test_enhanced_parser():
    """Test the enhanced rule-based parser"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🍔 TESTING ENHANCED RULE-BASED ORDER PARSER")
    print("=" * 80)
    
    # Initialize processor without LLM
    print("\n1️⃣ Initializing Enhanced Order Processor...")
    processor = OrderProcessor(use_llm=False)
    
    # Test orders with the new comprehensive menu
    test_orders = [
        # McDonald's
        "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
        "I want two big macs with extra cheese and a large coke",
        
        # Domino's
        "large pepperoni pizza with extra cheese and a side of wings",
        "medium pizza and cheesy bread with ranch",
        
        # Wingstop
        "dozen lemon pepper wings with ranch and some cajun corn",
        "garlic parmesan wings and a large sprite",
        
        # Shawarma
        "chicken shawarma wrap with extra tahini and hot sauce",
        "beef shawarma plate with rice and garlic sauce",
        "falafel wrap with hummus",
        
        # Dairy Queen
        "large oreo blizzard and a cheeseburger",
        "chicken strip basket with honey mustard",
        "small reeses blizzard"
    ]
    
    print(f"\n2️⃣ Processing {len(test_orders)} diverse test orders...")
    
    for i, order_text in enumerate(test_orders, 1):
        print(f"\n" + "="*80)
        print(f"📝 TEST ORDER {i}: {order_text}")
        print("="*80)
        
        try:
            # Process order with enhanced baseline only
            result = processor.process_order_text(order_text, use_both_parsers=False)
            
            # Show results
            if result.baseline_order:
                checkout = processor.get_checkout_display(result.baseline_order, "ENHANCED BASELINE")
                print(checkout)
                
                # Show metrics
                print(f"\n📊 METRICS:")
                print(f"Items Found: {len(result.baseline_order.items)}")
                print(f"Processing Time: {result.baseline_time:.3f}s")
                print(f"Total: ${result.baseline_order.total_amount:.2f}")
                print(f"Item Count: {result.baseline_order.item_count}")
                
                # Show processing notes
                if result.processing_notes:
                    print(f"Processing Notes: {', '.join(result.processing_notes)}")
                    
            else:
                print("❌ No items could be processed")
                if result.processing_notes:
                    for note in result.processing_notes:
                        print(f"  • {note}")
                
        except Exception as e:
            print(f"❌ Error processing order: {e}")
    
    # Show comprehensive menu
    print(f"\n" + "="*80)
    print("📋 COMPREHENSIVE MENU DATABASE")
    print("="*80)
    menu_info = processor.get_menu_info()
    print(menu_info)
    
    print(f"\n" + "="*80)
    print("✅ ENHANCED RULE-BASED TESTING COMPLETE!")
    print("🚀 Rule-based parser now supports:")
    print("  • McDonald's, Domino's, Wingstop, Shawarma, Dairy Queen")
    print("  • Smart quantity detection")  
    print("  • Context-aware size matching")
    print("  • Advanced modification parsing")
    print("  • Typo correction and fuzzy matching")
    print("="*80)


if __name__ == "__main__":
    test_enhanced_parser()