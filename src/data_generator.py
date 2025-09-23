import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any, Optional
from src.schema import RawMenuItem, MenuSchema
import re


class DataGenerator:
    """Generate synthetic messy menu data for testing"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        self.base_items = self._create_base_menu_items()
        self.typo_patterns = self._create_typo_patterns()
        self.abbreviations = self._create_abbreviations()
    
    def _create_base_menu_items(self) -> List[Dict[str, Any]]:
        """Create clean base menu items"""
        return [
            # Main Dishes
            {"name": "Chicken Shawarma with Fries", "category": "Main Dish", "cuisine": "Middle Eastern", "attributes": ["Spicy", "Large Portion", "Halal"]},
            {"name": "Margherita Pizza", "category": "Pizza", "cuisine": "Italian", "attributes": ["Vegetarian"]},
            {"name": "Beef Burger with Cheese", "category": "Burger", "cuisine": "American", "attributes": ["Large Portion"]},
            {"name": "Pad Thai Noodles", "category": "Main Dish", "cuisine": "Thai", "attributes": ["Spicy", "Gluten-Free"]},
            {"name": "Chicken Caesar Salad", "category": "Salad", "cuisine": "American", "attributes": ["Healthy", "Protein-Rich"]},
            {"name": "Fish and Chips", "category": "Main Dish", "cuisine": "American", "attributes": ["Fried", "Large Portion"]},
            {"name": "Vegetable Stir Fry", "category": "Main Dish", "cuisine": "Chinese", "attributes": ["Vegetarian", "Healthy"]},
            {"name": "Chicken Tikka Masala", "category": "Main Dish", "cuisine": "Indian", "attributes": ["Spicy", "Dairy-Free"]},
            {"name": "Spaghetti Carbonara", "category": "Pasta", "cuisine": "Italian", "attributes": ["Large Portion"]},
            {"name": "Greek Gyro", "category": "Sandwich", "cuisine": "Greek", "attributes": ["Halal", "Spicy"]},
            
            # Appetizers
            {"name": "Buffalo Wings", "category": "Appetizer", "cuisine": "American", "attributes": ["Spicy", "Fried"]},
            {"name": "Mozzarella Sticks", "category": "Appetizer", "cuisine": "Italian", "attributes": ["Vegetarian", "Fried"]},
            {"name": "Spring Rolls", "category": "Appetizer", "cuisine": "Chinese", "attributes": ["Vegetarian", "Steamed"]},
            {"name": "Hummus with Pita", "category": "Appetizer", "cuisine": "Middle Eastern", "attributes": ["Vegetarian", "Healthy"]},
            {"name": "Calamari Rings", "category": "Appetizer", "cuisine": "Italian", "attributes": ["Fried"]},
            
            # Soups
            {"name": "Tomato Soup", "category": "Soup", "cuisine": "American", "attributes": ["Vegetarian", "Healthy"]},
            {"name": "Chicken Noodle Soup", "category": "Soup", "cuisine": "American", "attributes": ["Healthy"]},
            {"name": "Miso Soup", "category": "Soup", "cuisine": "Japanese", "attributes": ["Vegetarian", "Healthy"]},
            
            # Desserts
            {"name": "Chocolate Cake", "category": "Dessert", "cuisine": "American", "attributes": ["Large Portion"]},
            {"name": "Tiramisu", "category": "Dessert", "cuisine": "Italian", "attributes": []},
            {"name": "Ice Cream Sundae", "category": "Dessert", "cuisine": "American", "attributes": ["Large Portion"]},
            
            # Beverages
            {"name": "Fresh Orange Juice", "category": "Beverage", "cuisine": "American", "attributes": ["Healthy", "Organic"]},
            {"name": "Green Tea", "category": "Beverage", "cuisine": "Japanese", "attributes": ["Healthy"]},
            {"name": "Coca Cola", "category": "Beverage", "cuisine": "American", "attributes": []},
            
            # Side Dishes
            {"name": "French Fries", "category": "Side Dish", "cuisine": "American", "attributes": ["Fried", "Vegetarian"]},
            {"name": "Garlic Bread", "category": "Side Dish", "cuisine": "Italian", "attributes": ["Vegetarian"]},
            {"name": "Rice Pilaf", "category": "Side Dish", "cuisine": "Middle Eastern", "attributes": ["Vegetarian"]},
        ]
    
    def _create_typo_patterns(self) -> Dict[str, str]:
        """Common typo patterns to apply to menu items"""
        return {
            'chicken': 'chiken',
            'cheese': 'chese',
            'sandwich': 'sandwhich',
            'pizza': 'piza',
            'vegetables': 'vegtables',
            'chocolate': 'chocolat',
            'with': 'w/',
            'and': '&',
            'fresh': 'freash',
            'grilled': 'griled',
            'special': 'specail',
            'delicious': 'delicous',
            'homemade': 'home made',
            'traditional': 'traditonal'
        }
    
    def _create_abbreviations(self) -> Dict[str, str]:
        """Common abbreviations used in menu items"""
        return {
            'chicken': 'chkn',
            'sandwich': 'sndwch',
            'with': 'w/',
            'and': '&',
            'barbeque': 'bbq',
            'barbecue': 'bbq',
            'french fries': 'fries',
            'vegetables': 'vegs',
            'deluxe': 'dlx',
            'special': 'spcl',
            'original': 'orig',
            'extra': 'x-tra',
            'large': 'lg',
            'small': 'sm',
            'medium': 'med'
        }
    
    def add_typos(self, text: str, typo_probability: float = 0.3) -> str:
        """Add random typos to text"""
        words = text.lower().split()
        result = []
        
        for word in words:
            if random.random() < typo_probability and word in self.typo_patterns:
                result.append(self.typo_patterns[word])
            else:
                result.append(word)
        
        return ' '.join(result)
    
    def add_abbreviations(self, text: str, abbrev_probability: float = 0.4) -> str:
        """Add abbreviations to text"""
        text_lower = text.lower()
        result = text_lower
        
        for full, abbrev in self.abbreviations.items():
            if random.random() < abbrev_probability and full in text_lower:
                result = result.replace(full, abbrev)
        
        return result
    
    def add_formatting_issues(self, text: str) -> str:
        """Add random formatting issues"""
        # Random capitalization
        if random.random() < 0.3:
            text = text.upper()
        elif random.random() < 0.3:
            text = text.lower()
        
        # Random extra spaces
        if random.random() < 0.2:
            text = re.sub(r'\s+', '  ', text)
        
        # Random punctuation issues
        if random.random() < 0.2:
            text = text.replace(',', '')
        
        # Random missing/extra characters
        if random.random() < 0.1:
            pos = random.randint(0, len(text) - 1)
            text = text[:pos] + text[pos+1:]  # Remove character
        
        return text.strip()
    
    def generate_messy_data(self, num_items: int = 100) -> List[Dict[str, Any]]:
        """Generate messy menu data"""
        messy_items = []
        
        for i in range(num_items):
            # Select random base item
            base_item = random.choice(self.base_items)
            original_name = base_item["name"]
            
            # Apply random transformations
            messy_name = original_name
            
            # Apply typos
            if random.random() < 0.4:
                messy_name = self.add_typos(messy_name)
            
            # Apply abbreviations
            if random.random() < 0.3:
                messy_name = self.add_abbreviations(messy_name)
            
            # Apply formatting issues
            if random.random() < 0.5:
                messy_name = self.add_formatting_issues(messy_name)
            
            # Create messy item
            messy_item = {
                "raw_name": messy_name,
                "restaurant_name": f"Restaurant {random.randint(1, 20)}",
                "price": f"${random.uniform(5.99, 29.99):.2f}",
                # Ground truth for evaluation
                "ground_truth": {
                    "item_name": original_name,
                    "category": base_item["category"],
                    "cuisine": base_item["cuisine"],
                    "attributes": base_item["attributes"]
                }
            }
            
            messy_items.append(messy_item)
        
        return messy_items
    
    def save_to_csv(self, data: List[Dict[str, Any]], filepath: str):
        """Save data to CSV file"""
        # Flatten the data for CSV
        flattened_data = []
        for item in data:
            flat_item = {
                "raw_name": item["raw_name"],
                "restaurant_name": item.get("restaurant_name", ""),
                "price": item.get("price", ""),
                "ground_truth_name": item["ground_truth"]["item_name"],
                "ground_truth_category": item["ground_truth"]["category"],
                "ground_truth_cuisine": item["ground_truth"]["cuisine"],
                "ground_truth_attributes": "|".join(item["ground_truth"]["attributes"])
            }
            flattened_data.append(flat_item)
        
        df = pd.DataFrame(flattened_data)
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
    
    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        df = pd.read_csv(filepath)
        data = []
        
        for _, row in df.iterrows():
            item = {
                "raw_name": row["raw_name"],
                "restaurant_name": row.get("restaurant_name", ""),
                "price": row.get("price", ""),
                "ground_truth": {
                    "item_name": row["ground_truth_name"],
                    "category": row["ground_truth_category"],
                    "cuisine": row["ground_truth_cuisine"],
                    "attributes": row["ground_truth_attributes"].split("|") if row["ground_truth_attributes"] else []
                }
            }
            data.append(item)
        
        return data


class DataCleaner:
    """Clean and preprocess menu data"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Basic text cleaning"""
        if pd.isna(text):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', str(text)).strip()
        
        # Fix common patterns
        text = text.replace('w/', 'with')
        text = text.replace('&', 'and')
        text = text.replace('  ', ' ')
        
        return text
    
    @staticmethod
    def normalize_price(price_str: str) -> float:
        """Extract numeric price from string"""
        if pd.isna(price_str):
            return 0.0
        
        # Extract numbers and decimal points
        price_match = re.search(r'\d+\.?\d*', str(price_str))
        if price_match:
            return float(price_match.group())
        return 0.0


# Example usage and data generation
if __name__ == "__main__":
    generator = DataGenerator()
    
    # Generate sample data
    sample_data = generator.generate_messy_data(50)
    
    # Save to CSV
    generator.save_to_csv(sample_data, "../data/sample_messy_menu.csv")
    
    # Display some examples
    print("Sample messy menu items:")
    for item in sample_data[:5]:
        print(f"Raw: {item['raw_name']}")
        print(f"Ground Truth: {item['ground_truth']['item_name']}")
        print(f"Category: {item['ground_truth']['category']}")
        print("-" * 50)