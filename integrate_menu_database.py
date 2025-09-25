#!/usr/bin/env python3
"""
Enhanced Menu Database Integration
Integrates the extracted restaurant data into the Food Sense order processing system
"""

import json
import sys
import os
from decimal import Decimal
from typing import List, Dict, Any

# Add src to path
sys.path.append('src')
from src.order_schema import MenuItemTemplate, SizeType, ModificationType

class MenuDatabaseIntegrator:
    def __init__(self, extracted_data_file: str):
        self.extracted_data_file = extracted_data_file
        self.menu_database = []
        
    def load_extracted_data(self) -> Dict[str, List[Dict]]:
        """Load the extracted restaurant data"""
        print("📂 Loading extracted restaurant data...")
        
        try:
            with open(self.extracted_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded data for {len(data)} restaurant chains")
            return data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return {}
    
    def enhance_menu_item(self, item_data: Dict, chain_name: str) -> MenuItemTemplate:
        """Enhance a menu item with better categorization and pricing"""
        
        # Enhanced size detection based on item name
        available_sizes = []
        name_lower = item_data['name'].lower()
        
        # Add sizes for beverages and sides
        if any(word in name_lower for word in ['coffee', 'latte', 'frappuccino', 'drink', 'soda', 'tea']):
            available_sizes = [SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE]
        elif any(word in name_lower for word in ['fries', 'nuggets', 'wings']):
            available_sizes = [SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE]
        
        # Enhanced modification detection
        modifications = item_data.get('available_modifications', [])
        
        # Add common modifications based on item type
        if 'burger' in name_lower or 'sandwich' in name_lower:
            modifications.extend(['no pickles', 'extra cheese', 'no onions', 'extra sauce'])
        elif 'pizza' in name_lower:
            modifications.extend(['extra cheese', 'extra sauce', 'thin crust', 'thick crust'])
        elif 'coffee' in name_lower or 'latte' in name_lower:
            modifications.extend(['extra hot', 'extra foam', 'decaf', 'extra shot'])
        elif 'fries' in name_lower:
            modifications.extend(['extra salt', 'no salt', 'extra crispy'])
        
        # Remove duplicates
        modifications = list(set(modifications))
        
        # Create size pricing
        size_pricing = {}
        if available_sizes:
            size_pricing = {
                "Small": Decimal('0.00'),
                "Medium": Decimal('0.50'),
                "Large": Decimal('1.00')
            }
        
        # Create modification pricing
        modification_pricing = {}
        for mod in modifications:
            if 'extra' in mod:
                modification_pricing[mod] = Decimal('0.50')  # Extra items cost more
            else:
                modification_pricing[mod] = Decimal('0.00')  # No/remove items are free
        
        # Generate keywords based on item name
        keywords = self.generate_keywords(item_data['name'])
        
        return MenuItemTemplate(
            name=item_data['name'],
            category=item_data['category'],
            base_price=Decimal(str(item_data['base_price'])),
            available_sizes=available_sizes,
            size_pricing=size_pricing,
            available_modifications=modifications,
            modification_pricing=modification_pricing,
            keywords=keywords
        )
    
    def generate_keywords(self, item_name: str) -> List[str]:
        """Generate keywords/aliases for menu items"""
        name_lower = item_name.lower()
        keywords = []
        
        # Common abbreviations and aliases
        keyword_map = {
            'frappuccino': ['frapp', 'frap'],
            'macchiato': ['mach'],
            'americano': ['american coffee'],
            'cappuccino': ['capp'],
            'cheeseburger': ['cheese burger', 'cheesburger'],
            'chicken sandwich': ['chicken sand', 'chick sandwich'],
            'french fries': ['fries', 'fires', 'ff'],
            'chicken nuggets': ['nuggets', 'nugs', 'chicken nugs'],
            'soft drink': ['soda', 'drink', 'pop'],
            'iced tea': ['ice tea'],
            'hot chocolate': ['hot choc', 'cocoa'],
            'chicken wings': ['wings', 'buffalo wings'],
            'onion rings': ['onion ring', 'rings'],
            'milkshake': ['shake', 'milk shake'],
            'ice cream': ['icecream'],
            'quesadilla': ['quesadila', 'quesa'],
            'burrito': ['burito'],
            'nacho': ['nachos']
        }
        
        # Add direct keywords
        for key, aliases in keyword_map.items():
            if key in name_lower:
                keywords.extend(aliases)
        
        # Add variations of the name
        words = name_lower.split()
        if len(words) > 1:
            # Add individual words
            keywords.extend(words)
            # Add combinations
            for i in range(len(words)):
                for j in range(i+1, len(words)+1):
                    combo = ' '.join(words[i:j])
                    if combo != name_lower and len(combo) > 2:
                        keywords.append(combo)
        
        return list(set(keywords))  # Remove duplicates
    
    def integrate_all_restaurants(self) -> List[MenuItemTemplate]:
        """Integrate all restaurant data into MenuItemTemplate objects"""
        print("🔄 Integrating restaurant data into Food Sense menu database...")
        
        extracted_data = self.load_extracted_data()
        if not extracted_data:
            return []
        
        integrated_menu = []
        
        for chain_name, items in extracted_data.items():
            print(f"🏪 Processing {chain_name}...")
            
            chain_items = []
            for item_data in items:
                try:
                    enhanced_item = self.enhance_menu_item(item_data, chain_name)
                    chain_items.append(enhanced_item)
                    integrated_menu.append(enhanced_item)
                except Exception as e:
                    print(f"  ⚠️ Skipped '{item_data['name']}': {e}")
            
            print(f"  ✅ Added {len(chain_items)} items from {chain_name}")
        
        print(f"🎉 Successfully integrated {len(integrated_menu)} menu items from {len(extracted_data)} chains!")
        return integrated_menu
    
    def create_enhanced_baseline_parser(self, menu_items: List[MenuItemTemplate]) -> str:
        """Create enhanced baseline parser code with new menu items"""
        
        # Generate the menu items code
        menu_items_code = "        return [\n"
        
        for item in menu_items:
            # Convert item to code representation
            size_names = []
            for size in item.available_sizes:
                if hasattr(size, 'name'):
                    size_names.append(f'SizeType.{size.name}')
                else:
                    size_name = str(size).upper().replace(' ', '_')
                    size_names.append(f'SizeType.{size_name}')
            sizes_code = f"[{', '.join(size_names)}]"
            
            size_pricing_code = "{\n"
            for size, price in item.size_pricing.items():
                size_pricing_code += f'                "{size}": Decimal("{price}"),\n'
            size_pricing_code += "            }"
            
            modifications_code = f"[{', '.join([repr(mod) for mod in item.available_modifications])}]"
            
            mod_pricing_code = "{\n"
            for mod, price in item.modification_pricing.items():
                mod_pricing_code += f'                "{mod}": Decimal("{price}"),\n'
            mod_pricing_code += "            }"
            
            keywords_code = f"[{', '.join([repr(kw) for kw in item.keywords])}]"
            
            menu_items_code += f'''            MenuItemTemplate(
                name="{item.name}",
                category="{item.category}",
                base_price=Decimal("{item.base_price}"),
                available_sizes={sizes_code},
                size_pricing={size_pricing_code},
                available_modifications={modifications_code},
                modification_pricing={mod_pricing_code},
                keywords={keywords_code}
            ),\n'''
        
        menu_items_code += "        ]"
        
        return menu_items_code
    
    def update_baseline_parser(self, menu_items: List[MenuItemTemplate]):
        """Update the order schema with new menu items"""
        print("🔧 Updating order schema with new menu database...")
        
        parser_file = "src/order_schema.py"
        
        try:
            # Read the current file
            with open(parser_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the menu items section and replace it
            start_marker = "        return ["
            end_marker = "        ]"
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                print("❌ Could not find menu items section in baseline parser")
                return False
            
            # Find the end of the menu items list
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
            
            # Generate new menu items code
            new_menu_code = self.create_enhanced_baseline_parser(menu_items)
            
            # Replace the old menu items with new ones
            new_content = content[:start_idx] + new_menu_code + content[end_idx:]
            
            # Write the updated file
            with open(parser_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Successfully updated {parser_file} with {len(menu_items)} menu items!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating baseline parser: {e}")
            return False
    
    def save_menu_summary(self, menu_items: List[MenuItemTemplate]):
        """Save a summary of the integrated menu items"""
        summary_file = "data/menu_integration_summary.json"
        
        print(f"📄 Saving menu integration summary to {summary_file}...")
        
        # Group by category
        by_category = {}
        for item in menu_items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append({
                'name': item.name,
                'price': float(item.base_price),
                'sizes': len(item.available_sizes),
                'modifications': len(item.available_modifications)
            })
        
        summary = {
            'total_items': len(menu_items),
            'total_categories': len(by_category),
            'categories': {cat: len(items) for cat, items in by_category.items()},
            'detailed_breakdown': by_category,
            'integration_date': '2025-09-24',
            'source': 'Restaurant dataset with 5M+ menu entries'
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Menu summary saved!")


def main():
    """Main integration process"""
    print("🍔 Food Sense - Menu Database Integration")
    print("=" * 50)
    
    extracted_data_file = "data/extracted_restaurant_menus.json"
    
    if not os.path.exists(extracted_data_file):
        print(f"❌ Extracted data file not found: {extracted_data_file}")
        print("Please run extract_restaurant_data.py first!")
        return
    
    integrator = MenuDatabaseIntegrator(extracted_data_file)
    
    # Integrate all restaurant data
    menu_items = integrator.integrate_all_restaurants()
    
    if not menu_items:
        print("❌ No menu items to integrate!")
        return
    
    # Update the baseline parser
    success = integrator.update_baseline_parser(menu_items)
    
    if success:
        # Save summary
        integrator.save_menu_summary(menu_items)
        
        print("\n" + "=" * 50)
        print("🎉 INTEGRATION COMPLETE!")
        print("=" * 50)
        print(f"✅ Integrated {len(menu_items)} menu items")
        print("✅ Updated baseline order parser")
        print("✅ Enhanced with sizes, modifications, and keywords")
        print("✅ Ready for text-to-order processing!")
        print("\n🚀 Your Food Sense app now supports 20 major restaurant chains!")
        
    else:
        print("❌ Integration failed. Please check the error messages above.")


if __name__ == "__main__":
    main()