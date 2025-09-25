#!/usr/bin/env python3
"""
Restaurant Brand Organization
Reorganizes menu items by restaurant brands instead of food categories
"""

import json
import sys
import os
from decimal import Decimal
from typing import List, Dict, Any
from collections import defaultdict

# Add src to path
sys.path.append('src')
from src.order_schema import MenuItemTemplate, SizeType, ModificationType

class RestaurantBrandOrganizer:
    def __init__(self):
        self.restaurant_keywords = {
            "McDonald's": ["mcdonald", "mcchicken", "big mac", "quarter pounder", "mcflurry", "mcnugget"],
            "Starbucks": ["frappuccino", "macchiato", "americano", "latte", "venti", "grande", "caramel ribbon"],
            "Taco Bell": ["taco", "burrito", "quesadilla", "chalupa", "crunchwrap", "beefy", "nacho"],
            "KFC": ["kfc", "colonel", "popcorn chicken", "famous bowl", "zinger", "hot wings"],
            "Burger King": ["whopper", "burger king", "king", "chicken fries", "impossible whopper"],
            "Subway": ["footlong", "subway", "italian bmt", "meatball marinara", "turkey breast"],
            "Pizza Hut": ["pizza hut", "pepperoni pizza", "meat lovers", "supreme pizza", "stuffed crust"],
            "Chick-fil-A": ["chick-fil-a", "chick fil a", "chicken sandwich", "waffle fries", "nuggets"],
            "Wendy's": ["wendy", "baconator", "frosty", "spicy chicken", "dave's single"],
            "Dairy Queen": ["dairy queen", "dq", "blizzard", "dilly bar", "hot dog", "chicken strip basket"],
            "Five Guys": ["five guys", "cajun fries", "bacon cheeseburger", "little cheeseburger"],
            "Chipotle": ["chipotle", "burrito bowl", "barbacoa", "carnitas", "sofritas", "guac"],
            "Dunkin'": ["dunkin", "donut", "iced coffee", "coolatta", "munchkins", "bagel"],
            "Popeyes": ["popeyes", "louisiana", "spicy chicken", "biscuit", "red beans"],
            "Arby's": ["arby", "roast beef", "curly fries", "beef n cheddar", "turkey gyro"],
            "Sonic": ["sonic", "cherry limeade", "mozzarella sticks", "corn dog", "slush"],
            "Panda Express": ["panda express", "orange chicken", "chow mein", "fried rice", "beijing beef"],
            "Papa John's": ["papa john", "garlic sauce", "pepperoni pizza", "the works"],
            "Carl's Jr": ["carl's jr", "famous star", "western bacon", "hand-breaded"],
            "Wingstop": ["wingstop", "lemon pepper", "garlic parmesan", "atomic wings", "louisiana rub"]
        }
    
    def identify_restaurant(self, item_name: str) -> str:
        """Identify which restaurant an item belongs to based on keywords"""
        name_lower = item_name.lower()
        
        # Check each restaurant's keywords
        for restaurant, keywords in self.restaurant_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return restaurant
        
        # Default categorization based on common patterns
        if any(word in name_lower for word in ['coffee', 'latte', 'frappuccino', 'americano']):
            return "Starbucks"
        elif any(word in name_lower for word in ['burger', 'whopper']):
            return "Burger King"
        elif any(word in name_lower for word in ['pizza']):
            return "Pizza Hut"
        elif any(word in name_lower for word in ['chicken sandwich', 'nuggets']):
            return "Chick-fil-A"
        elif any(word in name_lower for word in ['taco', 'burrito']):
            return "Taco Bell"
        else:
            return "General"  # Fallback category
    
    def load_current_menu(self) -> List[MenuItemTemplate]:
        """Load current menu items from order_schema.py"""
        print("📂 Loading current menu items from order_schema.py...")
        
        try:
            from src.order_schema import OrderSchema
            menu_items = OrderSchema.create_sample_menu()
            print(f"✅ Loaded {len(menu_items)} menu items")
            return menu_items
        except Exception as e:
            print(f"❌ Error loading menu items: {e}")
            return []
    
    def organize_by_restaurant(self, menu_items: List[MenuItemTemplate]) -> Dict[str, List[MenuItemTemplate]]:
        """Organize menu items by restaurant brand"""
        print("🏪 Organizing menu items by restaurant brand...")
        
        restaurant_groups = defaultdict(list)
        
        for item in menu_items:
            restaurant = self.identify_restaurant(item.name)
            restaurant_groups[restaurant].append(item)
        
        # Sort restaurants by number of items (descending)
        sorted_restaurants = dict(sorted(restaurant_groups.items(), 
                                       key=lambda x: len(x[1]), reverse=True))
        
        print(f"✅ Organized items into {len(sorted_restaurants)} restaurant brands:")
        for restaurant, items in sorted_restaurants.items():
            print(f"  • {restaurant}: {len(items)} items")
        
        return sorted_restaurants
    
    def create_restaurant_menu_code(self, restaurant_groups: Dict[str, List[MenuItemTemplate]]) -> str:
        """Create the menu code organized by restaurant"""
        print("🔧 Generating restaurant-organized menu code...")
        
        menu_code = "        return [\n"
        
        for restaurant, items in restaurant_groups.items():
            menu_code += f"            # {restaurant} Menu Items\n"
            
            for item in items:
                # Convert sizes
                size_names = []
                for size in item.available_sizes:
                    if hasattr(size, 'name'):
                        size_names.append(f'SizeType.{size.name}')
                    else:
                        size_name = str(size).upper().replace(' ', '_')
                        size_names.append(f'SizeType.{size_name}')
                sizes_code = f"[{', '.join(size_names)}]"
                
                # Convert size pricing
                size_pricing_code = "{\n"
                for size, price in item.size_pricing.items():
                    size_pricing_code += f'                "{size}": Decimal("{price}"),\n'
                size_pricing_code += "            }"
                
                # Convert modifications
                modifications_code = f"[{', '.join([repr(mod) for mod in item.available_modifications])}]"
                
                # Convert modification pricing
                mod_pricing_code = "{\n"
                for mod, price in item.modification_pricing.items():
                    mod_pricing_code += f'                "{mod}": Decimal("{price}"),\n'
                mod_pricing_code += "            }"
                
                # Convert keywords
                keywords_code = f"[{', '.join([repr(kw) for kw in item.keywords])}]"
                
                menu_code += f'''            MenuItemTemplate(
                name="{item.name}",
                category="{item.category}",
                base_price=Decimal("{item.base_price}"),
                available_sizes={sizes_code},
                size_pricing={size_pricing_code},
                available_modifications={modifications_code},
                modification_pricing={mod_pricing_code},
                keywords={keywords_code}
            ),\n'''
            
            menu_code += "\n"  # Add spacing between restaurants
        
        menu_code += "        ]"
        return menu_code
    
    def update_order_schema(self, restaurant_groups: Dict[str, List[MenuItemTemplate]]):
        """Update order_schema.py with restaurant-organized menu"""
        print("📝 Updating order_schema.py with restaurant-organized menu...")
        
        schema_file = "src/order_schema.py"
        
        try:
            # Read current file
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the create_sample_menu method
            start_marker = "        return ["
            start_idx = content.find(start_marker)
            
            if start_idx == -1:
                print("❌ Could not find menu items section")
                return False
            
            # Find the end of the method
            bracket_count = 0
            end_idx = start_idx + len(start_marker)
            in_string = False
            escape_next = False
            
            for i in range(start_idx + len(start_marker), len(content)):
                char = content[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        if bracket_count == 0:
                            end_idx = i + 1
                            break
                        bracket_count -= 1
            
            # Generate new menu code
            new_menu_code = self.create_restaurant_menu_code(restaurant_groups)
            
            # Replace the old menu with new restaurant-organized menu
            new_content = content[:start_idx] + new_menu_code + content[end_idx:]
            
            # Write updated file
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Successfully updated {schema_file} with restaurant-organized menu!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating schema file: {e}")
            return False
    
    def save_restaurant_summary(self, restaurant_groups: Dict[str, List[MenuItemTemplate]]):
        """Save restaurant organization summary"""
        summary_file = "data/restaurant_organization_summary.json"
        
        print(f"📄 Saving restaurant organization summary to {summary_file}...")
        
        summary = {
            'total_restaurants': len(restaurant_groups),
            'total_items': sum(len(items) for items in restaurant_groups.values()),
            'restaurants': {},
            'organization_date': '2025-09-24',
            'organization_type': 'restaurant_brands'
        }
        
        for restaurant, items in restaurant_groups.items():
            summary['restaurants'][restaurant] = {
                'item_count': len(items),
                'categories': list(set(item.category for item in items)),
                'sample_items': [item.name for item in items[:5]]  # First 5 items
            }
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Restaurant organization summary saved!")


def main():
    """Main restaurant organization process"""
    print("🏪 Food Sense - Restaurant Brand Organization")
    print("=" * 50)
    
    organizer = RestaurantBrandOrganizer()
    
    # Load current menu items
    menu_items = organizer.load_current_menu()
    if not menu_items:
        print("❌ No menu items found!")
        return
    
    # Organize by restaurant brand
    restaurant_groups = organizer.organize_by_restaurant(menu_items)
    
    # Update order schema
    success = organizer.update_order_schema(restaurant_groups)
    
    if success:
        # Save summary
        organizer.save_restaurant_summary(restaurant_groups)
        
        print("\n" + "=" * 50)
        print("🎉 RESTAURANT ORGANIZATION COMPLETE!")
        print("=" * 50)
        
        total_items = sum(len(items) for items in restaurant_groups.values())
        print(f"✅ Organized {total_items} items into {len(restaurant_groups)} restaurant brands")
        
        print("\n🏪 RESTAURANT BREAKDOWN:")
        for restaurant, items in restaurant_groups.items():
            categories = set(item.category for item in items)
            print(f"  • {restaurant}: {len(items)} items ({', '.join(categories)})")
        
        print("\n🚀 Menu is now organized by restaurant brands!")
        print("✅ Ready for brand-specific ordering experience!")
        
    else:
        print("❌ Organization failed. Please check the error messages above.")


if __name__ == "__main__":
    main()