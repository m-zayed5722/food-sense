"""
Rule-based Order Parser
Uses keyword matching and pattern recognition to parse natural language orders
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
import logging
from src.order_schema import (
    Order, OrderItem, Modification, MenuItemTemplate, OrderSchema,
    SizeType, ModificationType
)


class BaselineOrderParser:
    """Enhanced rule-based parser for converting text to orders with restaurant detection"""
    
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
        
        # Build keyword indexes for faster matching
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
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
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
    
    def get_restaurant_menu_items(self, restaurant: str) -> List[MenuItemTemplate]:
        """Get menu items for a specific restaurant"""
        return self.restaurant_to_items.get(restaurant, [])
    
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
            'pep': 'pepperoni',
            'dq': 'dairy queen',
            'mcd': 'mcdonalds',
            'reeses': "reese's",
            'gp': 'garlic parmesan',
            'lp': 'lemon pepper',
            'shawerma': 'shawarma',
            'shwarma': 'shawarma'
        }
        
        for typo, correction in typo_fixes.items():
            text = text.replace(typo, correction)
        
        # Normalize spacing and punctuation
        import re
        text = re.sub(r'[,;]', ' ', text)  # Replace commas/semicolons with spaces
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        
        return text
    
    def extract_quantities(self, text: str) -> Dict[str, int]:
        """Extract quantity information from text with improved intelligence"""
        quantities = {}
        words = text.split()
        
        # Enhanced quantity patterns with better context matching
        import re
        
        # Pattern 1: "number + item" (e.g., "2 big macs", "three chicken wings")
        for i, word in enumerate(words):
            # Check for numeric quantities
            qty = None
            if word.isdigit():
                qty = int(word)
            elif word in self.schema.QUANTITY_KEYWORDS:
                qty = self.schema.QUANTITY_KEYWORDS[word]
            
            if qty and qty > 0 and i + 1 < len(words):
                # Look ahead for menu item keywords in next few words
                search_window = words[i+1:min(i+4, len(words))]
                search_text = ' '.join(search_window).lower()
                
                # Find the best matching item for this quantity
                best_match = None
                best_score = 0
                
                for keyword, item in self.keyword_to_item.items():
                    if keyword in search_text:
                        score = len(keyword)  # Longer keywords get higher priority
                        if score > best_score:
                            best_match = keyword
                            best_score = score
                
                if best_match:
                    quantities[best_match] = qty
        
        # Pattern 2: Look for implied quantities from context
        # e.g., "a couple of wings" = 2, "some fries" = 1, "bunch of" = 3
        context_quantities = {
            'couple': 2, 'pair': 2, 'few': 2,
            'some': 1, 'bunch': 3, 'several': 3,
            'half dozen': 6, 'dozen': 12
        }
        
        for context_word, qty in context_quantities.items():
            if context_word in text:
                # Find nearby items
                context_pos = text.find(context_word)
                before_after = text[max(0, context_pos-20):context_pos+50]
                
                for keyword, item in self.keyword_to_item.items():
                    if keyword in before_after and keyword not in quantities:
                        quantities[keyword] = qty
                        break
        
        # Pattern 3: Multiple item indicators ("wings and fries", "burger with fries")
        # Default to 1 for each item if no explicit quantity found
        
        return quantities
    
    def extract_sizes(self, text: str) -> Dict[str, SizeType]:
        """Extract size information from text with improved context awareness"""
        sizes = {}
        words = text.split()
        
        # Build a more comprehensive size keyword map
        size_patterns = {
            # Standard sizes
            'small': SizeType.SMALL, 'sm': SizeType.SMALL, 'mini': SizeType.SMALL,
            'medium': SizeType.MEDIUM, 'med': SizeType.MEDIUM, 'm': SizeType.MEDIUM, 'regular': SizeType.MEDIUM,
            'large': SizeType.LARGE, 'lg': SizeType.LARGE, 'l': SizeType.LARGE, 'big': SizeType.LARGE,
            'extra large': SizeType.EXTRA_LARGE, 'xl': SizeType.EXTRA_LARGE, 'jumbo': SizeType.EXTRA_LARGE,
            'huge': SizeType.EXTRA_LARGE, 'super': SizeType.EXTRA_LARGE
        }
        
        # Find size keywords and their nearby menu items
        for i, word in enumerate(words):
            size_found = None
            
            # Check for exact size matches
            if word in size_patterns:
                size_found = size_patterns[word]
            
            # Check for multi-word sizes (like "extra large")
            if i + 1 < len(words):
                two_word = f"{word} {words[i+1]}"
                if two_word in size_patterns:
                    size_found = size_patterns[two_word]
            
            if size_found:
                # Look for menu items nearby (prioritize items after the size word)
                search_ranges = [
                    words[i+1:min(i+4, len(words))],  # Look ahead first
                    words[max(0, i-3):i]  # Then look behind
                ]
                
                for search_words in search_ranges:
                    search_text = ' '.join(search_words).lower()
                    
                    # Find best matching menu item
                    best_match = None
                    best_score = 0
                    
                    for keyword, item in self.keyword_to_item.items():
                        if keyword in search_text:
                            # Check if this item actually supports this size
                            if hasattr(item, 'available_sizes') and item.available_sizes:
                                if size_found in item.available_sizes:
                                    score = len(keyword)  # Longer matches are better
                                    if score > best_score:
                                        best_match = keyword
                                        best_score = score
                    
                    if best_match:
                        sizes[best_match] = size_found
                        break  # Stop searching once we find a match
        
        return sizes
    
    def extract_modifications(self, text: str) -> Dict[str, List[Modification]]:
        """Extract modifications from text with enhanced multiple modification detection"""
        modifications = {}
        
        # First pass: Handle sequential modifications (no X no Y, extra X extra Y)
        self._extract_sequential_modifications(text, modifications)
        
        # Second pass: Handle standard patterns with simplified approach
        modification_patterns = [
            # Simple and effective single modification patterns
            (r'\bno\s+(\w+)', ModificationType.REMOVE),
            (r'\bextra\s+(\w+)', ModificationType.EXTRA), 
            (r'\bwith\s+([\w\s]+?)(?=\s+(?:large|medium|small|and|\d|$))', ModificationType.ADD),
            (r'\bwith\s+([\w\s]+)$', ModificationType.ADD),  # Handle end of string
            (r'\badd\s+([\w\s]+?)(?=\s+(?:large|medium|small|extra|no|and|\d|$))', ModificationType.ADD),
            (r'\binclude\s+([\w\s]+?)(?=\s+(?:large|medium|small|extra|no|and|\d|$))', ModificationType.ADD),
            
            # Negative modifications
            (r'\bwithout\s+(\w+)', ModificationType.REMOVE),
            (r'\bhold\s+(?:the\s+)?(\w+)', ModificationType.REMOVE),
            (r'\bskip\s+(?:the\s+)?(\w+)', ModificationType.REMOVE),
            
            # On the side
            (r'([\w\s,]+?)\s+on\s+the\s+side', ModificationType.ON_SIDE),
            (r'\bside\s+of\s+([\w\s]+)', ModificationType.ON_SIDE),
        ]
        
        import re
        
        for pattern, mod_type in modification_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                mod_text = match.group(1).strip()
                if not mod_text:
                    continue
                
                # Process the modification text directly (no sequential check for now)
                self._add_modification(mod_text, mod_type, modifications)
        
        # Third pass: Look for standalone condiment mentions
        self._extract_standalone_condiments(text, modifications)
        
        return modifications
    
    def _extract_sequential_modifications(self, text: str, modifications: Dict[str, List[Modification]]):
        """Extract sequential modifications like 'no pickles no lettuce' or 'extra ketchup extra mayo'"""
        import re
        
        # Pattern for sequential "no" modifications - only match if there are multiple "no"s
        no_pattern = r'\bno\s+(\w+(?:\s+\w+)*)\s+no\s+((?:\w+(?:\s+\w+)*(?:\s+no\s+\w+(?:\s+\w+)*)*)+)'
        no_matches = re.finditer(no_pattern, text, re.IGNORECASE)
        
        for match in no_matches:
            # First item
            self._add_modification(match.group(1).strip(), ModificationType.REMOVE, modifications)
            # Remaining items (split by "no")
            remaining_text = match.group(2)
            items = re.split(r'\s+no\s+', remaining_text)
            for item in items:
                item = item.strip()
                if item and len(item) > 1:
                    self._add_modification(item, ModificationType.REMOVE, modifications)
        
        # Pattern for sequential "extra" modifications - only match if there are multiple "extra"s
        extra_pattern = r'\bextra\s+(\w+(?:\s+\w+)*)\s+extra\s+((?:\w+(?:\s+\w+)*(?:\s+extra\s+\w+(?:\s+\w+)*)*)+)'
        extra_matches = re.finditer(extra_pattern, text, re.IGNORECASE)
        
        for match in extra_matches:
            # First item
            self._add_modification(match.group(1).strip(), ModificationType.EXTRA, modifications)
            # Remaining items (split by "extra")
            remaining_text = match.group(2)
            items = re.split(r'\s+extra\s+', remaining_text)
            for item in items:
                item = item.strip()
                if item and len(item) > 1:
                    self._add_modification(item, ModificationType.EXTRA, modifications)
    
    def _is_sequential_modification(self, text: str, start: int, end: int) -> bool:
        """Check if a match is part of a sequential modification pattern"""
        # Extract the matched text
        matched_text = text[start:end]
        
        # Look for explicit sequential patterns in the context
        context_before = text[max(0, start-30):start]
        context_after = text[end:end+30]
        full_context = context_before + matched_text + context_after
        
        # Check for actual sequential patterns (multiple instances of same modifier)
        if 'no ' in matched_text:
            # Count "no" occurrences in the full context
            no_count = full_context.lower().count(' no ')
            if no_count <= 1:  # Single "no" should not be considered sequential
                return False
                
        if 'extra ' in matched_text:
            # Count "extra" occurrences in the full context  
            extra_count = full_context.lower().count(' extra ')
            if extra_count <= 1:  # Single "extra" should not be considered sequential
                return False
        
        return False  # Default to not sequential
    
    def _process_modification_text(self, mod_text: str, mod_type: ModificationType, modifications: Dict[str, List[Modification]]):
        """Process modification text and extract individual items"""
        # Clean up the modification text
        mod_text = mod_text.strip().rstrip(',').rstrip('and').strip()
        
        # Split multiple modifications (e.g., "mayo and ketchup", "sauce, pickles, onions")
        mod_items = []
        if ' and ' in mod_text:
            mod_items = [item.strip() for item in mod_text.split(' and ')]
        elif ',' in mod_text:
            mod_items = [item.strip() for item in mod_text.split(',')]
        else:
            mod_items = [mod_text.strip()]
        
        # Create modification objects
        for mod_item in mod_items:
            if mod_item and len(mod_item) > 1:  # Skip very short/empty items
                self._add_modification(mod_item, mod_type, modifications)
    
    def _add_modification(self, mod_item: str, mod_type: ModificationType, modifications: Dict[str, List[Modification]]):
        """Add a single modification to the modifications dictionary"""
        # Clean common words
        mod_item = mod_item.replace('the ', '').replace('some ', '').replace('a ', '').strip()
        
        if mod_item and len(mod_item) > 1:
            # Check if already exists to avoid duplicates
            existing_items = [mod.item.lower() for mod in modifications.get('all', [])]
            if mod_item.lower() not in existing_items:
                # Handle both enum and string values for modification type
                mod_type_str = mod_type.value if hasattr(mod_type, 'value') else str(mod_type)
                mod = Modification(
                    type=mod_type,
                    item=mod_item,
                    description=f"{mod_type_str} {mod_item}"
                )
                
                # Store modifications (associated with all items for now)
                if 'all' not in modifications:
                    modifications['all'] = []
                modifications['all'].append(mod)
    
    def _extract_standalone_condiments(self, text: str, modifications: Dict[str, List[Modification]]):
        """Extract common condiments mentioned without explicit modification words"""
        # Also look for common sauce/condiment mentions without explicit "with"
        common_condiments = [
            'mayo', 'mayonnaise', 'ketchup', 'mustard', 'ranch', 'bbq sauce', 'hot sauce',
            'tahini', 'garlic sauce', 'honey mustard', 'blue cheese', 'marinara',
            'special sauce', 'buffalo sauce'
        ]
        
        for condiment in common_condiments:
            if condiment in text and not any(condiment in mod.item for mod in modifications.get('all', [])):
                # Only add if not already captured
                mod = Modification(
                    type=ModificationType.ADD,
                    item=condiment,
                    description=f"add {condiment}"
                )
                if 'all' not in modifications:
                    modifications['all'] = []
                modifications['all'].append(mod)
        
        return modifications
    
    def find_menu_items(self, text: str, restaurant_items: List[MenuItemTemplate] = None) -> List[Tuple[MenuItemTemplate, float]]:
        """Find menu items mentioned in text with confidence scores, optionally filtered by restaurant"""
        search_items = restaurant_items if restaurant_items is not None else self.menu_items
        found_items = []
        
        # Build temporary keyword index for search items
        search_keywords = {}
        for item in search_items:
            for keyword in item.keywords:
                search_keywords[keyword.lower()] = item
        
        # First pass: Look for exact multi-word matches (highest priority)
        for keyword, item in search_keywords.items():
            if len(keyword.split()) > 1:  # Multi-word keywords
                if keyword in text:
                    confidence = 0.95  # High confidence for exact multi-word matches
                    if not any(existing_item == item for existing_item, _ in found_items):
                        found_items.append((item, confidence))
        
        # Second pass: Look for exact single-word matches
        for keyword, item in search_keywords.items():
            if len(keyword.split()) == 1:  # Single word keywords
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    # Check if this is a new item (not already found with multi-word match)
                    if not any(existing_item == item for existing_item, _ in found_items):
                        confidence = 0.9  # High confidence for exact single-word matches
                        found_items.append((item, confidence))
        
        # Third pass: Look for partial matches only if we haven't found items and no restaurant filter
        if len(found_items) == 0 and restaurant_items is None:
            words = text.split()
            for keyword, item in search_keywords.items():
                if not any(existing_item == item for existing_item, _ in found_items):
                    # Check for partial matches in individual words
                    for word in words:
                        if len(word) >= 4 and len(keyword) >= 4:
                            # Simple fuzzy matching - check if words share significant portion
                            if (word in keyword and len(word) >= len(keyword) * 0.6) or \
                               (keyword in word and len(keyword) >= len(word) * 0.6):
                                confidence = 0.6  # Lower confidence for fuzzy matches
                                found_items.append((item, confidence))
                                break
        
        # Remove duplicates and sort by confidence
        unique_items = {}
        for item, confidence in found_items:
            item_key = item.name
            if item_key not in unique_items or confidence > unique_items[item_key][1]:
                unique_items[item_key] = (item, confidence)
        
        result = [(item, conf) for item, conf in unique_items.values()]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def parse_order(self, text: str) -> Order:
        """Parse natural language text into a structured order with restaurant detection"""
        self.logger.info(f"Parsing order text: '{text}'")
        
        # Preprocess text
        clean_text = self.preprocess_text(text)
        
        # Detect restaurant first
        detected_restaurant, confidence = self.detect_restaurant(clean_text)
        self.logger.info(f"Detected restaurant: {detected_restaurant} (confidence: {confidence:.2f})")
        
        # Get restaurant-specific menu items
        if detected_restaurant and confidence > 0.3:
            restaurant_items = self.get_restaurant_menu_items(detected_restaurant)
            self.logger.info(f"Using {len(restaurant_items)} items from {detected_restaurant}")
        else:
            # Fall back to all items if no restaurant detected or low confidence
            restaurant_items = None
            self.logger.info("No restaurant detected or low confidence, using all menu items")
        
        # Extract information
        quantities = self.extract_quantities(clean_text)
        sizes = self.extract_sizes(clean_text)
        modifications = self.extract_modifications(clean_text)
        
        # Find menu items (restaurant-filtered if detected)
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
                # Handle both enum and string values for size
                size_key = size.value if hasattr(size, 'value') else str(size)
                size_adjustment = menu_item.size_pricing.get(size_key, Decimal('0.00'))
                base_price += size_adjustment
            
            # Get modifications
            item_modifications = modifications.get('all', [])
            
            # Filter modifications to only include those available for this item
            valid_modifications = []
            for mod in item_modifications:
                if mod.item.lower() in [m.lower() for m in menu_item.available_modifications]:
                    # Add pricing if available
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
        
        # Store detected restaurant info
        customer_notes = text if len(text) > 100 else None
        if detected_restaurant:
            restaurant_note = f"Restaurant: {detected_restaurant}"
            customer_notes = restaurant_note if not customer_notes else f"{restaurant_note}\n{customer_notes}"
        
        # Create and return order
        order = Order(
            items=order_items,
            customer_notes=customer_notes
        )
        
        self.logger.info(f"Parsed order with {len(order_items)} items, total: ${order.total_amount:.2f}")
        return order
    
    def get_order_summary(self, order: Order) -> str:
        """Generate a human-readable order summary"""
        if not order.items:
            return "No items in order"
        
        summary_lines = []
        summary_lines.append("🛒 ORDER SUMMARY")
        
        # Extract restaurant info from customer notes
        if order.customer_notes and "Restaurant:" in order.customer_notes:
            restaurant_line = [line for line in order.customer_notes.split('\n') if 'Restaurant:' in line][0]
            summary_lines.append(f"🏪 {restaurant_line}")
        
        summary_lines.append("=" * 40)
        
        for item in order.items:
            line = f"• {item.quantity}x {item.name}"
            if item.size:
                # Handle both enum and string values
                size_str = item.size.value if hasattr(item.size, 'value') else str(item.size)
                line += f" ({size_str})"
            line += f" - ${item.total_price:.2f}"
            summary_lines.append(line)
            
            # Add modifications
            for mod in item.modifications:
                # Handle both enum and string values for modification type
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
        
        return "\n".join(summary_lines)
    
    def evaluate_parsing_accuracy(self, test_cases: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate parsing accuracy on test cases"""
        if not test_cases:
            return {}
        
        correct_items = 0
        correct_quantities = 0
        correct_sizes = 0
        total_cases = len(test_cases)
        
        for case in test_cases:
            text = case.get('text', '')
            expected = case.get('expected', {})
            
            parsed_order = self.parse_order(text)
            
            # Check if correct items were found
            expected_items = expected.get('items', [])
            if len(parsed_order.items) == len(expected_items):
                correct_items += 1
            
            # Additional accuracy checks can be added here
        
        return {
            'item_accuracy': correct_items / total_cases if total_cases > 0 else 0,
            'overall_accuracy': correct_items / total_cases if total_cases > 0 else 0
        }


# Example usage and test cases
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = BaselineOrderParser()
    
    # Test cases
    test_inputs = [
        "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
        "I want two big macs with extra cheese and a large coke",
        "can I get a small sprite and chicken nuggets with bbq sauce",
        "one apple pie and medium fries please"
    ]
    
    print("🍔 BASELINE ORDER PARSER RESULTS")
    print("=" * 60)
    
    for i, text in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: {text}")
        print("-" * 60)
        
        order = parser.parse_order(text)
        summary = parser.get_order_summary(order)
        print(summary)