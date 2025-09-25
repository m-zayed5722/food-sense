#!/usr/bin/env python3
"""
Restaurant Data Extractor
Extracts popular restaurant chains and their menu items from the restaurant dataset
"""

import pandas as pd
import json
from typing import Dict, List, Set
from collections import defaultdict, Counter
import re
import sys
import os

# Add src to path
sys.path.append('src')
from src.order_schema import MenuItemTemplate, SizeType, ModificationType

class RestaurantDataExtractor:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.restaurants_file = os.path.join(data_path, "restaurants.csv")
        self.menus_file = os.path.join(data_path, "restaurant-menus.csv")
        
        # Target popular restaurant chains to focus on
        self.target_chains = [
            "McDonald's", "KFC", "Burger King", "Subway", "Pizza Hut", 
            "Domino's", "Taco Bell", "Starbucks", "Dunkin'", "Chipotle",
            "Wendy's", "Dairy Queen", "Papa John's", "Little Caesars",
            "Arby's", "Popeyes", "Tim Hortons", "Sonic", "Carl's Jr",
            "Jack in the Box", "Five Guys", "In-N-Out", "Wingstop",
            "Panda Express", "Chick-fil-A"
        ]
    
    def load_restaurants_sample(self, sample_size: int = 10000) -> pd.DataFrame:
        """Load a sample of restaurants to find popular chains"""
        print(f"📊 Loading restaurants sample ({sample_size:,} rows)...")
        try:
            df = pd.read_csv(self.restaurants_file, nrows=sample_size)
            print(f"✅ Loaded {len(df):,} restaurants")
            return df
        except Exception as e:
            print(f"❌ Error loading restaurants: {e}")
            return pd.DataFrame()
    
    def find_popular_chains(self, restaurants_df: pd.DataFrame) -> Dict[str, List[int]]:
        """Find restaurant chains and their IDs"""
        print("🔍 Analyzing restaurant chains...")
        
        chain_restaurants = defaultdict(list)
        
        for _, row in restaurants_df.iterrows():
            name = str(row['name']).strip()
            restaurant_id = row['id']
            
            # Check if this restaurant matches any target chain
            for chain in self.target_chains:
                if chain.lower() in name.lower():
                    chain_restaurants[chain].append(restaurant_id)
                    break
        
        # Filter chains with at least 3 locations
        popular_chains = {
            chain: ids for chain, ids in chain_restaurants.items() 
            if len(ids) >= 3
        }
        
        print(f"📈 Found {len(popular_chains)} popular chains:")
        for chain, ids in popular_chains.items():
            print(f"  • {chain}: {len(ids)} locations")
        
        return popular_chains
    
    def extract_menu_items(self, restaurant_ids: List[int], chain_name: str, limit: int = 50) -> List[Dict]:
        """Extract menu items for specific restaurant IDs"""
        print(f"🍽️ Extracting menu items for {chain_name}...")
        
        menu_items = []
        processed_count = 0
        
        # Read menu file in chunks to handle large size
        chunk_size = 10000
        for chunk in pd.read_csv(self.menus_file, chunksize=chunk_size):
            # Filter for our target restaurants
            filtered_chunk = chunk[chunk['restaurant_id'].isin(restaurant_ids)]
            
            for _, row in filtered_chunk.iterrows():
                if len(menu_items) >= limit:
                    break
                
                item = {
                    'chain': chain_name,
                    'restaurant_id': row['restaurant_id'],
                    'category': str(row.get('category', 'Main Dish')),
                    'name': str(row['name']).strip(),
                    'description': str(row.get('description', '')),
                    'price': self.parse_price(row.get('price', 0))
                }
                
                # Skip duplicates and invalid items
                if (item['name'] and item['name'] != 'nan' and 
                    not any(existing['name'].lower() == item['name'].lower() 
                           for existing in menu_items)):
                    menu_items.append(item)
            
            processed_count += len(chunk)
            if processed_count % 100000 == 0:
                print(f"  Processed {processed_count:,} menu entries...")
            
            if len(menu_items) >= limit:
                break
        
        print(f"✅ Extracted {len(menu_items)} menu items for {chain_name}")
        return menu_items
    
    def parse_price(self, price_str) -> float:
        """Parse price string to float"""
        if pd.isna(price_str) or price_str == '' or price_str == 'nan':
            return 5.99  # Default price
        
        try:
            # Remove currency symbols and extract number
            price_clean = re.sub(r'[^\d\.]', '', str(price_str))
            if price_clean:
                return float(price_clean)
            return 5.99
        except:
            return 5.99
    
    def categorize_menu_item(self, item: Dict) -> str:
        """Categorize menu item based on name and description"""
        name = item['name'].lower()
        desc = item['description'].lower()
        text = f"{name} {desc}"
        
        # Category mapping
        if any(word in text for word in ['pizza', 'pepperoni', 'margherita']):
            return 'Pizza'
        elif any(word in text for word in ['burger', 'cheeseburger', 'whopper']):
            return 'Burger'
        elif any(word in text for word in ['fries', 'fry', 'potato']):
            return 'Side Dish'
        elif any(word in text for word in ['drink', 'soda', 'coke', 'pepsi', 'sprite', 'coffee', 'tea']):
            return 'Beverage'
        elif any(word in text for word in ['chicken', 'nugget', 'wing', 'tender']):
            return 'Main Dish'
        elif any(word in text for word in ['salad', 'lettuce', 'greens']):
            return 'Salad'
        elif any(word in text for word in ['sandwich', 'sub', 'wrap']):
            return 'Sandwich'
        elif any(word in text for word in ['dessert', 'ice cream', 'cookie', 'cake', 'pie']):
            return 'Dessert'
        else:
            return 'Main Dish'
    
    def detect_sizes_and_modifications(self, name: str, description: str) -> Dict:
        """Detect available sizes and modifications from item name/description"""
        text = f"{name} {description}".lower()
        
        sizes = []
        if any(word in text for word in ['small', 'medium', 'large', 'extra large']):
            sizes = [SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE]
        
        modifications = []
        if any(word in text for word in ['cheese', 'extra cheese']):
            modifications.append('cheese')
        if any(word in text for word in ['bacon', 'extra bacon']):
            modifications.append('bacon')
        if any(word in text for word in ['sauce', 'ketchup', 'mayo']):
            modifications.append('sauce')
        
        return {
            'available_sizes': sizes,
            'available_modifications': modifications
        }
    
    def create_menu_template(self, item: Dict) -> MenuItemTemplate:
        """Create MenuItemTemplate from extracted item"""
        category = self.categorize_menu_item(item)
        extras = self.detect_sizes_and_modifications(item['name'], item['description'])
        
        return MenuItemTemplate(
            name=item['name'],
            category=category,
            base_price=item['price'],
            available_sizes=extras['available_sizes'],
            available_modifications=extras['available_modifications']
        )
    
    def extract_all_chains(self, max_chains: int = 20, items_per_chain: int = 15) -> Dict[str, List[MenuItemTemplate]]:
        """Extract menu items for all popular chains"""
        print(f"🚀 Starting extraction for top {max_chains} restaurant chains...")
        
        # Load restaurants and find chains
        restaurants_df = self.load_restaurants_sample(50000)  # Larger sample for better chain detection
        if restaurants_df.empty:
            return {}
        
        popular_chains = self.find_popular_chains(restaurants_df)
        
        # Limit to max_chains
        selected_chains = dict(list(popular_chains.items())[:max_chains])
        
        all_menu_items = {}
        
        for chain_name, restaurant_ids in selected_chains.items():
            try:
                # Extract menu items for this chain
                raw_items = self.extract_menu_items(restaurant_ids[:5], chain_name, items_per_chain)
                
                # Convert to MenuItemTemplate objects
                menu_templates = []
                for item in raw_items:
                    try:
                        template = self.create_menu_template(item)
                        menu_templates.append(template)
                    except Exception as e:
                        print(f"  ⚠️ Skipped item '{item['name']}': {e}")
                
                if menu_templates:
                    all_menu_items[chain_name] = menu_templates
                    print(f"✅ {chain_name}: {len(menu_templates)} items")
                
            except Exception as e:
                print(f"❌ Error processing {chain_name}: {e}")
        
        return all_menu_items
    
    def save_extracted_data(self, menu_data: Dict[str, List[MenuItemTemplate]], output_file: str):
        """Save extracted menu data to JSON file"""
        print(f"💾 Saving extracted data to {output_file}...")
        
        # Convert to serializable format
        serializable_data = {}
        for chain, items in menu_data.items():
            serializable_data[chain] = []
            for item in items:
                item_dict = {
                    'name': item.name,
                    'category': item.category,
                    'base_price': float(item.base_price),
                    'available_sizes': [size.value if hasattr(size, 'value') else str(size) for size in item.available_sizes],
                    'available_modifications': item.available_modifications
                }
                serializable_data[chain].append(item_dict)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data saved successfully!")
        return serializable_data


def main():
    """Main extraction process"""
    print("🍔 Food Sense - Restaurant Data Extractor")
    print("=" * 50)
    
    data_path = r"C:\Users\mzaye\OneDrive\Documents\Data\restaurants\archive"
    output_file = "data/extracted_restaurant_menus.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    extractor = RestaurantDataExtractor(data_path)
    
    # Extract menu data for 15-20 popular chains
    menu_data = extractor.extract_all_chains(max_chains=20, items_per_chain=15)
    
    if menu_data:
        # Save the data
        saved_data = extractor.save_extracted_data(menu_data, output_file)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 50)
        
        total_items = sum(len(items) for items in menu_data.values())
        print(f"🏪 Restaurant Chains: {len(menu_data)}")
        print(f"🍽️ Total Menu Items: {total_items}")
        
        print("\n📋 CHAIN BREAKDOWN:")
        for chain, items in menu_data.items():
            print(f"  • {chain}: {len(items)} items")
        
        print(f"\n✅ Data saved to: {output_file}")
        print("🚀 Ready to integrate into Food Sense app!")
        
    else:
        print("❌ No menu data extracted. Please check the dataset files.")


if __name__ == "__main__":
    main()