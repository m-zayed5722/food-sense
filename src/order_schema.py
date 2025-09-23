"""
Order Schema for Text-to-Order Feature
Defines data structures for order items, modifications, and complete orders
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal


class SizeType(str, Enum):
    """Available item sizes"""
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    EXTRA_LARGE = "Extra Large"


class ModificationType(str, Enum):
    """Types of modifications"""
    ADD = "add"
    REMOVE = "remove"
    SUBSTITUTE = "substitute"
    EXTRA = "extra"
    ON_SIDE = "on_side"


class Modification(BaseModel):
    """Individual modification to an order item"""
    type: ModificationType
    item: str
    description: Optional[str] = None
    price_change: Decimal = Field(default=Decimal('0.00'))
    
    class Config:
        use_enum_values = True


class OrderItem(BaseModel):
    """Individual item in an order"""
    name: str = Field(..., description="Name of the menu item")
    quantity: int = Field(default=1, ge=1, description="Quantity ordered")
    size: Optional[SizeType] = Field(default=None, description="Size if applicable")
    base_price: Decimal = Field(default=Decimal('0.00'), description="Base price for the item")
    modifications: List[Modification] = Field(default_factory=list, description="Modifications to the item")
    special_instructions: Optional[str] = Field(default=None, description="Special preparation instructions")
    
    @property
    def total_price(self) -> Decimal:
        """Calculate total price including modifications"""
        mod_price = sum(mod.price_change for mod in self.modifications)
        return (self.base_price + mod_price) * self.quantity
    
    class Config:
        use_enum_values = True


class Order(BaseModel):
    """Complete order containing multiple items"""
    items: List[OrderItem] = Field(default_factory=list, description="Items in the order")
    customer_notes: Optional[str] = Field(default=None, description="Special notes from customer")
    estimated_time: Optional[int] = Field(default=None, description="Estimated preparation time in minutes")
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate order subtotal"""
        return sum(item.total_price for item in self.items)
    
    @property
    def tax_amount(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate tax amount (default 8%)"""
        return self.subtotal * tax_rate
    
    @property
    def total_amount(self, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate total amount including tax"""
        return self.subtotal + self.tax_amount
    
    @property
    def item_count(self) -> int:
        """Total number of items in order"""
        return sum(item.quantity for item in self.items)


class MenuItemTemplate(BaseModel):
    """Template for menu items with pricing and options"""
    name: str
    category: str
    base_price: Decimal
    available_sizes: List[SizeType] = Field(default_factory=list)
    size_pricing: Dict[str, Decimal] = Field(default_factory=dict)  # Size -> additional price
    available_modifications: List[str] = Field(default_factory=list)
    modification_pricing: Dict[str, Decimal] = Field(default_factory=dict)  # Modification -> price change
    keywords: List[str] = Field(default_factory=list)  # Alternative names/keywords
    
    class Config:
        use_enum_values = True


class OrderSchema:
    """Schema validation and utilities for orders"""
    
    # Common size keywords
    SIZE_KEYWORDS = {
        'small': SizeType.SMALL,
        'sm': SizeType.SMALL,
        'medium': SizeType.MEDIUM,
        'med': SizeType.MEDIUM,
        'm': SizeType.MEDIUM,
        'large': SizeType.LARGE,
        'lg': SizeType.LARGE,
        'l': SizeType.LARGE,
        'extra large': SizeType.EXTRA_LARGE,
        'xl': SizeType.EXTRA_LARGE,
        'jumbo': SizeType.EXTRA_LARGE
    }
    
    # Common modification keywords
    MODIFICATION_KEYWORDS = {
        'add': ModificationType.ADD,
        'extra': ModificationType.EXTRA,
        'remove': ModificationType.REMOVE,
        'no': ModificationType.REMOVE,
        'without': ModificationType.REMOVE,
        'substitute': ModificationType.SUBSTITUTE,
        'replace': ModificationType.SUBSTITUTE,
        'on the side': ModificationType.ON_SIDE,
        'side': ModificationType.ON_SIDE
    }
    
    # Quantity keywords
    QUANTITY_KEYWORDS = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'a': 1, 'an': 1, 'single': 1, 'double': 2, 'triple': 3
    }
    
    @classmethod
    def normalize_size(cls, size_text: str) -> Optional[SizeType]:
        """Normalize size text to SizeType enum"""
        if not size_text:
            return None
        return cls.SIZE_KEYWORDS.get(size_text.lower().strip())
    
    @classmethod
    def normalize_modification_type(cls, mod_text: str) -> ModificationType:
        """Normalize modification text to ModificationType enum"""
        if not mod_text:
            return ModificationType.ADD
        return cls.MODIFICATION_KEYWORDS.get(mod_text.lower().strip(), ModificationType.ADD)
    
    @classmethod
    def extract_quantity(cls, text: str) -> int:
        """Extract quantity from text"""
        text_lower = text.lower().strip()
        
        # Check for number keywords
        for word, qty in cls.QUANTITY_KEYWORDS.items():
            if word in text_lower:
                return qty
        
        # Look for digits
        import re
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        
        return 1  # Default quantity
    
    @classmethod
    def is_valid_order_item(cls, item: Dict[str, Any]) -> bool:
        """Validate order item data"""
        required_fields = ['name']
        return all(field in item for field in required_fields)
    
    @classmethod
    def create_sample_menu(cls) -> List[MenuItemTemplate]:
        """Create comprehensive sample menu for testing"""
        return [
            # McDonald's
            MenuItemTemplate(
                name="Big Mac",
                category="Burger",
                base_price=Decimal('6.49'),
                available_sizes=[SizeType.MEDIUM],
                available_modifications=["special sauce", "lettuce", "cheese", "pickles", "onions", "no special sauce", "extra cheese"],
                modification_pricing={
                    "extra cheese": Decimal('0.50'),
                    "extra special sauce": Decimal('0.30')
                },
                keywords=["big mac", "bigmac", "big-mac", "mcdonalds big mac"]
            ),
            MenuItemTemplate(
                name="McChicken",
                category="Burger",
                base_price=Decimal('4.99'),
                available_sizes=[SizeType.MEDIUM],
                available_modifications=["mayo", "lettuce", "pickles", "onions", "ketchup", "no mayo", "extra mayo"],
                modification_pricing={
                    "extra mayo": Decimal('0.30'),
                    "extra lettuce": Decimal('0.25')
                },
                keywords=["mcchicken", "mc chicken", "chicken burger", "chicken sandwich", "mcdonalds chicken"]
            ),
            MenuItemTemplate(
                name="French Fries",
                category="Side",
                base_price=Decimal('2.49'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('0.50'),
                    "Large": Decimal('1.00')
                },
                available_modifications=["salt", "no salt", "ketchup", "extra salt"],
                keywords=["fries", "french fries", "fires", "mcdonalds fries", "mcd fries"]  # Common typo
            ),
            
            # Domino's
            MenuItemTemplate(
                name="Pepperoni Pizza",
                category="Pizza",
                base_price=Decimal('12.99'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('3.00'),
                    "Large": Decimal('6.00')
                },
                available_modifications=["extra cheese", "extra pepperoni", "thin crust", "thick crust", "no cheese"],
                modification_pricing={
                    "extra cheese": Decimal('1.50'),
                    "extra pepperoni": Decimal('2.00'),
                    "thin crust": Decimal('0.00'),
                    "thick crust": Decimal('1.00')
                },
                keywords=["pepperoni pizza", "pepperoni", "dominos pizza", "domino's pizza", "pizza"]
            ),
            MenuItemTemplate(
                name="Chicken Wings",
                category="Appetizer",
                base_price=Decimal('9.99'),
                available_modifications=["buffalo sauce", "bbq sauce", "honey mustard", "ranch", "blue cheese", "hot sauce"],
                modification_pricing={
                    "extra sauce": Decimal('0.50')
                },
                keywords=["chicken wings", "wings", "dominos wings", "buffalo wings", "bbq wings"]
            ),
            MenuItemTemplate(
                name="Cheesy Bread",
                category="Side",
                base_price=Decimal('6.99'),
                available_modifications=["extra cheese", "garlic", "marinara sauce", "ranch"],
                modification_pricing={
                    "extra cheese": Decimal('1.00')
                },
                keywords=["cheesy bread", "cheese bread", "dominos bread", "garlic bread"]
            ),
            
            # Wingstop
            MenuItemTemplate(
                name="Lemon Pepper Wings",
                category="Main",
                base_price=Decimal('11.99'),
                available_modifications=["ranch", "blue cheese", "extra seasoning", "mild", "hot"],
                keywords=["lemon pepper wings", "lemon pepper", "wingstop lemon pepper", "lp wings"]
            ),
            MenuItemTemplate(
                name="Garlic Parmesan Wings",
                category="Main", 
                base_price=Decimal('11.99'),
                available_modifications=["ranch", "blue cheese", "extra garlic", "extra parmesan"],
                modification_pricing={
                    "extra parmesan": Decimal('0.75')
                },
                keywords=["garlic parmesan wings", "garlic parm", "gp wings", "parmesan wings", "wingstop garlic"]
            ),
            MenuItemTemplate(
                name="Cajun Fried Corn",
                category="Side",
                base_price=Decimal('4.99'),
                available_modifications=["extra cajun seasoning", "butter", "no seasoning"],
                keywords=["cajun corn", "fried corn", "cajun fried corn", "wingstop corn", "corn"]
            ),
            
            # Shawarma Restaurant
            MenuItemTemplate(
                name="Chicken Shawarma Wrap",
                category="Main",
                base_price=Decimal('8.99'),
                available_modifications=["tahini", "garlic sauce", "hot sauce", "pickles", "tomatoes", "onions", "no sauce", "extra meat"],
                modification_pricing={
                    "extra meat": Decimal('2.50'),
                    "extra sauce": Decimal('0.50')
                },
                keywords=["chicken shawarma", "shawarma wrap", "chicken wrap", "shawarma", "chk shawarma"]
            ),
            MenuItemTemplate(
                name="Beef Shawarma Plate",
                category="Main",
                base_price=Decimal('12.99'),
                available_modifications=["tahini", "garlic sauce", "hot sauce", "rice", "salad", "pita bread", "extra meat"],
                modification_pricing={
                    "extra meat": Decimal('3.00'),
                    "extra rice": Decimal('1.00')
                },
                keywords=["beef shawarma", "shawarma plate", "beef plate", "shawarma platter", "beef shawarma plate"]
            ),
            MenuItemTemplate(
                name="Falafel Wrap",
                category="Main",
                base_price=Decimal('7.99'),
                available_modifications=["tahini", "hummus", "hot sauce", "pickles", "tomatoes", "cucumber", "extra falafel"],
                modification_pricing={
                    "extra falafel": Decimal('1.50')
                },
                keywords=["falafel wrap", "falafel", "vegetarian wrap", "veg wrap", "falafel sandwich"]
            ),
            
            # Dairy Queen
            MenuItemTemplate(
                name="Oreo Blizzard",
                category="Dessert",
                base_price=Decimal('4.99'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('1.50'),
                    "Large": Decimal('2.50')
                },
                available_modifications=["extra oreo", "chocolate sauce", "caramel sauce"],
                modification_pricing={
                    "extra oreo": Decimal('0.75')
                },
                keywords=["oreo blizzard", "blizzard", "oreo", "dq blizzard", "dairy queen oreo"]
            ),
            MenuItemTemplate(
                name="Reese's Blizzard",
                category="Dessert",
                base_price=Decimal('4.99'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('1.50'),
                    "Large": Decimal('2.50')
                },
                available_modifications=["extra reese's", "chocolate sauce", "peanut butter sauce"],
                modification_pricing={
                    "extra reese's": Decimal('0.75')
                },
                keywords=["reeses blizzard", "reese's blizzard", "reese blizzard", "peanut butter blizzard", "dq reeses"]
            ),
            MenuItemTemplate(
                name="DQ Cheeseburger",
                category="Burger",
                base_price=Decimal('5.99'),
                available_modifications=["cheese", "lettuce", "tomato", "pickles", "onions", "ketchup", "mustard", "mayo", "no cheese"],
                modification_pricing={
                    "extra cheese": Decimal('0.50'),
                    "bacon": Decimal('1.50')
                },
                keywords=["dq cheeseburger", "dairy queen cheeseburger", "dq burger", "cheeseburger", "dairy queen burger"]
            ),
            MenuItemTemplate(
                name="Chicken Strip Basket",
                category="Main",
                base_price=Decimal('8.99'),
                available_modifications=["fries", "onion rings", "honey mustard", "bbq sauce", "ranch", "extra strips"],
                modification_pricing={
                    "extra strips": Decimal('2.00'),
                    "onion rings": Decimal('1.00')
                },
                keywords=["chicken strips", "chicken strip basket", "dq chicken", "chicken tenders", "strips basket"]
            ),
            
            # Additional common drinks and sides
            MenuItemTemplate(
                name="Sprite",
                category="Beverage",
                base_price=Decimal('1.99'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('0.30'),
                    "Large": Decimal('0.60')
                },
                available_modifications=["ice", "no ice", "extra ice", "lemon"],
                keywords=["sprite", "lemon lime soda", "lemon-lime"]
            ),
            MenuItemTemplate(
                name="Coca Cola",
                category="Beverage",
                base_price=Decimal('1.99'),
                available_sizes=[SizeType.SMALL, SizeType.MEDIUM, SizeType.LARGE],
                size_pricing={
                    "Small": Decimal('0.00'),
                    "Medium": Decimal('0.30'),
                    "Large": Decimal('0.60')
                },
                available_modifications=["ice", "no ice", "extra ice"],
                keywords=["coke", "coca cola", "cola", "pepsi"]
            )
        ]


# Export commonly used types
__all__ = [
    'OrderItem', 'Order', 'Modification', 'MenuItemTemplate', 'OrderSchema',
    'SizeType', 'ModificationType'
]