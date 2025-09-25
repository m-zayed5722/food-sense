"""
Enhanced Restaurant-Aware Order Parser
Detects restaurant context and filters menu items accordingly
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
import logging
from src.order_schema import (
    Order, OrderItem, Modification, MenuItemTemplate, OrderSchema,
    SizeType, ModificationType
)


class RestaurantAwareOrderParser:
    """Enhanced parser that detects restaurant context first"""
    
    def __init__(self, menu_items: List[MenuItemTemplate] = None):
        self.logger = logging.getLogger(__name__)
        self.menu_items = menu_items or OrderSchema.create_sample_menu()
        self.schema = OrderSchema()
        
        # Restaurant detection keywords
        self.restaurant_keywords = {
            "McDonald's": [
                "mcdonald", "mcchicken", "big mac", "quarter pounder", "mcflurry", 
                "mcnugget", "mcdouble", "filet-o-fish", "happy meal", "mcpick", "mccafe"
            ],
            "Starbucks": [
                "starbucks", "frappuccino", "macchiato", "americano", "latte", "venti", 
                "grande", "caramel ribbon", "pike place", "blonde roast", "cold brew"
            ],
            "Taco Bell": [
                "taco bell", "taco", "burrito", "quesadilla", "chalupa", "crunchwrap", 
                "beefy", "nacho", "doritos locos", "mexican pizza", "cantina"
            ],
            "KFC": [
                "kfc", "colonel", "popcorn chicken", "famous bowl", "zinger", "hot wings",
                "original recipe", "extra crispy", "chicken bucket"
            ],
            "Burger King": [
                "burger king", "whopper", "king", "chicken fries", "impossible whopper",
                "croissanwich", "onion rings", "hershey's pie"
            ],
            "Subway": [
                "subway", "footlong", "italian bmt", "meatball marinara", "turkey breast",
                "spicy italian", "veggie delite", "oven roasted"
            ],
            "Pizza Hut": [
                "pizza hut", "pepperoni pizza", "meat lovers", "supreme pizza", "stuffed crust",
                "pan pizza", "thin crust", "personal pan"
            ],
            "Chick-fil-A": [
                "chick-fil-a", "chick fil a", "chicken sandwich", "waffle fries", "nuggets",
                "spicy deluxe", "original chicken", "polynesian sauce"
            ],
            "Wendy's": [
                "wendy", "baconator", "frosty", "spicy chicken", "dave's single",
                "jr bacon cheeseburger", "chicken go wrap"
            ],
            "Dairy Queen": [
                "dairy queen", "dq", "blizzard", "dilly bar", "hot dog", "chicken strip basket",
                "oreo blizzard", "brazier burger"
            ],
            "Five Guys": [
                "five guys", "cajun fries", "bacon cheeseburger", "little cheeseburger",
                "all the way", "regular fries"
            ],
            "Chipotle": [
                "chipotle", "burrito bowl", "barbacoa", "carnitas", "sofritas", "guac",
                "cilantro lime", "pico de gallo"
            ],
            "Dunkin'": [
                "dunkin", "donut", "iced coffee", "coolatta", "munchkins", "bagel",
                "boston kreme", "glazed donut"
            ],
            "Popeyes": [
                "popeyes", "louisiana", "spicy chicken", "biscuit", "red beans",
                "chicken tender", "cajun fries"
            ],
            "Arby's": [
                "arby", "roast beef", "curly fries", "beef n cheddar", "turkey gyro",
                "classic roast beef", "horsey sauce"
            ],
            "Sonic": [
                "sonic", "cherry limeade", "mozzarella sticks", "corn dog", "slush",
                "ocean water", "cherry slush"
            ],
            "Panda Express": [
                "panda express", "orange chicken", "chow mein", "fried rice", "beijing beef",
                "honey walnut shrimp", "teriyaki chicken"
            ],
            "Papa John's": [
                "papa john", "garlic sauce", "pepperoni pizza", "the works",
                "better ingredients", "papa's pizza"
            ],
            "Carl's Jr": [
                "carl's jr", "famous star", "western bacon", "hand-breaded",
                "six dollar burger", "crisscut fries"
            ],
            "Wingstop": [
                "wingstop", "lemon pepper", "garlic parmesan", "atomic wings", "louisiana rub",
                "boneless wings", "original hot"
            ]
        }
        
        # Build indexes
        self._build_indexes()
    
    def _build_indexes(self):
        """Build keyword indexes for menu items"""
        self.name_to_item = {}
        self.keyword_to_item = {}
        self.restaurant_to_items = {}
        
        for item in self.menu_items:
            # Index by exact name
            self.name_to_item[item.name.lower()] = item
            
            # Index by keywords
            for keyword in item.keywords:
                self.keyword_to_item[keyword.lower()] = item
            
            # Index by restaurant
            restaurant = self._identify_item_restaurant(item)
            if restaurant not in self.restaurant_to_items:
                self.restaurant_to_items[restaurant] = []
            self.restaurant_to_items[restaurant].append(item)
    
    def _identify_item_restaurant(self, item: MenuItemTemplate) -> str:
        """Identify which restaurant an item belongs to"""
        name_lower = item.name.lower()
        
        for restaurant, keywords in self.restaurant_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return restaurant
        
        return "General"
    
    def detect_restaurant(self, text: str) -> Tuple[Optional[str], float]:
        """Detect restaurant from input text with confidence score"""
        text_lower = text.lower()
        restaurant_scores = {}
        
        # Check for explicit restaurant mentions
        for restaurant, keywords in self.restaurant_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Longer keywords get higher scores
                    keyword_score = len(keyword) / 10.0
                    # Exact word boundaries get bonus
                    if re.search(r'\\b' + re.escape(keyword) + r'\\b', text_lower):
                        keyword_score *= 1.5
                    score += keyword_score
            
            if score > 0:
                restaurant_scores[restaurant] = score
        
        if not restaurant_scores:
            return None, 0.0
        
        # Return restaurant with highest score
        best_restaurant = max(restaurant_scores.items(), key=lambda x: x[1])
        confidence = min(best_restaurant[1] / 2.0, 1.0)  # Normalize confidence
        
        return best_restaurant[0], confidence
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Fix common typos and variations
        typo_fixes = {
            'fires': 'fries',
            'mcchiken': 'mcchicken',
            'sprit': 'sprite',
            'burgr': 'burger',
            'mayo': 'mayonnaise',
            'w/': 'with',
            '&': 'and',
            'chk': 'chicken',
            'bf': 'beef',
            'pep': 'pepperoni'
        }
        
        for typo, correction in typo_fixes.items():
            text = text.replace(typo, correction)
        
        # Normalize spacing and punctuation
        text = re.sub(r'[,;]', ' ', text)
        text = re.sub(r'\\s+', ' ', text)
        
        return text
    
    def get_restaurant_menu_items(self, restaurant: str) -> List[MenuItemTemplate]:
        """Get menu items for a specific restaurant"""
        return self.restaurant_to_items.get(restaurant, [])
    
    def extract_quantities(self, text: str) -> Dict[str, int]:
        """Extract quantity information from text"""
        quantities = {}
        words = text.split()
        
        # Number words to digits
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'a': 1, 'an': 1, 'single': 1, 'double': 2, 'triple': 3
        }
        
        for i, word in enumerate(words):
            qty = None
            if word.isdigit():
                qty = int(word)
            elif word in number_words:
                qty = number_words[word]
            
            if qty and qty > 0 and i + 1 < len(words):
                # Look for menu item keywords in next few words
                search_window = words[i+1:min(i+4, len(words))]
                search_text = ' '.join(search_window).lower()
                
                # Find matching keywords
                for keyword in self.keyword_to_item.keys():
                    if keyword in search_text:
                        quantities[keyword] = qty
                        break
        
        return quantities
    
    def extract_sizes(self, text: str) -> Dict[str, SizeType]:
        """Extract size information from text"""
        sizes = {}
        
        size_patterns = {
            'small': SizeType.SMALL, 'sm': SizeType.SMALL, 'mini': SizeType.SMALL,
            'medium': SizeType.MEDIUM, 'med': SizeType.MEDIUM, 'regular': SizeType.MEDIUM,
            'large': SizeType.LARGE, 'lg': SizeType.LARGE, 'big': SizeType.LARGE,
            'extra large': SizeType.EXTRA_LARGE, 'xl': SizeType.EXTRA_LARGE, 'jumbo': SizeType.EXTRA_LARGE
        }
        
        words = text.split()
        for i, word in enumerate(words):
            size_found = None
            
            if word in size_patterns:
                size_found = size_patterns[word]
            elif i + 1 < len(words) and f"{word} {words[i+1]}" in size_patterns:
                size_found = size_patterns[f"{word} {words[i+1]}"]
            
            if size_found:
                # Look for menu items nearby
                search_ranges = [
                    words[i+1:min(i+4, len(words))],
                    words[max(0, i-3):i]
                ]
                
                for search_words in search_ranges:
                    search_text = ' '.join(search_words).lower()
                    for keyword in self.keyword_to_item.keys():
                        if keyword in search_text:
                            item = self.keyword_to_item[keyword]
                            if hasattr(item, 'available_sizes') and size_found in item.available_sizes:
                                sizes[keyword] = size_found
                                break
                    if keyword in sizes:
                        break
        
        return sizes
    
    def extract_modifications(self, text: str) -> List[Modification]:
        """Extract modifications from text"""
        modifications = []
        
        modification_patterns = [
            (r'\\bno\\s+(\\w+)', ModificationType.REMOVE),
            (r'\\bextra\\s+(\\w+)', ModificationType.EXTRA),
            (r'\\bwith\\s+(\\w+)', ModificationType.ADD),
            (r'\\bwithout\\s+(\\w+)', ModificationType.REMOVE),
            (r'\\badd\\s+(\\w+)', ModificationType.ADD),
        ]
        
        for pattern, mod_type in modification_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mod_item = match.group(1).strip()
                if mod_item:
                    mod = Modification(
                        type=mod_type,
                        item=mod_item,
                        description=f"{mod_type.value} {mod_item}"
                    )
                    modifications.append(mod)
        
        return modifications
    
    def find_menu_items(self, text: str, restaurant_items: List[MenuItemTemplate]) -> List[Tuple[MenuItemTemplate, float]]:
        """Find menu items from restaurant-specific list"""
        found_items = []
        
        # Build temporary keyword index for this restaurant
        restaurant_keywords = {}
        for item in restaurant_items:
            for keyword in item.keywords:
                restaurant_keywords[keyword.lower()] = item
        
        # Find exact matches first
        for keyword, item in restaurant_keywords.items():
            if keyword in text:
                # Check for word boundaries for better precision
                if re.search(r'\\b' + re.escape(keyword) + r'\\b', text):
                    confidence = 0.95
                else:
                    confidence = 0.8
                
                # Avoid duplicates
                if not any(existing_item == item for existing_item, _ in found_items):
                    found_items.append((item, confidence))
        
        # Sort by confidence
        found_items.sort(key=lambda x: x[1], reverse=True)
        
        return found_items
    
    def parse_order(self, text: str) -> Tuple[Order, Optional[str]]:
        """Parse natural language text into a structured order with restaurant detection"""
        self.logger.info(f"Parsing order text: '{text}'")
        
        # Preprocess text
        clean_text = self.preprocess_text(text)
        
        # Detect restaurant first
        detected_restaurant, confidence = self.detect_restaurant(clean_text)
        self.logger.info(f"Detected restaurant: {detected_restaurant} (confidence: {confidence:.2f})")
        
        # Get restaurant-specific menu items
        if detected_restaurant:
            restaurant_items = self.get_restaurant_menu_items(detected_restaurant)
            self.logger.info(f"Using {len(restaurant_items)} items from {detected_restaurant}")
        else:
            # Fall back to all items if no restaurant detected
            restaurant_items = self.menu_items
            self.logger.info("No restaurant detected, using all menu items")
        
        # Extract information
        quantities = self.extract_quantities(clean_text)
        sizes = self.extract_sizes(clean_text)
        modifications = self.extract_modifications(clean_text)
        
        # Find menu items (restaurant-filtered)
        found_items = self.find_menu_items(clean_text, restaurant_items)
        
        # Create order items
        order_items = []
        for menu_item, confidence in found_items:
            # Get quantity (default to 1)
            quantity = 1
            for keyword in menu_item.keywords:
                if keyword in quantities:
                    quantity = quantities[keyword]
                    break
            
            # Get size
            size = None
            for keyword in menu_item.keywords:
                if keyword in sizes:
                    size = sizes[keyword]
                    break
            
            # Calculate base price with size adjustment
            base_price = menu_item.base_price
            if size and hasattr(menu_item, 'size_pricing'):
                size_key = size.value if hasattr(size, 'value') else str(size)
                size_adjustment = menu_item.size_pricing.get(size_key, Decimal('0.00'))
                base_price += size_adjustment
            
            # Filter modifications for this item
            valid_modifications = []
            for mod in modifications:
                if mod.item.lower() in [m.lower() for m in menu_item.available_modifications]:
                    if hasattr(menu_item, 'modification_pricing'):
                        mod.price_change = menu_item.modification_pricing.get(
                            mod.item.lower(), Decimal('0.00')
                        )
                    valid_modifications.append(mod)
            
            # Create order item
            order_item = OrderItem(
                name=menu_item.name,
                quantity=quantity,
                size=size,
                base_price=base_price,
                modifications=valid_modifications
            )
            
            order_items.append(order_item)
            self.logger.info(f"Added item: {order_item.name} (qty: {quantity}, size: {size})")
        
        # Create order
        order = Order(
            items=order_items,
            customer_notes=text if len(text) > 100 else None
        )
        
        self.logger.info(f"Parsed order with {len(order_items)} items, total: ${order.total_amount:.2f}")
        return order, detected_restaurant
    
    def get_order_summary(self, order: Order, restaurant: Optional[str] = None) -> str:
        """Generate a human-readable order summary with restaurant info"""
        if not order.items:
            return "No items in order"
        
        summary_lines = []
        summary_lines.append("🛒 ORDER SUMMARY")
        if restaurant:
            summary_lines.append(f"🏪 Restaurant: {restaurant}")
        summary_lines.append("=" * 40)
        
        for item in order.items:
            line = f"• {item.quantity}x {item.name}"
            if item.size:
                size_str = item.size.value if hasattr(item.size, 'value') else str(item.size)
                line += f" ({size_str})"
            line += f" - ${item.total_price:.2f}"
            summary_lines.append(line)
            
            # Add modifications
            for mod in item.modifications:
                mod_type_str = mod.type.value if hasattr(mod.type, 'value') else str(mod.type)
                mod_line = f"  └─ {mod_type_str.title()} {mod.item}"
                if mod.price_change > 0:
                    mod_line += f" (+${mod.price_change:.2f})"
                elif mod.price_change < 0:
                    mod_line += f" (-${abs(mod.price_change):.2f})"
                summary_lines.append(mod_line)
        
        summary_lines.append("-" * 40)
        summary_lines.append(f"Subtotal: ${order.subtotal:.2f}")
        summary_lines.append(f"Tax (8%): ${order.tax_amount:.2f}")
        summary_lines.append(f"TOTAL: ${order.total_amount:.2f}")
        
        return "\\n".join(summary_lines)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = RestaurantAwareOrderParser()
    
    # Test the problematic case
    test_text = "craving a McChicken with large fries and medium sprite, mayo and ketchup included"
    print(f"🧪 Testing: {test_text}")
    print("=" * 60)
    
    order, restaurant = parser.parse_order(test_text)
    summary = parser.get_order_summary(order, restaurant)
    print(summary)