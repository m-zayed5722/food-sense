import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from src.schema import MenuItem, MenuSchema
import json


@dataclass
class CategoryRule:
    """Rule for categorizing menu items"""
    keywords: Set[str]
    category: str
    priority: int = 1  # Higher priority rules are checked first


@dataclass
class CuisineRule:
    """Rule for determining cuisine type"""
    keywords: Set[str]
    cuisine: str
    priority: int = 1


@dataclass
class AttributeRule:
    """Rule for determining attributes"""
    keywords: Set[str]
    attribute: str
    priority: int = 1


class BaselineClassifier:
    """Rule-based baseline classifier for menu items"""
    
    def __init__(self):
        self.category_rules = self._create_category_rules()
        self.cuisine_rules = self._create_cuisine_rules()
        self.attribute_rules = self._create_attribute_rules()
    
    def _create_category_rules(self) -> List[CategoryRule]:
        """Create category classification rules"""
        return [
            # Pizza
            CategoryRule({"pizza", "margherita", "pepperoni", "hawaiian"}, "Pizza", 10),
            
            # Burger
            CategoryRule({"burger", "cheeseburger", "hamburger"}, "Burger", 10),
            
            # Pasta
            CategoryRule({"pasta", "spaghetti", "linguine", "penne", "carbonara", "alfredo", "bolognese"}, "Pasta", 10),
            
            # Sandwich
            CategoryRule({"sandwich", "sub", "hoagie", "panini", "wrap", "gyro"}, "Sandwich", 9),
            
            # Soup
            CategoryRule({"soup", "bisque", "chowder", "broth", "miso"}, "Soup", 9),
            
            # Salad
            CategoryRule({"salad", "caesar", "cobb", "greek salad", "garden"}, "Salad", 9),
            
            # Appetizer
            CategoryRule({"wings", "appetizer", "starter", "nachos", "dip", "rings", "sticks", "rolls", "calamari"}, "Appetizer", 8),
            
            # Dessert
            CategoryRule({"cake", "ice cream", "dessert", "pie", "cookie", "brownie", "tiramisu", "cheesecake", "sundae"}, "Dessert", 8),
            
            # Beverage
            CategoryRule({"juice", "soda", "coffee", "tea", "water", "cola", "beer", "wine", "drink", "beverage"}, "Beverage", 8),
            
            # Side Dish
            CategoryRule({"fries", "bread", "rice", "mashed potatoes", "coleslaw", "side"}, "Side Dish", 7),
            
            # Main Dish (catch-all with lower priority)
            CategoryRule({"chicken", "beef", "fish", "pork", "lamb", "steak", "salmon", "shrimp", "curry", "stir fry", "grilled", "roasted"}, "Main Dish", 5),
        ]
    
    def _create_cuisine_rules(self) -> List[CuisineRule]:
        """Create cuisine classification rules"""
        return [
            # Italian
            CuisineRule({"pizza", "pasta", "spaghetti", "carbonara", "alfredo", "tiramisu", "mozzarella", "italian"}, "Italian", 10),
            
            # Chinese
            CuisineRule({"stir fry", "fried rice", "spring rolls", "dim sum", "szechuan", "kung pao", "chow mein", "chinese"}, "Chinese", 10),
            
            # Mexican
            CuisineRule({"tacos", "burritos", "quesadilla", "nachos", "salsa", "guacamole", "enchiladas", "mexican"}, "Mexican", 10),
            
            # Indian
            CuisineRule({"curry", "tikka", "masala", "biryani", "naan", "tandoori", "vindaloo", "indian"}, "Indian", 10),
            
            # Japanese
            CuisineRule({"sushi", "sashimi", "miso", "teriyaki", "tempura", "ramen", "udon", "japanese"}, "Japanese", 10),
            
            # Thai
            CuisineRule({"pad thai", "tom yum", "green curry", "red curry", "thai basil", "thai"}, "Thai", 10),
            
            # Middle Eastern
            CuisineRule({"shawarma", "hummus", "falafel", "kebab", "baklava", "tabbouleh", "middle eastern"}, "Middle Eastern", 10),
            
            # Greek
            CuisineRule({"gyro", "moussaka", "souvlaki", "tzatziki", "greek salad", "feta", "greek"}, "Greek", 10),
            
            # French
            CuisineRule({"croissant", "quiche", "escargot", "ratatouille", "bouillabaisse", "french"}, "French", 10),
            
            # American (default)
            CuisineRule({"burger", "fries", "wings", "bbq", "american", "club sandwich"}, "American", 5),
        ]
    
    def _create_attribute_rules(self) -> List[AttributeRule]:
        """Create attribute classification rules"""
        return [
            # Dietary restrictions
            AttributeRule({"vegetarian", "veggie", "garden", "vegetable", "no meat"}, "Vegetarian", 10),
            AttributeRule({"vegan", "plant based", "no dairy"}, "Vegan", 10),
            AttributeRule({"gluten free", "gf", "no gluten"}, "Gluten-Free", 10),
            AttributeRule({"dairy free", "no dairy", "lactose free"}, "Dairy-Free", 10),
            AttributeRule({"halal"}, "Halal", 10),
            AttributeRule({"kosher"}, "Kosher", 10),
            
            # Spice level
            AttributeRule({"spicy", "hot", "jalapeño", "chili", "pepper", "buffalo"}, "Spicy", 9),
            AttributeRule({"mild", "not spicy"}, "Mild", 9),
            
            # Portion size
            AttributeRule({"large", "big", "jumbo", "family size", "xl", "extra large"}, "Large Portion", 8),
            AttributeRule({"small", "mini", "little", "snack size", "sm"}, "Small Portion", 8),
            
            # Cooking method
            AttributeRule({"fried", "deep fried", "crispy"}, "Fried", 7),
            AttributeRule({"grilled", "barbecue", "bbq"}, "Grilled", 7),
            AttributeRule({"baked", "oven baked"}, "Baked", 7),
            AttributeRule({"steamed"}, "Steamed", 7),
            AttributeRule({"raw", "fresh", "uncooked"}, "Raw", 7),
            
            # Health attributes
            AttributeRule({"healthy", "fresh", "organic", "natural"}, "Healthy", 6),
            AttributeRule({"protein", "high protein"}, "Protein-Rich", 6),
            AttributeRule({"low carb", "keto", "ketogenic"}, "Low-Carb", 6),
            AttributeRule({"organic"}, "Organic", 6),
        ]
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for rule matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Replace common abbreviations
        text = text.replace("w/", "with")
        text = text.replace("&", "and")
        text = text.replace("chkn", "chicken")
        text = text.replace("sndwch", "sandwich")
        text = text.replace("bbq", "barbecue")
        text = text.replace("lg", "large")
        text = text.replace("sm", "small")
        text = text.replace("med", "medium")
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def classify_category(self, item_name: str) -> str:
        """Classify menu item category using rules"""
        processed_text = self.preprocess_text(item_name)
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.category_rules, key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            for keyword in rule.keywords:
                if keyword in processed_text:
                    return rule.category
        
        # Default category if no rules match
        return "Main Dish"
    
    def classify_cuisine(self, item_name: str) -> str:
        """Classify menu item cuisine using rules"""
        processed_text = self.preprocess_text(item_name)
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.cuisine_rules, key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            for keyword in rule.keywords:
                if keyword in processed_text:
                    return rule.cuisine
        
        # Default cuisine if no rules match
        return "American"
    
    def classify_attributes(self, item_name: str) -> List[str]:
        """Classify menu item attributes using rules"""
        processed_text = self.preprocess_text(item_name)
        attributes = []
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(self.attribute_rules, key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            for keyword in rule.keywords:
                if keyword in processed_text and rule.attribute not in attributes:
                    attributes.append(rule.attribute)
        
        return attributes
    
    def classify_item(self, raw_name: str) -> MenuItem:
        """Classify a single menu item completely"""
        # Clean the item name
        cleaned_name = self._clean_item_name(raw_name)
        
        # Classify all aspects
        category = self.classify_category(raw_name)
        cuisine = self.classify_cuisine(raw_name)
        attributes = self.classify_attributes(raw_name)
        
        return MenuItem(
            item_name=cleaned_name,
            category=category,
            cuisine=cuisine,
            attributes=attributes
        )
    
    def _clean_item_name(self, raw_name: str) -> str:
        """Clean and format item name for display"""
        if not raw_name:
            return ""
        
        # Basic cleaning
        cleaned = raw_name.strip()
        
        # Replace common abbreviations with full words
        cleaned = cleaned.replace("w/", "with")
        cleaned = cleaned.replace("&", "and")
        cleaned = cleaned.replace("chkn", "chicken")
        cleaned = cleaned.replace("sndwch", "sandwich")
        
        # Proper capitalization
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    def batch_classify(self, raw_names: List[str]) -> List[MenuItem]:
        """Classify multiple menu items"""
        return [self.classify_item(name) for name in raw_names]
    
    def get_classification_confidence(self, raw_name: str) -> Dict[str, float]:
        """Return confidence scores for classifications (simple rule counting)"""
        processed_text = self.preprocess_text(raw_name)
        
        confidence = {
            "category": 0.0,
            "cuisine": 0.0,
            "attributes": 0.0
        }
        
        # Count matching keywords for each type
        category_matches = sum(1 for rule in self.category_rules 
                             for keyword in rule.keywords 
                             if keyword in processed_text)
        
        cuisine_matches = sum(1 for rule in self.cuisine_rules 
                            for keyword in rule.keywords 
                            if keyword in processed_text)
        
        attribute_matches = sum(1 for rule in self.attribute_rules 
                              for keyword in rule.keywords 
                              if keyword in processed_text)
        
        # Simple confidence based on number of matches
        confidence["category"] = min(category_matches / 3.0, 1.0)
        confidence["cuisine"] = min(cuisine_matches / 3.0, 1.0)
        confidence["attributes"] = min(attribute_matches / 5.0, 1.0)
        
        return confidence


# Example usage
if __name__ == "__main__":
    classifier = BaselineClassifier()
    
    # Test with some sample items
    test_items = [
        "chiken shawarma w/ fries",
        "MARGHERITA PIZA",
        "beef burger w cheese",
        "pad thai noodles",
        "vegetable stir fry",
        "buffalo wings"
    ]
    
    print("Baseline Classification Results:")
    print("=" * 60)
    
    for item in test_items:
        result = classifier.classify_item(item)
        confidence = classifier.get_classification_confidence(item)
        
        print(f"Raw: {item}")
        print(f"Cleaned: {result.item_name}")
        print(f"Category: {result.category} (confidence: {confidence['category']:.2f})")
        print(f"Cuisine: {result.cuisine} (confidence: {confidence['cuisine']:.2f})")
        print(f"Attributes: {result.attributes} (confidence: {confidence['attributes']:.2f})")
        print("-" * 60)