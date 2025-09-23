"""
Order Processing Pipeline
Main pipeline that handles text-to-order conversion with dual processing
"""

from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import time
import logging
from dataclasses import dataclass

from src.order_schema import Order, OrderItem, MenuItemTemplate, OrderSchema
from src.baseline_order_parser import BaselineOrderParser
from src.llm_order_parser import LLMOrderParser, MockLLMOrderParser, get_order_parser
from src.llm_enricher import LLMConfig


@dataclass
class OrderProcessingResult:
    """Result of order processing"""
    baseline_order: Optional[Order] = None
    llm_order: Optional[Order] = None
    baseline_time: float = 0.0
    llm_time: float = 0.0
    baseline_summary: str = ""
    llm_summary: str = ""
    processing_notes: List[str] = None
    
    def __post_init__(self):
        if self.processing_notes is None:
            self.processing_notes = []


class OrderProcessor:
    """Main order processing pipeline with dual baseline/LLM processing"""
    
    def __init__(self, config: LLMConfig = None, menu_items: List[MenuItemTemplate] = None, use_llm: bool = False):
        self.logger = logging.getLogger(__name__)
        self.config = config or LLMConfig()
        self.menu_items = menu_items or OrderSchema.create_sample_menu()
        
        # Initialize parsers
        self.baseline_parser = BaselineOrderParser(self.menu_items)
        
        # Only initialize LLM parser if explicitly requested
        if use_llm:
            self.llm_parser = get_order_parser(self.menu_items, self.config)
        else:
            self.llm_parser = None
        
        self.logger.info(f"Initialized order processor with {len(self.menu_items)} menu items")
        self._log_available_features()
    
    def _log_available_features(self):
        """Log available features and parser status"""
        features = []
        
        if self.llm_parser:
            if isinstance(self.llm_parser, LLMOrderParser):
                features.append("✅ LLM Parser (Ollama)")
            else:
                features.append("🔧 Mock LLM Parser")
        else:
            features.append("❌ LLM Parser Disabled")
        
        features.append("✅ Enhanced Baseline Parser")
        features.append("✅ Comprehensive Menu Database")
        features.append("✅ Smart Price Calculation")
        
        self.logger.info("Available features: " + ", ".join(features))
    
    def process_order_text(self, text: str, use_both_parsers: bool = False) -> OrderProcessingResult:
        """Process order text with baseline and optionally LLM parsers"""
        if not text or not text.strip():
            return OrderProcessingResult(
                processing_notes=["Empty input text provided"]
            )
        
        self.logger.info(f"🍔 Processing order: '{text}'")
        result = OrderProcessingResult()
        
        # Process with baseline parser
        try:
            self.logger.info("🤔 Processing with enhanced baseline parser...")
            start_time = time.time()
            result.baseline_order = self.baseline_parser.parse_order(text)
            result.baseline_time = time.time() - start_time
            
            if result.baseline_order:
                result.baseline_summary = self.baseline_parser.get_order_summary(result.baseline_order)
                result.processing_notes.append(f"✅ Baseline: Found {len(result.baseline_order.items)} items")
            else:
                result.processing_notes.append("❌ Baseline: No items found")
                
        except Exception as e:
            self.logger.error(f"Baseline parser failed: {e}")
            result.processing_notes.append(f"❌ Baseline error: {str(e)}")
        
        # Process with LLM parser if requested and available
        if use_both_parsers and self.llm_parser:
            try:
                self.logger.info("🤖 Processing with LLM parser...")
                start_time = time.time()
                result.llm_order = self.llm_parser.parse_order(text)
                result.llm_time = time.time() - start_time
                
                if result.llm_order:
                    result.llm_summary = self.llm_parser.get_order_summary(result.llm_order)
                    result.processing_notes.append(f"✅ LLM: Found {len(result.llm_order.items)} items")
                else:
                    result.processing_notes.append("❌ LLM: No items found")
                    
            except Exception as e:
                self.logger.error(f"LLM parser failed: {e}")
                result.processing_notes.append(f"❌ LLM error: {str(e)}")
        elif use_both_parsers and not self.llm_parser:
            result.processing_notes.append("ℹ️ LLM parser not available (disabled)")
        
        # Log results
        self.logger.info(f"✅ Processing complete: Baseline={result.baseline_time:.2f}s" + 
                        (f", LLM={result.llm_time:.2f}s" if result.llm_time > 0 else ""))
        return result
    
    def compare_parsing_results(self, result: OrderProcessingResult) -> Dict[str, Any]:
        """Compare baseline vs LLM parsing results"""
        comparison = {
            'baseline_items': 0,
            'llm_items': 0,
            'baseline_total': Decimal('0.00'),
            'llm_total': Decimal('0.00'),
            'baseline_time': result.baseline_time,
            'llm_time': result.llm_time,
            'accuracy_metrics': {},
            'differences': []
        }
        
        # Count items and totals
        if result.baseline_order:
            comparison['baseline_items'] = len(result.baseline_order.items)
            comparison['baseline_total'] = result.baseline_order.total_amount
        
        if result.llm_order:
            comparison['llm_items'] = len(result.llm_order.items)
            comparison['llm_total'] = result.llm_order.total_amount
        
        # Find differences
        if result.baseline_order and result.llm_order:
            baseline_items = {item.name.lower(): item for item in result.baseline_order.items}
            llm_items = {item.name.lower(): item for item in result.llm_order.items}
            
            # Items in baseline but not LLM
            baseline_only = set(baseline_items.keys()) - set(llm_items.keys())
            if baseline_only:
                comparison['differences'].append(f"Baseline found extra items: {', '.join(baseline_only)}")
            
            # Items in LLM but not baseline
            llm_only = set(llm_items.keys()) - set(baseline_items.keys())
            if llm_only:
                comparison['differences'].append(f"LLM found extra items: {', '.join(llm_only)}")
            
            # Price differences
            price_diff = abs(comparison['llm_total'] - comparison['baseline_total'])
            if price_diff > Decimal('0.50'):  # Significant price difference
                comparison['differences'].append(f"Price difference: ${price_diff:.2f}")
        
        return comparison
    
    def get_checkout_display(self, order: Order, parser_type: str = "LLM") -> str:
        """Generate checkout-ready display for an order"""
        if not order or not order.items:
            return "🛒 Empty Cart\nAdd some items to get started!"
        
        lines = []
        lines.append(f"🛒 {parser_type.upper()} CHECKOUT")
        lines.append("=" * 50)
        lines.append("")
        
        # Order items
        for i, item in enumerate(order.items, 1):
            lines.append(f"{i}. {item.quantity}x {item.name}")
            
            if item.size:
                # Handle both enum and string values
                size_str = item.size.value if hasattr(item.size, 'value') else str(item.size)
                lines.append(f"   Size: {size_str}")
            
            if item.modifications:
                lines.append("   Modifications:")
                for mod in item.modifications:
                    # Handle both enum and string values for modification type
                    mod_type_str = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                    mod_text = f"     • {mod_type_str.title()} {mod.item}"
                    if mod.price_change != 0:
                        mod_text += f" ({'+' if mod.price_change > 0 else ''}${mod.price_change:.2f})"
                    lines.append(mod_text)
            
            if item.special_instructions:
                lines.append(f"   Note: {item.special_instructions}")
            
            lines.append(f"   Price: ${item.total_price:.2f}")
            lines.append("")
        
        # Order totals
        lines.append("-" * 50)
        lines.append(f"Items: {order.item_count}")
        lines.append(f"Subtotal: ${order.subtotal:.2f}")
        lines.append(f"Tax (8%): ${order.tax_amount:.2f}")
        lines.append("=" * 50)
        lines.append(f"TOTAL: ${order.total_amount:.2f}")
        
        if order.estimated_time:
            lines.append("")
            lines.append(f"⏱️ Estimated time: {order.estimated_time} minutes")
        
        if order.customer_notes:
            lines.append("")
            lines.append(f"📝 Special notes: {order.customer_notes}")
        
        return "\n".join(lines)
    
    def create_order_comparison_display(self, result: OrderProcessingResult) -> str:
        """Create side-by-side comparison of parsing results"""
        lines = []
        lines.append("🔄 PARSING COMPARISON")
        lines.append("=" * 80)
        
        # Processing times
        lines.append(f"⏱️ Processing Times: Baseline={result.baseline_time:.2f}s, LLM={result.llm_time:.2f}s")
        lines.append("")
        
        # Side by side summaries
        if result.baseline_order or result.llm_order:
            baseline_lines = result.baseline_summary.split('\n') if result.baseline_summary else ["No baseline result"]
            llm_lines = result.llm_summary.split('\n') if result.llm_summary else ["No LLM result"]
            
            max_lines = max(len(baseline_lines), len(llm_lines))
            
            lines.append("📊 BASELINE                    |  🤖 LLM")
            lines.append("-" * 30 + "+" + "-" * 30)
            
            for i in range(max_lines):
                baseline_line = baseline_lines[i] if i < len(baseline_lines) else ""
                llm_line = llm_lines[i] if i < len(llm_lines) else ""
                
                # Truncate long lines
                if len(baseline_line) > 28:
                    baseline_line = baseline_line[:25] + "..."
                if len(llm_line) > 28:
                    llm_line = llm_line[:25] + "..."
                
                lines.append(f"{baseline_line:<30}|  {llm_line}")
        
        # Comparison metrics
        comparison = self.compare_parsing_results(result)
        if comparison['differences']:
            lines.append("")
            lines.append("🔍 KEY DIFFERENCES:")
            for diff in comparison['differences']:
                lines.append(f"  • {diff}")
        
        # Processing notes
        if result.processing_notes:
            lines.append("")
            lines.append("📋 PROCESSING NOTES:")
            for note in result.processing_notes:
                lines.append(f"  • {note}")
        
        return "\n".join(lines)
    
    def get_menu_info(self) -> str:
        """Get formatted menu information"""
        lines = []
        lines.append("📋 AVAILABLE MENU ITEMS")
        lines.append("=" * 50)
        
        categories = {}
        for item in self.menu_items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for category, items in categories.items():
            lines.append(f"\n🍽️ {category.upper()}")
            lines.append("-" * 30)
            
            for item in items:
                line = f"• {item.name} - ${item.base_price:.2f}"
                
                if item.available_sizes:
                    # Handle both enum values and string values
                    sizes = [
                        s.value if hasattr(s, 'value') else str(s) 
                        for s in item.available_sizes
                    ]
                    line += f" (Sizes: {', '.join(sizes)})"
                
                lines.append(line)
                
                if item.available_modifications:
                    mods = ", ".join(item.available_modifications[:5])  # Show first 5
                    if len(item.available_modifications) > 5:
                        mods += "..."
                    lines.append(f"  Modifications: {mods}")
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize processor
    processor = OrderProcessor()
    
    # Test orders
    test_orders = [
        "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
        "I want two big macs with extra cheese and a large coke",
        "can I get a small sprite and chicken nuggets with bbq sauce please"
    ]
    
    print("🍔 ORDER PROCESSING PIPELINE TEST")
    print("=" * 80)
    
    for i, order_text in enumerate(test_orders, 1):
        print(f"\n📝 Test Order {i}: {order_text}")
        print("=" * 80)
        
        # Process order
        result = processor.process_order_text(order_text)
        
        # Display comparison
        comparison = processor.create_order_comparison_display(result)
        print(comparison)
        
        # Show preferred checkout (LLM if available, otherwise baseline)
        preferred_order = result.llm_order or result.baseline_order
        if preferred_order:
            print("\n" + "=" * 80)
            checkout = processor.get_checkout_display(preferred_order, "PREFERRED")
            print(checkout)