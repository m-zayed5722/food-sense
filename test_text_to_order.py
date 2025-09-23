"""
Test Text-to-Order Feature
Test the new order processing functionality
"""

import sys
import os
import logging

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from src.order_processor import OrderProcessor
from src.baseline_order_parser import BaselineOrderParser
from src.llm_order_parser import get_order_parser


def test_order_processing():
    """Test the complete order processing pipeline"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("🍔 TESTING TEXT-TO-ORDER FEATURE")
    print("=" * 80)
    
    # Initialize processor
    print("\n1️⃣ Initializing Order Processor...")
    processor = OrderProcessor()
    
    # Test orders
    test_orders = [
        "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
        "I want two big macs with extra cheese and a large coke",
        "can I get a small sprite and chicken nuggets with bbq sauce please",
        "one apple pie and medium fries no salt"
    ]
    
    print(f"\n2️⃣ Processing {len(test_orders)} test orders...")
    
    for i, order_text in enumerate(test_orders, 1):
        print(f"\n" + "="*80)
        print(f"📝 TEST ORDER {i}: {order_text}")
        print("="*80)
        
        try:
            # Process order with both parsers
            result = processor.process_order_text(order_text, use_both_parsers=True)
            
            # Show comparison
            comparison = processor.create_order_comparison_display(result)
            print(comparison)
            
            # Show checkout for preferred order
            preferred_order = result.llm_order or result.baseline_order
            if preferred_order:
                parser_type = "LLM" if result.llm_order else "Baseline"
                checkout = processor.get_checkout_display(preferred_order, parser_type)
                print("\n" + "="*80)
                print(checkout)
                
                # Show metrics
                print(f"\n📊 METRICS:")
                print(f"Items: {preferred_order.item_count}")
                print(f"Total: ${preferred_order.total_amount:.2f}")
                if hasattr(preferred_order, 'estimated_time') and preferred_order.estimated_time:
                    print(f"Est. Time: {preferred_order.estimated_time} min")
            else:
                print("❌ No order could be processed")
                
        except Exception as e:
            print(f"❌ Error processing order: {e}")
    
    # Show menu info
    print(f"\n" + "="*80)
    print("📋 AVAILABLE MENU")
    print("="*80)
    menu_info = processor.get_menu_info()
    print(menu_info)
    
    print(f"\n" + "="*80)
    print("✅ TEXT-TO-ORDER TESTING COMPLETE!")
    print("="*80)


def test_individual_parsers():
    """Test individual parsers separately"""
    print("\n🧪 TESTING INDIVIDUAL PARSERS")
    print("=" * 80)
    
    test_text = "craving mcchicken with large fries and medium sprite, mayo and ketchup included"
    
    # Test baseline parser
    print("\n📝 Testing Baseline Parser...")
    baseline_parser = BaselineOrderParser()
    baseline_order = baseline_parser.parse_order(test_text)
    if baseline_order:
        baseline_summary = baseline_parser.get_order_summary(baseline_order)
        print(baseline_summary)
    else:
        print("❌ Baseline parser failed")
    
    # Test LLM parser
    print(f"\n🤖 Testing LLM Parser...")
    llm_parser = get_order_parser(use_mock=False)  # Try real LLM first
    llm_order = llm_parser.parse_order(test_text)
    if llm_order:
        llm_summary = llm_parser.get_order_summary(llm_order)
        print(llm_summary)
    else:
        print("❌ LLM parser failed")


if __name__ == "__main__":
    test_order_processing()
    test_individual_parsers()