from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import pandas as pd
import json


class MenuItem(BaseModel):
    """Schema for structured menu item data"""
    item_name: str = Field(..., description="Clean, formatted item name")
    category: str = Field(..., description="Food category (e.g., Main Dish, Appetizer, Dessert)")
    cuisine: str = Field(..., description="Cuisine type (e.g., Italian, Chinese, American)")
    attributes: List[str] = Field(default=[], description="Item attributes (e.g., Spicy, Vegetarian, Gluten-Free)")


class RawMenuItem(BaseModel):
    """Schema for raw/messy menu item data"""
    raw_name: str = Field(..., description="Original messy item name")
    restaurant_name: Optional[str] = Field(None, description="Restaurant name if available")
    price: Optional[str] = Field(None, description="Price information if available")


class MenuSchema:
    """Centralized schema definitions and validation"""
    
    CATEGORIES = [
        "Main Dish", "Appetizer", "Dessert", "Beverage", "Side Dish", 
        "Soup", "Salad", "Pizza", "Sandwich", "Pasta", "Burger"
    ]
    
    CUISINES = [
        "American", "Italian", "Chinese", "Mexican", "Indian", "Japanese",
        "Thai", "French", "Mediterranean", "Middle Eastern", "Greek",
        "Korean", "Vietnamese", "Spanish", "Lebanese", "Turkish"
    ]
    
    ATTRIBUTES = [
        "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Spicy", "Mild",
        "Large Portion", "Small Portion", "Halal", "Kosher", "Organic",
        "Low-Carb", "Keto-Friendly", "Protein-Rich", "Healthy", "Fried",
        "Grilled", "Baked", "Steamed", "Raw"
    ]
    
    @classmethod
    def validate_item(cls, item_data: Dict[str, Any]) -> MenuItem:
        """Validate and create a MenuItem from dictionary data"""
        return MenuItem(**item_data)
    
    @classmethod
    def to_dict(cls, item: MenuItem) -> Dict[str, Any]:
        """Convert MenuItem to dictionary"""
        return item.dict()
    
    @classmethod
    def from_json(cls, json_str: str) -> MenuItem:
        """Create MenuItem from JSON string"""
        data = json.loads(json_str)
        return cls.validate_item(data)
    
    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if category is valid"""
        return category in cls.CATEGORIES
    
    @classmethod
    def is_valid_cuisine(cls, cuisine: str) -> bool:
        """Check if cuisine is valid"""
        return cuisine in cls.CUISINES
    
    @classmethod
    def get_valid_attributes(cls, attributes: List[str]) -> List[str]:
        """Filter and return only valid attributes"""
        return [attr for attr in attributes if attr in cls.ATTRIBUTES]