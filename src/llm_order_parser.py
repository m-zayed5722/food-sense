"""
LLM-based Order Parser
Uses large language models to parse natural language orders with high accuracy
"""

import json
import logging
from typing import List, Dict, Optional, Any, Union
from decimal import Decimal
from src.order_schema import (
    Order, OrderItem, Modification, MenuItemTemplate, OrderSchema,
    SizeType, ModificationType
)
from src.llm_enricher import LLMConfig, OllamaClient


class LLMOrderParser:
    """LLM-based parser for converting text to orders"""
    
    def __init__(self, menu_items: List[MenuItemTemplate] = None, config: LLMConfig = None):
        self.logger = logging.getLogger(__name__)
        self.menu_items = menu_items or OrderSchema.create_sample_menu()
        self.config = config or LLMConfig()
        self.client = OllamaClient(config)
        self.schema = OrderSchema()
        
        # Create menu context for the LLM
        self._create_menu_context()
    
    def _create_menu_context(self):
        """Create menu context string for LLM prompts"""
        menu_lines = []
        menu_lines.append("AVAILABLE MENU ITEMS:")
        
        for item in self.menu_items:
            line = f"• {item.name} - ${item.base_price}"
            
            if item.available_sizes:
                # Handle both enum values and string values
                sizes_str = ", ".join([
                    s.value if hasattr(s, 'value') else str(s) 
                    for s in item.available_sizes
                ])
                line += f" (Sizes: {sizes_str})"
            
            if item.available_modifications:
                mods_str = ", ".join(item.available_modifications)
                line += f" (Modifications: {mods_str})"
            
            if item.keywords:
                keywords_str = ", ".join(item.keywords)
                line += f" (Also called: {keywords_str})"
            
            menu_lines.append(line)
        
        self.menu_context = "\n".join(menu_lines)
    
    def create_order_prompt(self, text: str) -> str:
        """Create prompt for order parsing"""
        return f"""You are an expert restaurant order processing assistant. Your task is to parse customer orders from natural language and return structured JSON.

{self.menu_context}

SIZES: Small, Medium, Large, Extra Large
MODIFICATION TYPES: add, remove, extra, substitute, on_side

IMPORTANT RULES:
1. Return ONLY valid JSON with no additional text
2. Match menu items by name or keywords (be flexible with spelling)
3. Extract quantities, sizes, and modifications accurately
4. If an item isn't on the menu, suggest the closest match or skip it
5. Calculate prices based on base prices and size/modification adjustments
6. Be conservative with modifications - only include what's clearly requested

Size pricing (add to base price):
- Small: +$0.00, Medium: +$0.30-0.50, Large: +$0.60-1.00

Response format:
{{
  "items": [
    {{
      "name": "Menu Item Name",
      "quantity": 1,
      "size": "Medium",
      "base_price": "4.99",
      "modifications": [
        {{
          "type": "add",
          "item": "mayo",
          "price_change": "0.00"
        }}
      ],
      "special_instructions": "any special notes"
    }}
  ],
  "customer_notes": "original customer request if complex",
  "estimated_time": 15
}}

Customer order: "{text}"

Return JSON:"""
    
    def parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response and extract JSON"""
        if not response:
            return None
        
        # Try to find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            self.logger.warning("No JSON found in order parsing response")
            return None
        
        json_str = response[json_start:json_end]
        
        try:
            data = json.loads(json_str)
            
            # Validate required structure
            if 'items' not in data:
                self.logger.warning("No 'items' field in JSON response")
                return None
            
            if not isinstance(data['items'], list):
                self.logger.warning("'items' field is not a list")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in order parsing response: {e}")
            return None
    
    def validate_and_fix_order_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix LLM output data"""
        if not data or 'items' not in data:
            return None
        
        validated_items = []
        
        for item_data in data['items']:
            try:
                # Validate and fix item name
                if 'name' not in item_data:
                    self.logger.warning("Skipping item without name")
                    continue
                
                # Validate quantity
                quantity = item_data.get('quantity', 1)
                if not isinstance(quantity, int) or quantity < 1:
                    quantity = 1
                
                # Validate size
                size = item_data.get('size')
                if size:
                    normalized_size = self.schema.normalize_size(size)
                    if not normalized_size:
                        self.logger.warning(f"Invalid size '{size}', removing")
                        size = None
                    else:
                        size = normalized_size.value
                
                # Validate base price
                base_price = item_data.get('base_price', '0.00')
                try:
                    base_price = Decimal(str(base_price))
                except (ValueError, TypeError):
                    base_price = Decimal('0.00')
                
                # Validate modifications
                modifications = []
                for mod_data in item_data.get('modifications', []):
                    if isinstance(mod_data, dict) and 'item' in mod_data:
                        mod_type = mod_data.get('type', 'add')
                        price_change = mod_data.get('price_change', '0.00')
                        
                        try:
                            price_change = Decimal(str(price_change))
                        except (ValueError, TypeError):
                            price_change = Decimal('0.00')
                        
                        modifications.append({
                            'type': mod_type,
                            'item': mod_data['item'],
                            'price_change': str(price_change)
                        })
                
                validated_item = {
                    'name': item_data['name'],
                    'quantity': quantity,
                    'size': size,
                    'base_price': str(base_price),
                    'modifications': modifications,
                    'special_instructions': item_data.get('special_instructions')
                }
                
                validated_items.append(validated_item)
                
            except Exception as e:
                self.logger.warning(f"Error validating item {item_data}: {e}")
                continue
        
        return {
            'items': validated_items,
            'customer_notes': data.get('customer_notes'),
            'estimated_time': data.get('estimated_time')
        }
    
    def create_order_from_data(self, data: Dict[str, Any]) -> Optional[Order]:
        """Create Order object from validated data"""
        if not data or not data.get('items'):
            return None
        
        order_items = []
        
        for item_data in data['items']:
            try:
                # Create modifications
                modifications = []
                for mod_data in item_data.get('modifications', []):
                    mod_type = self.schema.normalize_modification_type(mod_data['type'])
                    modifications.append(Modification(
                        type=mod_type,
                        item=mod_data['item'],
                        price_change=Decimal(mod_data['price_change'])
                    ))
                
                # Create order item
                size_enum = None
                if item_data.get('size'):
                    size_enum = self.schema.normalize_size(item_data['size'])
                
                order_item = OrderItem(
                    name=item_data['name'],
                    quantity=item_data['quantity'],
                    size=size_enum,
                    base_price=Decimal(item_data['base_price']),
                    modifications=modifications,
                    special_instructions=item_data.get('special_instructions')
                )
                
                order_items.append(order_item)
                
            except Exception as e:
                self.logger.error(f"Error creating order item: {e}")
                continue
        
        if not order_items:
            return None
        
        return Order(
            items=order_items,
            customer_notes=data.get('customer_notes'),
            estimated_time=data.get('estimated_time')
        )
    
    def parse_order(self, text: str) -> Optional[Order]:
        """Parse natural language text into a structured order using LLM"""
        if not self.client.is_available():
            self.logger.error("Ollama server not available for order parsing")
            return None
        
        self.logger.info(f"🤖 LLM parsing order: '{text}' (this may take 1-10 minutes)...")
        
        # Create prompt
        prompt = self.create_order_prompt(text)
        
        # Generate response
        response = self.client.generate(prompt)
        if not response:
            self.logger.error(f"No response from LLM for order: {text}")
            return None
        
        self.logger.info(f"✅ LLM response received for order parsing")
        
        # Parse response
        data = self.parse_llm_response(response)
        if not data:
            self.logger.error(f"Failed to parse LLM response for order: {text}")
            return None
        
        # Validate and fix data
        validated_data = self.validate_and_fix_order_data(data)
        if not validated_data:
            self.logger.error(f"Failed to validate order data for: {text}")
            return None
        
        # Create order object
        order = self.create_order_from_data(validated_data)
        if not order:
            self.logger.error(f"Failed to create order object for: {text}")
            return None
        
        self.logger.info(f"🍽️ Successfully parsed order: {len(order.items)} items, total: ${order.total_amount:.2f}")
        return order
    
    def get_order_summary(self, order: Order) -> str:
        """Generate a human-readable order summary"""
        if not order or not order.items:
            return "No items in order"
        
        summary_lines = []
        summary_lines.append("🤖 LLM ORDER SUMMARY")
        summary_lines.append("=" * 40)
        
        for item in order.items:
            line = f"• {item.quantity}x {item.name}"
            if item.size:
                line += f" ({item.size.value})"
            line += f" - ${item.total_price:.2f}"
            summary_lines.append(line)
            
            # Add modifications
            for mod in item.modifications:
                mod_line = f"  └─ {mod.type.value.title()} {mod.item}"
                if mod.price_change > 0:
                    mod_line += f" (+${mod.price_change:.2f})"
                elif mod.price_change < 0:
                    mod_line += f" (-${abs(mod.price_change):.2f})"
                summary_lines.append(mod_line)
            
            # Add special instructions
            if item.special_instructions:
                summary_lines.append(f"  🗒️ {item.special_instructions}")
        
        summary_lines.append("-" * 40)
        summary_lines.append(f"Subtotal: ${order.subtotal:.2f}")
        summary_lines.append(f"Tax (8%): ${order.tax_amount:.2f}")
        summary_lines.append(f"TOTAL: ${order.total_amount:.2f}")
        
        if order.estimated_time:
            summary_lines.append(f"⏱️ Estimated time: {order.estimated_time} minutes")
        
        if order.customer_notes:
            summary_lines.append(f"📝 Notes: {order.customer_notes}")
        
        return "\n".join(summary_lines)


class MockLLMOrderParser:
    """Mock order parser for testing when LLM is not available"""
    
    def __init__(self, menu_items: List[MenuItemTemplate] = None):
        self.logger = logging.getLogger(__name__)
        self.menu_items = menu_items or OrderSchema.create_sample_menu()
    
    def parse_order(self, text: str) -> Order:
        """Mock order parsing - returns a simple order"""
        self.logger.info(f"🔧 Using mock LLM parser for: '{text}'")
        
        # Simple mock logic - create a basic order
        mock_item = OrderItem(
            name="Mock Item",
            quantity=1,
            base_price=Decimal('9.99'),
            modifications=[]
        )
        
        return Order(
            items=[mock_item],
            customer_notes=f"Mock parsing of: {text}"
        )
    
    def get_order_summary(self, order: Order) -> str:
        """Generate mock summary"""
        return "🔧 MOCK LLM ORDER SUMMARY\n(LLM not available)"


# Factory function
def get_order_parser(menu_items: List[MenuItemTemplate] = None, 
                    config: LLMConfig = None, 
                    use_mock: bool = False) -> Union[LLMOrderParser, MockLLMOrderParser]:
    """Get appropriate order parser based on availability"""
    if use_mock:
        return MockLLMOrderParser(menu_items)
    
    parser = LLMOrderParser(menu_items, config)
    if not parser.client.is_available():
        logging.warning("Ollama not available for order parsing, using mock parser")
        return MockLLMOrderParser(menu_items)
    
    return parser


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test LLM order parser
    parser = get_order_parser()
    
    test_inputs = [
        "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
        "I want two big macs with extra cheese and a large coke",
        "can I get a small sprite and chicken nuggets with bbq sauce",
    ]
    
    print("🤖 LLM ORDER PARSER RESULTS")
    print("=" * 60)
    
    for i, text in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: {text}")
        print("-" * 60)
        
        order = parser.parse_order(text)
        if order:
            summary = parser.get_order_summary(order)
            print(summary)
        else:
            print("❌ Failed to parse order")